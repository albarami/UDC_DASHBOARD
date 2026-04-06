# Start the server with:
#   python main.py
# This uses subprocess to guarantee the correct Python interpreter for reload.

"""
UDC CEO Dashboard — FastAPI Backend

Integration layer: receives CEO messages, sends them to C1 with governed
tool definitions, executes tools when C1 calls them, streams the final
C1-rendered dashboard response back to the frontend.
"""

import json
import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from thesys_genui_sdk.context import get_assistant_message, write_content, write_think_item
from thesys_genui_sdk.fast_api import with_c1_response

from system_prompt import SYSTEM_PROMPT
from tools import TOOL_DEFINITIONS, TOOL_IMPLEMENTATIONS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("udc-dashboard")

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="UDC CEO Dashboard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.environ["THESYS_API_KEY"],
    base_url="https://api.thesys.dev/v1/embed",
)

MODEL = "c1/anthropic/claude-sonnet-4/v-20251230"

THINKING_LABELS: dict[str, tuple[str, str]] = {
    "get_executive_overview": (
        "Building your executive dashboard",
        "Pulling portfolio performance, financial position, and risk indicators",
    ),
    "get_commercial_leasing_dashboard": (
        "Analyzing commercial portfolio",
        "Occupancy, tenant risk, lease expiry, and zone performance",
    ),
    "get_finance_dashboard": (
        "Loading financial position",
        "Revenue, profitability, cash flow, and receivables",
    ),
    "get_maintenance_dashboard": (
        "Reviewing operations",
        "Work orders, SLA compliance, contractor performance, and satisfaction",
    ),
    "get_asset_attention_index": (
        "Scoring asset priorities",
        "Ranking all assets by vacancy, maintenance, receivables, and risk",
    ),
    "get_collections_priority": (
        "Prioritizing collections",
        "Ranking overdue accounts by amount, age, and tenant risk",
    ),
    "get_zone_deep_dive": (
        "Drilling into zone data",
        "Loading asset-level detail for the selected zone",
    ),
}

message_stores: dict[str, list[dict[str, Any]]] = {}


def _get_messages(thread_id: str) -> list[dict[str, Any]]:
    """Get or create the message history for a conversation thread.

    Args:
        thread_id: Unique identifier for the conversation session.

    Returns:
        List of message dicts for this thread.
    """
    if thread_id not in message_stores:
        message_stores[thread_id] = []
    return message_stores[thread_id]


class ChatRequest(BaseModel):
    """Incoming chat request from the frontend."""

    prompt: dict[str, Any]
    threadId: str
    responseId: str


@app.post("/api/chat")
@with_c1_response()
async def chat(request: ChatRequest) -> None:
    """Handle a CEO chat message through the C1 tool-calling pipeline.

    Flow:
        1. Add user message to thread history
        2. Show initial thinking state
        3. Enter tool-calling loop (C1 decides which tools to call)
        4. Execute governed tools, feed results back to C1
        5. Stream C1's final rendered dashboard response
        6. Save assistant message to thread history
    """
    thread_id = request.threadId
    prompt_text = request.prompt.get("content", "")[:80]
    logger.info("Chat request: threadId=%s, prompt=%s", thread_id, prompt_text)
    print(f">>> CHAT REQUEST: threadId={thread_id}, prompt={prompt_text}", flush=True)

    messages = _get_messages(thread_id)
    messages.append(request.prompt)

    await write_think_item(
        title="Preparing your dashboard...",
        description="Connecting to UDC's governed data systems",
    )

    all_messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *[{k: v for k, v in m.items() if k != "id"} for m in messages],
    ]

    # Tool-calling loop: C1 may call multiple tools across multiple rounds
    while True:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=all_messages,
            tools=TOOL_DEFINITIONS,
            stream=False,
        )

        message = completion.choices[0].message
        tool_calls = message.tool_calls or []

        if not tool_calls:
            break

        all_messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        })

        for tc in tool_calls:
            func_name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")

            print(f">>> TOOL CALL: {func_name}({args})", flush=True)
            logger.info("Tool call: %s(%s)", func_name, args)

            label = THINKING_LABELS.get(func_name, ("Processing...", "Fetching data"))
            await write_think_item(title=label[0], description=label[1])

            if func_name in TOOL_IMPLEMENTATIONS:
                result = TOOL_IMPLEMENTATIONS[func_name](**args)
            else:
                result = json.dumps({"error": f"Unknown tool: {func_name}"})

            print(f">>> TOOL RESULT: {func_name} returned {len(result)} bytes", flush=True)
            logger.info("Tool result: %s returned %d bytes", func_name, len(result))

            all_messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # Final streaming call: C1 renders the dashboard from tool results
    stream = client.chat.completions.create(
        model=MODEL,
        messages=all_messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            await write_content(delta.content)

    assistant_msg = get_assistant_message()
    assistant_msg["id"] = request.responseId
    messages.append(assistant_msg)

    logger.info("Chat complete: threadId=%s, responseId=%s", thread_id, request.responseId)
    print(f">>> CHAT COMPLETE: threadId={thread_id}, responseId={request.responseId}", flush=True)


if __name__ == "__main__":
    import subprocess

    port = int(os.environ.get("PORT", 8000))
    logger.info("Starting UDC CEO Dashboard backend on port %d", port)
    logger.info("Python: %s", sys.executable)
    subprocess.run([
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--reload",
    ])

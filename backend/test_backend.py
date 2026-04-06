"""Test the FastAPI backend end-to-end."""
import requests

BASE_URL = "http://localhost:8000"


def _send_and_read(prompt: str, thread_id: str, response_id: str) -> str:
    """Send a chat request and read the full streamed response."""
    resp = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "prompt": {"role": "user", "content": prompt},
            "threadId": thread_id,
            "responseId": response_id,
        },
        stream=True,
        timeout=120,
    )
    assert resp.status_code == 200, f"Status {resp.status_code}"

    # Read stream incrementally instead of blocking on .text
    chunks = []
    for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            chunks.append(chunk)
    return "".join(chunks)


def test_chat_endpoint():
    print("\n=== TESTING FASTAPI BACKEND ===\n")

    # Test 1: Executive overview
    print("  Test 1: 'How are we doing?' ...")
    content = _send_and_read("How are we doing?", "test-1", "resp-001")
    assert len(content) > 100, f"Response too short: {len(content)} chars"
    print(f"    {len(content)} chars — PASSED")

    # Test 2: Zone deep dive (requires parameter)
    print("  Test 2: 'Tell me about Porto Arabia' ...")
    content2 = _send_and_read("Tell me about Porto Arabia", "test-2", "resp-002")
    assert len(content2) > 100, f"Response too short: {len(content2)} chars"
    print(f"    {len(content2)} chars — PASSED")

    # Test 3: Follow-up in same session
    print("  Test 3: Follow-up 'Show me collections priority' ...")
    content3 = _send_and_read("Now show me the collections priority", "test-1", "resp-003")
    assert len(content3) > 100, f"Response too short: {len(content3)} chars"
    print(f"    {len(content3)} chars — PASSED")

    print("\n  ALL 3 BACKEND TESTS PASSED\n")


if __name__ == "__main__":
    test_chat_endpoint()

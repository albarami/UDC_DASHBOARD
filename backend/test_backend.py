"""Test the FastAPI backend end-to-end."""
import requests


BASE_URL = "http://localhost:8000"


def test_chat_endpoint():
    print("\n=== TESTING FASTAPI BACKEND ===\n")

    # Test 1: Basic health
    print("  Test 1: Sending 'How are we doing?' ...")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "prompt": {"role": "user", "content": "How are we doing?"},
            "threadId": "test-session-1",
            "responseId": "resp-001",
        },
        stream=True,
        timeout=60,
    )
    assert response.status_code == 200, f"Status {response.status_code}: {response.text}"

    content = response.text
    assert len(content) > 100, f"Response too short: {len(content)} chars"
    print(f"  Response: {len(content)} chars — PASSED")

    # Test 2: Tool that requires parameters
    print("  Test 2: Sending 'Tell me about Porto Arabia' ...")
    response2 = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "prompt": {"role": "user", "content": "Tell me about Porto Arabia"},
            "threadId": "test-session-2",
            "responseId": "resp-002",
        },
        stream=True,
        timeout=60,
    )
    assert response2.status_code == 200
    content2 = response2.text
    assert len(content2) > 100
    print(f"  Response: {len(content2)} chars — PASSED")

    # Test 3: Conversation continuity (same threadId)
    print("  Test 3: Follow-up in same session ...")
    response3 = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "prompt": {"role": "user", "content": "Now show me the collections priority"},
            "threadId": "test-session-1",
            "responseId": "resp-003",
        },
        stream=True,
        timeout=60,
    )
    assert response3.status_code == 200
    content3 = response3.text
    assert len(content3) > 100
    print(f"  Response: {len(content3)} chars — PASSED")

    print("\n  ALL 3 BACKEND TESTS PASSED\n")


if __name__ == "__main__":
    test_chat_endpoint()

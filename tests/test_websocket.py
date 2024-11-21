import pytest, os
import asyncio
import websockets
import json
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock

load_dotenv()

WEBSOCKET_URL = "ws://localhost:8000/ws/question"
MAX_MESSAGES_PER_SECOND = int(os.getenv("no_of_request"))


@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting functionality"""
    async def send_rapid_messages(num_messages):
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            for _ in range(num_messages):
                payload = {
                    "text_id": 1,
                    "question": f"Test question {_}"
                }
                await websocket.send(json.dumps(payload))
                response = await websocket.recv()
                yield response
    
    # Collect all responses
    responses = [r async for r in send_rapid_messages(MAX_MESSAGES_PER_SECOND + 2)]
    
    # Check if rate limit error occurs
    rate_limit_errors = [
        json.loads(resp) for resp in responses 
        if "error" in json.loads(resp) and "Rate limit" in json.loads(resp)["error"]
    ]
    
    assert len(rate_limit_errors) > 0

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test basic WebSocket connection"""
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            # Connection successful if no exception is raised
            assert websocket.open
    except Exception as e:
        pytest.fail(f"WebSocket connection failed: {e}")

@pytest.mark.asyncio
async def test_valid_question_flow():
    """Test complete flow of sending a question and receiving an answer"""
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        # Prepare a valid question payload
        question_payload = {
            "text_id": 1,  # Assuming a valid text_id exists
            "question": "What is the main topic of the document?"
        }
        
        # Send question
        await websocket.send(json.dumps(question_payload))
        
        # Wait for and parse response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Validate response structure
        assert "answer" in response_data or "error" in response_data

@pytest.mark.asyncio
async def test_invalid_message_format():
    """Test handling of invalid message format"""
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        # Send malformed JSON
        await websocket.send("Invalid JSON")
        
        # Expect an error response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        assert "error" in response_data
        assert "Invalid message format" in response_data["error"]

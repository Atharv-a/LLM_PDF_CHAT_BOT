import json
import os
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import PDFText
from services.nlp_services import generate_answer
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

# Store message counts per user (IP address as key)
message_counts = defaultdict(list)

# Define rate limit constants
MAX_MESSAGES_PER_SECOND = int(os.getenv("no_of_request"))
TIME_WINDOW = int(os.getenv("time_window"))

# Connection manager for handling WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        """Send JSON message to WebSocket."""
        await websocket.send_text(json.dumps(message))

# Create an instance of ConnectionManager
manager = ConnectionManager()

# WebSocket Router
websocket_router = APIRouter()

@websocket_router.websocket("/ws/question")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    print(MAX_MESSAGES_PER_SECOND, TIME_WINDOW)
    await manager.connect(websocket)
    user_ip = websocket.client.host  # Unique identifier for rate limiting

    try:
        while True:
            # Receive message
            try:
                data = await websocket.receive_text()
                question_request = json.loads(data)
            except Exception:
                await manager.send_message(
                    {"error": "Invalid message format or error receiving data."}, websocket
                )
                continue

            current_time = time.time()

            # Rate limiting: Cleanup old timestamps and check limits
            timestamps = message_counts[user_ip]
            message_counts[user_ip] = [
                timestamp for timestamp in timestamps if current_time - timestamp < TIME_WINDOW
            ]

            if len(message_counts[user_ip]) >= MAX_MESSAGES_PER_SECOND:
                await manager.send_message(
                    {"error": "Rate limit exceeded. Please wait before sending more messages."},
                    websocket,
                )
                continue

            # Add the current timestamp
            message_counts[user_ip].append(current_time)

            # Process the question
            text_id = question_request.get("text_id")
            question = question_request.get("question")

            # Validate input
            if not text_id or not question:
                await manager.send_message(
                    {"error": "Invalid request. 'text_id' and 'question' are required."},
                    websocket,
                )
                continue

            # Fetch PDF text
            pdf_text = db.query(PDFText).filter(PDFText.id == text_id).first()
            if not pdf_text:
                await manager.send_message(
                    {"error": "PDF text not found."}, websocket
                )
                continue

            # Generate answer and send response
            try:
                answer = generate_answer(question, pdf_text.text)
                await manager.send_message({"answer": answer}, websocket)
            except Exception as e:
                await manager.send_message(
                    {"error": f"Failed to process the question: {str(e)}"}, websocket
                )

    except WebSocketDisconnect:
        # Gracefully handle WebSocket disconnection
        manager.disconnect(websocket)
        print(f"Client disconnected: {user_ip}")

    except Exception as e:
        # Log unexpected errors and notify the client
        print(f"Unexpected error: {str(e)}")
        await manager.send_message(
            {"error": f"An unexpected error occurred: {str(e)}"}, websocket
        )
        manager.disconnect(websocket)

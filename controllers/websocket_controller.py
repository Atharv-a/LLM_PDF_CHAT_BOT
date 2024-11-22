import json
import os
import time
import traceback
from starlette.websockets import WebSocketState
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import PDFText
from services.nlp_services import generate_answer
from dotenv import load_dotenv
from collections import defaultdict
import logging

load_dotenv()

logger = logging.getLogger("websocket_controller")
logging.basicConfig(level=logging.INFO)

# Rate limit constants
MAX_MESSAGES_PER_SECOND = int(os.getenv("no_of_request"))
TIME_WINDOW = int(os.getenv("time_window"))

# Rate-limiting storage
message_counts = defaultdict(list)

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected: {websocket.client.host}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected: {websocket.client.host}")

    async def send_message(self, message: dict, websocket: WebSocket):
        if websocket.application_state == WebSocketState.CONNECTED: 
            await websocket.send_text(json.dumps(message))




manager = ConnectionManager()
websocket_router = APIRouter()

@websocket_router.websocket("/ws/question")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    user_ip = websocket.headers.get("x-forwarded-for", websocket.client.host)
    logger.info(f"WebSocket request from IP: {user_ip}")

    await manager.connect(websocket)
    try:
        while True:
            current_time = time.time()

            # Receive message
            try:
                data = await websocket.receive_text()
                question_request = json.loads(data)
            except Exception as e:
                logger.warning(f"Invalid data received: {e}")
                await manager.send_message(
                    {"error": "Invalid message format or error receiving data."}, websocket
                )
                continue

            # Rate limiting
            timestamps = message_counts[user_ip]
            message_counts[user_ip] = [
                ts for ts in timestamps if current_time - ts < TIME_WINDOW
            ]
            if len(message_counts[user_ip]) >= MAX_MESSAGES_PER_SECOND:
                await manager.send_message(
                    {"error": "Rate limit exceeded. Please wait before sending more messages."},
                    websocket,
                )
                continue

            message_counts[user_ip].append(current_time)

            # Validate input
            text_id = question_request.get("text_id")
            question = question_request.get("question")

            if not isinstance(text_id, int) or not question:
                await manager.send_message(
                    {"error": "Invalid request. 'text_id' must be an integer, and 'question' is required."},
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

            # Generate answer
            try:
                answer = generate_answer(question, pdf_text.text)
                await manager.send_message({"answer": answer}, websocket)
            except Exception as e:
                logger.error(f"Error generating answer: {e}\n{traceback.format_exc()}")
                await manager.send_message(
                    {"error": "Failed to process the question. Please try again later."}, websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected: {user_ip}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
        await manager.send_message(
            {"error": "An unexpected error occurred. Please try again later."}, websocket
        )
    finally:
        db.close()  # Ensure the database session is closed

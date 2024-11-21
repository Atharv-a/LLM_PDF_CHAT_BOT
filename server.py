from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.pdf_endpoints_controller import router
from controllers.websocket_controller import websocket_router
from dotenv import load_dotenv
from startup import startup_event
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Logger setup
import logging
logger = logging.getLogger("pdf_chat_bot")
logging.basicConfig(level=logging.INFO)

# Lifespan function for app lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform startup tasks
    try:
        logger.info("Starting application setup...")
        await startup_event(app)
        logger.info("Application setup completed successfully.")
        yield  # Hand over control to the application runtime
    except Exception as e:
        logger.critical(f"Critical error during startup: {e}")
        raise
    finally:
        # Cleanup tasks if needed during shutdown
        logger.info("Application shutting down.")

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include application routes
app.include_router(router)
app.include_router(websocket_router)

# Root endpoint
@app.get("/")
def root():
    # Root endpoint to confirm the application is running
    return {"message": "Welcome to Pdf Chat Bot!"}

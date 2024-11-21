from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from db.database import SessionLocal, get_db
from db.models import PDFText
from .pdf_endpoints_service import upload_pdf_service #, ask_question_service
from .schema import UploadResponse, QuestionRequest, AnswerResponse
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv
load_dotenv()

# Import the APIRouter from FastAPI
no_of_request = int(os.getenv('no_of_request', 5))  # default to 5 if not set
no_of_minutes = int(os.getenv('minutes', 1))  # default to 1 if not set

router = APIRouter()

# Define a POST endpoint for uploading PDFs
@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    rate_limit = Depends(RateLimiter(times=no_of_request, minutes=no_of_minutes))
):
    try:
        # Delegate the functionality to the service layer
        result = upload_pdf_service(file, db)
    except Exception as e:
        # Handle unexpected exceptions gracefully
        raise HTTPException(status_code=500, detail=str(e))

    # Return the result as a response
    return {"id": result["id"], "filename": result["filename"], "message": "File successfully uploaded and text extracted."}

# Define a POST endpoint for asking questions
# @router.post("/ask", response_model=AnswerResponse)
# async def ask_question(
#     request: QuestionRequest, 
#     db: Session = Depends(get_db),
#     rate_limit =Depends(RateLimiter(times=no_of_request, minutes=no_of_minutes))
#     ):
#     try:
#         # Delegate functionality to the service layer
#         answer = ask_question_service(request.question, request.text_id, db)
#     except Exception as e:
#         # Handle any unexpected errors
#         raise HTTPException(status_code=500, detail=str(e))
#     # Return the generated answer
#     return {"answer": answer}
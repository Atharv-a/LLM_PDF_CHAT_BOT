from sqlalchemy.orm import Session
from db.models import PDFText
from services.pdf_service import pdf_to_text
from services.nlp_services import generate_answer
from botocore.exceptions import NoCredentialsError
from aws.s3client import s3_client, S3_BUCKET_NAME
from fastapi import HTTPException

def upload_pdf_service(file, db: Session):
    # Check if the uploaded file is a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")

    # Read the contents of the uploaded file
    contents = file.file.read()  # Note: Using `file.file.read()` since this will be a file-like object

    # Process the PDF and extract the text
    text = pdf_to_text(contents)

    # Save the extracted text to PostgreSQL
    pdf_text = PDFText(filename=file.filename, text=text)
    db.add(pdf_text)
    db.commit()
    db.refresh(pdf_text)

    # Save the PDF to S3
    try:
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=file.filename, Body=contents)
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail=str(e))

    # Return success response data
    return {"id": pdf_text.id, "filename": file.filename}


# def ask_question_service(question: str, text_id: int, db: Session):
#     # Retrieve the PDF text from the database based on the provided ID
#     pdf_text = db.query(PDFText).filter(PDFText.id == text_id).first()
#     if not pdf_text:
#         raise HTTPException(status_code=404, detail="PDF text not found")
#     print("Retrieval: ",pdf_text)

#     # Generate an answer to the question based on the PDF text
#     answer = generate_answer(question, pdf_text.text)

#     return answer
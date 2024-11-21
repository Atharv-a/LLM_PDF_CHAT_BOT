import pytest
import os
from io import BytesIO
from unittest.mock import patch, MagicMock
from db.models import PDFText
from services.pdf_service import pdf_to_text
from controllers.pdf_endpoints_service import upload_pdf_service
from sqlalchemy.orm import Session
from fastapi import HTTPException
from starlette.datastructures import UploadFile  # Import UploadFile class

# Mocked PDF extraction function (aligning with the actual content of the PDF)
def mock_pdf_to_text(contents):
    """
    Simulates text extraction from a PDF.
    Always returns 'test_text' regardless of input.
    """
    return "test_text"

# Mocked S3 client
class MockS3Client:
    def put_object(self, Bucket, Key, Body):
        """
        Simulates uploading an object to S3.
        Always returns a successful response.
        """
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

# Test for successful PDF upload
@patch("services.pdf_service.pdf_to_text", side_effect=mock_pdf_to_text)
@patch("aws.s3client.s3_client.put_object", autospec=True)  # Mock `put_object` directly
def test_upload_pdf_service(mock_put_object, mock_pdf_extraction, test_db: Session):
    """
    Test the upload of a valid PDF file and verify:
      - PDF text extraction is successful.
      - S3 upload is invoked with correct parameters.
      - The database entry is created with the correct content.
    """
    # File path for the test PDF
    file_path = "tests/test_files/test_document.pdf"

    # Ensure the file exists before proceeding
    assert os.path.exists(file_path), f"Test file at {file_path} not found."

    # Open the file and use it as the UploadFile in the test
    with open(file_path, "rb") as f:
        file_content = f.read()  # Read the file content
        file = UploadFile(filename="test_document.pdf", file=BytesIO(file_content))  # Create UploadFile with content

        # Call the service with the file and the test database
        result = upload_pdf_service(file, test_db)

    # Assertions
    db_entry = test_db.query(PDFText).filter(PDFText.filename == "test_document.pdf").first()
    assert db_entry is not None
    assert db_entry.text.strip() == "test_text"

    mock_put_object.assert_called_once_with(
        Bucket="test",  
        Key="test_document.pdf",
        Body=file_content,
    )

# Test for invalid file type upload
def test_upload_pdf_service_invalid_file(test_db: Session):
    """
    Test the upload of an invalid file type and verify:
      - An HTTPException is raised with the appropriate error message.
    """
    # File path for the test text file
    file_path = "tests/test_files/test_document.txt"

    # Ensure the file exists before proceeding
    assert os.path.exists(file_path), f"Test file at {file_path} not found."

    # Open the file and use it as the UploadFile in the test
    with open(file_path, "rb") as f:
        file = UploadFile(filename="test_document.txt", file=BytesIO(f.read()))  # Create UploadFile with content

        # Test that it raises an HTTPException for invalid file type
        with pytest.raises(HTTPException) as excinfo:
            upload_pdf_service(file, test_db)

        # Verify the exception details
        assert excinfo.value.status_code == 400
        assert excinfo.value.detail == "Invalid file type. Only PDFs are allowed."

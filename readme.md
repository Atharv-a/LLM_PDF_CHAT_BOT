# PDF Chat Bot

## Project Overview
PDF Chat Bot is an intelligent web application that allows users to upload PDF documents and interactively ask questions about their content using advanced natural language processing techniques.

## Features
- PDF file upload with text extraction
- WebSocket-based interactive questioning
- Rate limiting to prevent abuse
- Vector-based semantic search
- Powered by Google Generative AI

## Technology Stack
- Backend: FastAPI
- Database: PostgreSQL
- Vector Store: FAISS
- Embeddings: Google Generative AI
- Caching/Rate Limiting: Redis
- Storage: AWS S3 (LocalStack for development)

## Prerequisites
- Python 3.9+
- PostgreSQL
- Redis
- Google Cloud Service Account
- AWS S3 (or LocalStack)

## Configuration
1. Create a `.env` file with the following variables:
```
# Database Configuration
database_hostname=
database_port=
database_password=
database_name=
database_username=

# AWS S3 Configuration
aws_access_key_id=
aws_secret_access_key=
aws_endpoint_url=
s3_region_name=
s3_bucket_name=

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json
google_api_key=

# Redis Configuration
REDIS_HOST=
REDIS_PORT=
REDIS_PASSWORD=

# Rate Limiting
no_of_request=5
minutes=1
```

## Installation
1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set up the database
5. Configure environment variables
6. Run the application: `uvicorn main:app --reload`

## Testing
Run tests using pytest:
```bash
pytest tests/
```

## Architecture
- **Controllers**: Handle HTTP and WebSocket endpoints
- **Services**: Implement core business logic
- **Database**: Store PDF text and metadata
- **NLP**: Process and answer questions semantically

## Limitations
- Currently supports single PDF upload
- Limited to Google Generative AI for embeddings and question answering

## Future Improvements
- Multi-document support
- Enhanced authentication
- Advanced semantic search capabilities

<!-- ## License
[Specify your license]

## Contributing
[Add contribution guidelines]
``` -->

## Security Considerations
- Use environment-specific configurations
- Implement proper authentication
- Validate and sanitize all inputs
- Monitor and log application activities

## API Documentation

### PDF Upload Endpoint
- **URL**: `/upload`
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Parameters**:
  - `file`: PDF file to upload (required)
- **Response**:
  ```json
  {
    "id": 123,
    "filename": "document.pdf",
    "message": "File successfully uploaded and text extracted."
  }
- **Errors**:
  - 400: Invalid file type
  - 429: Rate limit exceeded
  - 500: Server error

### WebSocket Question Endpoint
- **URL**: `/ws/question`
- **Protocol**: WebSocket
- **Request Payload**:
  ```json
  {
    "text_id": 123,
    "question": "What is the main topic?"
  }
  ```
- **Response Payload**:
  ```json
  {
    "answer": "Detailed answer based on PDF content"
  }
- **Error Responses**:
  - Rate limit exceeded
  - Invalid message format
  - PDF text not found

### Rate Limiting
- Maximum: 2 requests per 30 seconds
- Excess requests result in temporary block

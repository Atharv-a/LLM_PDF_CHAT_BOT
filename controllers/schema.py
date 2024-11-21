from pydantic import BaseModel

# Define the UploadResponse model
class UploadResponse(BaseModel):
    id: int
    filename: str
    message: str

# Define the QuestionRequest model
class QuestionRequest(BaseModel):
    text_id: int
    question: str

# Define the AnswerResponse model
class AnswerResponse(BaseModel):
    answer: str
# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy your application code to the container
COPY . /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y libpq-dev gcc

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port (e.g., 8000 for FastAPI/Uvicorn)
EXPOSE 8000

# Start the backend application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

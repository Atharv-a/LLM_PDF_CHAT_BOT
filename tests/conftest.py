import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from main import app

# Use SQLite in-memory database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create engine and session for the test database
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    # Use FastAPI TestClient for API tests
    return TestClient(app)

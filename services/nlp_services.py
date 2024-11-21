from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from google.auth import exceptions, credentials
import google.auth  # Import google.auth for authentication
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
load_dotenv()

# LLM implementation using langchain and google_genai for answering any question on pdf that user may have


credentials = Credentials.from_service_account_file(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
# Initialize Embeddings client (for vector search)
# Use the correct model for embeddings (e.g., text-bison or another embedding-supported model)
embeddings = GoogleGenerativeAIEmbeddings(
    credentials=credentials, 
    model="models/embedding-001"
)  # Updated model name for embeddings
genai.configure(api_key=os.getenv("google_api_key"))

# Function to split text into chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

# Function to create and save the vector store
def get_vector_store(text_chunks):
    # Embedding model for FAISS
    if len(text_chunks) == 0:
        raise ValueError("No text chunks were created. Please check the input text.")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")  # Save the index locally

# Create a conversational chain using Chat-based model
def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, 
    if the answer is not in the provided context just say, "Answer is not available in the context", 
    don't provide the wrong answer.

    Context: {context}
    Question: {question}

    Answer:
    """

    # Use a Chat-based model for answering questions
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)  # Chat model for context-based answering

    # Prepare the prompt template
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    # Load the QA chain with the model and prompt
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

# Function to handle user input and return a response
def user_input(user_question):
    # Load the saved FAISS index and use the embeddings model
    new_db = FAISS.load_local("faiss_index", embeddings,allow_dangerous_deserialization = True)
    
    # Check if similarity search returns any documents
    docs = new_db.similarity_search(user_question)
    if not docs:  # No documents found
        return "No relevant documents found in the index."

    # Prepare the QA chain
    chain = get_conversational_chain()

    # Generate response from the chain
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    
    # Check if the response contains the necessary output
    if "output_text" in response:
        return response["output_text"]
    else:
        return "No answer was found for your question."

# Main function to generate the answer based on provided text and user question
def generate_answer(question: str, text: str):
    # Step 1: Split text into chunks
    
    text_chunks = get_text_chunks(text)
    # Step 2: Create and save the vector store
    get_vector_store(text_chunks)
    # Step 3: Use the user input function to fetch a response based on the question
    response = user_input(question)
    
    return response

"""
Production-ready version of main.py with proper error handling and configuration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Import your existing modules
from chat_manager import ChatManager
from database import DatabaseManager
from knowledge_service import KnowledgeService
from models_config import ModelsConfig
from enhanced_chat import ChatProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Qwen Chatbot API",
    description="AI-powered chatbot with multiple models",
    version="1.0.0"
)

# Configure CORS for production
origins = os.getenv("FRONTEND_URL", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    # Use environment variable for API key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY environment variable not set")
    
    # Initialize database with configurable path
    db_path = os.getenv("DATABASE_PATH", "chatbot.db")
    db = DatabaseManager(db_path)
    
    # Initialize other services
    knowledge_service = KnowledgeService(db)
    models_config = ModelsConfig()
    chat_manager = ChatManager(
        api_key=api_key,
        knowledge_service=knowledge_service,
        models_config=models_config
    )
    chat_processor = ChatProcessor(api_key=api_key)
    
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str
    model: Optional[str] = "general"
    images: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    model: str

class ChatSession(BaseModel):
    session_id: str
    title: str
    timestamp: str
    preview: str

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str

class DeleteSessionRequest(BaseModel):
    session_id: str

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Save user message
        db.save_conversation(request.session_id, "user", request.message)
        
        # Create memory for session
        memory = chat_manager.get_or_create_memory(request.session_id)
        
        # Process chat with selected model
        result = chat_processor.process_chat(request, memory)
        
        # Save AI response
        db.save_conversation(request.session_id, "assistant", result["response"])
        
        return ChatResponse(
            response=result["response"],
            session_id=request.session_id,
            timestamp=result["timestamp"],
            model=request.model
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get available models
@app.get("/api/models")
async def get_models():
    try:
        return {"models": models_config.get_available_models()}
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get chat sessions
@app.get("/api/sessions", response_model=List[ChatSession])
async def get_sessions():
    try:
        sessions = db.get_all_sessions()
        return [
            ChatSession(
                session_id=s["session_id"],
                title=s["title"],
                timestamp=s["timestamp"],
                preview=s["preview"]
            )
            for s in sessions
        ]
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get session history
@app.get("/api/sessions/{session_id}/history", response_model=List[ChatMessage])
async def get_session_history(session_id: str):
    try:
        messages = db.get_conversation_history(session_id, limit=100)
        return [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error getting session history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Delete session
@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    try:
        success = db.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "An unexpected error occurred",
        "detail": str(exc) if os.getenv("DEBUG") == "true" else "Internal server error"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
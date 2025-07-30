"""
Enhanced FastAPI Backend with Full Qwen Capabilities
Supports vision, embeddings, educational features, and more
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
from datetime import datetime

from database import DatabaseManager
from knowledge_service import KnowledgeService
from enhanced_chat_v2 import EnhancedChatProcessor
from models_config import model_selector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Qwen Multi-Model Chatbot API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    images: Optional[List[str]] = None
    session_id: Optional[str] = "default"
    model: Optional[str] = "general"
    educational_mode: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    model: str
    features_used: Optional[List[str]] = []
    sources: Optional[List[str]] = None
    educational_context: Optional[Dict] = None

class ChatSession(BaseModel):
    session_id: str
    title: str
    timestamp: str
    preview: str
    message_count: int

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str
    has_image: Optional[bool] = False

# Initialize services
try:
    # Get API key from environment
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.warning("DASHSCOPE_API_KEY not found in environment")
        # Try to read from file for development
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("DASHSCOPE_API_KEY"):
                        api_key = line.split("=")[1].strip()
                        break
        except:
            pass
    
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY not configured")
    
    # Initialize database
    db = DatabaseManager()
    knowledge_service = KnowledgeService(db)
    
    # Initialize enhanced chat processor
    chat_processor = EnhancedChatProcessor(
        api_key=api_key,
        knowledge_service=knowledge_service,
        conversation_service=None  # Add if needed
    )
    
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

# Store sessions in memory (use database for production)
sessions = {}

@app.get("/")
async def root():
    return {"message": "Enhanced Qwen Multi-Model Chatbot API with Vision, Embeddings, and Educational Features"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info(f"Chat request - Model: {request.model}, Has images: {bool(request.images)}")
        
        # Save user message
        db.save_conversation(request.session_id, "user", request.message)
        
        # Process with enhanced chat processor
        result = chat_processor.process_chat({
            "message": request.message,
            "images": request.images,
            "session_id": request.session_id,
            "model": request.model,
            "educational_mode": request.educational_mode,
            "context": request.context
        })
        
        # Save assistant response
        db.save_conversation(request.session_id, "assistant", result["response"])
        
        # Create/update session
        if request.session_id not in sessions:
            sessions[request.session_id] = {
                "title": request.message[:50] + "..." if len(request.message) > 50 else request.message,
                "created": datetime.now(),
                "message_count": 0
            }
        sessions[request.session_id]["message_count"] += 2
        sessions[request.session_id]["last_updated"] = datetime.now()
        
        return ChatResponse(
            response=result["response"],
            session_id=request.session_id,
            timestamp=result.get("timestamp", datetime.now().isoformat()),
            model=result.get("model", request.model),
            features_used=result.get("features_used", []),
            sources=result.get("sources"),
            educational_context=result.get("educational_context")
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def get_models():
    """Get available models with enhanced capabilities"""
    return {
        "models": [
            {
                "id": "general",
                "name": "General Assistant",
                "description": "Fast, intelligent responses with web search",
                "capabilities": ["web_search", "current_events", "general_knowledge"]
            },
            {
                "id": "everest",
                "name": "Everest Academy Assistant",
                "description": "Specialized for Everest Academy with Grade 9 resources",
                "capabilities": ["grade9_resources", "school_info", "educational_support"]
            },
            {
                "id": "web-scraper",
                "name": "Web Research Assistant",
                "description": "Deep web research and content extraction",
                "capabilities": ["web_scraping", "price_comparison", "content_analysis"]
            },
            {
                "id": "vision",
                "name": "Vision Assistant",
                "description": "Analyze images, diagrams, and visual content",
                "capabilities": ["image_analysis", "ocr", "diagram_understanding"]
            },
            {
                "id": "tutor",
                "name": "AI Tutor",
                "description": "Educational support with Harvard/Oxford methods",
                "capabilities": ["socratic_method", "personalized_tutoring", "adaptive_learning"]
            },
            {
                "id": "math",
                "name": "Math Specialist",
                "description": "Advanced mathematical problem solving",
                "capabilities": ["equation_solving", "proofs", "step_by_step_solutions"]
            }
        ],
        "default": "general"
    }

@app.get("/api/sessions", response_model=List[ChatSession])
async def get_sessions():
    """Get all chat sessions"""
    try:
        db_sessions = db.get_all_sessions()
        return [
            ChatSession(
                session_id=s["session_id"],
                title=s["title"],
                timestamp=s["timestamp"],
                preview=s["preview"],
                message_count=sessions.get(s["session_id"], {}).get("message_count", 0)
            )
            for s in db_sessions
        ]
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return []

@app.get("/api/sessions/{session_id}/history", response_model=List[ChatMessage])
async def get_session_history(session_id: str):
    """Get chat history for a session"""
    try:
        messages = db.get_conversation_history(session_id, limit=100)
        return [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"],
                has_image=msg["content"].startswith("![") if msg["role"] == "user" else False
            )
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    try:
        success = db.delete_session(session_id)
        if session_id in sessions:
            del sessions[session_id]
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/folders")
async def get_folders():
    """Get folder structure (placeholder)"""
    return {
        "folders": [
            {"id": "1", "name": "School Work", "count": 5},
            {"id": "2", "name": "Research", "count": 3},
            {"id": "3", "name": "Personal", "count": 8}
        ]
    }

@app.post("/api/educational/socratic")
async def socratic_dialogue(topic: str, response: str, depth: int = 1):
    """Engage in Socratic dialogue"""
    result = chat_processor.educational_handler.create_socratic_dialogue(topic, response, depth)
    return result

@app.post("/api/educational/assessment")
async def generate_assessment(topic: str, objectives: List[str], style: str = "mixed"):
    """Generate educational assessment"""
    result = chat_processor.educational_handler.generate_assessment(topic, objectives, style)
    return result

@app.post("/api/educational/study-path")
async def create_study_path(student_profile: Dict, topic: str):
    """Create personalized study path"""
    result = chat_processor.educational_handler.adaptive_learning_path(student_profile, topic)
    return result

@app.post("/api/embeddings/search")
async def semantic_search(query: str, documents: List[Dict], top_k: int = 5):
    """Perform semantic search on documents"""
    results = chat_processor.embeddings_handler.semantic_search(query, documents, top_k)
    return {"results": results}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "models": ["qwen-max", "qwen-vl-max", "qwen-math-plus", "text-embedding-v3"],
        "features": ["vision", "embeddings", "educational", "web_search"],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
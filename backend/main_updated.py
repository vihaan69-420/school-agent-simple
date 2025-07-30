from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import json
from database import DatabaseManager
from knowledge_service import KnowledgeService, ConversationService
from enhanced_chat import ChatProcessor
from models_config import model_selector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Qwen v2.5-Max Multi-Model Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: Optional[str] = "default"
    model: Optional[str] = "general"

class ChatResponse(BaseModel):
    message: str
    success: bool
    error: Optional[str] = None
    model: Optional[str] = None
    sources: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class KnowledgeEntry(BaseModel):
    category: str
    title: str
    content: str
    tags: Optional[List[str]] = None

class KnowledgeResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None

# Global memory store for different sessions
memory_store: Dict[str, ConversationBufferMemory] = {}

# Initialize database and services
db_manager = DatabaseManager()
knowledge_service = KnowledgeService(db_manager)
conversation_service = ConversationService(db_manager)

def get_memory(session_id: str) -> ConversationBufferMemory:
    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
    return memory_store[session_id]

def initialize_qwen_llm():
    try:
        llm = ChatOpenAI(
            model="qwen-max-2025-01-25",
            openai_api_key="sk-e7497e17ae164aa9b8509eaeee5ab614",
            openai_api_base="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            temperature=0.7,
            max_tokens=400,
            request_timeout=30
        )
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize Qwen LLM: {e}")
        raise

qwen_llm = initialize_qwen_llm()
chat_processor = ChatProcessor(qwen_llm, knowledge_service, conversation_service)

@app.get("/")
async def root():
    return {"message": "Qwen v2.5-Max Multi-Model Chatbot API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info(f"Received chat request with {len(request.messages)} messages using model: {request.model}")
        
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Get the latest user message
        latest_message = request.messages[-1]
        if latest_message.role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from user")
        
        # Get memory for this session
        memory = get_memory(request.session_id)
        
        # Process chat with selected model
        result = chat_processor.process_chat(request, memory)
        
        # Save conversation to database
        conversation_service.save_message(request.session_id, "user", latest_message.content)
        conversation_service.save_message(request.session_id, "assistant", result['message'])
        
        # Add messages to memory
        memory.chat_memory.add_user_message(latest_message.content)
        memory.chat_memory.add_ai_message(result['message'])
        
        logger.info("Response generated successfully")
        
        return ChatResponse(
            message=result['message'],
            success=result.get('success', True),
            error=result.get('error'),
            model=result.get('metadata', {}).get('model'),
            sources=result.get('sources'),
            metadata=result.get('metadata')
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            message="I apologize, but I encountered an error while processing your request. Please try again.",
            success=False,
            error=str(e)
        )

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "model": "qwen-max-2025-01-25"}

@app.get("/api/models")
async def get_available_models():
    """Get information about available models"""
    return {
        "models": model_selector.get_all_models_info(),
        "default": "general"
    }

# Knowledge Base API Endpoints
@app.post("/api/knowledge", response_model=KnowledgeResponse)
async def add_knowledge(entry: KnowledgeEntry):
    try:
        knowledge_id = knowledge_service.add_knowledge_entry(
            entry.category, entry.title, entry.content, entry.tags
        )
        return KnowledgeResponse(
            success=True,
            data={"id": knowledge_id, "message": "Knowledge entry added successfully"}
        )
    except Exception as e:
        logger.error(f"Error adding knowledge: {e}")
        return KnowledgeResponse(
            success=False,
            error=str(e)
        )

@app.get("/api/knowledge", response_model=KnowledgeResponse)
async def search_knowledge(query: str = None, category: str = None):
    try:
        results = knowledge_service.search_knowledge(query=query, category=category)
        return KnowledgeResponse(
            success=True,
            data={"results": results, "count": len(results)}
        )
    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        return KnowledgeResponse(
            success=False,
            error=str(e)
        )

@app.get("/api/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def get_knowledge(knowledge_id: int):
    try:
        result = knowledge_service.get_knowledge_by_id(knowledge_id)
        if result:
            return KnowledgeResponse(
                success=True,
                data=result
            )
        else:
            return KnowledgeResponse(
                success=False,
                error="Knowledge entry not found"
            )
    except Exception as e:
        logger.error(f"Error getting knowledge: {e}")
        return KnowledgeResponse(
            success=False,
            error=str(e)
        )

@app.put("/api/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def update_knowledge(knowledge_id: int, entry: KnowledgeEntry):
    try:
        success = knowledge_service.update_knowledge_entry(
            knowledge_id, entry.category, entry.title, entry.content, entry.tags
        )
        if success:
            return KnowledgeResponse(
                success=True,
                data={"message": "Knowledge entry updated successfully"}
            )
        else:
            return KnowledgeResponse(
                success=False,
                error="Knowledge entry not found or update failed"
            )
    except Exception as e:
        logger.error(f"Error updating knowledge: {e}")
        return KnowledgeResponse(
            success=False,
            error=str(e)
        )

@app.delete("/api/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def delete_knowledge(knowledge_id: int):
    try:
        success = knowledge_service.delete_knowledge_entry(knowledge_id)
        if success:
            return KnowledgeResponse(
                success=True,
                data={"message": "Knowledge entry deleted successfully"}
            )
        else:
            return KnowledgeResponse(
                success=False,
                error="Knowledge entry not found"
            )
    except Exception as e:
        logger.error(f"Error deleting knowledge: {e}")
        return KnowledgeResponse(
            success=False,
            error=str(e)
        )

@app.get("/api/knowledge/categories", response_model=KnowledgeResponse)
async def get_categories():
    try:
        categories = knowledge_service.get_all_categories()
        return KnowledgeResponse(
            success=True,
            data={"categories": categories}
        )
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return KnowledgeResponse(
            success=False,
            error=str(e)
        )

# Conversation History API Endpoints
@app.get("/api/conversation/{session_id}", response_model=KnowledgeResponse)
async def get_conversation_history(session_id: str, limit: int = 50):
    try:
        history = conversation_service.get_conversation_history(session_id, limit)
        return KnowledgeResponse(
            success=True,
            data={"history": history, "count": len(history)}
        )
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return KnowledgeResponse(
            success=False,
            error=str(e)
        )

@app.delete("/api/conversation/{session_id}", response_model=KnowledgeResponse)
async def clear_conversation_history(session_id: str):
    try:
        success = conversation_service.clear_conversation(session_id)
        if success:
            return KnowledgeResponse(
                success=True,
                data={"message": "Conversation history cleared successfully"}
            )
        else:
            return KnowledgeResponse(
                success=False,
                error="No conversation history found for this session"
            )
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        return KnowledgeResponse(
            success=False,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
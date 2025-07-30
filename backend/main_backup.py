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
from dynamic_scraper import get_dynamic_content_for_query
from general_web_assistant import enhance_query_with_website_context
from models_config import ModelType, model_selector, get_model_by_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Qwen v2.5-Max Chatbot API")

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
            max_tokens=400,  # Much smaller for speed
            request_timeout=30  # 30 second timeout
        )
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize Qwen LLM: {e}")
        raise

qwen_llm = initialize_qwen_llm()

def is_school_related_query(query: str) -> bool:
    """Check if query is related to Everest Academy or school topics"""
    school_keywords = [
        'everest', 'academy', 'school', 'admission', 'tuition', 'fee', 'curriculum', 
        'academic', 'program', 'grade', 'student', 'teacher', 'faculty', 'course',
        'enrollment', 'application', 'campus', 'facility', 'schedule', 'calendar',
        'ap', 'advanced placement', 'manila', 'philippines', 'bgc', 'taguig'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in school_keywords)

def needs_dynamic_scraping(query: str) -> bool:
    """Check if query needs dynamic web scraping for accurate URLs and instructions"""
    scraping_keywords = [
        'how to', 'steps', 'process', 'apply', 'application', 'form', 'fill',
        'submit', 'procedure', 'instructions', 'guide', 'tutorial', 'url',
        'link', 'page', 'website', 'where', 'find', 'locate', 'access'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in scraping_keywords)

@app.get("/")
async def root():
    return {"message": "Qwen v2.5-Max Chatbot API is running"}

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
        
        # Get model type
        model_type = get_model_by_id(request.model) or ModelType.GENERAL
        model_config = model_selector.get_model_config(model_type)
        
        # Get memory for this session
        memory = get_memory(request.session_id)
        
        # Context selection based on model type
        context = ""
        dynamic_content = ""
        sources = []
        
        if model_type == ModelType.GENERAL:
            # Fast response, no external data
            pass
            
        elif model_type == ModelType.EVEREST:
            # Always use Everest context
            context = conversation_service.get_recent_context(
                request.session_id, 
                latest_message.content, 
                knowledge_service
            )
            
            # Always try to get fresh web data for Everest queries
            try:
                logger.info(f"Everest model: scraping for {latest_message.content}")
                dynamic_content = get_dynamic_content_for_query(latest_message.content)
            except Exception as e:
                logger.error(f"Everest scraping failed: {e}")
                
        elif model_type == ModelType.WEB_SCRAPER:
            # Enhanced web scraping for any website
            web_enhancement = enhance_query_with_website_context(latest_message.content)
            
            if web_enhancement['has_website_context']:
                dynamic_content = web_enhancement['website_context']
                logger.info(f"Web scraper model: found web context")
            else:
                # Try to extract intent and search for relevant content
                logger.info(f"Web scraper model: no URL found, analyzing intent")
                # Could add additional logic here to search for content
        
        # Prepare system message with context
        system_message = ""
        if context or dynamic_content:
            # Combine static context and dynamic content
            full_context = ""
            if context:
                full_context += context
            if dynamic_content:
                full_context += "\n\n" + dynamic_content
            
            system_message = f"""You are a helpful AI assistant for Everest Academy Manila. Use the following context to provide accurate and helpful responses:

{full_context}

Guidelines:
- Answer ALL questions helpfully and accurately, both general questions and Everest Academy-specific questions
- For Everest Academy questions: Use the provided knowledge base context and cite source URLs when available
- For general questions: Provide comprehensive answers without requiring school context
- IMPORTANT: Only provide URLs that are explicitly shown in the context as (Source: ...). Do NOT create or guess URLs
- When citing information from the website, include the EXACT source URL shown in the context
- If information comes from the live website (indicated by source URLs), mention that it's current information from everestmanila.com
- Valid Everest Academy URLs include: https://everestmanila.com, https://everestmanila.com/about/contact, https://everestmanila.com/about/welcome, https://everestmanila.com/who-we-are, etc.
- Reference the conversation history to maintain context
- If you don't have specific information about Everest Academy, suggest checking the official website at https://everestmanila.com/
- Be helpful, accurate, and professional in your responses for all topics

Current user query: {latest_message.content}
"""
        else:
            # For general questions, use a much simpler system message for speed
            system_message = f"""You are VihaanGPT. Answer briefly and accurately.

Query: {latest_message.content}
"""
        
        # Convert request messages to LangChain format
        messages = []
        
        # Add system message
        if system_message:
            messages.append(HumanMessage(content=system_message))
        
        # For general questions, only add the latest message for speed
        if not context:
            # Only add the current message for maximum speed
            messages.append(HumanMessage(content=latest_message.content))
        else:
            # Add recent conversation messages for school questions
            for msg in request.messages:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))
        
        # Generate response using Qwen with timeout handling
        logger.info("Generating response with Qwen...")
        try:
            response = qwen_llm.invoke(messages)
        except Exception as e:
            logger.warning(f"Primary LLM call failed ({e}), providing fallback response")
            # Provide intelligent fallback responses
            if context:
                fallback_content = "I apologize for the delay. Could you please rephrase your question? I'm here to help with information about Everest Academy Manila."
            else:
                # Smart fallbacks for common general questions
                query_lower = latest_message.content.lower()
                if 'weather' in query_lower:
                    fallback_content = "I can't access real-time weather data. Please check your local weather app or website for current conditions."
                elif any(word in query_lower for word in ['time', 'date', 'today']):
                    fallback_content = "I don't have access to real-time data. Please check your device's clock or calendar."
                elif 'hello' in query_lower or 'hi' in query_lower:
                    fallback_content = "Hello! I'm VihaanGPT, your AI assistant. How can I help you today?"
                else:
                    fallback_content = "I'm experiencing a brief delay. Could you please try rephrasing your question?"
            
            # Create a mock response object
            class MockResponse:
                def __init__(self, content):
                    self.content = content
            
            response = MockResponse(fallback_content)
        
        # Save conversation to database
        conversation_service.save_message(request.session_id, "user", latest_message.content)
        conversation_service.save_message(request.session_id, "assistant", response.content)
        
        # Add messages to memory
        memory.chat_memory.add_user_message(latest_message.content)
        memory.chat_memory.add_ai_message(response.content)
        
        logger.info("Response generated successfully")
        
        return ChatResponse(
            message=response.content,
            success=True
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
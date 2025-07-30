"""
Enhanced Chat Processor V2 with Full Qwen Capabilities
Includes vision, embeddings, educational features, and multiple models
"""
import logging
import time
import json
from typing import List, Dict, Optional, Union
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_models.tongyi import ChatTongyi as ChatQwenMaxWithContext
import dashscope

from models_config import ModelType, model_selector, get_model_by_id
from dynamic_scraper import get_dynamic_content_for_query
from general_web_assistant import enhance_query_with_website_context
from web_search import enhance_with_web_search
from grade9_knowledge_indexer import grade9_indexer
from markdown_cleaner import clean_markdown_response
from vision_handler import VisionHandler, ImageProcessor
from embeddings_handler import EmbeddingsHandler, StudyMaterialsIndex
from educational_features import EducationalFeaturesHandler, TeachingMethod
from qwen_models import QwenModelType, QWEN_MODEL_CONFIGS

logger = logging.getLogger(__name__)

class EnhancedChatProcessor:
    """Enhanced chat processor with full Qwen capabilities"""
    
    def __init__(self, api_key: str, knowledge_service=None, conversation_service=None):
        self.api_key = api_key
        dashscope.api_key = api_key
        
        # Initialize all Qwen models
        self.models = {
            "qwen-max": ChatQwenMaxWithContext(
                model="qwen-max",
                api_key=api_key,
                temperature=0.7,
                max_tokens=8192
            ),
            "qwen-plus": ChatQwenMaxWithContext(
                model="qwen-plus",
                api_key=api_key,
                temperature=0.7,
                max_tokens=4096
            ),
            "qwen-turbo": ChatQwenMaxWithContext(
                model="qwen-turbo",
                api_key=api_key,
                temperature=0.5,
                max_tokens=4096
            ),
            "qwen-math-plus": ChatQwenMaxWithContext(
                model="qwen-math-plus",
                api_key=api_key,
                temperature=0.3,
                max_tokens=4096
            )
        }
        
        # Initialize handlers
        self.vision_handler = VisionHandler(api_key)
        self.embeddings_handler = EmbeddingsHandler(api_key)
        self.educational_handler = EducationalFeaturesHandler(self.models["qwen-max"])
        self.study_index = StudyMaterialsIndex(self.embeddings_handler)
        
        # Services
        self.knowledge_service = knowledge_service
        self.conversation_service = conversation_service
        
        # Cache for embeddings
        self.embeddings_cache = {}
        
    def process_chat(self, request, memory=None) -> dict:
        """Process chat with enhanced capabilities"""
        start_time = time.time()
        
        try:
            # Extract message and check for images
            message = request.get("message", "")
            images = request.get("images", [])
            session_id = request.get("session_id", "default")
            model = request.get("model", "general")
            
            # Check if this is an image query
            if images:
                return self._process_vision_query(message, images)
            
            # Check for educational features
            if any(keyword in message.lower() for keyword in ["teach me", "explain", "tutor", "study", "learn"]):
                return self._process_educational_query(message, session_id)
            
            # Check for math problems
            if any(keyword in message.lower() for keyword in ["solve", "calculate", "equation", "math", "formula"]):
                return self._process_math_query(message)
            
            # Regular chat processing based on model
            model_type = get_model_by_id(model) or ModelType.GENERAL
            
            if model_type == ModelType.GENERAL:
                return self._process_general_enhanced(message)
            elif model_type == ModelType.EVEREST:
                return self._process_everest_enhanced(message, session_id)
            elif model_type == ModelType.WEB_SCRAPER:
                return self._process_web_enhanced(message)
            else:
                return self._process_general_enhanced(message)
                
        except Exception as e:
            logger.error(f"Enhanced chat processor error: {e}")
            return {
                "response": "I encountered an error processing your request. Please try again.",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_vision_query(self, message: str, images: List[str]) -> dict:
        """Process queries with images using Qwen-VL"""
        logger.info("Processing vision query")
        
        # Compress images if needed
        processed_images = []
        for img in images:
            if img.startswith('data:image'):
                compressed = ImageProcessor.compress_image(img)
                processed_images.append(compressed)
            else:
                processed_images.append(img)
        
        # Analyze with vision model
        result = self.vision_handler.analyze_image(
            processed_images,
            message or "What is in this image?",
            model="qwen-vl-max"
        )
        
        if result["success"]:
            return {
                "response": clean_markdown_response(result["message"]),
                "success": True,
                "model": "qwen-vl-max",
                "features_used": ["vision", "image_analysis"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "response": result["message"],
                "success": False,
                "error": result.get("error"),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_educational_query(self, message: str, session_id: str) -> dict:
        """Process educational queries with advanced teaching methods"""
        logger.info("Processing educational query")
        
        # Determine teaching method based on query
        if "socratic" in message.lower() or "question" in message.lower():
            result = self.educational_handler.create_socratic_dialogue(
                topic=message,
                student_response="",
                depth_level=1
            )
        elif "tutor" in message.lower() or "feedback" in message.lower():
            result = self.educational_handler.oxford_tutorial(
                essay_or_problem=message,
                subject="General"
            )
        elif "case" in message.lower() or "scenario" in message.lower():
            result = self.educational_handler.harvard_case_method(
                case_scenario=message,
                student_analysis=""
            )
        elif "problem" in message.lower() or "exercise" in message.lower():
            result = self.educational_handler.mit_problem_sets(
                topic=message,
                difficulty="medium"
            )
        else:
            # Default to adaptive learning path
            student_profile = {
                "learning_style": "mixed",
                "knowledge_level": "intermediate",
                "available_time": "flexible",
                "goals": "comprehensive understanding"
            }
            result = self.educational_handler.adaptive_learning_path(
                student_profile=student_profile,
                topic=message
            )
        
        response = result.get("response") or result.get("feedback") or result.get("learning_path", "")
        
        return {
            "response": clean_markdown_response(str(response)),
            "success": True,
            "model": "qwen-max",
            "features_used": ["educational", result["method"]],
            "educational_context": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _process_math_query(self, message: str) -> dict:
        """Process mathematical queries with Qwen-Math"""
        logger.info("Processing math query with specialized model")
        
        prompt = f"""You are an expert mathematics tutor. Solve this problem step-by-step:

{message}

Provide:
1. Problem understanding
2. Step-by-step solution
3. Final answer clearly marked
4. Verification of the answer
5. Common mistakes to avoid"""
        
        messages = [HumanMessage(content=prompt)]
        
        try:
            response = self.models["qwen-math-plus"].invoke(messages)
            
            return {
                "response": clean_markdown_response(response.content),
                "success": True,
                "model": "qwen-math-plus",
                "features_used": ["mathematical_reasoning", "step_by_step_solution"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Math model error: {e}")
            # Fallback to regular model
            return self._process_general_enhanced(message)
    
    def _process_general_enhanced(self, message: str) -> dict:
        """Enhanced general processing with current info"""
        current_date = datetime.now()
        date_str = current_date.strftime("%B %d, %Y")
        day_name = current_date.strftime("%A")
        
        # Check if query needs web search
        web_search_result = enhance_with_web_search(message, self.api_key)
        features_used = []
        
        context = ""
        if web_search_result.get('needs_search'):
            context = web_search_result.get('search_context', '')
            features_used.append('web_search')
        
        system_prompt = f"""You are an advanced AI assistant powered by Qwen-Max with access to current information.
Today's date: {date_str} ({day_name})
Current time: {current_date.strftime("%I:%M %p")}

{context}

Capabilities:
- Current events and real-time information
- Complex reasoning and analysis
- Creative problem solving
- Technical expertise

Provide helpful, accurate, and engaging responses."""
        
        messages = [HumanMessage(content=system_prompt + "\n\nUser: " + message)]
        
        try:
            response = self.models["qwen-max"].invoke(messages)
            
            return {
                "response": clean_markdown_response(response.content),
                "success": True,
                "model": "qwen-max",
                "features_used": features_used,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"General model error: {e}")
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_everest_enhanced(self, message: str, session_id: str) -> dict:
        """Enhanced Everest processing with Grade 9 resources and embeddings"""
        features_used = ['everest_knowledge', 'grade9_resources']
        
        # Search Grade 9 resources
        grade9_results = grade9_indexer.search_resources(message)
        grade9_context = grade9_indexer.format_for_context(grade9_results) if grade9_results else ""
        
        # Get knowledge base context
        context = ""
        if self.conversation_service:
            context = self.conversation_service.get_recent_context(
                session_id,
                message,
                self.knowledge_service
            )
        
        # Try web scraping for current info
        dynamic_content = ""
        try:
            dynamic_content = get_dynamic_content_for_query(message)
            if dynamic_content:
                features_used.append('web_scraping')
        except Exception as e:
            logger.error(f"Scraping error: {e}")
        
        # Use embeddings for semantic search if available
        if self.knowledge_service:
            # Search knowledge base using embeddings
            knowledge_docs = []
            # Convert knowledge to searchable format
            # This would need to be implemented in knowledge_service
            semantic_results = self.embeddings_handler.semantic_search(
                message,
                knowledge_docs,
                top_k=3
            )
            if semantic_results:
                features_used.append('semantic_search')
        
        # Combine all context
        full_context = f"""
{context}

{grade9_context}

{dynamic_content}

You are an AI assistant for Everest Academy Manila with access to:
1. Grade 9 study materials and resources
2. Current school information from the website
3. Educational best practices

Provide helpful, accurate responses for students, parents, and teachers."""
        
        messages = [HumanMessage(content=full_context + "\n\nUser: " + message)]
        
        try:
            response = self.models["qwen-max"].invoke(messages)
            
            return {
                "response": clean_markdown_response(response.content),
                "success": True,
                "model": "qwen-max",
                "features_used": features_used,
                "grade9_resources": len(grade9_results) if grade9_results else 0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Everest model error: {e}")
            return {
                "response": "I apologize for the error. Please visit https://everestmanila.com for assistance.",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_web_enhanced(self, message: str) -> dict:
        """Enhanced web processing with better scraping"""
        features_used = ['web_scraping']
        
        web_enhancement = enhance_query_with_website_context(message)
        
        if not web_enhancement['has_website_context']:
            return {
                "response": """I'm the Web Research Assistant with advanced capabilities. Please include a website URL in your query.

I can:
- Analyze e-commerce products and prices
- Extract information from articles and blogs
- Research technical documentation
- Compare products across sites
- Summarize long content

Example: "Find the best laptops under $1000 on amazon.com" """,
                "success": True,
                "features_used": [],
                "timestamp": datetime.now().isoformat()
            }
        
        dynamic_content = web_enhancement['website_context']
        cleaned_query = web_enhancement['cleaned_query']
        
        system_prompt = f"""You are an advanced web research assistant.

Web Content:
{dynamic_content}

Instructions:
1. Analyze the content thoroughly
2. Extract specific information requested
3. Provide accurate prices, specifications, and details
4. Include all relevant URLs
5. Organize information clearly

User Query: {cleaned_query}"""
        
        messages = [HumanMessage(content=system_prompt)]
        
        try:
            response = self.models["qwen-max"].invoke(messages)
            
            # Extract sources
            sources = self._extract_sources(response.content)
            sources.extend(self._extract_sources(dynamic_content))
            sources = list(dict.fromkeys(sources))
            
            return {
                "response": clean_markdown_response(response.content),
                "success": True,
                "model": "qwen-max",
                "features_used": features_used,
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Web scraper error: {e}")
            return {
                "response": "Error processing web content. Please check the URL and try again.",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_sources(self, text: str) -> List[str]:
        """Extract URLs from text"""
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
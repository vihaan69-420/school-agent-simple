#!/usr/bin/env python3
"""
Enhanced chat endpoint with model-specific handling
"""

from fastapi import HTTPException
from langchain.schema import HumanMessage, AIMessage
import logging
from typing import List, Dict, Optional
import time
from datetime import datetime

from models_config import ModelType, model_selector, get_model_by_id
from dynamic_scraper import get_dynamic_content_for_query
from general_web_assistant import enhance_query_with_website_context
from web_search import enhance_with_web_search
from grade9_knowledge_indexer import grade9_indexer
from markdown_cleaner import clean_markdown_response
from simple_vision_handler import analyze_image_with_qwen_vl

logger = logging.getLogger(__name__)

class ChatProcessor:
    """Handles chat processing for different models"""
    
    def __init__(self, qwen_llm, knowledge_service, conversation_service):
        self.qwen_llm = qwen_llm
        self.knowledge_service = knowledge_service
        self.conversation_service = conversation_service
    
    def process_chat(self, request, memory) -> dict:
        """Process chat based on selected model"""
        start_time = time.time()
        
        # Get model configuration
        model_type = get_model_by_id(request.model) or ModelType.GENERAL
        model_config = model_selector.get_model_config(model_type)
        
        logger.info(f"Processing with {model_config.display_name}")
        
        # Get latest message
        latest_message = request.messages[-1]
        
        # Check if message contains image data
        if 'data:image' in latest_message.content:
            return self._process_image_query(latest_message.content)
        
        # Process based on model type
        if model_type == ModelType.GENERAL:
            result = self._process_general(request, latest_message, model_config)
        elif model_type == ModelType.EVEREST:
            result = self._process_everest(request, latest_message, model_config)
        elif model_type == ModelType.WEB_SCRAPER:
            result = self._process_web_scraper(request, latest_message, model_config)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Add metadata
        result['metadata'] = {
            'model': model_config.display_name,
            'model_id': model_type.value,
            'processing_time': time.time() - start_time,
            'features_used': result.get('features_used', [])
        }
        
        return result
    
    def _process_general(self, request, latest_message, model_config) -> dict:
        """Process general queries with web search capability"""
        features_used = []
        
        # Get current date dynamically
        current_date = datetime.now()
        date_str = current_date.strftime("%B %d, %Y")
        day_name = current_date.strftime("%A")
        
        # Determine current US president based on date
        if current_date.year > 2025 or (current_date.year == 2025 and current_date.month >= 1 and current_date.day >= 20):
            current_president = "Donald Trump (47th President)"
        else:
            current_president = "Joe Biden (46th President)"
        
        # Check if web search is needed
        web_search_result = enhance_with_web_search(latest_message.content)
        
        # Build dynamic system prompt with current date
        system_prompt = f"""You are a helpful, fast AI assistant with access to current information through web search.
Today's date: {date_str} ({day_name})
Current year: {current_date.year}
Current month: {current_date.strftime('%B')}
Current US President: {current_president}
Context: You have real-time awareness and can search the web for current information when needed.

Instructions:
1. If you have web search results, use them to provide accurate, current information
2. Always cite your sources when using web search results
3. Be concise and direct in your responses
4. If web search fails or returns no results, acknowledge this honestly"""
        
        # Add web search results if available
        user_query = latest_message.content
        if web_search_result['needs_search'] and web_search_result['search_results']:
            features_used.append('web_search')
            user_query = f"{web_search_result['enhanced_context']}\n\nUser Question: {latest_message.content}"
        
        # Create messages for LLM with conversation history
        messages = []
        
        # Add system prompt
        messages.append(HumanMessage(content=system_prompt))
        
        # Include conversation history from request
        for msg in request.messages[:-1]:  # All messages except the latest
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        
        # Add the current query
        messages.append(HumanMessage(content=user_query))
        
        # Configure LLM for speed
        self.qwen_llm.temperature = model_config.temperature
        self.qwen_llm.max_tokens = model_config.max_tokens
        
        try:
            response = self.qwen_llm.invoke(messages)
            
            # Extract any sources from the response
            sources = []
            if web_search_result['needs_search']:
                sources = self._extract_sources(response.content)
                if web_search_result.get('search_results'):
                    sources.append("Web Search Results")
            
            return {
                'message': clean_markdown_response(response.content),
                'success': True,
                'features_used': features_used,
                'sources': sources if sources else None
            }
        except Exception as e:
            logger.error(f"General model error: {e}")
            return {
                'message': "I apologize, but I encountered an error. Please try again.",
                'success': False,
                'error': str(e)
            }
    
    def _process_everest(self, request, latest_message, model_config) -> dict:
        """Process Everest Academy queries with optimized performance"""
        features_used = []
        
        # Check if query is about Grade 9 resources
        query_lower = latest_message.content.lower()
        grade9_keywords = ['grade 9', 'grade nine', 'g9', 'study', 'lesson', 'chapter', 'topic', 'subject', 'math', 'science']
        is_grade9_query = any(keyword in query_lower for keyword in grade9_keywords)
        
        # Get knowledge base context with reduced limit for speed
        context = self.conversation_service.get_recent_context(
            request.session_id,
            latest_message.content,
            self.knowledge_service
        )
        features_used.append('knowledge_base')
        
        # Only scrape if question likely needs fresh data
        dynamic_content = ""
        scraping_keywords = ['admission', 'apply', 'tuition', 'fee', 'contact', 'schedule', 'process']
        should_scrape = any(keyword in latest_message.content.lower() for keyword in scraping_keywords)
        
        if should_scrape:
            try:
                logger.info("Fetching targeted Everest Academy data...")
                dynamic_content = get_dynamic_content_for_query(latest_message.content)
                if dynamic_content:
                    features_used.append('web_scraping')
            except Exception as e:
                logger.error(f"Everest scraping error: {e}")
        
        # Check for Grade 9 resources if relevant
        grade9_context = ""
        if is_grade9_query:
            # Search for relevant Grade 9 resources
            grade9_results = grade9_indexer.search_resources(latest_message.content)
            if grade9_results:
                grade9_context = grade9_indexer.format_for_context(grade9_results)
                features_used.append('grade9_resources')
        
        # Combine contexts efficiently
        full_context = context
        if dynamic_content:
            full_context += f"\n\n{dynamic_content}"
        if grade9_context:
            full_context += f"\n\n{grade9_context}"
        
        # Build optimized Everest prompt
        system_prompt = f"""{model_config.system_prompt}

Context and Knowledge Base:
{full_context}

CRITICAL Instructions:
1. Interpret all questions as Everest Academy related
2. Use URLs from context ONLY - cite each URL only ONCE
3. Be concise - provide essential information first
4. For admissions: mention https://everestmanila.com/admissions/application-process
5. Format: Brief answer → Key details → Source (if any)
6. DO NOT repeat the same link multiple times in your response
7. For Grade 9 study resources: List available materials and topics when asked
8. If student asks about specific subjects, provide relevant Grade 9 resources

User Question: {latest_message.content}"""
        
        # Configure LLM
        self.qwen_llm.temperature = model_config.temperature
        self.qwen_llm.max_tokens = model_config.max_tokens
        
        messages = [HumanMessage(content=system_prompt)]
        
        try:
            response = self.qwen_llm.invoke(messages)
            
            # Extract sources from response
            sources = self._extract_sources(response.content)
            
            return {
                'message': clean_markdown_response(response.content),
                'success': True,
                'features_used': features_used,
                'sources': sources
            }
        except Exception as e:
            logger.error(f"Everest model error: {e}")
            return {
                'message': "I apologize for the error. Please visit https://everestmanila.com or contact admissions@everestmanila.edu.ph for assistance.",
                'success': False,
                'error': str(e)
            }
    
    def _process_web_scraper(self, request, latest_message, model_config) -> dict:
        """Process web scraping queries for any website"""
        features_used = ['web_scraping']
        
        # Check for website context
        web_enhancement = enhance_query_with_website_context(latest_message.content)
        
        if not web_enhancement['has_website_context']:
            # No URL found - provide guidance
            return {
                'message': """I'm the Web Research Assistant. To help you effectively, please include a website URL in your query.

Examples:
- "Find the latest iPhone prices on amazon.com"
- "What does this article say about AI? https://example.com/ai-article"
- "Extract product details from https://store.com/product/123"

I can analyze e-commerce sites, blogs, news articles, documentation, and more. Just provide the URL!""",
                'success': True,
                'features_used': []
            }
        
        # We have web context
        dynamic_content = web_enhancement['website_context']
        cleaned_query = web_enhancement['cleaned_query']
        
        # Build research-focused prompt
        system_prompt = f"""{model_config.system_prompt}

Web Research Context:
{dynamic_content}

Research Instructions:
1. Analyze the scraped content thoroughly
2. Extract specific information requested by the user
3. Provide exact quotes when relevant
4. Include all source URLs with [Source: URL] format
5. Structure information clearly with headers/sections
6. For products: include prices, specifications, availability
7. For articles: summarize key points, quotes, conclusions
8. Always verify and cite your sources

User's Research Query: {cleaned_query}"""
        
        # Configure LLM for detailed analysis
        self.qwen_llm.temperature = model_config.temperature
        self.qwen_llm.max_tokens = model_config.max_tokens
        
        messages = [HumanMessage(content=system_prompt)]
        
        try:
            response = self.qwen_llm.invoke(messages)
            
            # Extract all sources
            sources = self._extract_sources(response.content)
            sources.extend(self._extract_sources(dynamic_content))
            
            # Remove duplicates
            sources = list(dict.fromkeys(sources))
            
            return {
                'message': clean_markdown_response(response.content),
                'success': True,
                'features_used': features_used,
                'sources': sources,
                'research_metadata': {
                    'websites_analyzed': len(sources),
                    'query_type': 'web_research'
                }
            }
        except Exception as e:
            logger.error(f"Web scraper model error: {e}")
            return {
                'message': "I encountered an error while researching. Please check the URL and try again.",
                'success': False,
                'error': str(e)
            }
    
    def _extract_sources(self, text: str) -> List[str]:
        """Extract source URLs from text"""
        import re
        sources = []
        
        # Pattern for [Source: URL] format
        pattern1 = r'\[Source:\s*(https?://[^\]]+)\]'
        sources.extend(re.findall(pattern1, text))
        
        # Pattern for (Source: URL) format
        pattern2 = r'\(Source:\s*(https?://[^\)]+)\)'
        sources.extend(re.findall(pattern2, text))
        
        # Pattern for URL: format
        pattern3 = r'URL:\s*(https?://[^\s]+)'
        sources.extend(re.findall(pattern3, text))
        
        return list(set(sources))
    
    def _process_image_query(self, content: str) -> dict:
        """Process queries containing images using Qwen-VL"""
        try:
            # Extract image data and text
            import re
            
            # Find image data URL
            image_match = re.search(r'(data:image[^)]+)', content)
            if not image_match:
                return {
                    'message': "I couldn't find a valid image in your message.",
                    'success': False
                }
            
            image_data = image_match.group(1)
            
            # Extract question text (remove image markdown)
            text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', content).strip()
            if not text:
                text = "What is in this image?"
            
            # Get API key
            api_key = self.qwen_llm.openai_api_key
            
            # Analyze image
            logger.info("Processing image with Qwen-VL")
            response = analyze_image_with_qwen_vl(image_data, text, api_key)
            
            return {
                'message': clean_markdown_response(response),
                'success': True,
                'features_used': ['vision', 'image_analysis'],
                'metadata': {
                    'model': 'qwen-vl-max',
                    'capabilities': ['image_understanding', 'ocr', 'visual_qa']
                }
            }
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            return {
                'message': f"I encountered an error analyzing the image: {str(e)}",
                'success': False,
                'error': str(e)
            }  # Remove duplicates
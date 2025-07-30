#!/usr/bin/env python3
"""
Model configuration system for different AI assistants
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class ModelType(Enum):
    GENERAL = "general"
    EVEREST = "everest"
    WEB_SCRAPER = "web_scraper"

@dataclass
class ModelConfig:
    """Configuration for each model type"""
    name: str
    display_name: str
    description: str
    icon: str
    color: str
    temperature: float
    max_tokens: int
    features: Dict[str, bool]
    system_prompt: str
    response_style: str

# Model configurations
MODEL_CONFIGS = {
    ModelType.GENERAL: ModelConfig(
        name="general",
        display_name="Study Companion",
        description="Quick, accurate responses for general academic queries and homework help.",
        icon="⚡",
        color="#1e3a8a",  # Navy Blue
        temperature=0.7,
        max_tokens=500,
        features={
            "web_scraping": False,
            "web_search": True,
            "knowledge_base": False,
            "streaming": True,
            "citations": True
        },
        system_prompt="""You are a helpful, fast AI assistant with web search capabilities for current information. Be concise and direct in your responses.""",
        response_style="concise"
    ),
    
    ModelType.EVEREST: ModelConfig(
        name="everest",
        display_name="Everest Scholar",
        description="Official Everest Academy assistant with comprehensive school information.",
        icon="🎓",
        color="#d97706",  # Gold
        temperature=0.5,
        max_tokens=600,  # Reduced for speed
        features={
            "web_scraping": True,
            "knowledge_base": True,
            "streaming": True,
            "citations": True
        },
        system_prompt="""You are the official AI assistant for Everest Academy Manila. 
Always interpret questions in the context of Everest Academy. Provide accurate information with proper source URLs.
IMPORTANT: Only cite each URL ONCE - do not repeat the same link multiple times.
Be concise but thorough. Focus on the most relevant information.""",
        response_style="detailed"
    ),
    
    ModelType.WEB_SCRAPER: ModelConfig(
        name="web_scraper",
        display_name="Research Scholar",
        description="Advanced academic research tool for comprehensive web analysis and citations.",
        icon="🌐",
        color="#1e40af",  # Academic Blue
        temperature=0.3,
        max_tokens=1200,
        features={
            "web_scraping": True,
            "knowledge_base": False,
            "streaming": True,
            "citations": True,
            "multi_site": True
        },
        system_prompt="""You are an advanced web research assistant. Your primary function is to:
1. Extract and analyze content from any website mentioned by the user
2. Provide detailed citations with exact URLs and page sections
3. Structure information clearly with sources
4. Handle e-commerce, blogs, news sites, documentation, etc.
Always cite your sources with [Source: URL] format.""",
        response_style="research"
    )
}

class ModelSelector:
    """Handles model selection and configuration"""
    
    def __init__(self):
        self.current_model = ModelType.GENERAL
        self.model_stats = {
            model: {
                "usage_count": 0,
                "avg_response_time": 0,
                "last_used": None
            } for model in ModelType
        }
    
    def get_model_config(self, model_type: ModelType) -> ModelConfig:
        """Get configuration for a specific model"""
        return MODEL_CONFIGS[model_type]
    
    def get_all_models_info(self) -> list:
        """Get information about all available models for UI"""
        return [
            {
                "id": model.value,
                "name": config.display_name,
                "description": config.description,
                "icon": config.icon,
                "color": config.color,
                "features": config.features
            }
            for model, config in MODEL_CONFIGS.items()
        ]
    
    def should_use_web_scraping(self, model_type: ModelType, query: str) -> bool:
        """Determine if web scraping should be used based on model and query"""
        config = self.get_model_config(model_type)
        
        if not config.features.get("web_scraping", False):
            return False
        
        if model_type == ModelType.EVEREST:
            # Only scrape for Everest-related queries
            return True
        elif model_type == ModelType.WEB_SCRAPER:
            # Always ready to scrape
            return True
        
        return False
    
    def should_use_knowledge_base(self, model_type: ModelType) -> bool:
        """Determine if knowledge base should be used"""
        config = self.get_model_config(model_type)
        return config.features.get("knowledge_base", False)
    
    def get_system_prompt(self, model_type: ModelType, context: str = "") -> str:
        """Get the system prompt for the model with optional context"""
        config = self.get_model_config(model_type)
        base_prompt = config.system_prompt
        
        if context:
            return f"{base_prompt}\n\nContext:\n{context}"
        
        return base_prompt
    
    def format_response(self, model_type: ModelType, response: str, sources: list = None) -> dict:
        """Format response based on model type"""
        config = self.get_model_config(model_type)
        
        formatted = {
            "message": response,
            "model": config.display_name,
            "model_id": model_type.value,
            "features_used": []
        }
        
        # Add sources if available
        if sources and config.features.get("citations", False):
            formatted["sources"] = sources
            formatted["features_used"].append("citations")
        
        # Add feature indicators
        if config.features.get("web_scraping", False):
            formatted["features_used"].append("web_scraping")
        if config.features.get("knowledge_base", False):
            formatted["features_used"].append("knowledge_base")
        
        return formatted

# Global model selector instance
model_selector = ModelSelector()

def get_model_by_id(model_id: str) -> Optional[ModelType]:
    """Get ModelType by string ID"""
    for model in ModelType:
        if model.value == model_id:
            return model
    return None
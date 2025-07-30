"""
Qwen Models Configuration - Using ALL available Qwen capabilities
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict

class QwenModelType(Enum):
    # Text Generation Models
    QWEN_MAX = "qwen-max"  # Most capable text model
    QWEN_PLUS = "qwen-plus"  # Balanced performance
    QWEN_TURBO = "qwen-turbo"  # Fast responses
    
    # Vision-Language Models
    QWEN_VL_MAX = "qwen-vl-max"  # Best vision model
    QWEN_VL_PLUS = "qwen-vl-plus"  # Vision with good performance
    
    # Specialized Models
    QWEN_MATH = "qwen-math-plus"  # Mathematical reasoning
    QWEN_CODER = "qwen-coder"  # Code generation
    
    # Embedding Models
    TEXT_EMBEDDING_V3 = "text-embedding-v3"  # Latest embeddings
    TEXT_EMBEDDING_V2 = "text-embedding-v2"  # Stable embeddings
    
    # Audio Models
    QWEN_AUDIO_TURBO = "qwen-audio-turbo"  # Speech recognition
    COSYVOICE = "cosyvoice-v1"  # Text to speech

@dataclass
class QwenModelConfig:
    model_name: str
    display_name: str
    description: str
    capabilities: List[str]
    max_tokens: int = 4096
    temperature: float = 0.7
    supports_vision: bool = False
    supports_audio: bool = False
    supports_tools: bool = True

# Model Configurations
QWEN_MODEL_CONFIGS = {
    QwenModelType.QWEN_MAX: QwenModelConfig(
        model_name="qwen-max",
        display_name="Qwen Max",
        description="Most capable model for complex reasoning",
        capabilities=["reasoning", "analysis", "creative_writing", "math", "coding"],
        max_tokens=8192,
        temperature=0.7,
        supports_tools=True
    ),
    
    QwenModelType.QWEN_VL_MAX: QwenModelConfig(
        model_name="qwen-vl-max",
        display_name="Qwen Vision Max",
        description="Analyzes images, diagrams, charts, and visual content",
        capabilities=["image_analysis", "ocr", "diagram_understanding", "visual_qa"],
        max_tokens=4096,
        temperature=0.7,
        supports_vision=True,
        supports_tools=True
    ),
    
    QwenModelType.QWEN_VL_PLUS: QwenModelConfig(
        model_name="qwen-vl-plus",
        display_name="Qwen Vision Plus",
        description="""Fast vision model for quick image analysis""",
        capabilities=["image_analysis", "ocr", "visual_qa"],
        max_tokens=4096,
        temperature=0.7,
        supports_vision=True
    ),
    
    QwenModelType.QWEN_MATH: QwenModelConfig(
        model_name="qwen-math-plus",
        display_name="Qwen Math Plus",
        description="Specialized for mathematical problem solving",
        capabilities=["math_solving", "proofs", "calculus", "statistics"],
        max_tokens=4096,
        temperature=0.3  # Lower temp for accuracy
    ),
    
    QwenModelType.QWEN_CODER: QwenModelConfig(
        model_name="qwen-coder",
        display_name="Qwen Coder",
        description="Optimized for code generation and analysis",
        capabilities=["code_generation", "debugging", "code_review", "refactoring"],
        max_tokens=8192,
        temperature=0.3
    ),
    
    QwenModelType.TEXT_EMBEDDING_V3: QwenModelConfig(
        model_name="text-embedding-v3",
        display_name="Text Embedding V3",
        description="Convert text to vectors for semantic search",
        capabilities=["embeddings", "similarity", "clustering"],
        max_tokens=8192
    ),
    
    QwenModelType.QWEN_AUDIO_TURBO: QwenModelConfig(
        model_name="qwen-audio-turbo",
        display_name="Qwen Audio",
        description="Transcribe and analyze audio content",
        capabilities=["speech_to_text", "audio_analysis"],
        supports_audio=True
    )
}

# Educational Features from Top Universities
EDUCATIONAL_FEATURES = {
    "harvard": {
        "case_method": "Analyze real-world scenarios and make decisions",
        "socratic_teaching": "Guide learning through questions",
        "peer_learning": "Collaborative problem solving"
    },
    "oxford": {
        "tutorial_system": "One-on-one personalized tutoring",
        "essay_feedback": "Detailed writing analysis and improvement",
        "critical_thinking": "Develop analytical reasoning"
    },
    "mit": {
        "problem_sets": "Hands-on problem solving",
        "project_based": "Learn by building",
        "flipped_classroom": "Interactive learning sessions"
    },
    "stanford": {
        "design_thinking": "Creative problem solving process",
        "entrepreneurial": "Innovation and startup mindset",
        "interdisciplinary": "Connect concepts across fields"
    }
}

# Study Tools and Features
STUDY_FEATURES = {
    "active_recall": {
        "flashcards": "Spaced repetition system",
        "quiz_generation": "Auto-generate practice questions",
        "concept_testing": "Check understanding"
    },
    "note_taking": {
        "cornell_notes": "Structured note-taking system",
        "mind_maps": "Visual concept mapping",
        "summary_generation": "Auto-summarize content"
    },
    "assessment": {
        "diagnostic_tests": "Identify knowledge gaps",
        "progress_tracking": "Monitor learning journey",
        "adaptive_questions": "Adjust difficulty based on performance"
    },
    "collaboration": {
        "study_groups": "Virtual study sessions",
        "peer_review": "Get feedback from others",
        "discussion_forums": "Topic-based discussions"
    }
}
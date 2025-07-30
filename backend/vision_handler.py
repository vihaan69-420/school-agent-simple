"""
Vision Handler for Qwen-VL Models
Handles image analysis, OCR, diagram understanding, etc.
"""
import base64
import logging
from typing import List, Dict, Optional, Union
from io import BytesIO
from PIL import Image
import dashscope
from dashscope import MultiModalConversation
from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)

class VisionHandler:
    def __init__(self, api_key: str):
        self.api_key = api_key
        dashscope.api_key = api_key
        
    def analyze_image(self, image_data: Union[str, List[str]], query: str, model: str = "qwen-vl-max") -> Dict:
        """
        Analyze images using Qwen-VL models
        
        Args:
            image_data: Base64 encoded image(s) or image URLs
            query: User's question about the image
            model: Which Qwen-VL model to use
        """
        try:
            # Prepare messages for vision model
            messages = []
            
            # Handle multiple images
            if isinstance(image_data, list):
                content = [{"text": query}]
                for img in image_data:
                    if img.startswith('data:image'):
                        # Extract base64 data
                        content.append({"image": img})
                    elif img.startswith('http'):
                        # URL
                        content.append({"image": img})
                    else:
                        # Assume it's base64 without prefix
                        content.append({"image": f"data:image/jpeg;base64,{img}"})
            else:
                # Single image
                content = [
                    {"text": query},
                    {"image": image_data if image_data.startswith(('data:', 'http')) else f"data:image/jpeg;base64,{image_data}"}
                ]
            
            messages.append({
                "role": "user",
                "content": content
            })
            
            # Call Qwen-VL API
            response = MultiModalConversation.call(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": response.output.choices[0].message.content,
                    "model_used": model,
                    "features": ["image_analysis", "visual_qa"]
                }
            else:
                logger.error(f"Vision API error: {response}")
                return {
                    "success": False,
                    "error": f"Vision API error: {response.message}",
                    "message": "I couldn't analyze the image. Please try again."
                }
                
        except Exception as e:
            logger.error(f"Vision handler error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error processing image. Please ensure the image is valid."
            }
    
    def extract_text_from_image(self, image_data: str) -> Dict:
        """Extract text from image using OCR capabilities"""
        return self.analyze_image(
            image_data, 
            "Extract all text from this image. Format it clearly and maintain the original structure.",
            model="qwen-vl-plus"
        )
    
    def analyze_diagram(self, image_data: str, subject: str = "general") -> Dict:
        """Analyze educational diagrams, charts, or graphs"""
        prompts = {
            "science": "Analyze this scientific diagram. Explain all components, labels, and relationships shown.",
            "math": "Analyze this mathematical diagram or graph. Explain the concepts, formulas, and relationships depicted.",
            "general": "Analyze this diagram thoroughly. Explain what it shows, all labeled parts, and the relationships between components."
        }
        
        return self.analyze_image(
            image_data,
            prompts.get(subject, prompts["general"]),
            model="qwen-vl-max"
        )
    
    def solve_visual_problem(self, image_data: str) -> Dict:
        """Solve problems shown in images (math problems, diagrams, etc.)"""
        return self.analyze_image(
            image_data,
            "This image contains a problem or question. Please analyze it and provide a detailed solution with step-by-step explanation.",
            model="qwen-vl-max"
        )
    
    def compare_images(self, images: List[str], query: str = "Compare these images") -> Dict:
        """Compare multiple images"""
        return self.analyze_image(images, query, model="qwen-vl-max")

class ImageProcessor:
    """Process images before sending to API"""
    
    @staticmethod
    def compress_image(image_data: str, max_size: int = 1024 * 1024) -> str:
        """Compress image to reduce size while maintaining quality"""
        try:
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            
            # Resize if too large
            max_dimension = 1920
            if image.width > max_dimension or image.height > max_dimension:
                image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Save with compression
            output = BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            compressed_data = base64.b64encode(output.getvalue()).decode()
            
            return f"data:image/jpeg;base64,{compressed_data}"
            
        except Exception as e:
            logger.error(f"Image compression error: {e}")
            return image_data  # Return original if compression fails
"""
Simple Vision Handler using Qwen-VL via Dashscope
"""
import logging
import dashscope
from dashscope import MultiModalConversation

logger = logging.getLogger(__name__)

def analyze_image_with_qwen_vl(image_data: str, text: str, api_key: str) -> str:
    """
    Analyze image using Qwen-VL model
    
    Args:
        image_data: Base64 encoded image data URL
        text: User's question about the image
        api_key: Dashscope API key
    """
    dashscope.api_key = api_key
    
    try:
        # Prepare the message with image
        messages = [{
            'role': 'user',
            'content': [
                {'text': text},
                {'image': image_data}
            ]
        }]
        
        # Call Qwen-VL
        response = MultiModalConversation.call(
            model='qwen-vl-max',
            messages=messages
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            logger.error(f"Qwen-VL API error: {response}")
            return f"I couldn't analyze the image. Error: {response.message}"
            
    except Exception as e:
        logger.error(f"Vision analysis error: {e}")
        return f"Error analyzing image: {str(e)}. Please make sure the image is valid."
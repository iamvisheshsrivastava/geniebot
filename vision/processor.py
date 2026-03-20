"""
Image processing module for GenieBot
Handles image captioning and tag extraction
"""

import io
from typing import Tuple, List, Dict
from PIL import Image
import requests
from transformers import BlipProcessor, BlipForConditionalGeneration

from utils.logger import setup_logger

logger = setup_logger(__name__)


class ImageProcessor:
    """Process images for captioning and tagging"""
    
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base"):
        """
        Initialize image processor
        
        Args:
            model_name: HuggingFace model name for image captioning
        """
        self.model_name = model_name
        
        logger.info(f"Loading image captioning model: {model_name}")
        
        try:
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name)
            logger.info("Image model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load image model: {e}")
            self.processor = None
            self.model = None
    
    def _is_model_available(self) -> bool:
        """Check if model is available"""
        return self.model is not None and self.processor is not None
    
    def _load_image(self, image_input) -> Image.Image:
        """
        Load image from bytes or file-like object
        
        Args:
            image_input: Bytes, file-like object, or PIL Image
        
        Returns:
            PIL Image object
        """
        if isinstance(image_input, Image.Image):
            return image_input
        
        if isinstance(image_input, bytes):
            return Image.open(io.BytesIO(image_input))
        
        if hasattr(image_input, 'read'):  # File-like object
            return Image.open(image_input)
        
        raise ValueError("Invalid image input")
    
    def generate_caption(self, image_input) -> str:
        """
        Generate caption for image
        
        Args:
            image_input: Image bytes, file path, or PIL Image
        
        Returns:
            Caption string
        """
        if not self._is_model_available():
            logger.error("Image model not available")
            return "Image processing model not available"
        
        try:
            logger.debug("Processing image for captioning")
            
            # Load image
            image = self._load_image(image_input)
            
            # Resize if too large (for memory efficiency)
            max_size = 512
            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                logger.debug("Image resized for memory efficiency")
            
            # Convert RGBA to RGB if needed
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Process image
            inputs = self.processor(image, return_tensors="pt")
            
            # Generate caption
            out = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            logger.debug(f"Generated caption: {caption}")
            
            return caption
        
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            return "Error: Could not process image"
    
    def extract_tags(self, caption: str, num_tags: int = 3) -> List[str]:
        """
        Extract tags from caption using simple keyword extraction
        
        Args:
            caption: Image caption
            num_tags: Number of tags to extract
        
        Returns:
            List of tag strings
        """
        logger.debug(f"Extracting tags from caption: {caption[:50]}...")
        
        # Simple tag extraction: take important nouns and adjectives
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'has',
            'have', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they'
        }
        
        # Split and clean words
        words = caption.lower().split()
        tags = []
        
        for word in words:
            # Clean word (remove punctuation)
            clean_word = ''.join(c for c in word if c.isalnum())
            
            # Add if not stop word and has reasonable length
            if clean_word and clean_word not in stop_words and len(clean_word) > 2:
                if clean_word not in tags:
                    tags.append(clean_word)
                    
                    if len(tags) == num_tags:
                        break
        
        logger.debug(f"Extracted tags: {tags}")
        
        return tags
    
    def process_image(self, image_input) -> Dict[str, any]:
        """
        Complete image processing pipeline
        
        Args:
            image_input: Image bytes, file path, or PIL Image
        
        Returns:
            Dictionary with caption and tags
        """
        logger.info("Starting image processing")
        
        try:
            # Generate caption
            caption = self.generate_caption(image_input)
            
            # Extract tags
            tags = self.extract_tags(caption, num_tags=3)
            
            result = {
                "caption": caption,
                "tags": tags,
                "success": True
            }
            
            logger.info(f"Image processing complete: {caption[:50]}...")
            
            return result
        
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {
                "caption": "Error processing image",
                "tags": [],
                "success": False,
                "error": str(e)
            }
    
    def is_available(self) -> bool:
        """Check if vision model is available"""
        return self._is_model_available()

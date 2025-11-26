from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
from app.utils.logger import logger
import os

class DocumentPreprocessor:
    def preprocess(self, image_path: str) -> str:
        """
        Preprocess image for better OCR accuracy using PIL
        GENTLER preprocessing to avoid losing text
        """
        logger.info(f"Preprocessing image: {image_path}")
        
        try:
            # Load image
            img = Image.open(image_path)
            original_size = img.size
            logger.info(f"Original image size: {img.size}, mode: {img.mode}")
            
            # Convert RGBA to RGB first if needed
            if img.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = background
                logger.info("Converted RGBA to RGB")
            
            # Resize if too small (upscale for better OCR)
            min_dimension = 2000
            if min(img.size) < min_dimension:
                ratio = min_dimension / min(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Upscaled from {original_size} to {img.size}")
            
            # Convert to grayscale
            img = img.convert('L')
            logger.info("Converted to grayscale")
            
            # GENTLE contrast enhancement (not too aggressive)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)  # Reduced from 2.5
            logger.info("Enhanced contrast gently")
            
            # GENTLE sharpening (just once)
            img = img.filter(ImageFilter.SHARPEN)
            logger.info("Applied sharpening")
            
            # Save WITHOUT aggressive binarization
            base_name = os.path.splitext(image_path)[0]
            ext = os.path.splitext(image_path)[1]
            preprocessed_path = f"{base_name}_preprocessed{ext}"
            
            img.save(preprocessed_path)
            logger.info(f"Preprocessed image saved: {preprocessed_path}")
            
            return preprocessed_path
        
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}", exc_info=True)
            logger.warning("Falling back to original image")
            return image_path

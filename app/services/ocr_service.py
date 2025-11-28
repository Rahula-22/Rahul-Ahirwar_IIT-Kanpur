import pytesseract
from typing import Dict, List
from app.utils.logger import logger
import os
import platform

# Try to import cv2, fallback to PIL if not available
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    from PIL import Image
    import numpy as np
    HAS_CV2 = False
    logger.warning("OpenCV not available, using PIL for image loading")

# PDF support
try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
    logger.warning("pdf2image not available, PDF support disabled")

class OCRService:
    def __init__(self):
        logger.info("Initializing OCR Service...")
        
        # Check if running on Vercel (no Tesseract available)
        import os
        is_vercel = os.getenv('VERCEL') == '1'
        
        if not is_vercel:
            # Auto-detect Tesseract on Windows
            if platform.system() == 'Windows':
                self._setup_tesseract_windows()
            
            # Test Tesseract
            try:
                version = pytesseract.get_tesseract_version()
                logger.info(f"Tesseract OCR is available: {version}")
            except Exception as e:
                logger.warning(f"Tesseract not available: {e}")
                logger.warning("Using fallback OCR (Pillow only)")
        else:
            logger.warning("Running on Vercel - Tesseract not available, using fallback OCR")
    
    def _setup_tesseract_windows(self):
        """Auto-detect Tesseract installation on Windows"""
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\HP\Downloads\Tesseract-OCR.exe",
            r"C:\Tesseract-OCR\tesseract.exe",
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract found at: {path}")
                return
        
        logger.warning("Tesseract not found in common Windows locations")
    
    def extract_text(self, image_path: str) -> Dict[str, any]:
        """
        Extract text using Tesseract OCR or fallback
        """
        logger.info(f"Extracting text from: {image_path}")
        
        try:
            # Read image
            if image_path.lower().endswith('.pdf'):
                if not HAS_PDF2IMAGE:
                    raise RuntimeError("PDF support not available. Install: pip install pdf2image")
                logger.info("Converting PDF to image...")
                images = convert_from_path(image_path, dpi=300)
                image = np.array(images[0])
            else:
                if HAS_CV2:
                    image = cv2.imread(image_path)
                    if image is None:
                        raise ValueError(f"Failed to load image: {image_path}")
                else:
                    # Use PIL
                    pil_image = Image.open(image_path)
                    # Convert RGBA to RGB if needed
                    if pil_image.mode == 'RGBA':
                        background = Image.new('RGB', pil_image.size, (255, 255, 255))
                        background.paste(pil_image, mask=pil_image.split()[3])
                        pil_image = background
                    image = np.array(pil_image)
            
            logger.info(f"Image loaded successfully")
            
            # Try Tesseract if available
            try:
                import pytesseract
                logger.info("Running Tesseract OCR with multiple PSM modes...")
                
                # Try different page segmentation modes for better results
                configs = [
                    '--psm 3 -l eng+hin',  # English + Hindi
                    '--psm 6 -l eng+hin',  # Uniform block with multilingual
                    '--psm 4 -l eng',      # Single column English
                    '--psm 3',             # Default
                    '',                    # No special config
                ]
                
                texts = []
                for config in configs:
                    try:
                        if config:
                            text = pytesseract.image_to_string(image, config=config)
                        else:
                            text = pytesseract.image_to_string(image)
                        texts.append(text)
                        logger.info(f"OCR with {config if config else 'default'}: {len(text)} chars")
                        # If we got good text, stop trying
                        if len(text.strip()) > 100:
                            logger.info(f"Got good OCR result, stopping")
                            break
                    except Exception as e:
                        logger.warning(f"OCR with config '{config}' failed: {e}")
                
                # Use the longest result (usually most complete)
                tesseract_text = max(texts, key=len) if texts else ""
                
            except Exception as e:
                logger.warning(f"Tesseract OCR failed, using fallback: {e}")
                # Fallback: return basic image info for LLM
                tesseract_text = f"[Image: {image.shape[1]}x{image.shape[0]} pixels]\n"
                tesseract_text += "Note: OCR unavailable, please deploy on platform with Tesseract support for full functionality."
            
            # Log extracted text for debugging
            logger.info(f"Best OCR result: {len(tesseract_text)} characters")
            logger.info(f"OCR Text Preview (first 1000 chars):\n{tesseract_text[:1000]}")
            if len(tesseract_text) > 1000:
                logger.info(f"OCR Text Preview (last 500 chars):\n{tesseract_text[-500:]}")
            
            # Check if we got meaningful text
            if len(tesseract_text.strip()) < 50:
                logger.warning("OCR extracted very little text - image quality may be poor or Tesseract unavailable")
            
            # Also get data with bounding boxes for better structure (if Tesseract available)
            try:
                import pytesseract
                data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                bounding_boxes = self._extract_bounding_boxes(data)
            except Exception as e:
                logger.warning(f"Failed to extract bounding boxes: {e}")
                bounding_boxes = []
            
            logger.info(f"Extracted {len(tesseract_text)} characters")
            
            return {
                "text": tesseract_text,
                "bounding_boxes": bounding_boxes,
                "raw_tesseract": tesseract_text
            }
        
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}", exc_info=True)
            raise
    
    def _extract_bounding_boxes(self, data: Dict) -> List:
        """Extract bounding boxes from Tesseract data output"""
        bounding_boxes = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 30:  # Only confident detections
                text = data['text'][i].strip()
                if text:  # Only non-empty text
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    # Format similar to EasyOCR: [[coordinates], text, confidence]
                    bounding_boxes.append([
                        [[x, y], [x+w, y], [x+w, y+h], [x, y+h]],
                        text,
                        float(data['conf'][i]) / 100
                    ])
        
        return bounding_boxes

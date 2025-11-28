import time
import os
from typing import List
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService
from app.services.preprocessor import DocumentPreprocessor
from app.services.fraud_detector import FraudDetector
from app.models.schemas import ExtractionData, PagewiseLineItems, ExtractionResponse, TokenUsage
from app.utils.logger import logger

class DocumentProcessor:
    def __init__(self):
        logger.info("Initializing DocumentProcessor...")
        self.ocr_service = OCRService()
        self.llm_service = LLMService()
        self.preprocessor = DocumentPreprocessor()
        self.fraud_detector = FraudDetector()
        logger.info("DocumentProcessor initialized successfully")
    
    async def process_document(self, file_path: str) -> ExtractionResponse:
        """Process single or multi-page document"""
        start_time = time.time()
        logger.info(f"Processing document: {file_path}")
        
        try:
            # Step 1: Preprocess image
            logger.info("Step 1: Preprocessing image...")
            preprocessed_path = self.preprocessor.preprocess(file_path)
            logger.info(f"Preprocessing complete: {preprocessed_path}")
            
            # Step 2: OCR extraction
            logger.info("Step 2: Extracting text via OCR...")
            ocr_data = self.ocr_service.extract_text(preprocessed_path)
            text_length = len(ocr_data.get("text", ""))
            logger.info(f"OCR extraction complete: {text_length} characters extracted")
            
            # Check if OCR produced meaningful text
            if text_length < 50:
                logger.error("OCR produced very little text!")
                logger.error("Possible issues:")
                logger.error("1. Image quality is too poor")
                logger.error("2. Document contains handwritten text (Tesseract limitation)")
                logger.error("3. Document is not a valid invoice/bill")
                logger.error("4. Image is heavily skewed or rotated")
                
                # Return empty result but don't fail
                return ExtractionResponse(
                    is_success=True,
                    token_usage=TokenUsage(total_tokens=0, input_tokens=0, output_tokens=0),
                    data=ExtractionData(
                        pagewise_line_items=[
                            PagewiseLineItems(page_no="1", page_type="Unknown", bill_items=[])
                        ],
                        total_item_count=0,
                        reconciled_amount=0.0
                    )
                )
            
            # Step 3: Fraud detection
            logger.info("Step 3: Running fraud detection...")
            fraud_result = self.fraud_detector.detect([preprocessed_path], ocr_data)
            if fraud_result.get("detected"):
                logger.warning(f"Fraud indicators detected: {fraud_result.get('details')}")
            else:
                logger.info("No fraud indicators detected")
            
            # Step 4: LLM-based structured extraction
            logger.info("Step 4: Extracting structured data via LLM...")
            extraction_data, token_usage = await self.llm_service.extract_invoice_data(ocr_data)
            
            # Check if extraction is empty
            if extraction_data.get('total_item_count', 0) == 0:
                logger.error("⚠️  LLM returned 0 valid items!")
                logger.error("Debug information:")
                logger.error(f"- OCR text length: {text_length} chars")
                logger.error(f"- OCR quality seems poor (garbled text)")
                logger.error(f"- First 200 chars: {ocr_data.get('text', '')[:200]}")
                logger.error("\nPossible solutions:")
                logger.error("1. Use a clearer/higher resolution image")
                logger.error("2. Ensure the image is not rotated")
                logger.error("3. Check if the image is a valid medical bill")
                logger.error("4. Try rescanning the document")
                
                # Return empty but valid response
                return ExtractionResponse(
                    is_success=True,
                    token_usage=token_usage,
                    data=ExtractionData(
                        pagewise_line_items=[
                            PagewiseLineItems(page_no="1", page_type="Unknown", bill_items=[])
                        ],
                        total_item_count=0,
                        reconciled_amount=0.0
                    )
                )
            else:
                logger.info(f"✅ LLM extraction complete: {extraction_data.get('total_item_count')} items found")
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Total processing time: {processing_time:.2f}ms")
            
            return ExtractionResponse(
                is_success=True,
                token_usage=token_usage,
                data=ExtractionData(**extraction_data)
            )
        
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}", exc_info=True)
            return ExtractionResponse(
                is_success=False,
                error=str(e)
            )

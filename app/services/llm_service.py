import os
import json
from typing import Dict, List
from groq import Groq
from dotenv import load_dotenv
from app.utils.logger import logger
import asyncio

load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not set. LLM extraction will fail.")
            raise ValueError("GROQ_API_KEY is required. Get free API key from https://console.groq.com/")
        
        self.client = Groq(api_key=api_key)
        logger.info("Groq LLM Service initialized (FREE & FAST!)")
    
    async def extract_invoice_data(self, ocr_data: Dict, max_retries: int = 3) -> Dict:
        """
        Use Groq (Llama 3.3) to extract structured invoice data with retry logic
        FREE and much faster than OpenAI!
        """
        logger.info("Extracting structured data using Groq LLM...")
        
        for attempt in range(max_retries):
            try:
                prompt = self._build_extraction_prompt(ocr_data["text"])
                
                logger.info(f"Groq LLM attempt {attempt + 1}/{max_retries}")
                
                # Using Llama 3.3 70B - Latest and best model (still free!)
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",  # Updated to latest model
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                logger.info("Groq LLM extraction successful")
                
                return self._validate_and_reconcile(result)
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    raise
            
            except Exception as e:
                logger.error(f"Groq LLM extraction failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                else:
                    raise
    
    def _get_system_prompt(self) -> str:
        return """You are an expert at extracting structured data from medical bills, invoices, and receipts.
Your task is to extract ALL line items with their quantities, rates, and amounts.

CRITICAL RULES:
1. Extract EVERY single line item from the bill - do not skip any
2. Do NOT double-count any items
3. For each item, you MUST extract:
   - item_name: The service/product name (e.g., "WARD SERVICES", "LAB CHARGES", "MEDICINE") - REQUIRED
   - item_amount: The total amount for this line item (REQUIRED, MUST BE A NUMBER, NEVER null)
   - item_rate: The unit rate/price (can be null if not available)
   - item_quantity: The quantity (can be null if not available)
4. If you cannot find a clear amount for an item, DO NOT include that item
5. item_amount MUST ALWAYS be a valid number (float), never null or string
6. Look for items in sections like:
   - Ward/Room charges
   - Lab/Diagnostic charges
   - Pharmacy/Medicine charges
   - Consultation fees
   - Procedure charges
   - Other services
7. The bill may have sub-sections or categories - extract items from ALL sections
8. Calculate reconciled_amount as the sum of all item_amount values
9. Count total_item_count as the number of unique line items
10. Group items by page number (use "1" for single page documents)

IMPORTANT FORMATTING:
- All amounts MUST be numbers: 1500.00, 2500, 450.50
- NEVER use null for item_amount
- If you see amounts like "1,500" convert to 1500.00
- If you see amounts like "₹1500" or "Rs 1500", extract just the number: 1500.00

Return ONLY valid JSON with this exact structure:
{
    "pagewise_line_items": [
        {
            "page_no": "1",
            "bill_items": [
                {
                    "item_name": "WARD SERVICES",
                    "item_amount": 5000.00,
                    "item_rate": 2500.00,
                    "item_quantity": 2.0
                },
                {
                    "item_name": "LAB CHARGES",
                    "item_amount": 1500.00,
                    "item_rate": null,
                    "item_quantity": null
                }
            ]
        }
    ],
    "total_item_count": 2,
    "reconciled_amount": 6500.00
}

REMEMBER: item_amount must ALWAYS be a number, never null!"""
    
    def _build_extraction_prompt(self, ocr_text: str) -> str:
        # Log the OCR text for debugging
        logger.info(f"OCR text length: {len(ocr_text)} characters")
        logger.info(f"OCR text preview (first 500 chars):\n{ocr_text[:500]}")
        
        # Check if text is too garbled
        readable_ratio = sum(c.isalnum() or c.isspace() for c in ocr_text[:500]) / max(len(ocr_text[:500]), 1)
        logger.info(f"Readable character ratio: {readable_ratio:.2%}")
        
        if readable_ratio < 0.5:
            logger.warning("⚠️  OCR text appears heavily garbled (less than 50% readable characters)")
        
        return f"""Extract all line items from this medical bill/invoice. The OCR text may contain errors, use context to understand correctly.

IMPORTANT INSTRUCTIONS:
1. Look for ALL services, charges, medicines, and fees listed in the bill
2. Extract the service name and amount even if quantity/rate is missing
3. Common sections to check: Ward charges, Lab charges, Pharmacy, Consultations, Procedures
4. If you see a table, extract EVERY row as a separate line item
5. Don't skip items just because they lack quantity or rate - the amount is mandatory
6. Look for number patterns that indicate amounts (with decimal points or currency symbols)
7. CRITICAL: item_amount must ALWAYS be a valid number (like 1500.00, 500, 2500.50) NEVER null or text
8. If you cannot determine the exact amount, try to extract what you can see

EXAMPLES of what to extract:
- "Consultation Fee 500" → item_name: "Consultation Fee", item_amount: 500.00
- "Blood Test ₹1000" → item_name: "Blood Test", item_amount: 1000.00
- "Ward Charges 2500.50" → item_name: "Ward Charges", item_amount: 2500.50

OCR TEXT (may contain errors):
{ocr_text[:6000]}

Extract EVERY line item you can identify. Return valid JSON only.
If the text is very garbled but you can identify ANY services with amounts, extract those.
If you absolutely cannot find any items with clear amounts, return an empty bill_items array."""
    
    def _validate_and_reconcile(self, data: Dict) -> Dict:
        """Validate extraction and ensure amounts reconcile"""
        logger.info("Validating and reconciling amounts...")
        
        total_amount = 0.0
        total_items = 0
        
        # Filter out invalid items BEFORE creating the response
        for page in data.get("pagewise_line_items", []):
            valid_items = []
            
            for item in page.get("bill_items", []):
                # Handle None values for item_amount
                item_amount = item.get("item_amount")
                
                if item_amount is None:
                    logger.warning(f"Skipping item '{item.get('item_name', 'Unknown')}' - amount is None")
                    continue
                
                # Convert to float if it's a string
                try:
                    item_amount = float(item_amount)
                    item["item_amount"] = item_amount
                except (ValueError, TypeError):
                    logger.warning(f"Skipping item '{item.get('item_name', 'Unknown')}' - invalid amount: {item_amount}")
                    continue
                
                # Ensure rate and quantity are valid or None
                if item.get("item_rate") is not None:
                    try:
                        item["item_rate"] = float(item["item_rate"])
                    except (ValueError, TypeError):
                        item["item_rate"] = None
                
                if item.get("item_quantity") is not None:
                    try:
                        item["item_quantity"] = float(item["item_quantity"])
                    except (ValueError, TypeError):
                        item["item_quantity"] = None
                
                # Validate quantity * rate = amount (with tolerance)
                if item.get("item_quantity") is not None and item.get("item_rate") is not None:
                    expected = item["item_quantity"] * item["item_rate"]
                    if abs(expected - item_amount) > 0.1:
                        logger.warning(f"Amount mismatch for {item['item_name']}: expected {expected}, got {item_amount}")
                        # Use calculated value if significantly different
                        if abs(expected - item_amount) > 1.0:
                            item["item_amount"] = round(expected, 2)
                            item_amount = item["item_amount"]
                
                total_amount += item_amount
                total_items += 1
                valid_items.append(item)
            
            # Replace bill_items with only valid items
            page["bill_items"] = valid_items
        
        data["total_item_count"] = total_items
        data["reconciled_amount"] = round(total_amount, 2)
        
        logger.info(f"Validation complete: {total_items} items, total: {total_amount:.2f}")
        
        if total_items == 0:
            logger.error("⚠️  After validation, 0 valid items remain!")
            logger.error("This means the LLM returned items but all had invalid/None amounts")
            logger.error("The OCR text quality is likely too poor")
        
        return data

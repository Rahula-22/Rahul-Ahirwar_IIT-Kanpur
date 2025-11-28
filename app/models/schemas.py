from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from decimal import Decimal

class DocumentRequest(BaseModel):
    document: str  # URL or base64 string

class TokenUsage(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int

class BillItem(BaseModel):
    item_name: str
    item_amount: float  # Required, must be a number
    item_rate: Optional[float] = None
    item_quantity: Optional[float] = None

class PagewiseLineItems(BaseModel):
    page_no: str
    page_type: str = Field(..., description="Bill Detail | Final Bill | Pharmacy")
    bill_items: List[BillItem]

class ExtractionData(BaseModel):
    pagewise_line_items: List[PagewiseLineItems]
    total_item_count: int
    reconciled_amount: float # Kept as per "provide Final Total" requirement

class ExtractionResponse(BaseModel):
    is_success: bool
    token_usage: Optional[TokenUsage] = None
    data: Optional[ExtractionData] = None
    error: Optional[str] = None

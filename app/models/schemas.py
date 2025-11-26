from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from decimal import Decimal

class DocumentRequest(BaseModel):
    document: str  # URL or base64 string

class BillItem(BaseModel):
    item_name: str
    item_amount: float  # Required, must be a number
    item_rate: Optional[float] = None
    item_quantity: Optional[float] = None

class PagewiseLineItems(BaseModel):
    page_no: str
    bill_items: List[BillItem]

class ExtractionData(BaseModel):
    pagewise_line_items: List[PagewiseLineItems]
    total_item_count: int
    reconciled_amount: float

class ExtractionResponse(BaseModel):
    is_success: bool
    data: Optional[ExtractionData] = None
    error: Optional[str] = None

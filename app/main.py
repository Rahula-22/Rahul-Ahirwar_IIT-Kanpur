from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import os
from app.services.document_processor import DocumentProcessor
from app.models.schemas import DocumentRequest, ExtractionResponse
from app.utils.logger import logger
import httpx
import base64
import hashlib
import time

app = FastAPI(
    title="FinServ Invoice Extraction API",
    description="AI-powered invoice data extraction with fraud detection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

document_processor = DocumentProcessor()

@app.get("/")
async def root():
    """Serve the web UI"""
    return FileResponse('static/index.html')

@app.post("/extract-bill-data", response_model=ExtractionResponse)
async def extract_bill_data(request: DocumentRequest):
    """
    Extract line items and amounts from invoice documents
    Accepts document URL or base64 encoded image
    """
    start_time = time.time()
    temp_path = None
    
    try:
        logger.info(f"Received extraction request for document: {request.document[:50]}...")
        
        # Download document from URL or decode base64
        temp_path = await download_document(request.document)
        logger.info(f"Document downloaded to: {temp_path}")
        
        # Process document
        result = await document_processor.process_document(temp_path)
        
        processing_time = (time.time() - start_time) * 1000
        if result.is_success and result.data:
            logger.info(f"Extraction successful in {processing_time:.2f}ms - Items: {result.data.total_item_count}")
        
        return result
    
    except httpx.HTTPError as e:
        logger.error(f"HTTP error downloading document: {str(e)}")
        return ExtractionResponse(
            is_success=False,
            error=f"Failed to download document: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}", exc_info=True)
        return ExtractionResponse(
            is_success=False,
            error=f"Extraction failed: {str(e)}"
        )
    
    finally:
        # Cleanup temporary files
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                # Also remove preprocessed version if exists
                preprocessed_path = temp_path.replace('.', '_preprocessed.')
                if os.path.exists(preprocessed_path):
                    os.remove(preprocessed_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {str(e)}")

@app.post("/extract-bill-data-upload", response_model=ExtractionResponse)
async def extract_bill_data_upload(file: UploadFile = File(...)):
    """
    Extract line items from uploaded invoice image/PDF
    Accepts direct file upload instead of URL
    """
    start_time = time.time()
    temp_path = None

    try:
        logger.info(f"Received file upload: {file.filename}")

        # Save uploaded file
        os.makedirs("temp", exist_ok=True)
        # ensure unique name to avoid collisions
        safe_name = f"{int(time.time()*1000)}_{file.filename}"
        temp_path = os.path.join("temp", safe_name)

        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"File saved to: {temp_path}")

        # Process document
        result = await document_processor.process_document(temp_path)

        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Extraction successful in {processing_time:.2f}ms")

        return result

    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}", exc_info=True)
        return ExtractionResponse(
            is_success=False,
            error=f"Extraction failed: {str(e)}"
        )

    finally:
        # Cleanup temporary files
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                preprocessed_path = temp_path.replace('.', '_preprocessed.')
                if os.path.exists(preprocessed_path):
                    os.remove(preprocessed_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {str(e)}")

async def download_document(url_or_base64: str) -> str:
    """Download document from URL or decode base64 to temp file"""
    os.makedirs("temp", exist_ok=True)
    
    # Check if it's a URL
    if url_or_base64.startswith("http://") or url_or_base64.startswith("https://"):
        logger.info(f"Downloading from URL: {url_or_base64[:100]}...")
        
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(url_or_base64)
            response.raise_for_status()
            
            # Determine file extension from content type or URL
            content_type = response.headers.get("content-type", "").lower()
            if "png" in content_type or url_or_base64.lower().endswith(".png"):
                ext = ".png"
            elif "jpeg" in content_type or "jpg" in content_type or url_or_base64.lower().endswith((".jpg", ".jpeg")):
                ext = ".jpg"
            elif "pdf" in content_type or url_or_base64.lower().endswith(".pdf"):
                ext = ".pdf"
            else:
                ext = ".png"  # default
            
            # Create unique filename using hash
            file_hash = hashlib.md5(url_or_base64.encode()).hexdigest()[:8]
            temp_path = f"temp/document_{file_hash}{ext}"
            
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Downloaded {len(response.content)} bytes")
            return temp_path
    
    else:
        # Handle base64 encoded data
        logger.info("Decoding base64 data...")
        try:
            # Remove data URI prefix if present
            if "," in url_or_base64:
                url_or_base64 = url_or_base64.split(",", 1)[1]
            
            decoded_data = base64.b64decode(url_or_base64)
            temp_path = "temp/document_base64.png"
            
            with open(temp_path, "wb") as f:
                f.write(decoded_data)
            
            logger.info(f"Decoded {len(decoded_data)} bytes")
            return temp_path
        
        except Exception as e:
            logger.error(f"Failed to decode base64: {str(e)}")
            raise ValueError(f"Invalid base64 data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "ocr": "ready",
            "llm": "ready"
        }
    }

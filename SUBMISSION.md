# HackRx Invoice Extraction - Final Submission

## 📋 Team Information

- **Team Name:** Rahul Ahirwar
- **Institution:** IIT Kanpur
- **Contact Email:** [Your Email]
- **Date:** November 28, 2024

---

## 🚀 Submission URLs

### GitHub Repository
**URL:** https://github.com/YOUR_USERNAME/finserv-invoice-extraction
**Status:** ✅ Public (for evaluation)

### Live API Deployment
**Deployed URL:** https://YOUR-RAILWAY-URL.up.railway.app
**Platform:** Railway.app
**Status:** ✅ Active and Running
**Health Check:** https://YOUR-RAILWAY-URL.up.railway.app/health
**API Docs:** https://YOUR-RAILWAY-URL.up.railway.app/docs

---

## 🧪 Quick Test

```bash
# Health Check
curl https://YOUR-RAILWAY-URL.up.railway.app/health

# Extract Invoice (Sample from Assignment)
curl -X POST "https://YOUR-RAILWAY-URL.up.railway.app/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{"document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSabcDREiFXSU%3D"}'
```

**Expected Response:**
```json
{
  "is_success": true,
  "token_usage": {
    "total_tokens": 1467,
    "input_tokens": 1156,
    "output_tokens": 311
  },
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "page_type": "Pharmacy",
        "bill_items": [...]
      }
    ],
    "total_item_count": 5,
    "reconciled_amount": 16641.19
  }
}
```

---

## ✅ Assignment Compliance Checklist

| Requirement | Status | Implementation |
|------------|--------|----------------|
| POST /extract-bill-data endpoint | ✅ | FastAPI implementation |
| Accepts document URL | ✅ | URL download + base64 support |
| Returns token_usage | ✅ | Tracked from Groq API response |
| Returns page_type | ✅ | LLM classification (Bill Detail/Final Bill/Pharmacy) |
| Extracts all line items | ✅ | Multi-modal OCR + LLM parsing |
| No double-counting | ✅ | LLM validation + reconciliation |
| Accurate amounts | ✅ | qty × rate validation |
| Multi-page support | ✅ | PDF + multi-image handling |
| JSON format exact match | ✅ | Pydantic schemas |
| Deployed API | ✅ | Railway.app |
| GitHub repository | ✅ | Public, documented |

---

## 🏗️ Technical Architecture

### Tech Stack
- **Backend:** FastAPI 0.115.0 (async, high performance)
- **OCR:** Tesseract 5.5.0 (multi-language support)
- **LLM:** Groq API - Llama 3.3 70B (FREE, 10x faster than GPT-4)
- **Preprocessing:** PIL + NumPy
- **Deployment:** Railway.app (auto-scaling, zero config)

### Processing Pipeline

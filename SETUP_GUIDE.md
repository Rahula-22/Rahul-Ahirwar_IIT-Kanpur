# Complete Setup and Testing Guide

## Step 1: Install System Dependencies

### Windows:
1. **Install Python 3.9+**
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **Install Tesseract OCR**
   ```powershell
   # Download installer from:
   https://github.com/UB-Mannheim/tesseract/wiki
   
   # Install to default location: C:\Program Files\Tesseract-OCR
   
   # Add to PATH:
   # Control Panel > System > Advanced > Environment Variables
   # Add: C:\Program Files\Tesseract-OCR to PATH
   ```

3. **Verify Tesseract Installation**
   ```powershell
   tesseract --version
   # Should show: tesseract v5.x.x
   ```

### Ubuntu/Linux:
```bash
sudo apt-get update
sudo apt-get install -y python3.9 python3-pip tesseract-ocr libtesseract-dev
```

### macOS:
```bash
brew install python@3.9 tesseract
```

---

## Step 2: Setup Python Virtual Environment

```bash
# Navigate to project directory
cd c:\Users\HP\OneDrive\Desktop\finserv

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
```

---

## Step 3: Install Python Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements (this will take 2-3 minutes)
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

**Note:** We're using Tesseract OCR only for maximum compatibility and speed. EasyOCR has been removed due to Python 3.14 compatibility issues.

---

## Step 4: Get FREE Groq API Key

**No credit card required! ✅**

1. Go to: https://console.groq.com/keys
2. Sign up with Google/GitHub/Email (FREE!)
3. Create new API key
4. Copy the key (starts with `gsk_...`)

**See detailed guide:** [GET_GROQ_API_KEY.md](GET_GROQ_API_KEY.md)

---

## Step 5: Configure Environment Variables

```bash
# Create .env file from example
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/Mac

# Edit .env file and add your API key
notepad .env   # Windows
# nano .env    # Linux/Mac
```

**Add this line to .env:**
```
GROQ_API_KEY=gsk_your_actual_groq_key_here
```

**Save and close the file**

---

## Step 6: Create Required Directories

```bash
# Create temp and logs directories
mkdir temp
mkdir logs
```

---

## Step 7: Verify Installation

### Test 1: Check Python Imports
```bash
python -c "import fastapi, pytesseract, cv2, openai; print('✅ All imports successful')"
```

### Test 2: Check Tesseract
```bash
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

### Test 3: Check Groq API Key
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ Groq API Key loaded') if os.getenv('GROQ_API_KEY') and os.getenv('GROQ_API_KEY').startswith('gsk_') else print('❌ API Key missing')"
```

---

## Step 8: Start the API Server

```bash
# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['c:\\Users\\HP\\OneDrive\\Desktop\\finserv']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ Server is running when you see these messages**

---

## Step 9: Test the API

### Open a NEW terminal (keep server running in first terminal)

```bash
# Activate virtual environment again
cd c:\Users\HP\OneDrive\Desktop\finserv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# Run test script
python test_api.py
```

**Expected Output:**
```
Testing Invoice Extraction API...
Document URL: https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png...

Sending request...

✅ SUCCESS!
{
  "is_success": true,
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "bill_items": [
          {
            "item_name": "Livi 300mg Tab",
            "item_amount": 448.0,
            "item_rate": 32.0,
            "item_quantity": 14.0
          },
          ...
        ]
      }
    ],
    "total_item_count": 4,
    "reconciled_amount": 1699.84
  }
}

📊 Summary:
   Total Items: 4
   Reconciled Amount: ₹1699.84
```

---

## Step 10: Test via Browser

1. Open browser: http://localhost:8000
2. You should see:
   ```json
   {
     "message": "FinServ Invoice Extraction API",
     "status": "running",
     "version": "1.0.0"
   }
   ```

3. Open Swagger UI: http://localhost:8000/docs
4. Click on "POST /extract-bill-data"
5. Click "Try it out"
6. Paste this in Request Body:
   ```json
   {
     "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
   }
   ```
7. Click "Execute"
8. Check Response (should show extracted data)

---

## Step 11: Test with cURL

```bash
curl -X POST "http://localhost:8000/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d "{\"document\":\"https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D\"}"
```

---

## Step 12: Check Logs

```bash
# View application logs
type logs\app.log   # Windows
# cat logs/app.log  # Linux/Mac
```

**Should show:**
```
2024-xx-xx xx:xx:xx - finserv - INFO - Received extraction request...
2024-xx-xx xx:xx:xx - finserv - INFO - Document downloaded to: temp/document_xxxxx.png
2024-xx-xx xx:xx:xx - finserv - INFO - Processing document: temp/document_xxxxx.png
...
2024-xx-xx xx:xx:xx - finserv - INFO - Extraction successful in 2500.00ms
```

---

## 🎯 Success Criteria

✅ **All checks should pass:**

1. ✅ Tesseract installed and in PATH
2. ✅ All Python packages installed
3. ✅ OpenAI API key configured
4. ✅ Server starts without errors
5. ✅ Test script extracts data successfully
6. ✅ Swagger UI accessible
7. ✅ Logs show successful processing

---

## 🚨 Troubleshooting

### Issue 1: "tesseract is not recognized"
**Solution:**
```bash
# Windows: Add to PATH manually
# Go to: Control Panel > System > Advanced > Environment Variables
# Add: C:\Program Files\Tesseract-OCR
# Restart terminal
```

### Issue 2: "No module named 'app'"
**Solution:**
```bash
# Make sure you're in the project root
cd c:\Users\HP\OneDrive\Desktop\finserv
# Run from this directory
```

### Issue 3: "OpenAI API error"
**Solution:**
```bash
# Check API key in .env
cat .env
# Should show: OPENAI_API_KEY=sk-...
# Make sure no spaces or quotes around the key
```

### Issue 4: "EasyOCR taking too long"
**Solution:**
```bash
# Edit app/services/ocr_service.py
# Comment out EasyOCR initialization
# Use Tesseract only for faster processing
```

### Issue 5: Port 8000 already in use
**Solution:**
```bash
# Use different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

---

## 📊 Performance Benchmarks

Expected processing times:
- Simple invoice (1 page): 2-5 seconds
- Complex invoice (multi-page): 5-10 seconds
- Handwritten invoice: 8-15 seconds

---

## 🔄 Restart Instructions

```bash
# Stop server: Press CTRL+C in server terminal

# Restart server:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📦 Deployment Checklist

Before submitting to GitHub:

1. ✅ Remove `.env` file (contains API key)
2. ✅ Add `.gitignore` (already included)
3. ✅ Clear temp/ and logs/ directories
4. ✅ Test with fresh clone
5. ✅ Update README.md with team info
6. ✅ Create requirements.txt freeze:
   ```bash
   pip freeze > requirements_frozen.txt
   ```

---

## 🎓 Next Steps

1. **Test with training data** provided by organizers
2. **Measure accuracy** against ground truth
3. **Optimize preprocessing** for specific document types
4. **Fine-tune LLM prompts** for better extraction
5. **Create pitch deck** (use provided template)
6. **Submit to GitHub** private repository
7. **Deploy API** for leaderboard testing

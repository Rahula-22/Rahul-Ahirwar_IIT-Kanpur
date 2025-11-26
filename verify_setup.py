import sys
import os

print("=" * 50)
print("FinServ Setup Verification")
print("=" * 50)
print()

# Check 1: Python Version
print("1. Checking Python version...")
version = sys.version_info
print(f"   Python {version.major}.{version.minor}.{version.micro}")
if 3.9 <= version.minor <= 3.14:
    print("   ✅ Python version compatible")
else:
    print(f"   ⚠️  Python {version.major}.{version.minor} may have compatibility issues")
print()

# Check 2: Required Modules
print("2. Checking required modules...")
required_modules = [
    'fastapi',
    'uvicorn',
    'pytesseract',
    'groq',
    'PIL',
    'numpy',
    'httpx',
]

all_ok = True
for module in required_modules:
    try:
        if module == 'PIL':
            from PIL import Image
        else:
            __import__(module)
        print(f"   ✅ {module}")
    except ImportError as e:
        print(f"   ❌ {module} - {e}")
        all_ok = False
print()

# Check 3: Tesseract
print("3. Checking Tesseract OCR...")
tesseract_found = False

# Try proper installation path first
tesseract_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",  # Proper installation
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\HP\Downloads\Tesseract-OCR.exe",  # Old portable version
    r"C:\Tesseract-OCR\tesseract.exe",
]

import pytesseract

for path in tesseract_paths:
    if os.path.exists(path):
        print(f"   ℹ️  Found Tesseract at: {path}")
        pytesseract.pytesseract.tesseract_cmd = path
        tesseract_found = True
        break

if not tesseract_found:
    print(f"   ⚠️  Tesseract not found at expected locations")
    for path in tesseract_paths:
        print(f"      - {path}")
    print()
    print(f"   Please verify the exact path and update:")
    print(f"   app/services/ocr_service.py")

try:
    version = pytesseract.get_tesseract_version()
    print(f"   ✅ Tesseract {version} is accessible")
    tesseract_found = True
except Exception as e:
    print(f"   ❌ Tesseract not accessible - {e}")
    print()
    print("   Please ensure Tesseract is installed at:")
    print("   C:\\Program Files\\Tesseract-OCR")
    all_ok = False
print()

# Check 4: Environment Variables
print("4. Checking environment variables...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key and groq_key.startswith('gsk_'):
        print(f"   ✅ GROQ_API_KEY configured")
    else:
        print(f"   ⚠️  GROQ_API_KEY not set or invalid")
        print("   Get FREE API key from: https://console.groq.com/keys")
        print("   See GET_GROQ_API_KEY.md for instructions")
        all_ok = False
except Exception as e:
    print(f"   ❌ Error loading .env: {e}")
    all_ok = False
print()

# Check 5: Directories
print("5. Checking required directories...")
for directory in ['temp', 'logs', 'app', 'app/services', 'app/models']:
    if os.path.exists(directory):
        print(f"   ✅ {directory}/")
    else:
        print(f"   ❌ {directory}/ missing")
        all_ok = False
print()

# Check 6: Key Files
print("6. Checking key files...")
for file in ['requirements.txt', 'app/main.py', 'app/services/ocr_service.py', '.env']:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} missing")
        all_ok = False
print()

# Summary
print("=" * 50)
if all_ok:
    print("✅ ALL CHECKS PASSED!")
    print()
    print("You're ready to start the server:")
    print("  uvicorn app.main:app --reload")
else:
    print("❌ SOME CHECKS FAILED")
    print()
    print("Please fix the issues above before proceeding.")
    print("See QUICK_FIX.md for solutions.")
print("=" * 50)

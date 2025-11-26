import requests
import json
import time
import sys

# Test API endpoint
API_URL = "http://localhost:8000/extract-bill-data"

# Sample document URL from the assignment
SAMPLE_DOCUMENT = "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"

def check_server():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_extraction():
    print("="*70)
    print("FinServ Invoice Extraction API - Test")
    print("="*70)
    print()
    
    # Check if server is running
    print("Checking if server is running...")
    if not check_server():
        print()
        print("❌ ERROR: Server is not running!")
        print()
        print("Please start the server first:")
        print("  1. Open a new terminal")
        print("  2. Run: uvicorn app.main:app --reload")
        print("  3. Wait for 'Application startup complete' message")
        print("  4. Then run this test again")
        print()
        sys.exit(1)
    
    print("✅ Server is running")
    print()
    
    print(f"Testing with sample document...")
    print(f"URL: {SAMPLE_DOCUMENT[:80]}...")
    print()
    
    # Prepare request
    payload = {
        "document": SAMPLE_DOCUMENT
    }
    
    # Send request
    print("Sending request...")
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        print(f"Response received in {elapsed:.2f}s")
        print()
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            
            if result.get("is_success"):
                data = result.get("data", {})
                
                print("="*70)
                print("✅ SUCCESS!")
                print("="*70)
                print()
                
                print(f"📊 Summary:")
                print(f"   Total Items: {data.get('total_item_count')}")
                print(f"   Reconciled Amount: ₹{data.get('reconciled_amount')}")
                print(f"   Processing Time: {elapsed:.2f}s")
                print()
                
                print(f"📋 Extracted Line Items:")
                for page in data.get("pagewise_line_items", []):
                    print(f"\n   Page {page.get('page_no')}:")
                    for idx, item in enumerate(page.get("bill_items", []), 1):
                        print(f"   {idx}. {item.get('item_name')}")
                        print(f"      Amount: ₹{item.get('item_amount')}")
                        if item.get('item_quantity'):
                            print(f"      Qty: {item.get('item_quantity')}")
                        if item.get('item_rate'):
                            print(f"      Rate: ₹{item.get('item_rate')}")
                
                print()
                print("="*70)
                print("Full JSON Response:")
                print("="*70)
                print(json.dumps(result, indent=2))
                
                # Validation
                print()
                print("="*70)
                print("Validation:")
                print("="*70)
                expected_items = 4
                if data.get('total_item_count') == expected_items:
                    print(f"✅ Correct item count ({expected_items})")
                else:
                    print(f"⚠️  Item count mismatch: got {data.get('total_item_count')}, expected {expected_items}")
                
                if data.get('reconciled_amount') > 0:
                    print(f"✅ Amount reconciled: ₹{data.get('reconciled_amount')}")
                else:
                    print(f"⚠️  Reconciled amount is 0")
                
                if elapsed < 10:
                    print(f"✅ Latency acceptable: {elapsed:.2f}s")
                else:
                    print(f"⚠️  High latency: {elapsed:.2f}s")
                
            else:
                print("="*70)
                print("❌ EXTRACTION FAILED")
                print("="*70)
                print(f"\nError: {result.get('error')}")
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(response.text)
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>60s)")
        print("   The document may be too large or server is overloaded")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_extraction()

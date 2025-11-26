# How to Get FREE Groq API Key (No Credit Card Required!)

## Step 1: Sign Up for Groq

1. **Go to Groq Console:**
   - Visit: https://console.groq.com/

2. **Sign Up (FREE!):**
   - Click "Sign Up" or "Get Started"
   - Sign up with Google/GitHub or Email
   - **NO CREDIT CARD REQUIRED** ✅

## Step 2: Create API Key

1. **Go to API Keys:**
   - Visit: https://console.groq.com/keys
   - Or click on "API Keys" in the sidebar

2. **Create New Key:**
   - Click "Create API Key"
   - Give it a name (e.g., "FinServ Invoice Extraction")
   - Click "Submit"

3. **Copy Your Key:**
   - Copy the API key (starts with `gsk_...`)
   - **Save it now!** You won't be able to see it again

## Step 3: Add to .env File

```bash
# Open .env file
notepad .env   # Windows
# nano .env    # Linux/Mac
```

Replace the placeholder with your actual key:
```
GROQ_API_KEY=gsk_your_actual_key_here_abc123def456
```

Save and close the file.

## Step 4: Verify

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ Groq API Key loaded') if os.getenv('GROQ_API_KEY') and os.getenv('GROQ_API_KEY').startswith('gsk_') else print('❌ API Key invalid')"
```

---

## ✨ Why Groq?

- ✅ **100% FREE** - No credit card required
- ✅ **Super Fast** - 10x faster than OpenAI
- ✅ **High Quality** - Uses Llama 3.1 70B model
- ✅ **Generous Limits** - 30 requests/minute (plenty for testing)
- ✅ **No Hidden Costs** - Completely free tier

---

## 📊 Groq Free Tier Limits:

| Model | Requests/Min | Tokens/Min |
|-------|-------------|------------|
| Llama 3.3 70B | 30 | 6,000 |
| Llama 3.1 8B | 30 | 14,400 |

**More than enough for this assignment!**

---

## 🎯 Models Available:

We're using: `llama-3.3-70b-versatile`
- Latest Llama 3.3 model (Nov 2024)
- Best accuracy for invoice extraction
- Still very fast
- Completely free

---

## ⚠️ Important Notes:

- **Never commit .env to GitHub** (already in .gitignore)
- **Keep your API key secret**
- **No usage costs** - It's free!
- **No expiration** - Key works indefinitely

---

## 🚀 Ready to Test!

Once you've added your Groq API key, run:

```bash
python verify_setup.py
```

If you see **✅ GROQ_API_KEY configured**, you're ready to go!

# Troubleshooting Guide

## Common Issues & Solutions

### 1. Google API Key Error

**Error:**
```
Gemini failed: API key not valid...using fallback...
```

**Solution:**
- ✅ **This is normal!** Google API key is **optional**
- The app automatically uses fallback (PyPDF/python-docx)
- Only needed for: PDF, DOCX, PPTX file uploads

**To fix permanently:**
1. Remove the line from `.env` OR
2. Get real key from: https://makersuite.google.com/app/apikey
3. Replace `your_google_api_key_here` with actual key

---

### 2. Invalid Groq API Key (401 Error)

**Error:**
```
Error code: 401 - Invalid API Key
```

**Solution:**
1. Check your `.env` file has the correct Groq key
2. Make sure it's not the placeholder `your_groq_api_key_here`
3. Get a free key: https://console.groq.com

**Verify:**
```bash
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'Key: {os.getenv(\"GROQ_API_KEY\", \"NOT FOUND\")[:10]}...')"
```

---

### 3. Wrong Model Name

**Issue:**
Model name was accidentally changed to `"openai/gpt-oss-120b"`

**Solution:**
✅ **Fixed!** Now using `"llama-3.3-70b-versatile"`

**Valid Groq models:**
- `llama-3.3-70b-versatile` (recommended)
- `llama-3.1-70b-versatile`
- `mixtral-8x7b-32768`

---

### 4. Unexpected Output Style

**Issue:**
Generated content doesn't match expectations

**Possible causes:**
1. **Style Personalization is active** - Content matches your pasted "best posts"
2. **Different platform** - LinkedIn vs Twitter have different formats
3. **Critique loop** - Content gets revised if quality score < 90

**Solutions:**
- Clear "Best Posts" field to disable personalization
- Check which platform you selected
- Look at the critique score in the output

---

### 5. Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'langgraph'
```

**Solution:**
```bash
pip install -r requirements.txt
```

---

### 6. Port Already in Use

**Error:**
```
Address already in use: ('127.0.0.1', 8501)
```

**Solution:**
```bash
# Kill existing Streamlit
pkill -f streamlit

# Or use different port
streamlit run app.py --server.port 8502
```

---

### 7. .env File Not Loading

**Issue:**
API keys in `.env` not working

**Checklist:**
- ✅ File named exactly `.env` (not `.env.txt`)
- ✅ In the project root directory
- ✅ No quotes around values
- ✅ No spaces around `=`

**Correct format:**
```
GROQ_API_KEY=gsk_abc123...
GOOGLE_API_KEY=AIzaSy...
```

**Wrong format:**
```
GROQ_API_KEY = "gsk_abc123..."  ← No quotes, no spaces!
```

---

### 8. Streamlit Won't Start

**Error:**
Various startup errors

**Solutions:**
```bash
# Reinstall Streamlit
pip uninstall streamlit
pip install streamlit

# Clear cache
rm -rf ~/.streamlit
streamlit cache clear

# Restart
streamlit run app.py
```

---

## Quick Verification

Run this to check everything:
```bash
./verify_setup.sh
```

Expected output:
```
✅ All core modules imported successfully
✅ GROQ_API_KEY found in .env
✅ 9 agent files found
```

---

## Still Having Issues?

1. Check your `.env` file has correct Groq key
2. Model is set to `llama-3.3-70b-versatile`
3. Run `./verify_setup.sh`
4. Try the CLI test: `python3 cli_test.py`

**Most common fix:** Just restart Streamlit!
```bash
# Stop current (Ctrl+C)
# Start fresh
streamlit run app.py
```

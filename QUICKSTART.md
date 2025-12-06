# Quick Start Guide

## 🚦 Getting Started (3 minutes)

### Step 1: Install Dependencies
```bash
cd /Users/anujpatel/Desktop/AI-Demos-Project/Sankar-main
pip install -r requirements.txt
```

### Step 2: Set Up API Key
Create `.env` file (or copy from `.env.example`):
```bash
echo "GROQ_API_KEY=your_actual_key_here" > .env
```

Get your free Groq API key: https://console.groq.com

### Step 3: Test in Terminal
```bash
python cli_test.py
```

Expected output:
```
============================================================
Content Repurposing Engine - CLI Test
============================================================

🧠 Extracting core message...
✅ Core message extracted: AI Augmentation
   📌 Topic: AI Augmentation
   💡 Thesis: The future of AI is about augmenting...

✍️ Generating content for LinkedIn...
✅ Draft created for LinkedIn

🔍 Evaluating LinkedIn (attempt 1)...
   🔍 PASS: Score 92/100

✓ LinkedIn validated
   📏 1287 chars, 256 words
   🏷️  5 hashtags

============================================================
🎉 All platforms complete!
============================================================

📱 LINKEDIN
============================================================

[Your generated LinkedIn post here]
```

### Step 4: Launch Streamlit UI
```bash
streamlit run app.py
```

Then open: http://localhost:8501

---

## 🎯 Quick Test Commands

### Test with sample content:
```bash
python cli_test.py
```

### Test specific platforms:
Edit `cli_test.py` line 47:
```python
selected_platforms=["LinkedIn", "Reddit"],  # Change platforms here
```

### Enable A/B testing (1 platform only):
Edit `cli_test.py` line 49:
```python
ab_testing=True,  # Generate 3 variations
```

---

## ❓ Troubleshooting

### Error: "No module named 'langgraph'"
```bash
pip install --upgrade -r requirements.txt
```

### Error: "GROQ_API_KEY not found"
1. Create `.env` file with your key
2. Or run: `export GROQ_API_KEY=your_key`

### Error: "Rate limit exceeded"
- Groq free tier: 30 requests/minute
- Wait 60 seconds and retry

---

## 📖 Next Steps

1. ✅ **Test CLI** → Verify everything works
2. ✅ **Test Streamlit** → Try different platforms
3. ✅ **Read README_NEW.md** → Learn about the architecture
4. 🔜 **Phase 2** → User style analysis (coming soon!)

---

**Need help?** Check `README_NEW.md` for detailed documentation.

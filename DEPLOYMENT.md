# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites

Before deploying, ensure you have:
- A [GitHub](https://github.com) account
- A [Streamlit Cloud](https://streamlit.io/cloud) account (free)
- Your **Groq API Key** (get free at [console.groq.com](https://console.groq.com))
- (Optional) **Google API Key** for PDF processing

---

## Step 1: Push Your Code to GitHub

1. Create a new repository on GitHub
2. Push your code:

```bash
cd /path/to/Sankar-main
git init
git add .
git commit -m "Initial commit - Content Repurposing Engine"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub account (if not already connected)
4. Select your repository:
   - **Repository:** `YOUR_USERNAME/YOUR_REPO`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Deploy!"**

---

## Step 3: Configure Secrets (API Keys)

**IMPORTANT:** Never commit API keys to your repository!

1. After deployment, go to your app's settings
2. Click on **"Secrets"** in the sidebar
3. Add your secrets in TOML format:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
GOOGLE_API_KEY = "your_google_api_key_here"
```

4. Click **"Save"**
5. Your app will automatically restart with the new secrets

---

## Alternative: Use UI Input (No Secrets Needed)

Your app already supports entering API keys directly in the sidebar UI.
Users can:
1. Open your deployed app
2. Enter their own API keys in the sidebar
3. Start generating content

This way, each user uses their own API quota!

---

## Deployment Checklist

✅ `app.py` - Main Streamlit entry point
✅ `requirements.txt` - Python dependencies (created from requirements-fixed.txt)
✅ `.python-version` - Specifies Python 3.11
✅ `.streamlit/config.toml` - Streamlit configuration
✅ `agents/` - All AI agent modules
✅ `utils/` - Utility functions
✅ `workflow.py` - LangGraph workflow
✅ `config.py` - Configuration settings
✅ `styles.py` - Custom CSS styling

---

## Troubleshooting

### App fails to start
- Check the logs in Streamlit Cloud dashboard
- Ensure all dependencies in `requirements.txt` are correct
- Verify Python version compatibility

### "Module not found" errors
- All modules should be in the repository
- Check that `__init__.py` files exist in `agents/` and `utils/` directories

### API key errors
- Make sure secrets are properly configured
- Or use the sidebar UI to enter keys manually

---

## Your Deployed App URL

Once deployed, you'll get a URL like:
```
https://your-app-name.streamlit.app
```

Share this link with anyone you want to use your app!

---

## Performance Tips

1. **Initial load may be slow** - First load can take 30-60 seconds
2. **App hibernates** - Free tier apps sleep after inactivity
3. **Wake-up time** - Sleeping apps take 10-20 seconds to wake up

---

Built with ❤️ using Streamlit + LangGraph + Groq

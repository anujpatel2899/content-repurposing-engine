"""Configuration and constants for the Content Repurposing Engine."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Required for all content generation
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")  # Optional: Only for PDF/DOCX vision processing

# Model Configuration
GROQ_MODEL = "openai/gpt-oss-120b"  # Fast and powerful

# Speech-to-Text Configuration
GROQ_WHISPER_MODEL = "whisper-large-v3-turbo"  # Fast transcription
MAX_RECORDING_DURATION = 300  # 5 minutes in seconds

# Platform Configuration
SUPPORTED_PLATFORMS = [
    "LinkedIn",
    "Twitter/X",
    "Short Blog",
    "Email Sequence",
    "Reddit",
    "Substack"
]

# Generation Settings (Simplified - no critic/reviser loop anymore)
RATE_LIMIT_DELAY = 0.1  # Minimal delay for Groq

# Feature Toggles
ENABLE_PARALLEL_PROCESSING = True   # Generate all platforms simultaneously
ENABLE_STYLE_CACHING = True         # Cache analyzed writing styles
ENABLE_CONTENT_CLEANUP = True       # Post-process to remove AI patterns

# Cache Settings
CACHE_DIR = Path.home() / ".content_repurposing_cache"
CACHE_DIR.mkdir(exist_ok=True)
STYLE_CACHE_FILE = CACHE_DIR / "style_guides.json"
CORE_MESSAGE_CACHE_FILE = CACHE_DIR / "core_messages.json"

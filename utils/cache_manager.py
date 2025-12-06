"""Cache Manager for Phase 3 - Style guides and core messages."""
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict
from config import STYLE_CACHE_FILE, CORE_MESSAGE_CACHE_FILE, ENABLE_STYLE_CACHING


class CacheManager:
    """Manages caching for style guides and core messages."""
    
    @staticmethod
    def _generate_hash(content: str) -> str:
        """Generate hash for content."""
        return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def load_cache(cache_file: Path) -> Dict:
        """Load cache from file."""
        try:
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Cache load failed: {e}")
        return {}
    
    @staticmethod
    def save_cache(cache_file: Path, data: Dict):
        """Save cache to file."""
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Cache save failed: {e}")
    
    @classmethod
    def get_cached_style(cls, best_posts: str) -> Optional[Dict]:
        """Get cached style guide for given posts."""
        if not ENABLE_STYLE_CACHING or not best_posts:
            return None
        
        cache = cls.load_cache(STYLE_CACHE_FILE)
        posts_hash = cls._generate_hash(best_posts)
        
        if posts_hash in cache:
            print("💾 [CACHE] Using cached style guide")
            return cache[posts_hash]
        
        return None
    
    @classmethod
    def save_style(cls, best_posts: str, style_guide: Dict):
        """Save style guide to cache."""
        if not ENABLE_STYLE_CACHING or not best_posts:
            return
        
        cache = cls.load_cache(STYLE_CACHE_FILE)
        posts_hash = cls._generate_hash(best_posts)
        cache[posts_hash] = style_guide
        cls.save_cache(STYLE_CACHE_FILE, cache)
        print("💾 [CACHE] Style guide saved for future use")
    
    @classmethod
    def get_cached_core_message(cls, raw_text: str) -> Optional[Dict]:
        """Get cached core message for given text."""
        cache = cls.load_cache(CORE_MESSAGE_CACHE_FILE)
        text_hash = cls._generate_hash(raw_text)
        
        if text_hash in cache:
            print("💾 [CACHE] Using cached core message")
            return cache[text_hash]
        
        return None
    
    @classmethod
    def save_core_message(cls, raw_text: str, core_message: Dict):
        """Save core message to cache."""
        cache = cls.load_cache(CORE_MESSAGE_CACHE_FILE)
        text_hash = cls._generate_hash(raw_text)
        cache[text_hash] = core_message
        cls.save_cache(CORE_MESSAGE_CACHE_FILE, cache)
        print("💾 [CACHE] Core message saved for future use")
    
    @classmethod
    def clear_all_caches(cls):
        """Clear all caches."""
        for cache_file in [STYLE_CACHE_FILE, CORE_MESSAGE_CACHE_FILE]:
            if cache_file.exists():
                cache_file.unlink()
        print("🗑️ All caches cleared")

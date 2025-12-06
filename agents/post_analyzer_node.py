"""Post Analyzer Node - Extracts writing style from user's best posts."""
import json
from groq import Groq
from .schemas import RepurposingState
from config import GROQ_MODEL


STYLE_ANALYSIS_PROMPT = """You are an expert Content Analyst. Analyze these high-performing posts to extract the author's unique writing style.

Posts to analyze:
{posts}

Extract and return valid JSON with EXACTLY these keys:

1. "writing_style": Overall tone and voice (e.g., "professional yet conversational", "bold and contrarian")
2. "hook_patterns": List of 3-5 hook types used (e.g., "starts with questions", "uses statistics", "personal stories")
3. "story_structure": How they structure content (e.g., "problem-solution-action", "list-based with emojis")
4. "cta_style": Call-to-action patterns (e.g., "asks engaging questions", "invites discussion")
5. "emoji_usage": Emoji strategy (e.g., "minimal - only bullets", "frequent for emphasis")
6. "sentence_length": Typical sentence structure (e.g., "short punchy sentences", "mix of short and long")
7. "unique_phrases": List of 3-5 unique phrases or patterns they use
8. "formatting_style": How they format (e.g., "lots of line breaks", "uses bold for emphasis")

Be specific and actionable - these insights will be used to generate similar content.
"""


def analyze_best_posts_node(state: RepurposingState) -> RepurposingState:
    """
    Analyzes user's best performing posts to extract writing style patterns.
    
    Phase 3: Now uses caching - analyzes once, remembers forever!
    
    This creates a style guide that will be used by the generator to match
    the user's proven writing style.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with style_guide
    """
    # Skip if no best posts provided
    if not state.get("best_posts") or not state["best_posts"].strip():
        print("ℹ️  [POST ANALYZER] No best posts provided - using generic style")
        state["style_guide"] = None
        return state
    
    # Phase 3: Check cache first
    from utils import CacheManager
    cached_style = CacheManager.get_cached_style(state["best_posts"])
    
    if cached_style:
        state["style_guide"] = cached_style
        return state
    
    print("🔍 [POST ANALYZER] Analyzing user's best posts for style patterns...")
    
    client = Groq(api_key=state["groq_api_key"])
    
    # Create prompt
    prompt = STYLE_ANALYSIS_PROMPT.format(posts=state["best_posts"])
    
    # Call Groq with JSON mode
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert Content Analyst. Return valid JSON with the exact keys specified."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    
    # Parse JSON response
    style_data = json.loads(response.choices[0].message.content)
    
    state["style_guide"] = style_data
    
    # Phase 3: Save to cache
    CacheManager.save_style(state["best_posts"], style_data)
    
    print(f"✅ [POST ANALYZER] Style extracted: {style_data.get('writing_style', 'N/A')}")
    print(f"   📝 Hook patterns: {len(style_data.get('hook_patterns', []))} identified")
    print(f"   🎨 Unique phrases: {len(style_data.get('unique_phrases', []))} found")
    
    return state

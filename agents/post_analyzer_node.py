"""Post Analyzer Node - Extracts writing style from user's best posts with enhanced voice cloning."""
import json
from groq import Groq
from .schemas import RepurposingState
from config import GROQ_MODEL


STYLE_ANALYSIS_PROMPT = """You are an expert Content Analyst who can clone a writer's unique voice and style.

Analyze these high-performing posts deeply to extract EXACTLY what makes this author's content unique.

Posts to analyze:
{posts}

EXTRACT AND RETURN VALID JSON WITH THESE KEYS:

1. "writing_style": Their overall voice and personality
   - Are they formal or casual?
   - Confident or humble?
   - Provocative or safe?
   - What emotions do they evoke?
   
2. "hook_patterns": List of 3-5 SPECIFIC hook types they use
   - Don't just say "uses questions" - give examples like "Opens with controversial statements that challenge common wisdom"
   - What makes their first lines scroll-stopping?
   
3. "story_structure": How they organize content
   - Do they go problem→solution→action?
   - Do they use numbered lists?
   - How do they transition between ideas?
   - Do they use cliffhangers or teasers?
   
4. "cta_style": How they end posts
   - Do they ask questions?
   - Do they invite debate?
   - Direct or subtle?
   
5. "emoji_usage": Specific emoji patterns
   - Which emojis do they use?
   - Where do they place them?
   - Frequency?
   
6. "sentence_length": Their rhythm and pacing
   - Do they use fragments?
   - Long flowing sentences?
   - Mix of both?
   - One-word sentences for impact?
   
7. "unique_phrases": List of 5-10 ACTUAL phrases or patterns they use
   - Words they favor
   - Transition phrases
   - Opening patterns
   - Signature expressions
   
8. "formatting_style": Visual structure
   - Line breaks?
   - Bullet points?
   - Bold/emphasis?
   - Paragraph length?
   
9. "personality_markers": What makes them THEM
   - Humor style?
   - Self-deprecation?
   - Confidence level?
   - How they relate to audience?
   
10. "content_themes": What topics/angles they gravitate toward
    - Do they favor personal stories?
    - Data-driven content?
    - Contrarian takes?

Be EXTREMELY SPECIFIC. Generic insights are useless. 
The goal is to generate new content that sounds exactly like them.
"""


def analyze_best_posts_node(state: RepurposingState) -> RepurposingState:
    """
    Analyzes user's best performing posts to extract writing style patterns.
    
    Enhanced to extract:
    - Voice and personality markers
    - Specific phrases and patterns
    - Structural preferences
    - Engagement tactics
    
    Creates a comprehensive style guide for voice cloning.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with detailed style_guide
    """
    # Skip if no best posts provided
    if not state.get("best_posts") or not state["best_posts"].strip():
        print("ℹ️  [POST ANALYZER] No best posts provided - using generic style")
        state["style_guide"] = None
        return state
    
    # Check cache first
    from utils import CacheManager
    cached_style = CacheManager.get_cached_style(state["best_posts"])
    
    if cached_style:
        state["style_guide"] = cached_style
        return state
    
    print("🔍 [POST ANALYZER] Deep-analyzing user's best posts for voice cloning...")
    
    client = Groq(api_key=state["groq_api_key"])
    
    # Create prompt
    prompt = STYLE_ANALYSIS_PROMPT.format(posts=state["best_posts"])
    
    # Call Groq with JSON mode
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are an expert Content Analyst specializing in voice cloning and style analysis.

Your job is to extract everything that makes a writer unique so we can generate content that sounds EXACTLY like them.

Be extremely specific. Don't say "uses casual tone" - say "uses contractions frequently, starts sentences with 'Look,' and 'Here's the thing:', often includes self-deprecating humor about past failures."

Return valid JSON with all requested keys. Be detailed and actionable."""
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
    
    # Save to cache
    CacheManager.save_style(state["best_posts"], style_data)
    
    print(f"✅ [POST ANALYZER] Voice profile created:")
    print(f"   🎭 Style: {style_data.get('writing_style', 'N/A')[:60]}...")
    print(f"   🎣 Hook patterns: {len(style_data.get('hook_patterns', []))} identified")
    print(f"   💬 Unique phrases: {len(style_data.get('unique_phrases', []))} captured")
    print(f"   🎨 Personality: {style_data.get('personality_markers', 'N/A')[:50] if isinstance(style_data.get('personality_markers'), str) else 'Analyzed'}...")
    
    return state

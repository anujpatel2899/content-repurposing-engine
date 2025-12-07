"""Content Generator Node for LangGraph with Enhanced Human-Like Output."""
import json
from groq import Groq
from typing import List
from .schemas import RepurposingState
from .prompts import (
    GENERATOR_PROMPT, 
    VARIATIONS_PROMPT, 
    PLATFORM_RULES,
    ANTI_AI_RULES,
    HOOK_FORMULAS,
    ENGAGEMENT_RULES,
    get_enhanced_generator_prompt,
    get_enhanced_variations_prompt
)
from config import GROQ_MODEL


def generate_content_node(state: RepurposingState, platform: str) -> RepurposingState:
    """
    Generates human-like content for a specific platform.
    
    Features:
    - Anti-AI detection patterns
    - Viral hook formulas
    - Engagement engineering
    - Style matching from user's best posts
    
    Can generate either:
    - Single draft (normal mode)
    - 3 variations (A/B testing mode)
    """
    print(f"✍️ [GENERATOR] Generating human-like content for {platform}...")
    
    client = Groq(api_key=state["groq_api_key"])
    core_msg = state["core_message"]
    
    # Prepare style instructions
    style_instructions = ""
    if state.get("style_guide"):
        from .prompts import STYLE_GUIDE_INSTRUCTIONS
        style = state["style_guide"]
        
        style_instructions = STYLE_GUIDE_INSTRUCTIONS.format(
            writing_style=style.get("writing_style", "N/A"),
            hook_patterns="\n".join(f"- {p}" for p in style.get("hook_patterns", [])),
            story_structure=style.get("story_structure", "N/A"),
            cta_style=style.get("cta_style", "N/A"),
            emoji_usage=style.get("emoji_usage", "N/A"),
            sentence_length=style.get("sentence_length", "N/A"),
            unique_phrases="\n".join(f"- {p}" for p in style.get("unique_phrases", [])),
            formatting_style=style.get("formatting_style", "N/A")
        )
        print(f"   🎨 [GENERATOR] Using personalized style guide!")
    
    # A/B Testing mode - 3 variations
    if state.get("ab_testing", False):
        # Use enhanced variations prompt with anti-AI rules
        prompt = get_enhanced_variations_prompt().format(
            platform=platform,
            audience=state["audience"],
            platform_rules=PLATFORM_RULES.get(platform, ""),
            topic=core_msg["topic"],
            thesis=core_msg["thesis"],
            insights="\n".join(f"- {i}" for i in core_msg["insights"])
        )
        
        # Try up to 2 times to get 3 variations
        variations = []
        max_attempts = 2
        
        for attempt in range(max_attempts):
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a top-performing content creator known for viral, authentic posts.

CRITICAL: Return valid JSON with EXACTLY this structure:
{
    "variations": [
        "First complete variation content here...",
        "Second complete variation content here...",
        "Third complete variation content here..."
    ]
}

RULES FOR EACH VARIATION:
- NEVER use em dashes (—)
- NEVER use quotation marks for emphasis
- NEVER use words like: delve, crucial, leverage, comprehensive, robust, cutting-edge
- Write like a real human, not an AI assistant
- Each variation must be DISTINCT (different hook, different angle)
- Each variation must be COMPLETE and ready to post

You MUST return exactly 3 variations in the 'variations' array."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.85
            )
            
            data = json.loads(response.choices[0].message.content)
            
            # Try to extract variations from various possible response formats
            if isinstance(data.get("variations"), list):
                variations = data["variations"]
            elif isinstance(data.get("variation"), list):
                variations = data["variation"]
            else:
                # Try numbered keys like variation_1, variation_2, etc.
                variations = []
                for key in ["variation_1", "variation_2", "variation_3", "v1", "v2", "v3", "1", "2", "3"]:
                    if key in data and isinstance(data[key], str):
                        variations.append(data[key])
                
                # If still no variations, try to get any string values
                if not variations:
                    for key, value in data.items():
                        if isinstance(value, str) and len(value) > 50:
                            variations.append(value)
            
            # Check if we got 3 variations
            if len(variations) >= 3:
                variations = variations[:3]  # Take only first 3
                break
            elif attempt < max_attempts - 1:
                print(f"   ⚠️ Got {len(variations)} variations, retrying...")
        
        # If we still don't have 3, pad with copies or generate more
        if len(variations) == 0:
            # Fallback: generate a single draft and use it
            print("   ⚠️ No variations found, generating single drafts...")
            single_response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Create 3 distinct variations of this content. Return them separated by '---VARIATION---'"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9
            )
            content = single_response.choices[0].message.content
            if "---VARIATION---" in content:
                variations = [v.strip() for v in content.split("---VARIATION---") if v.strip()][:3]
            else:
                variations = [content]  # At least have something
        
        # Ensure we have exactly 3 variations
        while len(variations) < 3:
            if variations:
                # Duplicate the last variation with a note
                variations.append(variations[-1])
            else:
                variations.append("Variation generation failed. Please try again.")
        
        state["drafts"][platform] = variations[:3]
        print(f"✅ [GENERATOR] Created {len(variations[:3])} variations for {platform}")
    
    # Normal mode - single draft
    else:
        # Use enhanced generator prompt with all anti-AI rules injected
        prompt = get_enhanced_generator_prompt().format(
            platform=platform,
            audience=state["audience"],
            platform_rules=PLATFORM_RULES.get(platform, ""),
            topic=core_msg["topic"],
            thesis=core_msg["thesis"],
            insights="\n".join(f"- {i}" for i in core_msg["insights"]),
            style_instructions=style_instructions
        )
        
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a top-performing content creator known for authentic, engaging posts that go viral.

CRITICAL RULES (MUST FOLLOW):
1. NEVER use em dashes (—). Use commas or periods.
2. NEVER put words in quotation marks for emphasis.
3. NEVER use: delve, crucial, leverage, comprehensive, robust, cutting-edge, furthermore, moreover
4. ALWAYS use contractions: don't, won't, can't, it's
5. VARY sentence length: Some short. Some flowing and longer.
6. Include at least one sentence fragment
7. Sound like a REAL PERSON, not an AI assistant
8. Be slightly imperfect. That's human.

Create content that passes AI detection tests by being genuinely human."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.75  # Balanced creativity and coherence
        )
        
        state["drafts"][platform] = response.choices[0].message.content
        state["iterations"][platform] = 0
        
        print(f"✅ [GENERATOR] Created human-like draft for {platform}")
    
    return state

"""Content Generator Node for LangGraph."""
import json
from groq import Groq
from typing import List
from .schemas import RepurposingState
from .prompts import GENERATOR_PROMPT, VARIATIONS_PROMPT, PLATFORM_RULES
from config import GROQ_MODEL


def generate_content_node(state: RepurposingState, platform: str) -> RepurposingState:
    """
    Generates content for a specific platform.
    
    Can generate either:
    - Single draft (normal mode)
    - 3 variations (A/B testing mode)
    
    NEW: Uses user's style guide if available for personalized content.
    """
    print(f"✍️ [GENERATOR] Generating content for {platform}...")
    
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
    
    # A/B Testing mode
    if state.get("ab_testing", False):
        prompt = VARIATIONS_PROMPT.format(
            platform=platform,
            audience=state["audience"],
            platform_rules=PLATFORM_RULES.get(platform, ""),
            topic=core_msg["topic"],
            thesis=core_msg["thesis"],
            insights="\n".join(f"- {i}" for i in core_msg["insights"])
        )
        
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a world-class Content Creator. Return valid JSON with key 'variations' containing 3 strings."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )
        
        data = json.loads(response.choices[0].message.content)
        state["drafts"][platform] = data.get("variations", [])
        
        print(f"✅ [GENERATOR] Created 3 variations for {platform}")
    
    # Normal mode - single draft
    else:
        prompt = GENERATOR_PROMPT.format(
            platform=platform,
            audience=state["audience"],
            platform_rules=PLATFORM_RULES.get(platform, ""),
            topic=core_msg["topic"],
            thesis=core_msg["thesis"],
            insights="\n".join(f"- {i}" for i in core_msg["insights"]),
            style_instructions=style_instructions  # NEW: Include style guide
        )
        
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a world-class Content Creator. Create engaging, platform-native content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )
        
        state["drafts"][platform] = response.choices[0].message.content
        state["iterations"][platform] = 0
        
        print(f"✅ [GENERATOR] Created draft for {platform}")
    
    return state

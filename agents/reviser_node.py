"""Reviser Node for LangGraph with Human Authenticity Focus."""
from groq import Groq
from .schemas import RepurposingState
from .prompts import REVISER_PROMPT, PLATFORM_RULES, ANTI_AI_RULES, get_enhanced_reviser_prompt
from config import GROQ_MODEL


def revise_content_node(state: RepurposingState, platform: str) -> RepurposingState:
    """
    Revises content based on critic feedback with focus on human authenticity.
    
    Enhanced to:
    - Fix AI detection patterns (em dashes, banned words)
    - Add human authenticity markers
    - Improve engagement potential
    - Maintain platform compliance
    
    Only called when critique status is FAIL.
    """
    print(f"🔧 [REVISER] Revising {platform} content for human authenticity...")
    
    client = Groq(api_key=state["groq_api_key"])
    
    draft = state["drafts"].get(platform, "")
    critique = state["critiques"].get(platform, {})
    ai_issues = state.get("ai_issues", {}).get(platform, [])
    
    # Format AI issues for the prompt
    ai_issues_text = "\n".join(f"- {issue}" for issue in ai_issues) if ai_issues else "None detected"
    
    prompt = get_enhanced_reviser_prompt().format(
        platform=platform,
        audience=state["audience"],
        draft=draft,
        reasoning=critique.get("reasoning", ""),
        instructions=critique.get("suggested_revision", ""),
        ai_issues=ai_issues_text
    )
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are an expert Content Editor who transforms AI-sounding content into authentic human voice.

YOUR MISSION:
1. Remove ALL AI patterns:
   - Replace em dashes (—) with commas or periods
   - Remove quotation marks used for emphasis
   - Replace banned words (delve, crucial, leverage, etc.) with natural alternatives
   
2. Add human authenticity:
   - Vary sentence length dramatically
   - Include a sentence fragment somewhere
   - Add a casual interjection (honestly, look, here's the thing)
   - Make it slightly imperfect (that's authentic)
   
3. Keep the core message intact
4. Stay within platform constraints
5. Improve engagement potential

The revised content should pass AI detection tests by being genuinely human.

Output ONLY the revised content. No explanations or meta-commentary."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.75  # Higher temp for more natural variation
    )
    
    # Update draft with revision
    state["drafts"][platform] = response.choices[0].message.content
    
    # Increment iteration count
    state["iterations"][platform] = state["iterations"].get(platform, 0) + 1
    
    print(f"✅ [REVISER] Revised {platform} for authenticity (iteration {state['iterations'][platform]})")
    
    return state

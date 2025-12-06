"""Reviser Node for LangGraph."""
from groq import Groq
from .schemas import RepurposingState
from .prompts import REVISER_PROMPT
from config import GROQ_MODEL


def revise_content_node(state: RepurposingState, platform: str) -> RepurposingState:
    """
    Revises content based on critic feedback.
    
    Only called when critique status is FAIL.
    """
    print(f"🔧 [REVISER] Revising {platform} content...")
    
    client = Groq(api_key=state["groq_api_key"])
    
    draft = state["drafts"].get(platform, "")
    critique = state["critiques"].get(platform, {})
    
    prompt = REVISER_PROMPT.format(
        platform=platform,
        audience=state["audience"],
        draft=draft,
        reasoning=critique.get("reasoning", ""),
        instructions=critique.get("suggested_revision", "")
    )
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert Content Editor. Improve the content based on feedback."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )
    
    # Update draft with revision
    state["drafts"][platform] = response.choices[0].message.content
    
    # Increment iteration count
    state["iterations"][platform] = state["iterations"].get(platform, 0) + 1
    
    print(f"✅ [REVISER] Revised {platform} (iteration {state['iterations'][platform]})")
    
    return state

"""Critic Node for LangGraph."""
import json
from groq import Groq
from .schemas import RepurposingState, CritiqueResult
from .prompts import CRITIC_PROMPT, PLATFORM_RULES
from config import GROQ_MODEL


def critique_content_node(state: RepurposingState, platform: str) -> RepurposingState:
    """
    Critiques generated content for quality and compliance.
    
    Returns PASS/FAIL status with improvement suggestions.
    """
    # Skip critique for A/B variations
    if state.get("ab_testing", False):
        state["critiques"][platform] = CritiqueResult(
            status="PASS",
            reasoning="A/B variations generated - skipping critique",
            suggested_revision="",
            predicted_score=85
        )
        return state
    
    print(f"🔍 [CRITIC] Evaluating {platform} content...")
    
    client = Groq(api_key=state["groq_api_key"])
    draft = state["drafts"].get(platform, "")
    
    prompt = CRITIC_PROMPT.format(
        platform=platform,
        audience=state["audience"],
        platform_rules=PLATFORM_RULES.get(platform, ""),
        draft=draft
    )
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a strict Content Editor. Return valid JSON with keys: status, reasoning, suggested_revision, predicted_score."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    
    data = json.loads(response.choices[0].message.content)
    
    state["critiques"][platform] = CritiqueResult(
        status=data["status"],
        reasoning=data["reasoning"],
        suggested_revision=data["suggested_revision"],
        predicted_score=data["predicted_score"]
    )
    
    status_emoji = "✅" if data["status"] == "PASS" else "⚠️"
    print(f"{status_emoji} [CRITIC] {platform}: {data['status']} (Score: {data['predicted_score']}/100)")
    
    return state

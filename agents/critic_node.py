"""Critic Node for LangGraph with AI Detection Check."""
import json
from groq import Groq
from .schemas import RepurposingState, CritiqueResult
from .prompts import CRITIC_PROMPT, PLATFORM_RULES
from config import GROQ_MODEL


def critique_content_node(state: RepurposingState, platform: str) -> RepurposingState:
    """
    Critiques generated content for quality, compliance, AND human authenticity.
    
    Enhanced to check:
    - Platform compliance (character limits, structure)
    - Engagement potential
    - AI detection patterns (em dashes, banned words, etc.)
    - Human authenticity markers
    
    Returns PASS/FAIL status with specific improvement suggestions.
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
    
    print(f"🔍 [CRITIC] Evaluating {platform} content for quality and authenticity...")
    
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
                "content": """You are a ruthless Content Editor who detects AI-generated content and ensures human authenticity.

CRITIQUE PRIORITIES:
1. AI DETECTION (CRITICAL): 
   - Any em dashes (—) = AUTOMATIC FAIL
   - Quotation marks for emphasis = FAIL
   - Words like "delve", "crucial", "leverage", "comprehensive" = FAIL
   - Perfect parallelism = suspicious
   - Too polished = suspicious

2. PLATFORM COMPLIANCE:
   - Character/word limits
   - Hashtag count
   - Proper structure

3. ENGAGEMENT POTENTIAL:
   - Hook strength
   - Comment-worthy ending
   - Audience resonance

4. HUMAN MARKERS:
   - Sentence variety
   - Authentic voice
   - Specific details
   - Minor imperfections (good thing!)

Return valid JSON with keys:
- status: "PASS" or "FAIL"
- ai_detection_issues: list of AI patterns found (empty if none)
- reasoning: detailed explanation
- suggested_revision: specific fixes if FAIL
- predicted_score: 0-100
- strengths: what's working well

Be STRICT on AI detection. Content that sounds robotic is an automatic FAIL."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.2  # Low temp for consistent evaluation
    )
    
    data = json.loads(response.choices[0].message.content)
    
    # Extract AI detection issues for the reviser
    ai_issues = data.get("ai_detection_issues", [])
    
    state["critiques"][platform] = CritiqueResult(
        status=data.get("status", "FAIL"),
        reasoning=data.get("reasoning", ""),
        suggested_revision=data.get("suggested_revision", ""),
        predicted_score=data.get("predicted_score", 0)
    )
    
    # Store AI issues separately for reviser
    if "ai_issues" not in state:
        state["ai_issues"] = {}
    state["ai_issues"][platform] = ai_issues
    
    status_emoji = "✅" if data.get("status") == "PASS" else "⚠️"
    print(f"{status_emoji} [CRITIC] {platform}: {data.get('status')} (Score: {data.get('predicted_score', 0)}/100)")
    
    if ai_issues:
        print(f"   🤖 AI patterns detected: {', '.join(ai_issues[:3])}")
    
    if data.get("strengths"):
        print(f"   💪 Strengths: {data['strengths'][:100]}...")
    
    return state

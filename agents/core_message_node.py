"""Core Message Extraction Node for LangGraph with Enhanced Analysis."""
import json
from groq import Groq
from .schemas import RepurposingState, CoreMessage
from .prompts import CORE_MESSAGE_PROMPT, ANTI_AI_RULES, get_enhanced_core_message_prompt
from config import GROQ_MODEL


def extract_core_message_node(state: RepurposingState) -> RepurposingState:
    """
    Extracts the core message from raw text using Groq.
    
    Enhanced to extract:
    - Core topic and thesis
    - Key insights
    - Hook angles for engagement
    - Controversy potential for discussion
    - Story elements for personal touch
    
    This is the first node in the workflow.
    """
    print("🧠 [CORE MESSAGE] Extracting core message with engagement analysis...")
    
    # Initialize Groq client
    client = Groq(api_key=state["groq_api_key"])
    
    # Use enhanced prompt with anti-AI rules
    prompt = get_enhanced_core_message_prompt().format(raw_text=state["raw_text"])
    
    # Call Groq with JSON mode
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are an expert Content Strategist who identifies what makes content resonate and go viral.

Analyze the content deeply and extract:
1. The core message that must be preserved
2. Specific insights (not generic advice)
3. Hook angles that would stop the scroll
4. Elements that could spark discussion
5. Story elements that humanize the content

Return valid JSON with keys: topic, thesis, insights, audience_analysis, hook_angles, controversy_potential, story_elements.

Be specific and actionable. Generic analysis is useless."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.1  # Low temp for accurate extraction
    )
    
    # Parse JSON response
    data = json.loads(response.choices[0].message.content)
    
    # Update state with core message
    state["core_message"] = CoreMessage(
        topic=data.get("topic", ""),
        thesis=data.get("thesis", ""),
        insights=data.get("insights", []),
        audience_analysis=data.get("audience_analysis", "")
    )
    
    # Store additional engagement data for generator use
    state["engagement_data"] = {
        "hook_angles": data.get("hook_angles", []),
        "controversy_potential": data.get("controversy_potential", ""),
        "story_elements": data.get("story_elements", [])
    }
    
    # Initialize other state fields
    if "drafts" not in state:
        state["drafts"] = {}
    if "critiques" not in state:
        state["critiques"] = {}
    if "iterations" not in state:
        state["iterations"] = {}
    if "metadata" not in state:
        state["metadata"] = {}
    
    print(f"✅ [CORE MESSAGE] Extracted: {data.get('topic', 'Unknown')}")
    if data.get("hook_angles"):
        print(f"   🎣 Hook angles: {len(data['hook_angles'])} options")
    if data.get("controversy_potential"):
        print(f"   🔥 Controversy potential identified")
    
    return state

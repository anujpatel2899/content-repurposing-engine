"""Core Message Extraction Node for LangGraph."""
import json
from groq import Groq
from .schemas import RepurposingState, CoreMessage
from .prompts import CORE_MESSAGE_PROMPT
from config import GROQ_MODEL


def extract_core_message_node(state: RepurposingState) -> RepurposingState:
    """
    Extracts the core message from raw text using Groq.
    
    This is the first node in the workflow.
    """
    print("🧠 [CORE MESSAGE] Extracting core message...")
    
    # Initialize Groq client
    client = Groq(api_key=state["groq_api_key"])
    
    # Create prompt
    prompt = CORE_MESSAGE_PROMPT.format(raw_text=state["raw_text"])
    
    # Call Groq with JSON mode
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert Content Strategist. Return valid JSON with keys: topic, thesis, insights, audience_analysis."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.0001
    )
    
    # Parse JSON response
    data = json.loads(response.choices[0].message.content)
    
    # Update state
    state["core_message"] = CoreMessage(
        topic=data["topic"],
        thesis=data["thesis"],
        insights=data["insights"],
        audience_analysis=data["audience_analysis"]
    )
    
    # Initialize other state fields
    if "drafts" not in state:
        state["drafts"] = {}
    if "critiques" not in state:
        state["critiques"] = {}
    if "iterations" not in state:
        state["iterations"] = {}
    if "metadata" not in state:
        state["metadata"] = {}
    
    print(f"✅ [CORE MESSAGE] Extracted: {data['topic']}")
    
    return state

"""Type definitions for LangGraph state and agent outputs."""
from typing import TypedDict, List, Dict, Optional, Annotated
from typing_extensions import NotRequired
import operator


class CoreMessage(TypedDict):
    """Core message extracted from content."""
    topic: str
    thesis: str
    insights: List[str]
    audience_analysis: str


class CritiqueResult(TypedDict):
    """Critique result for a draft."""
    status: str  # "PASS" or "FAIL"
    reasoning: str
    suggested_revision: str
    predicted_score: int


class ContentMetadata(TypedDict):
    """Metadata about generated content."""
    character_count: int
    word_count: int
    hashtags: List[str]
    has_hook: bool
    has_cta: bool
    platform_compliant: bool
    suggestions: List[str]


class RepurposingState(TypedDict):
    """
    LangGraph state for the content repurposing workflow.
    This state is passed between all nodes in the graph.
    """
    # Input
    raw_text: str
    selected_platforms: List[str]
    audience: str
    ab_testing: bool
    groq_api_key: str
    
    # Phase 2: Best Posts Integration
    best_posts: NotRequired[str]  # User's best performing posts
    style_guide: NotRequired[Optional[Dict]]  # Extracted style patterns
    
    # Core Message
    core_message: NotRequired[CoreMessage]
    
    # Generated Content
    drafts: NotRequired[Dict[str, str]]  # platform -> draft
    
    # Critiques
    critiques: NotRequired[Dict[str, CritiqueResult]]  # platform -> critique
    
    # Iterations tracking
    iterations: NotRequired[Dict[str, int]]  # platform -> iteration count
    
    # Metadata
    metadata: NotRequired[Dict[str, ContentMetadata]]  # platform -> metadata
    
    # Streaming events
    events: NotRequired[List[Dict]]  # For tracking progress

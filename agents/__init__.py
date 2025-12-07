"""
Agents package for LangGraph nodes.

Enhanced with:
- Anti-AI detection patterns
- Viral hook formulas
- Engagement engineering
- Human authenticity markers
- Voice cloning from best posts
"""
from .core_message_node import extract_core_message_node
from .post_analyzer_node import analyze_best_posts_node
from .generator_node import generate_content_node
from .critic_node import critique_content_node
from .reviser_node import revise_content_node
from .validator_node import validate_content_node
from .schemas import RepurposingState, CoreMessage, CritiqueResult, ContentMetadata

# Export prompt utilities for external use
from .prompts import (
    PLATFORM_RULES,
    ANTI_AI_RULES,
    HOOK_FORMULAS,
    ENGAGEMENT_RULES,
    get_enhanced_generator_prompt,
    get_enhanced_core_message_prompt,
    get_enhanced_reviser_prompt,
    get_enhanced_variations_prompt,
    get_enhanced_remix_prompt,
    FIRST_COMMENT_PROMPT,
    CONTENT_REMIX_PROMPT,
)

__all__ = [
    # Nodes
    "extract_core_message_node",
    "analyze_best_posts_node",
    "generate_content_node",
    "critique_content_node",
    "revise_content_node",
    "validate_content_node",
    # Schemas
    "RepurposingState",
    "CoreMessage",
    "CritiqueResult",
    "ContentMetadata",
    # Prompts
    "PLATFORM_RULES",
    "ANTI_AI_RULES",
    "HOOK_FORMULAS",
    "ENGAGEMENT_RULES",
    "get_enhanced_generator_prompt",
    "get_enhanced_core_message_prompt",
    "get_enhanced_reviser_prompt",
    "get_enhanced_variations_prompt",
    "get_enhanced_remix_prompt",
    "FIRST_COMMENT_PROMPT",
    "CONTENT_REMIX_PROMPT",
]

"""Content Validator Node - Checks compliance and generates metadata."""
import re
from .schemas import RepurposingState, ContentMetadata


def validate_content_node(state: RepurposingState, platform: str) -> RepurposingState:
    """
    Validates content and generates metadata.
    
    Checks:
    - Character/word count
    - Hashtags
    - Hook detection
    - CTA detection
    - Platform compliance
    """
    print(f"✓ [VALIDATOR] Validating {platform} content...")
    
    draft = state["drafts"].get(platform, "")
    
    # Handle variations (A/B testing)
    if isinstance(draft, list):
        draft = " ".join(draft)  # Combine for metadata
    
    # Character and word count
    char_count = len(draft)
    word_count = len(draft.split())
    
    # Extract hashtags
    hashtags = re.findall(r'#\w+', draft)
    
    # Detect hook (question or bold statement in first 100 chars)
    has_hook = bool(re.search(r'[?!]', draft[:100]))
    
    # Detect CTA keywords
    cta_keywords = ['click', 'subscribe', 'comment', 'share', 'read more', 'learn', 'try', 'join']
    has_cta = any(kw in draft.lower() for kw in cta_keywords)
    
    # Platform compliance check
    platform_compliant = True
    suggestions = []
    
    # LinkedIn-specific validation
    if platform == "LinkedIn":
        if char_count > 1300:
            platform_compliant = False
            suggestions.append(f"Content exceeds 1,300 character limit ({char_count} chars)")
        if len(hashtags) < 3 or len(hashtags) > 5:
            suggestions.append(f"LinkedIn needs 3-5 hashtags (found {len(hashtags)})")
    
    # Twitter-specific validation
    elif platform == "Twitter/X":
        tweets = draft.split("\n\n")
        for i, tweet in enumerate(tweets):
            if len(tweet) > 280:
                platform_compliant = False
                suggestions.append(f"Tweet {i+1} exceeds 280 characters")
        if len(hashtags) > 2:
            suggestions.append(f"Twitter works best with 1-2 hashtags (found {len(hashtags)})")
    
    # Store metadata
    state["metadata"][platform] = ContentMetadata(
        character_count=char_count,
        word_count=word_count,
        hashtags=hashtags,
        has_hook=has_hook,
        has_cta=has_cta,
        platform_compliant=platform_compliant,
        suggestions=suggestions
    )
    
    compliance_emoji = "✅" if platform_compliant else "⚠️"
    print(f"{compliance_emoji} [VALIDATOR] {platform}: {char_count} chars, {len(hashtags)} hashtags")
    
    return state

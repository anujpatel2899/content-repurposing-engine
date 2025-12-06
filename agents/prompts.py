"""Prompt templates for all agents."""

# Platform-specific rules
PLATFORM_RULES = {
    "LinkedIn": """
    CHARACTER LIMIT: Maximum 1,300 characters (STRICT)
    HASHTAGS: Exactly 3-5 hashtags at the end
    TONE: Professional, thought leadership
    
    STRUCTURE:
    - Hook: First 1-2 lines grab attention
    - Body: 3-5 short paragraphs with line breaks
    - CTA: Clear call-to-action at the end
    - Hashtags: 3-5 relevant hashtags
    """,
    
    "Twitter/X": """
    THREAD LENGTH: 3-7 tweets (STRICT)
    CHARACTER LIMIT: 280 characters per tweet (STRICT)
    HASHTAGS: 1-2 hashtags maximum
    TONE: Punchy, conversational, witty
    
    STRUCTURE:
    - Tweet 1: Hook + thread indicator (1/7)
    - Tweets 2-6: One insight per tweet
    - Last Tweet: Summary + CTA
    """,
    
    "Short Blog": """
    WORD COUNT: 500-700 words (STRICT)
    TONE: Educational, SEO-friendly
    
    STRUCTURE:
    - Title: Compelling H1 with keyword
    - Introduction: 2-3 sentences
    - Body: 3-4 H2 sections
    - Conclusion: Summary + CTA
    """,
    
    "Email Sequence": """
    SEQUENCE: 3 emails (STRICT)
    TONE: Personal, storytelling, conversational
    
    EMAIL 1: Problem/Hook (150-200 words)
    EMAIL 2: Value/Proof (200-250 words)
    EMAIL 3: Solution/CTA (250-300 words)
    """,
    
    "Reddit": """
    WORD COUNT: 300-500 words (STRICT)
    TONE: Authentic, helpful, anti-corporate
    HASHTAGS: NONE
    
    STRUCTURE:
    - Title: Question or "TIL" format
    - Body: Personal insight or breakdown
    - TL;DR: 1-2 sentence summary
    """,
    
    "Substack": """
    WORD COUNT: 800-1200 words (STRICT)
    TONE: Intimate, conversational, personal
    
    STRUCTURE:
    - Subject: Personal, curiosity-driven
    - Opening: Personal anecdote
    - Body: 3-5 sub-sections
    - Conclusion: Reflection + question
    """
}

# Core Message Extraction Prompt
CORE_MESSAGE_PROMPT = """You are an expert Content Strategist. Analyze the provided text and extract its essence.

Output valid JSON with EXACTLY these keys:
1. "topic": The core topic or keyword
2. "thesis": The central thesis (1-2 sentences)
3. "insights": List of 5-7 key actionable insights
4. "audience_analysis": Brief analysis of target audience

Text to analyze:
{raw_text}
"""

# Generator Prompt
GENERATOR_PROMPT = """You are a world-class Content Creator specializing in {platform}.

Repurpose the Core Message into high-performing content for {platform}.

Target Audience: {audience}

Platform Rules (MUST FOLLOW):
{platform_rules}

Core Message:
- Topic: {topic}
- Thesis: {thesis}
- Insights: {insights}

{style_instructions}

CRITICAL: Strictly adhere to all constraints (length, hashtags, structure, tone).

Output ONLY the final content, no explanations.
"""

# Style-aware instructions (inserted when style guide exists)
STYLE_GUIDE_INSTRUCTIONS = """
🎨 IMPORTANT - MATCH THIS WRITING STYLE:

The user has provided examples of their best-performing content. Match their style:

**Writing Style:** {writing_style}

**Hook Patterns:** Use these types of hooks:
{hook_patterns}

**Story Structure:** Follow this structure:
{story_structure}

**CTA Style:** {cta_style}

**Emoji Usage:** {emoji_usage}

**Sentence Style:** {sentence_length}

**Unique Phrases:** Try to incorporate similar patterns:
{unique_phrases}

**Formatting:** {formatting_style}

Make it sound like THEM, not generic content!
"""

# Variations Prompt (for A/B testing)
VARIATIONS_PROMPT = """You are a world-class Content Creator for {platform}.

Create 3 DISTINCT variations for A/B testing.

Target Audience: {audience}

Platform Rules:
{platform_rules}

Core Message:
- Topic: {topic}
- Thesis: {thesis}
- Insights: {insights}

Generate 3 variations with different approaches:
1. Contrarian/Bold angle
2. Storytelling/Personal angle
3. Actionable/How-To angle

Output valid JSON with key "variations": [string, string, string]
"""

# Critic Prompt
CRITIC_PROMPT = """You are a strict Content Editor and Growth Hacker.

Evaluate the draft for {platform} against platform rules.

Target Audience: {audience}

Platform Rules:
{platform_rules}

Draft:
{draft}

Critique criteria:
1. Length constraints
2. Tone appropriateness
3. Hook strength
4. Formatting
5. Audience resonance

Output valid JSON with EXACTLY these keys:
- "status": "PASS" if excellent (90/100+), "FAIL" otherwise
- "reasoning": Why it passed/failed
- "suggested_revision": Specific fix instructions if FAIL, else ""
- "predicted_score": Integer 0-100 (virality potential)

Be strict!
"""

# Reviser Prompt
REVISER_PROMPT = """You are an expert Content Editor.

Revise the draft based on critic feedback.

Platform: {platform}
Audience: {audience}

Original Draft:
{draft}

Critique: {reasoning}
Instructions: {instructions}

Fix the issues while maintaining the core message.
Output ONLY the revised content.
"""

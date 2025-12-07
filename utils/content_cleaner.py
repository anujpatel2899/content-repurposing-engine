"""
Content Post-Processor: Cleans AI patterns from generated content.

This module removes:
- Em dashes (—) and en dashes (–)
- Quotation marks used for emphasis
- AI-typical words and phrases
- Other detectable AI patterns
"""
import re
from typing import Dict, List, Tuple
import random


# ============================================================================
# WORD REPLACEMENT MAPS
# ============================================================================

# Words to replace with more human alternatives
# Format: "ai_word": ["alternative1", "alternative2", ...]
WORD_REPLACEMENTS: Dict[str, List[str]] = {
    # Analysis/analytical words
    "analysis": ["breakdown", "look", "review", "take"],
    "analyze": ["look at", "break down", "review", "examine"],
    "analyzed": ["looked at", "reviewed", "examined", "broke down"],
    "analyzing": ["looking at", "reviewing", "breaking down"],
    
    # Corporate buzzwords
    "delve": ["dig into", "explore", "get into", "look at"],
    "delving": ["digging into", "exploring", "getting into"],
    "crucial": ["key", "important", "big", "major"],
    "leverage": ["use", "apply", "tap into", "work with"],
    "leveraging": ["using", "applying", "tapping into"],
    "utilize": ["use", "apply", "work with"],
    "utilizing": ["using", "applying", "working with"],
    "utilization": ["use", "usage"],
    "comprehensive": ["full", "complete", "thorough", "detailed"],
    "robust": ["strong", "solid", "reliable"],
    "streamline": ["simplify", "speed up", "make easier"],
    "streamlined": ["simplified", "faster", "smoother"],
    "optimize": ["improve", "make better", "tune"],
    "optimizing": ["improving", "tuning", "tweaking"],
    "optimization": ["improvement", "tuning"],
    "facilitate": ["help", "make easier", "enable"],
    "facilitating": ["helping", "enabling"],
    "implement": ["build", "create", "set up", "put in place"],
    "implementing": ["building", "creating", "setting up"],
    "implementation": ["setup", "rollout", "execution"],
    
    # Transition words
    "furthermore": ["also", "plus", "and"],
    "moreover": ["also", "and", "plus"],
    "additionally": ["also", "plus", "on top of that"],
    "consequently": ["so", "as a result", "because of this"],
    "nevertheless": ["still", "but", "even so"],
    "nonetheless": ["still", "but", "yet"],
    "henceforth": ["from now on", "going forward"],
    "thereby": ["so", "which", "and"],
    "wherein": ["where", "in which"],
    "thereof": ["of it", "of this"],
    "hereby": ["with this", "now"],
    
    # Fancy words
    "plethora": ["lot", "many", "tons"],
    "myriad": ["many", "lots of", "countless"],
    "multitude": ["many", "lots", "bunch"],
    "paramount": ["key", "top", "most important"],
    "pivotal": ["key", "critical", "turning point"],
    "groundbreaking": ["new", "innovative", "fresh"],
    "cutting-edge": ["latest", "modern", "new"],
    "game-changer": ["big deal", "major shift", "breakthrough"],
    "revolutionary": ["new", "innovative", "fresh"],
    "transformative": ["powerful", "impactful", "major"],
    "seamless": ["smooth", "easy", "simple"],
    "seamlessly": ["smoothly", "easily", "naturally"],
    "synergy": ["teamwork", "collaboration", "working together"],
    "paradigm": ["model", "approach", "way of thinking"],
    "holistic": ["complete", "full", "whole"],
    "ecosystem": ["system", "environment", "space"],
    "landscape": ["space", "world", "field"],
    "realm": ["area", "field", "space"],
    "sphere": ["area", "field", "world"],
    
    # AI-typical phrases (handled separately)
    "it is important to note": ["note that", "keep in mind"],
    "it's important to note": ["note that", "keep in mind"],
    "at the end of the day": ["ultimately", "in the end"],
    "the bottom line is": ["basically", "simply put"],
    "in today's world": ["today", "now", "these days"],
    "in the digital age": ["today", "now"],
    "without further ado": ["so", "let's go", "here it is"],
    "let's dive in": ["let's go", "here we go", "let's get into it"],
    "let's delve into": ["let's look at", "let's explore"],
    "first and foremost": ["first", "to start"],
    "last but not least": ["finally", "and"],
    "in conclusion": ["so", "to wrap up", "bottom line"],
    "to summarize": ["so", "in short", "basically"],
}

# Phrases to remove entirely or simplify
PHRASES_TO_SIMPLIFY: Dict[str, str] = {
    "utilize": "use",
    "utilization": "use",
    "leverage": "use",
    "facilitate": "help",
    "implement": "do",
    "subsequently": "then",
    "prior to": "before",
    "in order to": "to",
    "due to the fact that": "because",
    "in the event that": "if",
    "at this point in time": "now",
    "for the purpose of": "to",
    "in spite of the fact": "although",
    "on a daily basis": "daily",
    "in the near future": "soon",
    "a large number of": "many",
    "the vast majority of": "most",
    "in close proximity to": "near",
}


# ============================================================================
# CLEANUP FUNCTIONS
# ============================================================================

def clean_em_dashes(text: str) -> str:
    """Replace em dashes and en dashes with appropriate punctuation."""
    # Em dash (—) to comma or period based on context
    # Pattern: word—word or word — word
    text = re.sub(r'\s*—\s*', ', ', text)  # Em dash with spaces
    text = re.sub(r'—', ', ', text)  # Em dash without spaces
    
    # En dash (–) to hyphen
    text = re.sub(r'–', '-', text)
    
    # Clean up double commas that might result
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r'\.\s*,', '.', text)
    text = re.sub(r',\s*\.', '.', text)
    
    return text


def clean_emphasis_quotes(text: str) -> str:
    """Remove quotation marks used for emphasis on single words/short phrases."""
    # Pattern: "word" or "short phrase" (1-3 words) used for emphasis
    # Keep actual quotes (dialogue, citations)
    
    # Remove quotes around single words that aren't dialogue
    # Match "word" where word is 1-20 chars and not a full sentence
    text = re.sub(r'"(\w{1,20})"', r'\1', text)
    
    # Remove quotes around 2-3 word emphasis phrases
    text = re.sub(r'"(\w+\s\w+)"', r'\1', text)
    text = re.sub(r'"(\w+\s\w+\s\w+)"', r'\1', text)
    
    # Also handle curly quotes
    text = re.sub(r'["""](\w{1,20})["""]', r'\1', text)
    text = re.sub(r'["""](\w+\s\w+)["""]', r'\1', text)
    
    return text


def replace_ai_words(text: str) -> str:
    """Replace AI-typical words with human alternatives."""
    result = text
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_words = sorted(WORD_REPLACEMENTS.keys(), key=len, reverse=True)
    
    for ai_word in sorted_words:
        alternatives = WORD_REPLACEMENTS[ai_word]
        
        # Skip if word not in text (optimization)
        if ai_word.lower() not in result.lower():
            continue
        
        # Pick a replacement (first one is usually best)
        replacement = alternatives[0]
        
        # Use word boundaries to avoid partial matches
        # Example: "implement" shouldn't match inside "implementation"
        pattern = re.compile(r'\b' + re.escape(ai_word) + r'\b', re.IGNORECASE)
        
        def replace_match(match):
            original = match.group(0)
            # Preserve capitalization
            if original.isupper():
                return replacement.upper()
            elif original[0].isupper():
                return replacement.capitalize()
            return replacement
        
        result = pattern.sub(replace_match, result)
    
    return result


def clean_verbose_phrases(text: str) -> str:
    """Simplify verbose AI phrases."""
    result = text
    
    # Sort by length (longest first) to match longer phrases before shorter words
    sorted_phrases = sorted(PHRASES_TO_SIMPLIFY.keys(), key=len, reverse=True)
    
    for verbose in sorted_phrases:
        simple = PHRASES_TO_SIMPLIFY[verbose]
        
        # Use word boundaries for single/few word patterns
        if ' ' not in verbose:
            # Single word - use word boundaries
            pattern = re.compile(r'\b' + re.escape(verbose) + r'\b', re.IGNORECASE)
        else:
            # Multi-word phrase - case insensitive only
            pattern = re.compile(re.escape(verbose), re.IGNORECASE)
        
        result = pattern.sub(simple, result)
    
    return result


def add_human_imperfections(text: str) -> str:
    """Optionally add subtle human markers if text seems too perfect."""
    # This is subtle - we don't want to make it worse
    # Just ensure contractions are used
    
    contractions = [
        ("do not", "don't"),
        ("does not", "doesn't"),
        ("did not", "didn't"),
        ("will not", "won't"),
        ("would not", "wouldn't"),
        ("could not", "couldn't"),
        ("should not", "shouldn't"),
        ("can not", "can't"),
        ("cannot", "can't"),
        ("is not", "isn't"),
        ("are not", "aren't"),
        ("was not", "wasn't"),
        ("were not", "weren't"),
        ("have not", "haven't"),
        ("has not", "hasn't"),
        ("had not", "hadn't"),
        ("it is", "it's"),
        ("that is", "that's"),
        ("there is", "there's"),
        ("here is", "here's"),
        ("what is", "what's"),
        ("who is", "who's"),
        ("let us", "let's"),
        ("I am", "I'm"),
        ("you are", "you're"),
        ("we are", "we're"),
        ("they are", "they're"),
        ("I will", "I'll"),
        ("you will", "you'll"),
        ("we will", "we'll"),
        ("I would", "I'd"),
        ("you would", "you'd"),
        ("we would", "we'd"),
        ("I have", "I've"),
        ("you have", "you've"),
        ("we have", "we've"),
    ]
    
    result = text
    for formal, contraction in contractions:
        # Case-insensitive replacement
        pattern = re.compile(r'\b' + re.escape(formal) + r'\b', re.IGNORECASE)
        
        def replace_contraction(match):
            original = match.group(0)
            if original[0].isupper():
                return contraction.capitalize()
            return contraction
        
        result = pattern.sub(replace_contraction, result)
    
    return result


# ============================================================================
# MAIN CLEANUP FUNCTION
# ============================================================================

def clean_duplicate_words(text: str) -> str:
    """Remove accidental duplicate words like 'into into' or 'that that'."""
    # Pattern matches repeated words (case-insensitive)
    result = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
    return result


def cleanup_ai_content(text: str) -> str:
    """
    Main function to clean AI patterns from generated content.
    
    Applies all cleanup steps in optimal order:
    1. Simplify verbose phrases (longest matches first)
    2. Replace AI words (single word replacements)
    3. Remove em dashes
    4. Remove emphasis quotes
    5. Add contractions
    6. Clean duplicate words
    
    Args:
        text: Generated content to clean
        
    Returns:
        Cleaned content with AI patterns removed
    """
    if not text:
        return text
    
    # Apply all cleanup steps in optimal order
    result = text
    
    # Step 1: Phrases first (longer matches before word replacements)
    result = clean_verbose_phrases(result)
    
    # Step 2: Word replacements
    result = replace_ai_words(result)
    
    # Step 3: Punctuation cleanup
    result = clean_em_dashes(result)
    result = clean_emphasis_quotes(result)
    
    # Step 4: Contractions
    result = add_human_imperfections(result)
    
    # Step 5: Clean up duplicate words (e.g., "into into")
    result = clean_duplicate_words(result)
    
    # Step 6: Clean up spacing
    result = re.sub(r'  +', ' ', result)  # Double spaces
    result = re.sub(r'\s+([.,!?;:])', r'\1', result)  # Space before punctuation
    result = re.sub(r'([.,!?;:])\s*([.,!?;:])', r'\1', result)  # Double punctuation
    
    return result.strip()


def cleanup_content_list(contents: List[str]) -> List[str]:
    """Clean a list of content pieces (for A/B variations)."""
    return [cleanup_ai_content(content) for content in contents]


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test the cleanup
    test_text = """
    The analysis—a crucial step—helps you leverage your data effectively.
    
    It's important to note that we need to utilize comprehensive strategies
    to optimize our approach. Let's delve into the "robust" methodology.
    
    Furthermore, this groundbreaking implementation will facilitate seamless
    integration. In today's digital landscape, we must analyze the paradigm shift.
    """
    
    print("BEFORE:")
    print(test_text)
    print("\n" + "="*50 + "\n")
    print("AFTER:")
    print(cleanup_ai_content(test_text))

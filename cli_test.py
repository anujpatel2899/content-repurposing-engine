"""
Command-line interface for testing the Content Repurposing Engine.

Usage:
    python cli_test.py
"""
import os
from dotenv import load_dotenv
from workflow import run_workflow

# Load environment variables
load_dotenv()

def main():
    """Test the workflow from command line."""
    print("="*60)
    print("Content Repurposing Engine - CLI Test")
    print("="*60)
    
    # Get API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        groq_api_key = input("Enter your Groq API Key: ").strip()
    
    # Sample content
    sample_text = """
    The future of AI is not about replacing humans, but augmenting them.
    
    After working with over 100 companies implementing AI solutions, I've noticed 3 patterns:
    
    1. Companies that succeed treat AI as a tool, not a replacement
    2. The best results come from human-AI collaboration
    3. Training employees to work WITH AI is more valuable than just deploying AI
    
    The key insight: AI should handle repetitive tasks while humans focus on creative problem-solving
    and relationship building. This isn't about job loss - it's about job evolution.
    
    Companies investing in upskilling their workforce for AI collaboration are seeing 3x better ROI
    than those just automating tasks.
    """
    
    # Sample best posts (Phase 2) - Optional
    sample_best_posts = """
    Post 1:
    AI isn't magic. It's math.
    
    But here's what most people miss:
    
    The real magic happens when you combine AI with human intuition.
    
    I've seen companies spend millions on AI only to fail. Why? They forgot the human element.
    
    3 lessons:
    • AI automates tasks, not thinking
    • Humans provide context and creativity
    • Together they're unstoppable
    
    What's your experience with AI in your work?
    
    ---
    
    Post 2:
    Hot take: Your competition isn't other companies.
    
    It's the status quo.
    
    Most businesses fail because they can't convince customers to change their habits.
    
    Here's how I overcame this at my last startup:
    
    1. Started with early adopters
    2. Made switching effortless
    3. Showed immediate value
    
    Result? 200% growth in 6 months.
    
    The lesson: Sell the change, not just the product.
    """
    
    print("\n📝 Sample Content:")
    print(sample_text[:200] + "...")
    
    print("\n🎨 Sample Best Posts (for style matching):")
    print(sample_best_posts[:150] + "...")
    
    print("\n🎯 Target Platforms: LinkedIn, Twitter/X")
    print("👥 Audience: General Professional")
    print("\n" + "="*60 + "\n")
    
    # Run workflow with streaming
    for event in run_workflow(
        raw_text=sample_text,
        selected_platforms=["LinkedIn", "Twitter/X"],
        audience="General Professional",
        ab_testing=False,
        groq_api_key=groq_api_key,
        best_posts=sample_best_posts  # NEW: Phase 2
    ):
        event_type = event.get("type")
        message = event.get("message", "")
        
        if event_type == "status":
            print(f"\n{message}")
        
        elif event_type == "core_message":
            core = event.get("data", {})
            print(f"\n✅ {message}")
            print(f"   📌 Topic: {core.get('topic', 'N/A')}")
            print(f"   💡 Thesis: {core.get('thesis', 'N/A')[:80]}...")
        
        # NEW: Phase 2 - Style analysis
        elif event_type == "style_analyzed":
            style = event.get("data", {})
            print(f"\n🎨 {message}")
            print(f"   ✍️  Writing Style: {style.get('writing_style', 'N/A')}")
            print(f"   🎣 Hook Patterns: {len(style.get('hook_patterns', []))} identified")
            print(f"   📝 Unique Phrases: {len(style.get('unique_phrases', []))} found")
        
        elif event_type == "draft_generated":
            platform = event.get("platform")
            print(f"\n✅ {message}")
        
        elif event_type == "critique_complete":
            critique = event.get("critique", {})
            print(f"   🔍 {message}")
            print(f"   📊 Reasoning: {critique.get('reasoning', 'N/A')[:80]}...")
        
        elif event_type == "validation_complete":
            metadata = event.get("metadata", {})
            print(f"\n{message}")
            print(f"   📏 {metadata.get('character_count', 0)} chars, {metadata.get('word_count', 0)} words")
            print(f"   🏷️  {len(metadata.get('hashtags', []))} hashtags")
        
        elif event_type == "complete":
            state = event.get("state", {})
            print(f"\n\n{'='*60}")
            print(f"{message}")
            print(f"{'='*60}\n")
            
            # Display results
            for platform, draft in state.get("drafts", {}).items():
                print(f"\n{'='*60}")
                print(f"📱 {platform.upper()}")
                print(f"{'='*60}\n")
                print(draft)
                print()
                
                # Show metadata
                meta = state.get("metadata", {}).get(platform, {})
                print(f"\n📊 Metadata:")
                print(f"   Characters: {meta.get('character_count', 0)}")
                print(f"   Words: {meta.get('word_count', 0)}")
                print(f"   Hashtags: {', '.join(meta.get('hashtags', []))}")
                print(f"   Compliant: {'✅' if meta.get('platform_compliant') else '⚠️'}")
                
                if meta.get('suggestions'):
                    print(f"\n💡 Suggestions:")
                    for suggestion in meta.get('suggestions', []):
                        print(f"   - {suggestion}")
                
                print()

if __name__ == "__main__":
    main()

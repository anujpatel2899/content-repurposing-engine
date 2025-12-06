"""
LangGraph Workflow for Content Repurposing.

This is the main workflow that orchestrates all agents using LangGraph 1.0.

Phase 3: Now with parallel processing for 2x speed!
"""
from typing import Literal, Generator, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from langgraph.graph import StateGraph, END, START
from agents import (
    RepurposingState,
    extract_core_message_node,
    generate_content_node,
    critique_content_node,
    revise_content_node,
    validate_content_node,
)
from config import MAX_CRITIQUE_ITERATIONS, ENABLE_PARALLEL_PROCESSING


def create_repurposing_workflow() -> StateGraph:
    """
    Creates the LangGraph workflow for content repurposing.
    
    Workflow:
    1. Extract core message
    2. For each platform:
       - Generate content
       - Critique content
       - Revise if needed (max 2 iterations)
       - Validate and generate metadata
    """
    workflow = StateGraph(RepurposingState)
    
    # Add core message extraction node
    workflow.add_node("extract_core", extract_core_message_node)
    
    # Entry point
    workflow.add_edge(START, "extract_core")
    
    # After core message, we'll route to platform-specific generators
    # This is handled dynamically in the run_workflow function
    
    return workflow


def process_single_platform(state: RepurposingState, platform: str) -> Dict[str, Any]:
    """
    Process a single platform (for parallel execution).
    
    Phase 3: This runs in parallel for each platform to speed up generation.
    
    Returns dictionary with platform results.
    """
    results = {
        "platform": platform,
        "events": [],
        "draft": None,
        "critique": None,
        "metadata": None,
        "iterations": 0
    }
    
    try:
        # Generate
        state = generate_content_node(state, platform)
        results["draft"] = state["drafts"][platform]
        results["events"].append({"type": "draft_generated", "platform": platform})
        
        # Skip critique for A/B testing
        if state.get("ab_testing"):
            state = validate_content_node(state, platform)
            results["metadata"] = state["metadata"][platform]
            results["events"].append({"type": "validation_complete", "platform": platform})
            return results
        
        # Critique loop
        for iteration in range(MAX_CRITIQUE_ITERATIONS):
            state = critique_content_node(state, platform)
            critique = state["critiques"][platform]
            results["critique"] = critique
            results["events"].append({"type": "critique_complete", "iteration": iteration})
            
            if critique["status"] == "PASS":
                state = validate_content_node(state, platform)
                results["metadata"] = state["metadata"][platform]
                results["events"].append({"type": "validation_complete", "status": "PASS"})
                break
            
            # Revise if needed
            if iteration < MAX_CRITIQUE_ITERATIONS - 1:
                state = revise_content_node(state, platform)
                results["draft"] = state["drafts"][platform]
                results["iterations"] = iteration + 1
                results["events"].append({"type": "revision_complete", "iteration": iteration})
            else:
                state = validate_content_node(state, platform)
                results["metadata"] = state["metadata"][platform]
                results["events"].append({"type": "validation_complete", "status": "MAX_ITERATIONS"})
        
        return results
        
    except Exception as e:
        results["error"] = str(e)
        results["events"].append({"type": "error", "error": str(e)})
        return results


def run_workflow(
    raw_text: str,
    selected_platforms: list[str],
    audience: str = "General Professional",
    ab_testing: bool = False,
    groq_api_key: str = "",
    best_posts: str = "",  # NEW: Phase 2
) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
    """
    Runs the content repurposing workflow with streaming.
    
    Yields progress events as the workflow executes.
    
    Args:
        raw_text: Source content
        selected_platforms: List of platforms to generate for
        audience: Target audience
        ab_testing: Whether to generate A/B variations
        groq_api_key: Groq API key
        best_posts: User's best performing posts (optional, for style matching)
    
    Yields:
        Progress events with type and data
    
    Returns:
        Final state with all generated content
    """
    from agents import analyze_best_posts_node  # Import here
    
    # Initialize state
    state: RepurposingState = {
        "raw_text": raw_text,
        "selected_platforms": selected_platforms,
        "audience": audience,
        "ab_testing": ab_testing,
        "groq_api_key": groq_api_key,
        "best_posts": best_posts,  # NEW: Phase 2
    }
    
    # Step 1: Extract core message
    yield {
        "type": "status",
        "message": "🧠 Extracting core message...",
        "platform": None
    }
    
    state = extract_core_message_node(state)
    
    yield {
        "type": "core_message",
        "data": state["core_message"],
        "message": f"✅ Core message extracted: {state['core_message']['topic']}"
    }
    
    # Step 2: Analyze best posts (if provided) - NEW: Phase 2
    if best_posts and best_posts.strip():
        yield {
            "type": "status",
            "message": "🔍 Analyzing your writing style from best posts...",
            "platform": None
        }
        
        state = analyze_best_posts_node(state)
        
        if state.get("style_guide"):
            yield {
                "type": "style_analyzed",
                "data": state["style_guide"],
                "message": f"✅ Style extracted: {state['style_guide'].get('writing_style', 'N/A')}"
            }
    
    # Step 3: Process platforms (PARALLEL or SEQUENTIAL based on config)
    # Use local variable to track if we should use parallel processing
    use_parallel = ENABLE_PARALLEL_PROCESSING and len(selected_platforms) > 1
    
    if use_parallel:
        # Phase 3: PARALLEL PROCESSING - All platforms at once!
        yield {
            "type": "status",
            "message": f"⚡ Processing {len(selected_platforms)} platforms in parallel...",
            "platform": None
        }
        
        # Initialize state dictionaries for parallel processing
        if "drafts" not in state:
            state["drafts"] = {}
        if "critiques" not in state:
            state["critiques"] = {}
        if "metadata" not in state:
            state["metadata"] = {}
        if "iterations" not in state:
            state["iterations"] = {}
        
        try:
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=len(selected_platforms)) as executor:
                # Submit all platforms
                future_to_platform = {
                    executor.submit(process_single_platform, state.copy(), platform): platform
                    for platform in selected_platforms
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_platform):
                    platform = future_to_platform[future]
                    try:
                        result = future.result()
                        
                        # Update state with results
                        state["drafts"][platform] = result["draft"]
                        if result["critique"]:
                            state["critiques"][platform] = result["critique"]
                        if result["metadata"]:
                            state["metadata"][platform] = result["metadata"]
                        state["iterations"][platform] = result["iterations"]
                        
                        # Yield events
                        for event in result["events"]:
                            if event["type"] == "draft_generated":
                                yield {
                                    "type": "draft_generated",
                                    "platform": platform,
                                    "draft": result["draft"],
                                    "message": f"✅ Draft created for {platform}"
                                }
                            elif event["type"] == "validation_complete":
                                yield {
                                    "type": "validation_complete",
                                    "platform": platform,
                                    "metadata": result["metadata"],
                                    "message": f"✅ {platform} validated!"
                                }
                        
                    except Exception as e:
                        yield {
                            "type": "error",
                            "platform": platform,
                            "message": f"❌ {platform} failed: {str(e)}"
                        }
        
        except Exception as e:
            yield {
                "type": "status",
                "message": f"⚠️ Parallel processing failed: {e}, falling back to sequential...",
                "platform": None
            }
            # Fallback to sequential if parallel fails
            use_parallel = False
    
    if not use_parallel:
        # SEQUENTIAL PROCESSING - One platform at a time (original Phase 2 logic)
        for platform in selected_platforms:
            yield {
                "type": "status",
                "message": f"✍️ Generating content for {platform}...",
                "platform": platform
            }
            
            # Generate content first
            state = generate_content_node(state, platform)
            
            yield {
                "type": "draft_generated",
                "platform": platform,
                "draft": state["drafts"][platform],
                "message": f"✅ Draft created for {platform}"
            }
            
            # Skip critique for A/B testing
            if state.get("ab_testing"):
                state = validate_content_node(state, platform)
                yield {
                    "type": "validation_complete",
                    "platform": platform,
                    "metadata": state["metadata"][platform],
                    "message": f"✅ {platform} validated!"
                }
                continue
            
            # Critique loop with proper iteration tracking
            for iteration in range(MAX_CRITIQUE_ITERATIONS):
                state = critique_content_node(state, platform)
                
                critique = state["critiques"][platform]
                
                yield {
                    "type": "critique_complete",
                    "platform": platform,
                    "critique": critique,
                    "message": f"{critique['status']}: Score {critique['predicted_score']}/100"
                }
                
                # If PASS, validate and break
                if critique["status"] == "PASS":
                    state = validate_content_node(state, platform)
                    
                    yield {
                        "type": "validation_complete",
                        "platform": platform,
                        "metadata": state["metadata"][platform],
                        "message": f"✅ {platform} approved and validated!"
                    }
                    break
                
                # If FAIL and iterations remaining, revise
                if iteration < MAX_CRITIQUE_ITERATIONS - 1:
                    yield {
                        "type": "status",
                        "message": f"🔧 Revising {platform}...",
                        "platform": platform
                    }
                    
                    state = revise_content_node(state, platform)
                    
                    yield {
                        "type": "revision_complete",
                        "platform": platform,
                        "draft": state["drafts"][platform],
                        "message": f"✓ Revision {iteration + 1} complete"
                    }
                else:
                    # Max iterations reached, validate anyway
                    state = validate_content_node(state, platform)
                    
                    yield {
                        "type": "validation_complete",
                        "platform": platform,
                        "metadata": state["metadata"][platform],
                        "message": f"⚠️ {platform} validated (max iterations reached)"
                    }
    
    # Final status
    yield {
        "type": "complete",
        "message": "🎉 All platforms complete!",
        "state": state
    }
    
    return state

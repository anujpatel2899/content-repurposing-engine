"""
Content Repurposing Engine - Streamlit UI with LangGraph.

No FastAPI backend - Direct LangGraph integration with streaming!
"""
import streamlit as st
import os
import hashlib
from dotenv import load_dotenv
from styles import inject_custom_css
from workflow import run_workflow
from utils import extract_from_url, extract_from_file

# Load environment variables
load_dotenv()

# =============================================================================
# RATE LIMITING CONFIGURATION
# =============================================================================
MAX_FREE_REQUESTS = 10  # Maximum free requests per session using app's API key

# Initialize session state for rate limiting
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0
if 'using_own_key' not in st.session_state:
    st.session_state.using_own_key = False

st.set_page_config(
    page_title="Content Repurposing Engine",
    page_icon="✨",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
inject_custom_css()

st.title("Content Repurposing Engine")
st.caption("Powered by LangGraph + Groq + Gemini | Human-like content generation")

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("Configuration")
    
    # API Keys
    st.subheader("🔑 API Keys")
    
    groq_key = st.text_input("Groq API Key", type="password", help="Get free key at console.groq.com")
    google_key = st.text_input("Google API Key (Optional)", type="password", help="For PDF uploads")
    
    # Check if user entered their own key
    user_entered_key = False
    
    # Load from secrets (Streamlit Cloud) first
    app_groq_key = None
    try:
        app_groq_key = st.secrets.get("GROQ_API_KEY", None)
    except:
        pass
    
    # If user entered a key manually
    if groq_key:
        groq_key = groq_key.strip()
        user_entered_key = True
        st.session_state['groq_api_key'] = groq_key
        st.session_state['using_own_key'] = True
        os.environ['GROQ_API_KEY'] = groq_key
        st.success("✅ Using YOUR API key (unlimited)")
    # Else try to load from secrets or .env
    elif app_groq_key:
        groq_key = app_groq_key
        st.session_state['groq_api_key'] = groq_key
        st.session_state['using_own_key'] = False
        os.environ['GROQ_API_KEY'] = groq_key
        remaining = MAX_FREE_REQUESTS - st.session_state.request_count
        if remaining > 0:
            st.info(f"🎁 Free requests: {remaining}/{MAX_FREE_REQUESTS}")
        else:
            st.warning("⚠️ Free limit reached. Enter your own key!")
    elif os.getenv("GROQ_API_KEY"):
        groq_key = os.getenv("GROQ_API_KEY")
        st.session_state['groq_api_key'] = groq_key
        st.session_state['using_own_key'] = False
        remaining = MAX_FREE_REQUESTS - st.session_state.request_count
        if remaining > 0:
            st.info(f"🎁 Free requests: {remaining}/{MAX_FREE_REQUESTS}")
        else:
            st.warning("⚠️ Free limit reached. Enter your own key!")
    
    if google_key:
        google_key = google_key.strip()
        st.session_state['google_api_key'] = google_key
        os.environ['GOOGLE_API_KEY'] = google_key
    elif os.getenv("GOOGLE_API_KEY"):
        google_key = os.getenv("GOOGLE_API_KEY")
        st.session_state['google_api_key'] = google_key
    
    st.divider()
    
    # Platform Selection
    st.header("Target Platforms")
    st.caption("⚠️ Select maximum 2 platforms")
    platforms = ["LinkedIn", "Twitter/X", "Short Blog", "Email Sequence", "Reddit", "Substack"]
    selected_platforms = st.multiselect(
        "Select Platforms (Max 2)", 
        platforms,
        max_selections=2
    )
    st.session_state['selected_platforms'] = selected_platforms
    
    st.divider()
    
    # Audience
    st.header("Audience & Tone")
    audience = st.selectbox("Target Audience", ["General Professional", "B2B Tech", "Gen Z", "Finance", "Custom"])
    if audience == "Custom":
        audience = st.text_input("Enter Custom Audience")
    st.session_state['audience'] = audience
    
    st.divider()
    
    # A/B Testing
    st.header("A/B Testing")
    st.caption("💡 Generate 3 variations")
    
    can_ab_test = len(selected_platforms) == 1
    
    ab_testing = st.checkbox(
        "Generate 3 A/B Variations", 
        disabled=not can_ab_test,
        help="Select exactly 1 platform to enable"
    )
    
    if not can_ab_test:
        if len(selected_platforms) > 1:
            st.warning(f"⚠️ A/B testing requires 1 platform (you selected {len(selected_platforms)})")
        elif len(selected_platforms) == 0:
            st.info("ℹ️ Select 1 platform to enable A/B testing")
    
    st.session_state['ab_testing'] = ab_testing if can_ab_test else False
    
    st.divider()
    
    # Phase 2: Best Posts Input - NEW!
    st.header("🎨 Style Personalization")
    st.caption("💡 Optional: Paste 1-3 of your best posts to match your style")
    
    best_posts = st.text_area(
        "Your Best Performing Posts",
        height=150,
        placeholder="Paste your best LinkedIn/Twitter posts here...\n\nExample:\n'Just shipped my first AI product! Here's what I learned...[your full post]'\n\n'The secret to great content? Start with...[your full post]'",
        help="Paste 1-3 of your highest-performing posts. The AI will analyze your style and match it!"
    )
    
    st.session_state['best_posts'] = best_posts
    
    if best_posts and len(best_posts.strip()) > 100:
        st.success(f"✅ {len(best_posts.split())} words ready for style analysis")
    
    st.divider()
    
    # Estimated time
    if selected_platforms:
        estimated_time = len(selected_platforms) * 8 + 3
        st.info(f"⚡ Estimated: ~{estimated_time}s for {len(selected_platforms)} platform(s)")
        st.caption("✨ Live streaming - see progress in real-time!")

# --- Main Input Area ---
st.header("Source Content")
input_method = st.radio("Select Input Method", ["Text Paste", "URL", "File Upload"])

raw_text = ""

if input_method == "Text Paste":
    # Use session state to preserve text
    default_text = st.session_state.get('raw_text', '')
    raw_text = st.text_area("Paste your content", value=default_text, height=300, key="text_input")
    
    # Simple audio recording section
    st.divider()
    st.subheader("🎤 Or Record Audio")
    
    # Use Streamlit's built-in audio input (microphone button)
    audio_data = st.audio_input("Click the microphone to record", key="audio_recorder")
    
    if audio_data:
        # Show the recorded audio
        st.audio(audio_data)
        
        if st.button("📝 Transcribe Recording", type="primary", use_container_width=True):
            groq_api_key = st.session_state.get('groq_api_key', '') or os.getenv('GROQ_API_KEY', '')
            
            if not groq_api_key:
                st.error("❌ Please enter your Groq API key in the sidebar first!")
            else:
                with st.spinner("🎙️ Transcribing with Groq Whisper..."):
                    try:
                        from utils import transcribe_audio
                        
                        transcribed_text = transcribe_audio(audio_data, groq_api_key)
                        st.session_state['raw_text'] = transcribed_text
                        st.success(f"✅ Transcribed {len(transcribed_text.split())} words!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Transcription failed: {str(e)}")
    
    # Sync raw_text with session state
    if raw_text:
        st.session_state['raw_text'] = raw_text
    
    
elif input_method == "URL":
    url = st.text_input("Enter URL")
    if url:
        if st.button("Extract Content"):
            with st.spinner("Extracting from URL..."):
                try:
                    text, method = extract_from_url(url)
                    st.session_state['raw_text'] = text
                    st.session_state['extraction_method'] = method
                    st.success(f"✅ Extracted using {method}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if 'raw_text' in st.session_state and st.session_state.get('raw_text'):
            st.text_area("Extracted Text", value=st.session_state['raw_text'], height=300, disabled=True)

elif input_method == "File Upload":
    uploaded_file = st.file_uploader("Upload File", type=['pdf', 'docx', 'pptx', 'txt', 'md'])
    if uploaded_file:
        if st.button("Extract Content"):
            with st.spinner("Extracting from file..."):
                try:
                    file_bytes = uploaded_file.read()
                    google_api_key = st.session_state.get('google_api_key', '') or os.getenv('GOOGLE_API_KEY', '')
                    
                    text, method = extract_from_file(
                        file_bytes=file_bytes,
                        filename=uploaded_file.name,
                        google_api_key=google_api_key if google_api_key else None
                    )
                    st.session_state['raw_text'] = text
                    st.session_state['extraction_method'] = method
                    st.success(f"✅ Extracted using {method}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if 'raw_text' in st.session_state and st.session_state.get('raw_text'):
            st.text_area("Extracted Text", value=st.session_state['raw_text'], height=300, disabled=True)

# Store raw text
if raw_text:
    st.session_state['raw_text'] = raw_text

# --- Generation Trigger ---
st.divider()

# Show rate limit status if using app's key
if not st.session_state.get('using_own_key', False):
    remaining = MAX_FREE_REQUESTS - st.session_state.request_count
    if remaining > 0:
        st.info(f"🎁 **{remaining} free generations remaining** | Enter your own Groq API key for unlimited use!")
    else:
        st.error("⚠️ **Free limit reached!** Enter your own Groq API key in the sidebar to continue.")
        st.markdown("👉 Get a free key at [console.groq.com](https://console.groq.com)")

if st.button("Generate Content", type="primary"):
    groq_api_key = st.session_state.get('groq_api_key', '') or os.getenv('GROQ_API_KEY', '')
    
    # Check rate limit if using app's key
    using_own_key = st.session_state.get('using_own_key', False)
    if not using_own_key and st.session_state.request_count >= MAX_FREE_REQUESTS:
        st.error("🚫 You've used all your free requests!")
        st.warning("**To continue:**\n1. Go to [console.groq.com](https://console.groq.com)\n2. Create a free account\n3. Copy your API key\n4. Paste it in the sidebar")
        st.stop()
    
    if 'raw_text' not in st.session_state or not st.session_state['raw_text']:
        st.error("Please provide source content first.")
    elif not selected_platforms:
        st.error("Please select at least one platform.")
    elif not groq_api_key:
        st.error("Please enter your Groq API Key.")
    else:
        # Increment counter BEFORE generation if using app's key
        if not using_own_key:
            st.session_state.request_count += 1
        
        # Create status container for streaming updates
        status_container = st.status("🚀 Starting workflow...", expanded=True)
        
        # Platform-specific containers
        platform_containers = {}
        for platform in selected_platforms:
            platform_containers[platform] = st.empty()
        
        # Run workflow with streaming
        try:
            final_state = None
            
            for event in run_workflow(
                raw_text=st.session_state['raw_text'],
                selected_platforms=selected_platforms,
                audience=audience,
                ab_testing=st.session_state.get('ab_testing', False),
                groq_api_key=groq_api_key,
                best_posts=st.session_state.get('best_posts', '')
            ):
                event_type = event.get("type")
                message = event.get("message", "")
                
                if event_type == "status":
                    status_container.write(message)
                
                elif event_type == "core_message":
                    core = event.get("data", {})
                    status_container.write(f"✅ {message}")
                    status_container.json(core)
                
                # NEW: Phase 2 - Style analysis event
                elif event_type == "style_analyzed":
                    style = event.get("data", {})
                    status_container.write(f"🎨 {message}")
                    status_container.write("📝 **Detected Style Patterns:**")
                    status_container.json(style)
                
                elif event_type == "draft_generated":
                    status_container.write(f"✅ {message}")
                
                elif event_type == "critique_complete":
                    critique = event.get("critique", {})
                    status_icon = "✅" if critique.get("status") == "PASS" else "⚠️"
                    status_container.write(f"{status_icon} {message}")
                
                elif event_type == "revision_complete":
                    status_container.write(f"🔧 {message}")
                
                elif event_type == "validation_complete":
                    status_container.write(f"✓ {message}")
                
                elif event_type == "complete":
                    final_state = event.get("state")
                    status_container.update(label="✅ Generation Complete!", state="complete", expanded=False)
            
            # Store results
            if final_state:
                st.session_state['final_results'] = final_state
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# --- Display Results ---
if 'final_results' in st.session_state:
    results = st.session_state['final_results']
    drafts = results.get('drafts', {})
    critiques = results.get('critiques', {})
    metadata = results.get('metadata', {})
    
    st.header("Generated Content")
    
    tabs = st.tabs(selected_platforms)
    
    for i, platform in enumerate(selected_platforms):
        with tabs[i]:
            content = drafts.get(platform)
            critique = critiques.get(platform, {})
            platform_meta = metadata.get(platform, {})
            
            # Metadata Display
            if platform_meta:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    char_count = platform_meta.get('character_count', 0)
                    st.metric("Characters", f"{char_count:,}")
                
                with col2:
                    word_count = platform_meta.get('word_count', 0)
                    st.metric("Words", f"{word_count:,}")
                
                with col3:
                    hashtags = platform_meta.get('hashtags', [])
                    st.metric("Hashtags", len(hashtags))
                
                with col4:
                    compliant = platform_meta.get('platform_compliant', True)
                    st.metric("Compliance", "✅" if compliant else "⚠️")
                
                if hashtags:
                    st.caption(f"**Hashtags:** {' '.join(hashtags)}")
                
                suggestions = platform_meta.get('suggestions', [])
                if suggestions:
                    with st.expander("💡 Improvement Suggestions", expanded=False):
                        for suggestion in suggestions:
                            st.warning(suggestion)
                
                st.divider()
            
            # Quality Score
            if critique and critique.get('predicted_score'):
                score = critique.get('predicted_score')
                col1, col2 = st.columns([3, 1])
                with col2:
                    st.metric("Quality Score", f"{score}/100")
            
            # Content Display
            if isinstance(content, list):
                # A/B Variations
                st.subheader("🎯 3 Variations for A/B Testing")
                st.caption("Compare and choose the best one")
                
                for idx, variant in enumerate(content):
                    with st.expander(f"📝 Variation {idx+1}", expanded=(idx==0)):
                        st.markdown(variant)
                        st.divider()
                        if st.button(f"📋 Copy Variation {idx+1}", key=f"copy_{platform}_{idx}"):
                            st.code(variant, language="markdown")
            
            else:
                # Single Draft
                st.subheader("✨ Your Optimized Content")
                st.markdown(content)
                st.divider()
                st.caption("📋 Copy your content:")
                st.code(content, language="markdown")

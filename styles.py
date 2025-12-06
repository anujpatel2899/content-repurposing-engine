"""
Custom CSS for mobile responsiveness and better UX.
"""

def inject_custom_css():
    """Inject custom CSS for responsive design."""
    import streamlit as st
    
    st.markdown("""
    <style>
    /* Mobile-first responsive design */
    
    /* Make metrics stack on mobile */
    @media (max-width: 768px) {
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        
        /* Stack columns on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
        }
        
        /* Better button sizing */
        .stButton button {
            width: 100%;
            padding: 0.5rem 1rem;
        }
        
        /* Compact expanders */
        [data-testid="stExpander"] {
            margin-bottom: 0.5rem;
        }
    }
    
    /* Tablet adjustments */
    @media (min-width: 769px) and (max-width: 1024px) {
        [data-testid="column"] {
            min-width: 45% !important;
        }
    }
    
    /* Desktop - full width */
    @media (min-width: 1025px) {
        .main .block-container {
            max-width: 1200px;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    }
    
    /* Better code block styling */
    code {
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Compact tabs on mobile */
    @media (max-width: 768px) {
        [data-baseweb="tab-list"] {
            flex-wrap: wrap;
        }
        
        [data-baseweb="tab"] {
            font-size: 0.85rem;
            padding: 0.5rem 0.75rem;
        }
    }
    
    /* Better text area sizing */
    textarea {
        font-size: 0.9rem !important;
    }
    
    /* Improve expander headers */
    [data-testid="stExpander"] summary {
        font-weight: 600;
        padding: 0.75rem 1rem;
    }
    
    /* Better spacing */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Compact metrics */
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem;
    }
    </style>
    """, unsafe_allow_html=True)

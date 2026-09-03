"""
CSS styles for DORA Metrics Dashboard
"""
import streamlit as st


def apply_custom_styles():
    """Apply custom CSS styles to the dashboard."""
    st.markdown("""
    <style>
        .metric-card {
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f2f6;
            margin: 10px 0;
        }
        .elite {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-left: 5px solid #28a745;
            color: #155724;
        }
        .high {
            background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
            border-left: 5px solid #17a2b8;
            color: #0c5460;
        }
        .medium {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border-left: 5px solid #ffc107;
            color: #856404;
        }
        .low {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border-left: 5px solid #dc3545;
            color: #721c24;
        }
        .n\\/a {
            background: linear-gradient(135deg, #e2e3e5 0%, #d6d8db 100%);
            border-left: 5px solid #6c757d;
            color: #383d41;
        }
        .metric-card h2, .metric-card h3 {
            margin-top: 0;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

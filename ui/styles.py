"""
CSS styles for DORA Metrics Dashboard
Professional executive dashboard aesthetic
"""
import streamlit as st


def apply_custom_styles():
    """Apply custom CSS styles to the dashboard."""
    st.markdown("""
    <style>
        /* Global Typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Executive Summary Card */
        .exec-summary {
            background: linear-gradient(135deg, #1a1f36 0%, #2d3561 100%);
            border-radius: 12px;
            padding: 28px;
            color: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }

        .exec-summary h1 {
            font-size: 48px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -1px;
        }

        .exec-summary .subtitle {
            font-size: 16px;
            opacity: 0.8;
            margin-top: 4px;
        }

        .exec-summary .score {
            font-size: 18px;
            opacity: 0.9;
            margin-top: 12px;
            font-weight: 500;
        }

        /* Metric Cards - Professional */
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 8px 0;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        .metric-card h2, .metric-card h3 {
            margin: 0 0 8px 0;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-card p {
            margin: 4px 0;
            font-size: 14px;
            line-height: 1.5;
        }

        /* Status Badges - Cleaner Design */
        .elite {
            background: #ecfdf5;
            border-left: 4px solid #10b981;
            color: #065f46;
        }

        .elite h3 {
            color: #10b981;
        }

        .high {
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
            color: #1e40af;
        }

        .high h3 {
            color: #3b82f6;
        }

        .medium {
            background: #fefce8;
            border-left: 4px solid #eab308;
            color: #854d0e;
        }

        .medium h3 {
            color: #ca8a04;
        }

        .low {
            background: #fef2f2;
            border-left: 4px solid #ef4444;
            color: #991b1b;
        }

        .low h3 {
            color: #ef4444;
        }

        .n\\/a {
            background: #f9fafb;
            border-left: 4px solid #9ca3af;
            color: #4b5563;
        }

        .n\\/a h3 {
            color: #6b7280;
        }

        /* Compact Summary Bar */
        .summary-bar {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px 24px;
            margin: 16px 0;
            display: flex;
            justify-content: space-between;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        .summary-metric {
            text-align: center;
            padding: 0 16px;
        }

        .summary-metric .label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #6b7280;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .summary-metric .value {
            font-size: 24px;
            font-weight: 700;
            color: #111827;
        }

        .summary-metric .level {
            font-size: 12px;
            font-weight: 600;
            margin-top: 2px;
        }

        /* Trend Indicators */
        .trend-up {
            color: #10b981;
            font-weight: 600;
        }

        .trend-down {
            color: #ef4444;
            font-weight: 600;
        }

        .trend-neutral {
            color: #6b7280;
            font-weight: 600;
        }

        /* Remove excessive padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Cleaner headings */
        h1, h2, h3 {
            font-weight: 600;
            letter-spacing: -0.5px;
        }
    </style>
    """, unsafe_allow_html=True)

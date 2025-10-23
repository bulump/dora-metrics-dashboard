"""
DORA Metrics Dashboard - Streamlit Application
Interactive dashboard for tracking DevOps performance metrics.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv

from github_data_fetcher import GitHubDataFetcher
from dora_calculator import DORACalculator
from ai_insights import AIInsightsGenerator

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="DORA Metrics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .elite { background-color: #d4edda; border-left: 5px solid #28a745; }
    .high { background-color: #d1ecf1; border-left: 5px solid #17a2b8; }
    .medium { background-color: #fff3cd; border-left: 5px solid #ffc107; }
    .low { background-color: #f8d7da; border-left: 5px solid #dc3545; }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function."""
    st.title("📊 DORA Metrics Dashboard")
    st.markdown("**DevOps Research and Assessment Metrics for Software Delivery Performance**")

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")

        repo_name = st.text_input(
            "GitHub Repository",
            value="bulump/dora-metrics-dashboard",
            help="Enter repository in format: owner/repo"
        )

        days_back = st.slider(
            "Analysis Period (days)",
            min_value=7,
            max_value=90,
            value=30,
            help="Number of days to analyze"
        )

        enable_ai = st.checkbox(
            "Enable AI Insights",
            value=True,
            help="Generate AI-powered recommendations (requires ANTHROPIC_API_KEY)"
        )

        fetch_button = st.button("Fetch & Analyze", type="primary", use_container_width=True)

        st.divider()
        st.caption("Built with Claude AI")

    # Initialize session state
    if 'metrics_data' not in st.session_state:
        st.session_state['metrics_data'] = None

    # Fetch data
    if fetch_button:
        with st.spinner("Fetching data from GitHub..."):
            try:
                fetcher = GitHubDataFetcher()
                data = fetcher.fetch_all_data(repo_name, days_back)
                repo_stats = fetcher.get_repository_stats(repo_name)

                st.session_state['raw_data'] = data
                st.session_state['repo_stats'] = repo_stats

                # Calculate DORA metrics
                calculator = DORACalculator()
                metrics = calculator.calculate_all_metrics(
                    deployments=data['deployments'],
                    pull_requests=data['pull_requests'],
                    incidents=data['incidents'],
                    days_back=days_back
                )

                # Get overall performance
                overall = calculator.get_overall_performance_level(metrics)
                metrics['overall'] = overall

                st.session_state['metrics_data'] = metrics

                # Generate AI insights if enabled
                if enable_ai:
                    with st.spinner("Generating AI insights..."):
                        try:
                            ai_gen = AIInsightsGenerator()
                            insights = ai_gen.generate_insights(metrics, repo_stats)
                            st.session_state['ai_insights'] = insights
                        except Exception as e:
                            st.warning(f"Could not generate AI insights: {e}")
                            st.session_state['ai_insights'] = None

                st.success("✅ Data fetched and analyzed successfully!")

            except Exception as e:
                st.error(f"Error fetching data: {e}")
                st.info("Make sure GITHUB_TOKEN is set in your .env file")
                return

    # Display dashboard
    if st.session_state['metrics_data']:
        metrics = st.session_state['metrics_data']
        repo_stats = st.session_state.get('repo_stats', {})

        # Repository header
        st.markdown(f"### {repo_stats.get('full_name', repo_name)}")
        st.caption(repo_stats.get('description', ''))

        # Overall performance
        st.markdown("## Overall DORA Performance")
        overall = metrics['overall']

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            level_class = overall['overall_level'].lower()
            st.markdown(f"""
            <div class="metric-card {level_class}">
                <h2>{overall['overall_level']} Performance</h2>
                <p>{overall['description']}</p>
                <p><strong>Score:</strong> {overall['score']}/4.0</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.metric("Analysis Period", f"{metrics['period_days']} days")
            st.metric("Total Deployments", metrics['data_summary']['total_deployments'])

        with col3:
            st.metric("Total PRs", metrics['data_summary']['total_prs'])
            st.metric("Total Incidents", metrics['data_summary']['total_incidents'])

        st.divider()

        # Four key metrics
        st.markdown("## Four Key Metrics")

        # Create tabs for each metric
        tab1, tab2, tab3, tab4 = st.tabs([
            "🚀 Deployment Frequency",
            "⏱️ Lead Time for Changes",
            "🔧 Mean Time to Restore",
            "❌ Change Failure Rate"
        ])

        with tab1:
            display_deployment_frequency(metrics['deployment_frequency'])

        with tab2:
            display_lead_time(metrics['lead_time_for_changes'])

        with tab3:
            display_mttr(metrics['mean_time_to_restore'])

        with tab4:
            display_change_failure_rate(metrics['change_failure_rate'])

        st.divider()

        # DORA levels comparison chart
        st.markdown("## Metrics Overview")
        display_metrics_radar_chart(metrics)

        st.divider()

        # AI Insights
        if st.session_state.get('ai_insights'):
            display_ai_insights(st.session_state['ai_insights'])

    else:
        # Welcome message
        st.info("👆 Enter a repository name and click 'Fetch & Analyze' to get started")

        st.markdown("""
        ### What are DORA Metrics?

        DORA (DevOps Research and Assessment) metrics are four key indicators of software delivery performance:

        **1. Deployment Frequency** 🚀
        - How often you deploy to production
        - Elite: Multiple times per day

        **2. Lead Time for Changes** ⏱️
        - Time from commit to production
        - Elite: Less than one hour

        **3. Mean Time to Restore (MTTR)** 🔧
        - How quickly you recover from failures
        - Elite: Less than one hour

        **4. Change Failure Rate** ❌
        - Percentage of deployments causing failures
        - Elite: 0-15%

        ### Performance Levels
        - **Elite**: Top performers (Google, Amazon, Netflix)
        - **High**: High performers
        - **Medium**: Medium performers
        - **Low**: Low performers (needs improvement)
        """)


def display_deployment_frequency(metric: dict):
    """Display deployment frequency metric."""
    level_class = metric['level'].lower()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"""
        <div class="metric-card {level_class}">
            <h3>{metric['level']} Performance</h3>
            <p>{metric['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.metric("Deployments per Day", metric['deploys_per_day'])
        st.metric("Deployments per Week", metric['deploys_per_week'])
        st.metric("Total Deployments", metric['total_deployments'])

    with col2:
        # DORA levels reference
        st.markdown("""
        **DORA Levels:**
        - 🟢 Elite: Multiple deploys/day
        - 🔵 High: Weekly to daily
        - 🟡 Medium: Monthly to weekly
        - 🔴 Low: Less than monthly
        """)


def display_lead_time(metric: dict):
    """Display lead time metric."""
    level_class = metric['level'].lower()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"""
        <div class="metric-card {level_class}">
            <h3>{metric['level']} Performance</h3>
            <p>{metric['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.metric("Median Lead Time", f"{metric['median_hours']:.1f} hours")
        st.metric("Mean Lead Time", f"{metric['mean_hours']:.1f} hours")
        st.metric("P95 Lead Time", f"{metric['p95_hours']:.1f} hours")

    with col2:
        st.markdown("""
        **DORA Levels:**
        - 🟢 Elite: < 1 hour
        - 🔵 High: 1 day to 1 week
        - 🟡 Medium: 1 week to 1 month
        - 🔴 Low: > 1 month
        """)


def display_mttr(metric: dict):
    """Display MTTR metric."""
    level_class = metric['level'].lower()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"""
        <div class="metric-card {level_class}">
            <h3>{metric['level']} Performance</h3>
            <p>{metric['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        if metric['total_incidents'] > 0:
            st.metric("Median MTTR", f"{metric['median_hours']:.1f} hours")
            st.metric("Mean MTTR", f"{metric['mean_hours']:.1f} hours")
        else:
            st.success("🎉 No incidents in period!")

        st.metric("Total Incidents", metric['total_incidents'])

    with col2:
        st.markdown("""
        **DORA Levels:**
        - 🟢 Elite: < 1 hour
        - 🔵 High: < 1 day
        - 🟡 Medium: 1 day to 1 week
        - 🔴 Low: > 1 week
        """)


def display_change_failure_rate(metric: dict):
    """Display change failure rate metric."""
    level_class = metric['level'].lower()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"""
        <div class="metric-card {level_class}">
            <h3>{metric['level']} Performance</h3>
            <p>{metric['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.metric("Failure Rate", f"{metric['failure_rate_pct']:.1f}%")
        st.metric("Failed Deployments", f"{metric['failed_deployments']} / {metric['total_deployments']}")

    with col2:
        st.markdown("""
        **DORA Levels:**
        - 🟢 Elite: 0-15%
        - 🔵 High: 16-30%
        - 🟡 Medium: 31-45%
        - 🔴 Low: 46-100%
        """)


def display_metrics_radar_chart(metrics: dict):
    """Display radar chart comparing all metrics."""
    level_scores = {
        'Elite': 4,
        'High': 3,
        'Medium': 2,
        'Low': 1
    }

    categories = [
        'Deployment<br>Frequency',
        'Lead Time for<br>Changes',
        'Mean Time to<br>Restore',
        'Change Failure<br>Rate'
    ]

    values = [
        level_scores[metrics['deployment_frequency']['level']],
        level_scores[metrics['lead_time_for_changes']['level']],
        level_scores[metrics['mean_time_to_restore']['level']],
        level_scores[metrics['change_failure_rate']['level']]
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Current Performance',
        marker=dict(color='#1f77b4')
    ))

    # Add target (Elite) line
    fig.add_trace(go.Scatterpolar(
        r=[4, 4, 4, 4],
        theta=categories,
        fill='toself',
        name='Elite Performance',
        marker=dict(color='#2ca02c'),
        opacity=0.3
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4],
                ticktext=['', 'Low', 'Medium', 'High', 'Elite'],
                tickvals=[0, 1, 2, 3, 4]
            )
        ),
        showlegend=True,
        title="DORA Metrics Performance Radar"
    )

    st.plotly_chart(fig, use_container_width=True)


def display_ai_insights(insights: dict):
    """Display AI-generated insights."""
    if not insights.get('success'):
        st.warning("AI insights unavailable. Check your ANTHROPIC_API_KEY.")
        return

    st.markdown("## 🤖 AI-Powered Insights")

    st.markdown(insights['insights'])

    # Metrics summary
    with st.expander("📊 Metrics Summary"):
        summary = insights['metrics_summary']
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Deployment Frequency", summary['deployment_frequency'])
        with col2:
            st.metric("Lead Time", summary['lead_time'])
        with col3:
            st.metric("MTTR", summary['mttr'])
        with col4:
            st.metric("Change Failure Rate", summary['change_failure_rate'])


if __name__ == "__main__":
    main()

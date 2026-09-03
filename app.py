"""
DORA Metrics Dashboard - Streamlit Application
Interactive dashboard for tracking DevOps performance metrics.
"""
import streamlit as st
from dotenv import load_dotenv

from github_data_fetcher import GitHubDataFetcher
from dora_calculator import DORACalculator
from ai_insights import AIInsightsGenerator

# UI Components
from ui.styles import apply_custom_styles
from ui.metrics_display import (
    display_deployment_frequency,
    display_lead_time,
    display_mttr,
    display_change_failure_rate
)
from ui.charts import (
    display_metrics_radar_chart,
    display_deployment_timeline,
    display_lead_time_distribution,
    display_success_failure_chart
)
from ui.data_tables import (
    display_failed_deployments,
    display_process_compliance,
    display_data_quality,
    check_direct_commits
)
from ui.insights import (
    display_ai_insights,
    display_performance_summary,
    display_metric_context
)

# Load environment variables - override existing env vars
load_dotenv(override=True)

# Page configuration
st.set_page_config(
    page_title="DORA Metrics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_styles()


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
            value=False,
            help="Generate AI-powered recommendations (requires ANTHROPIC_API_KEY)"
        )

        use_demo_data = st.checkbox(
            "Use Demo Data",
            value=False,
            help="Use sample data for demonstration (bypasses GitHub API - useful for rate limits)"
        )

        fetch_button = st.button("Fetch & Analyze", type="primary", use_container_width=True)

        st.divider()
        st.caption("Built by Chris Bielinski")
        st.caption("Python · GitHub API · Streamlit · Claude AI")

    # Initialize session state
    if 'metrics_data' not in st.session_state:
        st.session_state['metrics_data'] = None

    # Fetch data
    if fetch_button:
        if use_demo_data:
            # Load sample data for demonstration
            with st.spinner("Loading demo data..."):
                try:
                    import json
                    with open('sample_dora_data.json', 'r') as f:
                        data = json.load(f)

                    repo_stats = {
                        'name': 'demo-project',
                        'full_name': 'example/demo-project',
                        'description': 'Sample DORA metrics demonstration',
                        'stars': 0,
                        'forks': 0,
                        'open_issues': 0,
                        'default_branch': 'main',
                        'language': 'Python'
                    }

                    st.info("📊 Using demo data - showcasing Elite-level DORA performance")

                except Exception as e:
                    st.error(f"Error loading demo data: {e}")
                    st.stop()
        else:
            # Fetch from GitHub
            with st.spinner("Fetching data from GitHub..."):
                try:
                    fetcher = GitHubDataFetcher()
                    data = fetcher.fetch_all_data(repo_name, days_back)
                    repo_stats = fetcher.get_repository_stats(repo_name)
                except Exception as e:
                    st.error(f"Error fetching data: {e}")
                    st.info("Make sure GITHUB_TOKEN is set in your .env file")
                    st.stop()

        # Store data in session state (works for both demo and real data)
        try:
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
            st.error(f"Error processing data: {e}")
            st.stop()

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

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            level_class = overall['overall_level'].lower().replace('/', r'\/')
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

        with col4:
            st.markdown("**Efficiency:**")
            if metrics['data_summary']['total_deployments'] > 0:
                avg_prs_per_deploy = metrics['data_summary']['total_prs'] / metrics['data_summary']['total_deployments']
                st.metric("PRs/Deploy", f"{avg_prs_per_deploy:.1f}")

                # Velocity: deployments per week
                velocity = (metrics['data_summary']['total_deployments'] / metrics['period_days']) * 7
                st.metric("Velocity", f"{velocity:.1f}/wk")

                # Check for direct commits (deployments without PRs)
                if st.session_state.get('raw_data'):
                    direct_commits = check_direct_commits(
                        st.session_state['raw_data']['deployments'],
                        st.session_state['raw_data']['pull_requests']
                    )
                    if direct_commits['count'] > 0:
                        st.metric(
                            "⚠️ Direct Commits",
                            direct_commits['count'],
                            delta=f"-{direct_commits['percentage']:.0f}% bypass PR",
                            delta_color="inverse"
                        )

        st.divider()

        # Data Quality & Provenance
        if st.session_state.get('raw_data'):
            display_data_quality(st.session_state['raw_data'], metrics)

        st.divider()

        # Key metrics
        st.markdown("## Key Metrics")

        # Create tabs for each metric
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🚀 Deployment Frequency",
            "⏱️ Lead Time for Changes",
            "🔧 Mean Time to Restore",
            "❌ Change Failure Rate",
            "🔍 Process Compliance"
        ])

        with tab1:
            display_deployment_frequency(metrics['deployment_frequency'])

            # Add trend chart
            if st.session_state.get('raw_data'):
                st.markdown("#### 📈 Deployment Timeline")
                display_deployment_timeline(st.session_state['raw_data']['deployments'])

            # Context and insights
            display_metric_context('deployment_frequency')

        with tab2:
            display_lead_time(metrics['lead_time_for_changes'])

            # Add distribution chart
            if st.session_state.get('raw_data'):
                st.markdown("#### 📊 Lead Time Distribution")
                display_lead_time_distribution(st.session_state['raw_data']['pull_requests'])

            # Context and insights
            display_metric_context('lead_time')

        with tab3:
            display_mttr(metrics['mean_time_to_restore'])

            # Context and insights
            display_metric_context('mttr')

        with tab4:
            display_change_failure_rate(metrics['change_failure_rate'])

            # Add success/failure pie chart
            st.markdown("#### 🎯 Deployment Success Rate")
            display_success_failure_chart(metrics['change_failure_rate'])

            # Add failed deployments table
            if st.session_state.get('raw_data'):
                st.markdown("#### ❌ Failed Deployments")
                display_failed_deployments(
                    st.session_state['raw_data']['deployments'],
                    st.session_state['raw_data']['pull_requests']
                )

            # Context and insights
            display_metric_context('change_failure_rate')

        with tab5:
            st.markdown("### 🔍 Process Compliance & Code Quality")

            if st.session_state.get('raw_data'):
                display_process_compliance(
                    st.session_state['raw_data']['deployments'],
                    st.session_state['raw_data']['pull_requests']
                )
            else:
                st.info("No data available for process compliance analysis")

            # Context and insights
            display_metric_context('process_compliance')

        st.divider()

        # Performance Summary
        display_performance_summary(metrics)

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


if __name__ == "__main__":
    main()

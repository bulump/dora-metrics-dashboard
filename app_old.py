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

# Load environment variables - override existing env vars
load_dotenv(override=True)

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
    .n\/a {
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
            st.markdown("---")
            st.markdown("### 📊 Context & Insights")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**What This Means:**")
                st.markdown("""
                - Higher deployment frequency = faster feedback loops
                - Elite teams deploy on-demand (multiple times per day)
                - Requires strong CI/CD automation and testing
                """)
            with col_b:
                st.markdown("**How to Improve:**")
                st.markdown("""
                - Automate deployment pipelines
                - Reduce batch sizes (deploy smaller changes)
                - Implement feature flags for safer releases
                - Improve automated testing coverage
                """)

        with tab2:
            display_lead_time(metrics['lead_time_for_changes'])

            # Add distribution chart
            if st.session_state.get('raw_data'):
                st.markdown("#### 📊 Lead Time Distribution")
                display_lead_time_distribution(st.session_state['raw_data']['pull_requests'])

            # Context and insights
            st.markdown("---")
            st.markdown("### 📊 Context & Insights")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**What This Means:**")
                st.markdown("""
                - Time from code commit to running in production
                - Lower lead time = faster value delivery
                - Elite teams achieve < 1 hour lead time
                - Key indicator of development velocity
                """)
            with col_b:
                st.markdown("**How to Improve:**")
                st.markdown("""
                - Streamline code review process
                - Automate testing and CI/CD
                - Reduce PR size and complexity
                - Minimize manual approval steps
                - Parallelize build and test stages
                """)

        with tab3:
            display_mttr(metrics['mean_time_to_restore'])

            # Context and insights
            st.markdown("---")
            st.markdown("### 📊 Context & Insights")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**What This Means:**")
                st.markdown("""
                - How quickly you recover from failures
                - Elite teams restore in < 1 hour
                - Measures resilience and incident response
                - Lower MTTR = better reliability
                """)
            with col_b:
                st.markdown("**How to Improve:**")
                st.markdown("""
                - Implement comprehensive monitoring/alerts
                - Practice incident response (game days)
                - Automate rollback procedures
                - Build better observability (logs, metrics, traces)
                - Create runbooks for common issues
                """)

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
            st.markdown("---")
            st.markdown("### 📊 Context & Insights")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**What This Means:**")
                st.markdown("""
                - Percentage of deployments causing failures
                - Elite teams maintain < 15% failure rate
                - Balances speed with quality
                - Lower rate = higher release confidence
                """)
            with col_b:
                st.markdown("**How to Improve:**")
                st.markdown("""
                - Increase test coverage (unit, integration, e2e)
                - Implement progressive rollouts (canary/blue-green)
                - Add pre-deployment validation checks
                - Use staging environments effectively
                - Conduct thorough code reviews
                """)

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
            st.markdown("---")
            st.markdown("### 📊 Context & Insights")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**What This Means:**")
                st.markdown("""
                - Direct commits bypass code review process
                - Higher direct commit rate = higher risk
                - Elite teams enforce PR-based workflows
                - Process compliance ensures code quality
                """)
            with col_b:
                st.markdown("**How to Improve:**")
                st.markdown("""
                - Enable branch protection rules
                - Require PR reviews before merge
                - Use CI/CD checks on all branches
                - Educate team on PR best practices
                - Monitor and audit direct commits
                """)

        st.divider()

        # Performance Summary
        st.markdown("## Performance Summary")

        sum_col1, sum_col2, sum_col3 = st.columns(3)

        with sum_col1:
            st.markdown("### 🎯 Key Strengths")
            strengths = []
            if metrics['deployment_frequency']['level'] in ['Elite', 'High']:
                strengths.append(f"✅ **{metrics['deployment_frequency']['level']} Deployment Frequency** - Deploying {metrics['deployment_frequency']['deploys_per_week']:.1f}x per week")
            if metrics['lead_time_for_changes']['level'] in ['Elite', 'High']:
                strengths.append(f"✅ **{metrics['lead_time_for_changes']['level']} Lead Time** - Median {metrics['lead_time_for_changes']['median_hours']:.1f}h")
            if metrics['mean_time_to_restore']['level'] in ['Elite', 'High']:
                strengths.append(f"✅ **{metrics['mean_time_to_restore']['level']} MTTR** - Recovering in {metrics['mean_time_to_restore']['median_hours']:.1f}h")
            if metrics['change_failure_rate']['level'] in ['Elite', 'High']:
                strengths.append(f"✅ **{metrics['change_failure_rate']['level']} Failure Rate** - Only {metrics['change_failure_rate']['failure_rate_pct']:.1f}% failures")

            if strengths:
                for strength in strengths:
                    st.markdown(strength)
            else:
                st.info("Focus on the improvement areas below to build strengths")

        with sum_col2:
            st.markdown("### ⚠️ Areas to Improve")
            improvements = []
            if metrics['deployment_frequency']['level'] in ['Low', 'Medium']:
                improvements.append(f"🔸 **Deployment Frequency** - Currently {metrics['deployment_frequency']['level']}")
            if metrics['lead_time_for_changes']['level'] in ['Low', 'Medium']:
                improvements.append(f"🔸 **Lead Time** - Median {metrics['lead_time_for_changes']['median_hours']:.1f}h")
            if metrics['mean_time_to_restore']['level'] in ['Low', 'Medium'] and metrics['mean_time_to_restore']['total_incidents'] > 0:
                improvements.append(f"🔸 **MTTR** - {metrics['mean_time_to_restore']['median_hours']:.1f}h recovery time")
            if metrics['change_failure_rate']['level'] in ['Low', 'Medium']:
                improvements.append(f"🔸 **Failure Rate** - {metrics['change_failure_rate']['failure_rate_pct']:.1f}% needs reduction")

            if improvements:
                for improvement in improvements:
                    st.markdown(improvement)
            else:
                st.success("🎉 All metrics performing well!")

        with sum_col3:
            st.markdown("### 📈 Next Steps")
            # Provide targeted recommendations based on lowest performing metric
            metric_scores = {
                'Deployment Frequency': {'level': metrics['deployment_frequency']['level'], 'score': {'Elite': 4, 'High': 3, 'Medium': 2, 'Low': 1}[metrics['deployment_frequency']['level']]},
                'Lead Time': {'level': metrics['lead_time_for_changes']['level'], 'score': {'Elite': 4, 'High': 3, 'Medium': 2, 'Low': 1}[metrics['lead_time_for_changes']['level']]},
                'MTTR': {'level': metrics['mean_time_to_restore']['level'], 'score': {'Elite': 4, 'High': 3, 'Medium': 2, 'Low': 1}[metrics['mean_time_to_restore']['level']]},
                'Failure Rate': {'level': metrics['change_failure_rate']['level'], 'score': {'Elite': 4, 'High': 3, 'Medium': 2, 'Low': 1}[metrics['change_failure_rate']['level']]}
            }

            lowest = min(metric_scores.items(), key=lambda x: x[1]['score'])

            st.markdown(f"**Priority: Improve {lowest[0]}**")

            recommendations = {
                'Deployment Frequency': "1. Automate your deployment pipeline\n2. Deploy smaller batches more frequently\n3. Implement trunk-based development",
                'Lead Time': "1. Reduce PR review time\n2. Automate testing\n3. Break down large features",
                'MTTR': "1. Improve monitoring and alerting\n2. Practice incident response\n3. Automate rollbacks",
                'Failure Rate': "1. Increase test coverage\n2. Implement progressive rollouts\n3. Strengthen code review"
            }

            st.markdown(recommendations.get(lowest[0], "Keep up the good work!"))

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
    level_class = metric['level'].lower().replace('/', r'\/')

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"""
        <div class="metric-card {level_class}">
            <h3>{metric['level']} Performance</h3>
            <p>{metric['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Main metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Per Day", f"{metric['deploys_per_day']:.1f}")
        with m2:
            st.metric("Per Week", f"{metric['deploys_per_week']:.1f}")
        with m3:
            st.metric("Total (30d)", metric['total_deployments'])

    with col2:
        st.markdown("**DORA Benchmarks:**")
        st.markdown("""
        - 🟢 Elite: Multiple/day
        - 🔵 High: Daily to weekly
        - 🟡 Medium: Weekly to monthly
        - 🔴 Low: < Monthly
        """)

    with col3:
        st.markdown("**Quick Stats:**")
        days_with_deploys = metric.get('days_with_deployments', 0)
        if metric['total_deployments'] > 0:
            st.metric("Active Days", f"{days_with_deploys}/30")
            avg_per_active = metric['total_deployments'] / max(days_with_deploys, 1)
            st.metric("Avg/Active Day", f"{avg_per_active:.1f}")

            # Progress bar to Elite level
            st.markdown("**Progress to Elite:**")
            # Elite = 1 deploy/day, show progress
            progress = min(100, int((metric['deploys_per_day'] / 1.0) * 100))
            st.progress(progress / 100)
            st.caption(f"{progress}% to Elite")


def display_lead_time(metric: dict):
    """Display lead time metric."""
    level_class = metric['level'].lower().replace('/', r'\/')

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"""
        <div class="metric-card {level_class}">
            <h3>{metric['level']} Performance</h3>
            <p>{metric['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Main metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Median", f"{metric['median_hours']:.1f}h")
        with m2:
            st.metric("Mean", f"{metric['mean_hours']:.1f}h")
        with m3:
            st.metric("P95", f"{metric['p95_hours']:.1f}h")

    with col2:
        st.markdown("**DORA Benchmarks:**")
        st.markdown("""
        - 🟢 Elite: < 1 hour
        - 🔵 High: 1 day to 1 week
        - 🟡 Medium: 1-4 weeks
        - 🔴 Low: > 1 month
        """)

    with col3:
        st.markdown("**Distribution:**")
        # Convert hours to days for easier reading
        if metric['median_hours'] < 24:
            st.metric("Median", f"{metric['median_hours']:.1f}h")
        else:
            st.metric("Median", f"{metric['median_hours']/24:.1f}d")

        if metric['p95_hours'] < 24:
            st.metric("P95", f"{metric['p95_hours']:.1f}h")
        else:
            st.metric("P95", f"{metric['p95_hours']/24:.1f}d")

        # Progress bar to Elite level
        st.markdown("**Progress to Elite:**")
        # Elite = < 1 hour
        progress = max(0, min(100, int((1 - metric['median_hours']) / 1 * 100)))
        if metric['median_hours'] <= 1:
            progress = 100
        elif metric['median_hours'] < 24:
            progress = int((24 - metric['median_hours']) / 24 * 100)
        else:
            progress = 10
        st.progress(progress / 100)
        st.caption(f"{progress}% to Elite")


def display_mttr(metric: dict):
    """Display MTTR metric."""
    level_class = metric['level'].lower().replace('/', r'\/')

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"""
        <div class="metric-card {level_class}">
            <h3>{metric['level']} Performance</h3>
            <p>{metric['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        if metric['total_incidents'] > 0:
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Median MTTR", f"{metric['median_hours']:.1f}h")
            with m2:
                st.metric("Mean MTTR", f"{metric['mean_hours']:.1f}h")
            with m3:
                st.metric("Total Incidents", metric['total_incidents'])
        else:
            st.success("🎉 No incidents in this period!")

    with col2:
        st.markdown("**DORA Benchmarks:**")
        st.markdown("""
        - 🟢 Elite: < 1 hour
        - 🔵 High: < 1 day
        - 🟡 Medium: 1 day to 1 week
        - 🔴 Low: > 1 week
        """)

    with col3:
        st.markdown("**Incident Stats:**")
        if metric['total_incidents'] > 0:
            # Calculate incidents per week
            incidents_per_week = (metric['total_incidents'] / 30) * 7
            st.metric("Per Week", f"{incidents_per_week:.1f}")

            # Show max MTTR if available
            if 'max_hours' in metric:
                st.metric("Longest", f"{metric['max_hours']:.1f}h")
        else:
            st.metric("Per Week", "0.0")
            st.metric("Status", "✅ Stable")


def display_change_failure_rate(metric: dict):
    """Display change failure rate metric."""
    level_class = metric['level'].lower().replace('/', r'\/')

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"""
        <div class="metric-card {level_class}">
            <h3>{metric['level']} Performance</h3>
            <p>{metric['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Failure Rate", f"{metric['failure_rate_pct']:.1f}%")
        with m2:
            st.metric("Failed", metric['failed_deployments'])
        with m3:
            st.metric("Successful", metric['total_deployments'] - metric['failed_deployments'])

    with col2:
        st.markdown("**DORA Benchmarks:**")
        st.markdown("""
        - 🟢 Elite: 0-15%
        - 🔵 High: 16-30%
        - 🟡 Medium: 31-45%
        - 🔴 Low: 46-100%
        """)

    with col3:
        st.markdown("**Reliability:**")
        success_rate = 100 - metric['failure_rate_pct']
        st.metric("Success Rate", f"{success_rate:.1f}%")

        # Show gap to elite
        gap_to_elite = max(0, metric['failure_rate_pct'] - 15)
        if gap_to_elite > 0:
            st.metric("Gap to Elite", f"-{gap_to_elite:.1f}%", delta_color="inverse")
        else:
            st.metric("Status", "✅ Elite")

        # Progress bar (inverse - lower is better)
        st.markdown("**Quality Progress:**")
        if metric['failure_rate_pct'] <= 15:
            progress = 100
        elif metric['failure_rate_pct'] < 100:
            progress = int((100 - metric['failure_rate_pct']) / 85 * 100)
        else:
            progress = 0
        st.progress(progress / 100)
        st.caption(f"{progress}% quality goal")


def display_metrics_radar_chart(metrics: dict):
    """Display radar chart comparing all metrics."""
    level_scores = {
        'Elite': 4,
        'High': 3,
        'Medium': 2,
        'Low': 1,
        'N/A': 0  # Show N/A as 0 on radar
    }

    categories = [
        'Deployment<br>Frequency',
        'Lead Time for<br>Changes',
        'Mean Time to<br>Restore',
        'Change Failure<br>Rate'
    ]

    values = [
        level_scores.get(metrics['deployment_frequency']['level'], 0),
        level_scores.get(metrics['lead_time_for_changes']['level'], 0),
        level_scores.get(metrics['mean_time_to_restore']['level'], 0),
        level_scores.get(metrics['change_failure_rate']['level'], 0)
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


def display_deployment_timeline(deployments):
    """Display deployment timeline chart with success/failure breakdown."""
    if not deployments:
        st.info("No deployment data available")
        return

    # Parse dates and count deployments per day (success vs failure)
    from collections import defaultdict
    from datetime import datetime

    daily_success = defaultdict(int)
    daily_failure = defaultdict(int)

    for deploy in deployments:
        deploy_date = datetime.fromisoformat(deploy['deployed_at'].replace('Z', '+00:00')).date()
        if deploy.get('status') == 'failure':
            daily_failure[deploy_date] += 1
        else:
            daily_success[deploy_date] += 1

    # Get all dates
    all_dates = sorted(set(list(daily_success.keys()) + list(daily_failure.keys())))
    dates = [str(d) for d in all_dates]
    success_counts = [daily_success[d] for d in all_dates]
    failure_counts = [daily_failure[d] for d in all_dates]

    # Create stacked bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=dates,
        y=success_counts,
        marker_color='#28a745',
        name='Successful',
        hovertemplate='<b>%{x}</b><br>Successful: %{y}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=dates,
        y=failure_counts,
        marker_color='#dc3545',
        name='Failed',
        hovertemplate='<b>%{x}</b><br>Failed: %{y}<extra></extra>'
    ))

    fig.update_layout(
        barmode='stack',
        xaxis_title="Date",
        yaxis_title="Deployments",
        height=300,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def display_lead_time_distribution(pull_requests):
    """Display lead time distribution histogram."""
    if not pull_requests:
        st.info("No PR data available")
        return

    from datetime import datetime

    lead_times = []
    for pr in pull_requests:
        if pr.get('created_at') and pr.get('merged_at'):
            created = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
            merged = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
            hours = (merged - created).total_seconds() / 3600
            lead_times.append(hours)

    if not lead_times:
        st.info("No lead time data available")
        return

    # Create histogram
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=lead_times,
        nbinsx=20,
        marker_color='#28a745',
        name='Lead Time'
    ))

    fig.update_layout(
        xaxis_title="Lead Time (hours)",
        yaxis_title="Number of PRs",
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def display_success_failure_chart(metric):
    """Display success/failure pie chart."""
    successful = metric['total_deployments'] - metric['failed_deployments']
    failed = metric['failed_deployments']

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=['Successful', 'Failed'],
        values=[successful, failed],
        marker_colors=['#28a745', '#dc3545'],
        hole=0.4,
        textinfo='label+percent+value',
        texttemplate='<b>%{label}</b><br>%{value} (%{percent})'
    ))

    fig.update_layout(
        height=300,
        showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def display_failed_deployments(deployments, pull_requests):
    """Display table of failed deployments with PR titles."""
    from datetime import datetime
    import pandas as pd

    # Filter for failed deployments
    failed = [d for d in deployments if d.get('status') == 'failure']

    if not failed:
        st.success("🎉 No failed deployments in this period!")
        return

    # Create SHA to PR mapping for quick lookup
    sha_to_pr = {}
    for pr in pull_requests:
        if pr.get('merge_commit_sha'):
            sha_to_pr[pr['merge_commit_sha']] = pr.get('title', 'N/A')
        if pr.get('sha'):
            sha_to_pr[pr['sha']] = pr.get('title', 'N/A')

    # Create DataFrame
    data = []
    for deploy in failed:
        deploy_time = datetime.fromisoformat(deploy['deployed_at'].replace('Z', '+00:00'))
        deploy_sha = deploy.get('sha', 'N/A')

        # Try to find matching PR title
        pr_title = sha_to_pr.get(deploy_sha, 'Direct commit (no PR)')

        # If it came from an inferred PR source, we can use the PR title from the deployment
        if deploy.get('source') == 'inferred_from_pr' and deploy.get('pr_title'):
            pr_title = deploy['pr_title']

        data.append({
            'Date': deploy_time.strftime('%Y-%m-%d'),
            'Time': deploy_time.strftime('%H:%M:%S'),
            'PR Title': pr_title,
            'Environment': deploy.get('environment', 'N/A'),
            'Deployer': deploy.get('creator', 'Unknown'),
            'SHA': deploy_sha[:8] if deploy_sha != 'N/A' else 'N/A',  # Short SHA
            'Source': deploy.get('source', 'N/A')
        })

    df = pd.DataFrame(data)

    # Sort by date/time descending
    df = df.sort_values(['Date', 'Time'], ascending=False)

    # Display count
    st.caption(f"Found {len(failed)} failed deployment(s)")

    # Display table with custom styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Date': st.column_config.TextColumn('📅 Date', width='small'),
            'Time': st.column_config.TextColumn('🕐 Time', width='small'),
            'PR Title': st.column_config.TextColumn('📝 PR Title', width='large'),
            'Environment': st.column_config.TextColumn('🌍 Environment', width='small'),
            'Deployer': st.column_config.TextColumn('👤 Deployer', width='small'),
            'SHA': st.column_config.TextColumn('🔗 Commit', width='small'),
            'Source': st.column_config.TextColumn('📦 Source', width='small')
        }
    )


def check_direct_commits(deployments, pull_requests):
    """Check for deployments that didn't go through PR process."""
    # Get all PR SHAs
    pr_shas = set()
    for pr in pull_requests:
        if pr.get('merge_commit_sha'):
            pr_shas.add(pr['merge_commit_sha'])
        # Also check the SHA field
        if pr.get('sha'):
            pr_shas.add(pr['sha'])

    # Check deployments against PRs
    direct_commits = []
    for deploy in deployments:
        deploy_sha = deploy.get('sha', '')
        # If deployment SHA doesn't match any PR, it's a direct commit
        if deploy_sha and deploy_sha not in pr_shas:
            direct_commits.append(deploy)

    total = len(deployments)
    direct_count = len(direct_commits)
    percentage = (direct_count / total * 100) if total > 0 else 0

    return {
        'count': direct_count,
        'percentage': percentage,
        'deployments': direct_commits
    }


def display_process_compliance(deployments, pull_requests):
    """Display process compliance analysis."""
    from datetime import datetime
    import pandas as pd

    direct_commits_data = check_direct_commits(deployments, pull_requests)

    # Display summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        total_deploys = len(deployments)
        st.metric("Total Deployments", total_deploys)

    with col2:
        pr_based = total_deploys - direct_commits_data['count']
        pr_percentage = (pr_based / total_deploys * 100) if total_deploys > 0 else 0
        st.metric(
            "PR-Based Deployments",
            f"{pr_based}",
            delta=f"{pr_percentage:.0f}% compliance"
        )

    with col3:
        st.metric(
            "⚠️ Direct Commits",
            direct_commits_data['count'],
            delta=f"-{direct_commits_data['percentage']:.0f}% bypass",
            delta_color="inverse"
        )

    # Visual compliance gauge
    st.markdown("#### 📊 PR Compliance Rate")
    compliance_rate = 100 - direct_commits_data['percentage']

    # Color code based on compliance
    if compliance_rate >= 95:
        color = "green"
        status = "Excellent"
    elif compliance_rate >= 80:
        color = "blue"
        status = "Good"
    elif compliance_rate >= 60:
        color = "orange"
        status = "Needs Improvement"
    else:
        color = "red"
        status = "Poor"

    # Progress bar
    st.progress(compliance_rate / 100)
    st.caption(f"{compliance_rate:.1f}% - {status}")

    # Display direct commits table if any exist
    if direct_commits_data['deployments']:
        st.markdown("#### ⚠️ Direct Commits (No PR)")
        st.warning(f"Found {len(direct_commits_data['deployments'])} deployment(s) that bypassed the PR process")

        data = []
        for deploy in direct_commits_data['deployments']:
            deploy_time = datetime.fromisoformat(deploy['deployed_at'].replace('Z', '+00:00'))
            data.append({
                'Date': deploy_time.strftime('%Y-%m-%d'),
                'Time': deploy_time.strftime('%H:%M:%S'),
                'Deployer': deploy.get('creator', 'Unknown'),
                'SHA': deploy.get('sha', 'N/A')[:8],
                'Environment': deploy.get('environment', 'N/A'),
                'Source': deploy.get('source', 'N/A')
            })

        df = pd.DataFrame(data)
        df = df.sort_values(['Date', 'Time'], ascending=False)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Date': st.column_config.TextColumn('📅 Date', width='medium'),
                'Time': st.column_config.TextColumn('🕐 Time', width='small'),
                'Deployer': st.column_config.TextColumn('👤 Deployer', width='medium'),
                'SHA': st.column_config.TextColumn('🔗 Commit', width='small'),
                'Environment': st.column_config.TextColumn('🌍 Environment', width='medium'),
                'Source': st.column_config.TextColumn('📦 Source', width='medium')
            }
        )

        # Recommendations
        st.info("💡 **Recommendation:** Enable branch protection rules to require pull request reviews before merging.")
    else:
        st.success("✅ All deployments went through the PR process - excellent process compliance!")


def display_data_quality(raw_data, metrics):
    """Display data quality and provenance information."""
    st.markdown("### 📊 Data Quality & Provenance")

    deployments = raw_data.get('deployments', [])

    # Count deployment sources
    source_counts = {
        'deployments_api': 0,
        'workflow_runs': 0,
        'inferred_from_pr': 0
    }

    for deploy in deployments:
        source = deploy.get('source', 'unknown')
        if source in source_counts:
            source_counts[source] += 1

    # Determine data quality level
    total_deploys = len(deployments)
    api_percentage = (source_counts['deployments_api'] / total_deploys * 100) if total_deploys > 0 else 0

    if api_percentage >= 80:
        quality_level = "High"
        quality_color = "🟢"
    elif api_percentage >= 50:
        quality_level = "Medium"
        quality_color = "🟡"
    else:
        quality_level = "Low"
        quality_color = "🟠"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Data Quality", f"{quality_color} {quality_level}")

    with col2:
        st.metric("GitHub API", source_counts['deployments_api'])

    with col3:
        st.metric("Workflow Runs", source_counts['workflow_runs'])

    with col4:
        st.metric("Inferred from PRs", source_counts['inferred_from_pr'])

    # Show lead time calculation method
    lead_time_method = metrics['lead_time_for_changes'].get('calculation_method', 'unknown')
    if lead_time_method == 'commit_to_production':
        matched = metrics['lead_time_for_changes'].get('matched_deployments', 0)
        st.info(f"✅ **Lead Time**: Using true commit-to-production calculation ({matched} PRs matched to deployments)")
    elif lead_time_method == 'pr_cycle_time_approximation':
        st.warning("⚠️ **Lead Time**: Using PR cycle time as approximation (PRs not matched to deployments)")

    # Show any insufficient data warnings
    warnings = []
    if metrics['deployment_frequency'].get('insufficient_data'):
        warnings.append("Deployment Frequency")
    if metrics['lead_time_for_changes'].get('insufficient_data'):
        warnings.append("Lead Time")
    if metrics['mean_time_to_restore'].get('insufficient_data'):
        warnings.append("MTTR")
    if metrics['change_failure_rate'].get('insufficient_data'):
        warnings.append("Change Failure Rate")

    if warnings:
        st.warning(f"⚠️ **Insufficient Data**: {', '.join(warnings)}")


if __name__ == "__main__":
    main()

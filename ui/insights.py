"""
AI insights and performance summary components
"""
import streamlit as st


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


def display_performance_summary(metrics):
    """Display performance summary with strengths, improvements, and recommendations."""
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
            'Deployment Frequency': {'level': metrics['deployment_frequency']['level'], 'score': {'Elite': 4, 'High': 3, 'Medium': 2, 'Low': 1, 'N/A': 0}[metrics['deployment_frequency']['level']]},
            'Lead Time': {'level': metrics['lead_time_for_changes']['level'], 'score': {'Elite': 4, 'High': 3, 'Medium': 2, 'Low': 1, 'N/A': 0}[metrics['lead_time_for_changes']['level']]},
            'MTTR': {'level': metrics['mean_time_to_restore']['level'], 'score': {'Elite': 4, 'High': 3, 'Medium': 2, 'Low': 1, 'N/A': 0}[metrics['mean_time_to_restore']['level']]},
            'Failure Rate': {'level': metrics['change_failure_rate']['level'], 'score': {'Elite': 4, 'High': 3, 'Medium': 2, 'Low': 1, 'N/A': 0}[metrics['change_failure_rate']['level']]}
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


def display_metric_context(metric_name: str):
    """Display context and insights for a specific metric."""
    st.markdown("---")
    st.markdown("### 📊 Context & Insights")

    contexts = {
        'deployment_frequency': {
            'what': """
            - Higher deployment frequency = faster feedback loops
            - Elite teams deploy on-demand (multiple times per day)
            - Requires strong CI/CD automation and testing
            """,
            'how': """
            - Automate deployment pipelines
            - Reduce batch sizes (deploy smaller changes)
            - Implement feature flags for safer releases
            - Improve automated testing coverage
            """
        },
        'lead_time': {
            'what': """
            - Time from code commit to running in production
            - Lower lead time = faster value delivery
            - Elite teams achieve < 1 hour lead time
            - Key indicator of development velocity
            """,
            'how': """
            - Streamline code review process
            - Automate testing and CI/CD
            - Reduce PR size and complexity
            - Minimize manual approval steps
            - Parallelize build and test stages
            """
        },
        'mttr': {
            'what': """
            - How quickly you recover from failures
            - Elite teams restore in < 1 hour
            - Measures resilience and incident response
            - Lower MTTR = better reliability
            """,
            'how': """
            - Implement comprehensive monitoring/alerts
            - Practice incident response (game days)
            - Automate rollback procedures
            - Build better observability (logs, metrics, traces)
            - Create runbooks for common issues
            """
        },
        'change_failure_rate': {
            'what': """
            - Percentage of deployments causing failures
            - Elite teams maintain < 15% failure rate
            - Balances speed with quality
            - Lower rate = higher release confidence
            """,
            'how': """
            - Increase test coverage (unit, integration, e2e)
            - Implement progressive rollouts (canary/blue-green)
            - Add pre-deployment validation checks
            - Use staging environments effectively
            - Conduct thorough code reviews
            """
        },
        'process_compliance': {
            'what': """
            - Direct commits bypass code review process
            - Higher direct commit rate = higher risk
            - Elite teams enforce PR-based workflows
            - Process compliance ensures code quality
            """,
            'how': """
            - Enable branch protection rules
            - Require PR reviews before merge
            - Use CI/CD checks on all branches
            - Educate team on PR best practices
            - Monitor and audit direct commits
            """
        }
    }

    context = contexts.get(metric_name, {'what': '', 'how': ''})

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**What This Means:**")
        st.markdown(context['what'])
    with col_b:
        st.markdown("**How to Improve:**")
        st.markdown(context['how'])

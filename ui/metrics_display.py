"""
Display components for individual DORA metrics
"""
import streamlit as st


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
        period_days = metric.get('period_days', 30)  # Get actual analysis period
        if metric['total_deployments'] > 0:
            st.metric("Active Days", f"{days_with_deploys}/{period_days}")
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

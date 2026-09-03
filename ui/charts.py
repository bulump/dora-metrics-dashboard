"""
Chart components for DORA Metrics Dashboard
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from collections import defaultdict


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


def display_deployment_timeline(deployments):
    """Display deployment timeline chart with success/failure breakdown."""
    if not deployments:
        st.info("No deployment data available")
        return

    # Parse dates and count deployments per day (success vs failure)
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

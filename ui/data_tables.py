"""
Data table components for DORA Metrics Dashboard
"""
import streamlit as st
import pandas as pd
from datetime import datetime


def display_failed_deployments(deployments, pull_requests):
    """Display table of failed deployments with PR titles."""
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

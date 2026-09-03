"""
DORA Metrics Calculator
Calculates the four key DORA metrics for software delivery performance.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import statistics


class DORACalculator:
    """Calculates DORA (DevOps Research and Assessment) metrics."""

    def __init__(self):
        """Initialize DORA calculator."""
        pass

    def calculate_all_metrics(
        self,
        deployments: List[Dict[str, Any]],
        pull_requests: List[Dict[str, Any]],
        incidents: List[Dict[str, Any]],
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate all four DORA metrics.

        Args:
            deployments: List of deployment events
            pull_requests: List of PRs (for lead time calculation)
            incidents: List of incident/failure events
            days_back: Number of days to analyze

        Returns:
            Dictionary containing all DORA metrics
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        # Filter to time window
        recent_deployments = [
            d for d in deployments
            if datetime.fromisoformat(d['deployed_at'].replace('Z', '+00:00')) >= cutoff_date
        ]
        recent_prs = [
            pr for pr in pull_requests
            if pr.get('merged_at') and
            datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00')) >= cutoff_date
        ]
        recent_incidents = [
            i for i in incidents
            if datetime.fromisoformat(i['created_at'].replace('Z', '+00:00')) >= cutoff_date
        ]

        return {
            'deployment_frequency': self.calculate_deployment_frequency(recent_deployments, days_back),
            'lead_time_for_changes': self.calculate_lead_time(recent_prs, recent_deployments),
            'mean_time_to_restore': self.calculate_mttr(recent_incidents),
            'change_failure_rate': self.calculate_change_failure_rate(recent_deployments, recent_incidents),
            'period_days': days_back,
            'data_summary': {
                'total_deployments': len(recent_deployments),
                'total_prs': len(recent_prs),
                'total_incidents': len(recent_incidents),
            },
            # Include filtered data for time-aware displays
            'filtered_data': {
                'deployments': recent_deployments,
                'pull_requests': recent_prs,
                'incidents': recent_incidents
            }
        }

    def calculate_deployment_frequency(
        self,
        deployments: List[Dict[str, Any]],
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate deployment frequency.

        DORA Levels:
        - Elite: Multiple deploys per day
        - High: Between once per day and once per week
        - Medium: Between once per week and once per month
        - Low: Fewer than once per month

        Args:
            deployments: List of deployment events
            days_back: Number of days analyzed

        Returns:
            Deployment frequency metrics
        """
        total_deployments = len(deployments)

        if total_deployments == 0:
            return {
                'deploys_per_day': 0,
                'deploys_per_week': 0,
                'total_deployments': 0,
                'days_with_deployments': 0,
                'level': 'N/A',
                'description': 'No deployments in period',
                'insufficient_data': True
            }

        deploys_per_day = total_deployments / days_back
        deploys_per_week = deploys_per_day * 7

        # Calculate days with deployments
        deployment_dates = set()
        for deploy in deployments:
            deploy_date = datetime.fromisoformat(deploy['deployed_at'].replace('Z', '+00:00')).date()
            deployment_dates.add(deploy_date)
        days_with_deployments = len(deployment_dates)

        # Determine DORA level
        if deploys_per_day >= 1:
            level = 'Elite'
            description = 'Multiple deploys per day' if deploys_per_day > 1 else 'Daily deployment'
        elif deploys_per_week >= 1:
            level = 'High'
            description = f'{deploys_per_week:.1f} deploys per week'
        elif deploys_per_week >= 0.25:  # Once per month
            level = 'Medium'
            description = 'Weekly to monthly deployments'
        else:
            level = 'Low'
            description = 'Less than once per month'

        return {
            'deploys_per_day': round(deploys_per_day, 2),
            'deploys_per_week': round(deploys_per_week, 2),
            'total_deployments': total_deployments,
            'days_with_deployments': days_with_deployments,
            'period_days': days_back,
            'level': level,
            'description': description
        }

    def calculate_lead_time(
        self,
        pull_requests: List[Dict[str, Any]],
        deployments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate lead time for changes (time from first commit to production deployment).

        DORA Levels:
        - Elite: Less than one hour
        - High: Between one day and one week
        - Medium: Between one week and one month
        - Low: More than one month

        Args:
            pull_requests: List of merged PRs
            deployments: List of deployments (optional, for true commit-to-prod)

        Returns:
            Lead time metrics
        """
        if not pull_requests:
            return {
                'median_hours': 0,
                'mean_hours': 0,
                'p95_hours': 0,
                'total_prs': 0,
                'level': 'N/A',
                'description': 'No PRs to analyze',
                'insufficient_data': True
            }

        lead_times = []

        # If we have deployments, calculate true commit-to-production lead time
        if deployments:
            # Create SHA to deployment mapping
            sha_to_deployment = {}
            for deploy in deployments:
                if deploy.get('sha'):
                    deploy_time = datetime.fromisoformat(deploy['deployed_at'].replace('Z', '+00:00'))
                    # Keep earliest deployment for each SHA
                    if deploy['sha'] not in sha_to_deployment or deploy_time < sha_to_deployment[deploy['sha']]:
                        sha_to_deployment[deploy['sha']] = deploy_time

            # Calculate lead time: PR created (proxy for first commit) to deployment
            for pr in pull_requests:
                if not pr.get('created_at') or not pr.get('merge_commit_sha'):
                    continue

                merge_sha = pr.get('merge_commit_sha')
                if merge_sha in sha_to_deployment:
                    created = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
                    deployed = sha_to_deployment[merge_sha]

                    lead_time_hours = (deployed - created).total_seconds() / 3600
                    if lead_time_hours >= 0:  # Only count positive lead times
                        lead_times.append(lead_time_hours)

        # Fallback: if no deployments or no matches, use PR created -> merged as approximation
        if not lead_times:
            for pr in pull_requests:
                if not pr.get('created_at') or not pr.get('merged_at'):
                    continue

                created = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
                merged = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))

                lead_time_hours = (merged - created).total_seconds() / 3600
                lead_times.append(lead_time_hours)

        if not lead_times:
            return {
                'median_hours': 0,
                'mean_hours': 0,
                'p95_hours': 0,
                'total_prs': len(pull_requests),
                'level': 'N/A',
                'description': 'No valid PR data',
                'insufficient_data': True
            }

        median_hours = statistics.median(lead_times)
        mean_hours = statistics.mean(lead_times)
        p95_hours = statistics.quantiles(lead_times, n=20)[18] if len(lead_times) >= 20 else max(lead_times)

        # Determine DORA level based on median
        if median_hours < 1:
            level = 'Elite'
            description = 'Less than one hour'
        elif median_hours < 24:
            level = 'High'
            description = f'{median_hours:.1f} hours'
        elif median_hours < 168:  # 1 week
            level = 'High'
            description = f'{median_hours/24:.1f} days'
        elif median_hours < 720:  # 1 month
            level = 'Medium'
            description = f'{median_hours/168:.1f} weeks'
        else:
            level = 'Low'
            description = 'More than one month'

        result = {
            'median_hours': round(median_hours, 2),
            'mean_hours': round(mean_hours, 2),
            'p95_hours': round(p95_hours, 2),
            'total_prs': len(pull_requests),
            'level': level,
            'description': description,
            'insufficient_data': False
        }

        # Add metadata about calculation method
        if deployments and len(lead_times) > 0:
            # Check if we actually used deployment matching or fell back to PR cycle time
            # If we had deployments but calculated from PR cycle time, we fell back
            first_pr = next((pr for pr in pull_requests if pr.get('created_at') and pr.get('merged_at')), None)
            if first_pr:
                first_pr_cycle_time = (
                    datetime.fromisoformat(first_pr['merged_at'].replace('Z', '+00:00')) -
                    datetime.fromisoformat(first_pr['created_at'].replace('Z', '+00:00'))
                ).total_seconds() / 3600
                # If median matches PR cycle time, we used fallback
                if abs(result['median_hours'] - first_pr_cycle_time) < 0.1 and len(pull_requests) == 1:
                    result['calculation_method'] = 'pr_cycle_time_approximation'
                else:
                    result['calculation_method'] = 'commit_to_production'
                    result['matched_deployments'] = len(lead_times)
            else:
                result['calculation_method'] = 'commit_to_production'
                result['matched_deployments'] = len(lead_times)
        elif deployments:
            # Had deployments but no matches - fell back to PR cycle time
            result['calculation_method'] = 'pr_cycle_time_approximation'
        else:
            result['calculation_method'] = 'pr_cycle_time_approximation'

        return result

    def calculate_mttr(
        self,
        incidents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate Mean Time to Restore (MTTR).

        DORA Levels:
        - Elite: Less than one hour
        - High: Less than one day
        - Medium: Between one day and one week
        - Low: More than one week

        Args:
            incidents: List of incidents with created_at and resolved_at

        Returns:
            MTTR metrics
        """
        if not incidents:
            return {
                'median_hours': 0,
                'mean_hours': 0,
                'max_hours': 0,
                'total_incidents': 0,
                'level': 'N/A',
                'description': 'No incidents in period',
                'insufficient_data': True
            }

        restore_times = []
        for incident in incidents:
            if not incident.get('created_at') or not incident.get('resolved_at'):
                continue

            created = datetime.fromisoformat(incident['created_at'].replace('Z', '+00:00'))
            resolved = datetime.fromisoformat(incident['resolved_at'].replace('Z', '+00:00'))

            restore_hours = (resolved - created).total_seconds() / 3600
            restore_times.append(restore_hours)

        if not restore_times:
            return {
                'median_hours': 0,
                'mean_hours': 0,
                'total_incidents': len(incidents),
                'level': 'Medium',
                'description': 'Incidents not yet resolved'
            }

        median_hours = statistics.median(restore_times)
        mean_hours = statistics.mean(restore_times)
        max_hours = max(restore_times)

        # Determine DORA level
        if median_hours < 1:
            level = 'Elite'
            description = f'{median_hours*60:.0f} minutes'
        elif median_hours < 24:
            level = 'High'
            description = f'{median_hours:.1f} hours'
        elif median_hours < 168:  # 1 week
            level = 'Medium'
            description = f'{median_hours/24:.1f} days'
        else:
            level = 'Low'
            description = 'More than one week'

        return {
            'median_hours': round(median_hours, 2),
            'mean_hours': round(mean_hours, 2),
            'max_hours': round(max_hours, 2),
            'total_incidents': len(incidents),
            'level': level,
            'description': description
        }

    def calculate_change_failure_rate(
        self,
        deployments: List[Dict[str, Any]],
        incidents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate change failure rate (% of deployments causing incidents).

        Correlates incidents with deployments using timing and SHA matching.

        DORA Levels:
        - Elite: 0-15%
        - High: 16-30%
        - Medium: 31-45%
        - Low: 46-100%

        Args:
            deployments: List of deployments
            incidents: List of incidents

        Returns:
            Change failure rate metrics
        """
        total_deployments = len(deployments)

        if total_deployments == 0:
            return {
                'failure_rate_pct': 0,
                'total_deployments': 0,
                'failed_deployments': 0,
                'level': 'N/A',
                'description': 'No deployments to measure',
                'insufficient_data': True
            }

        # Correlate incidents with deployments
        # Method 1: Count deployments explicitly marked as failed
        failed_deployments_set = set()
        for deploy in deployments:
            if deploy.get('status') == 'failure':
                failed_deployments_set.add(deploy.get('id'))

        # Method 2: Correlate incidents with deployments by time window
        # An incident is linked to a deployment if it occurs within 24h after deployment
        for incident in incidents:
            incident_time = datetime.fromisoformat(incident['created_at'].replace('Z', '+00:00'))

            # Find the most recent deployment before this incident
            closest_deploy = None
            closest_time_diff = None

            for deploy in deployments:
                deploy_time = datetime.fromisoformat(deploy['deployed_at'].replace('Z', '+00:00'))

                # Only consider deployments that happened before the incident
                if deploy_time < incident_time:
                    time_diff = (incident_time - deploy_time).total_seconds() / 3600  # hours

                    # Only link if incident is within 24 hours of deployment
                    if time_diff <= 24:
                        if closest_time_diff is None or time_diff < closest_time_diff:
                            closest_deploy = deploy
                            closest_time_diff = time_diff

            if closest_deploy:
                failed_deployments_set.add(closest_deploy.get('id'))

        failed_deployments = len(failed_deployments_set)
        failure_rate = (failed_deployments / total_deployments) * 100

        # Determine DORA level
        if failure_rate <= 15:
            level = 'Elite'
        elif failure_rate <= 30:
            level = 'High'
        elif failure_rate <= 45:
            level = 'Medium'
        else:
            level = 'Low'

        return {
            'failure_rate_pct': round(failure_rate, 2),
            'total_deployments': total_deployments,
            'failed_deployments': failed_deployments,
            'level': level,
            'description': f'{failure_rate:.1f}% of deployments cause incidents',
            'insufficient_data': False
        }

    def get_overall_performance_level(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine overall DORA performance level.

        Args:
            metrics: All DORA metrics

        Returns:
            Overall performance assessment
        """
        levels = {
            'Elite': 4,
            'High': 3,
            'Medium': 2,
            'Low': 1,
            'N/A': None  # Exclude from calculations
        }

        metric_levels = [
            metrics['deployment_frequency']['level'],
            metrics['lead_time_for_changes']['level'],
            metrics['mean_time_to_restore']['level'],
            metrics['change_failure_rate']['level']
        ]

        # Calculate average level, excluding N/A values
        valid_scores = [levels[level] for level in metric_levels if levels[level] is not None]

        if not valid_scores:
            return {
                'overall_level': 'N/A',
                'description': 'Insufficient data for assessment',
                'score': 0,
                'breakdown': {
                    'deployment_frequency': metrics['deployment_frequency']['level'],
                    'lead_time': metrics['lead_time_for_changes']['level'],
                    'mttr': metrics['mean_time_to_restore']['level'],
                    'change_failure_rate': metrics['change_failure_rate']['level']
                }
            }

        avg_score = sum(valid_scores) / len(valid_scores)

        if avg_score >= 3.5:
            overall = 'Elite'
            description = 'Outstanding software delivery performance'
        elif avg_score >= 2.5:
            overall = 'High'
            description = 'Strong software delivery performance'
        elif avg_score >= 1.5:
            overall = 'Medium'
            description = 'Moderate software delivery performance'
        else:
            overall = 'Low'
            description = 'Needs improvement in software delivery'

        # Add note if some metrics are N/A
        na_count = sum(1 for level in metric_levels if level == 'N/A')
        if na_count > 0:
            description += f' ({na_count} metric(s) have insufficient data)'

        return {
            'overall_level': overall,
            'description': description,
            'score': round(avg_score, 2),
            'breakdown': {
                'deployment_frequency': metrics['deployment_frequency']['level'],
                'lead_time': metrics['lead_time_for_changes']['level'],
                'mttr': metrics['mean_time_to_restore']['level'],
                'change_failure_rate': metrics['change_failure_rate']['level']
            }
        }

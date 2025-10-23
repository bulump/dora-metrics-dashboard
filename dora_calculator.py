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
            'lead_time_for_changes': self.calculate_lead_time(recent_prs),
            'mean_time_to_restore': self.calculate_mttr(recent_incidents),
            'change_failure_rate': self.calculate_change_failure_rate(recent_deployments, recent_incidents),
            'period_days': days_back,
            'data_summary': {
                'total_deployments': len(recent_deployments),
                'total_prs': len(recent_prs),
                'total_incidents': len(recent_incidents),
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
                'level': 'Low',
                'description': 'No deployments in period'
            }

        deploys_per_day = total_deployments / days_back
        deploys_per_week = deploys_per_day * 7

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
            'level': level,
            'description': description
        }

    def calculate_lead_time(
        self,
        pull_requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate lead time for changes (time from commit to production).

        DORA Levels:
        - Elite: Less than one hour
        - High: Between one day and one week
        - Medium: Between one week and one month
        - Low: More than one month

        Args:
            pull_requests: List of merged PRs

        Returns:
            Lead time metrics
        """
        if not pull_requests:
            return {
                'median_hours': 0,
                'mean_hours': 0,
                'p95_hours': 0,
                'total_prs': 0,
                'level': 'Low',
                'description': 'No PRs to analyze'
            }

        lead_times = []
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
                'level': 'Low',
                'description': 'No valid PR data'
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

        return {
            'median_hours': round(median_hours, 2),
            'mean_hours': round(mean_hours, 2),
            'p95_hours': round(p95_hours, 2),
            'total_prs': len(pull_requests),
            'level': level,
            'description': description
        }

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
                'total_incidents': 0,
                'level': 'Elite',
                'description': 'No incidents in period'
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

        DORA Levels:
        - Elite: 0-15%
        - High: 16-30%
        - Medium: 31-45%
        - Low: 46-100%

        Args:
            deployments: List of deployments
            incidents: List of incidents caused by deployments

        Returns:
            Change failure rate metrics
        """
        total_deployments = len(deployments)

        if total_deployments == 0:
            return {
                'failure_rate_pct': 0,
                'total_deployments': 0,
                'failed_deployments': 0,
                'level': 'Elite',
                'description': 'No deployments to measure'
            }

        # Count incidents that were caused by deployments
        failed_deployments = len(incidents)
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
            'description': f'{failure_rate:.1f}% of deployments cause incidents'
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
            'Low': 1
        }

        metric_levels = [
            metrics['deployment_frequency']['level'],
            metrics['lead_time_for_changes']['level'],
            metrics['mean_time_to_restore']['level'],
            metrics['change_failure_rate']['level']
        ]

        # Calculate average level
        avg_score = sum(levels[level] for level in metric_levels) / 4

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

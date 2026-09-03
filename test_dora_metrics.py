"""
Unit tests for DORA Metrics Calculator
Tests metric correctness, edge cases, and data quality.
"""
import pytest
from datetime import datetime, timezone, timedelta
from dora_calculator import DORACalculator


class TestDeploymentFrequency:
    """Tests for deployment frequency calculations."""

    def test_elite_level_multiple_per_day(self):
        """Test that multiple deploys per day = Elite."""
        calculator = DORACalculator()
        deployments = [
            {'deployed_at': (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat()}
            for i in range(60)  # 60 deployments in 30 days = 2/day
        ]
        result = calculator.calculate_deployment_frequency(deployments, days_back=30)
        assert result['level'] == 'Elite'
        assert result['deploys_per_day'] >= 1

    def test_high_level_weekly_deploys(self):
        """Test that weekly deploys = High."""
        calculator = DORACalculator()
        deployments = [
            {'deployed_at': (datetime.now(timezone.utc) - timedelta(days=i*7)).isoformat()}
            for i in range(4)  # 4 deployments over 30 days
        ]
        result = calculator.calculate_deployment_frequency(deployments, days_back=30)
        assert result['level'] in ['High', 'Medium']

    def test_zero_deployments_returns_na(self):
        """Test that zero deployments returns N/A, not Low or Elite."""
        calculator = DORACalculator()
        result = calculator.calculate_deployment_frequency([], days_back=30)
        assert result['level'] == 'N/A'
        assert result['insufficient_data'] is True
        assert result['total_deployments'] == 0


class TestLeadTime:
    """Tests for lead time calculations."""

    def test_commit_to_production_calculation(self):
        """Test true commit-to-production lead time."""
        calculator = DORACalculator()

        # Create PRs and deployments with matching SHAs
        prs = [
            {
                'created_at': '2024-01-01T10:00:00Z',
                'merged_at': '2024-01-01T12:00:00Z',
                'merge_commit_sha': 'abc123'
            }
        ]
        deployments = [
            {
                'sha': 'abc123',
                'deployed_at': '2024-01-01T14:00:00Z'  # 4 hours after PR created
            }
        ]

        result = calculator.calculate_lead_time(prs, deployments)
        assert result['calculation_method'] == 'commit_to_production'
        assert result['median_hours'] == 4.0
        assert result['insufficient_data'] is False

    def test_pr_cycle_time_fallback(self):
        """Test fallback to PR cycle time when deployments don't match."""
        calculator = DORACalculator()

        prs = [
            {
                'created_at': '2024-01-01T10:00:00Z',
                'merged_at': '2024-01-01T12:00:00Z',
                'merge_commit_sha': 'abc123'
            }
        ]
        deployments = [
            {
                'sha': 'different_sha',
                'deployed_at': '2024-01-01T14:00:00Z'
            }
        ]

        result = calculator.calculate_lead_time(prs, deployments)
        assert result['calculation_method'] == 'pr_cycle_time_approximation'
        assert result['median_hours'] == 2.0  # 2 hours between create and merge

    def test_no_prs_returns_na(self):
        """Test that no PRs returns N/A."""
        calculator = DORACalculator()
        result = calculator.calculate_lead_time([])
        assert result['level'] == 'N/A'
        assert result['insufficient_data'] is True

    def test_elite_lead_time_under_1_hour(self):
        """Test that lead time < 1 hour = Elite."""
        calculator = DORACalculator()
        prs = [
            {
                'created_at': '2024-01-01T10:00:00Z',
                'merged_at': '2024-01-01T10:30:00Z',
                'merge_commit_sha': 'abc123'
            }
        ]
        result = calculator.calculate_lead_time(prs)
        assert result['median_hours'] == 0.5
        assert result['level'] == 'Elite'


class TestMTTR:
    """Tests for Mean Time to Restore."""

    def test_no_incidents_returns_na(self):
        """Test that zero incidents returns N/A, not Elite."""
        calculator = DORACalculator()
        result = calculator.calculate_mttr([])
        assert result['level'] == 'N/A'
        assert result['insufficient_data'] is True
        assert result['total_incidents'] == 0

    def test_elite_mttr_under_1_hour(self):
        """Test that MTTR < 1 hour = Elite."""
        calculator = DORACalculator()
        incidents = [
            {
                'created_at': '2024-01-01T10:00:00Z',
                'resolved_at': '2024-01-01T10:30:00Z'
            }
        ]
        result = calculator.calculate_mttr(incidents)
        assert result['median_hours'] == 0.5
        assert result['level'] == 'Elite'

    def test_unresolved_incidents_excluded(self):
        """Test that unresolved incidents are excluded from MTTR."""
        calculator = DORACalculator()
        incidents = [
            {
                'created_at': '2024-01-01T10:00:00Z',
                'resolved_at': None  # Not resolved
            }
        ]
        result = calculator.calculate_mttr(incidents)
        # Should be N/A since no resolved incidents
        assert result['total_incidents'] == 1


class TestChangeFailureRate:
    """Tests for Change Failure Rate."""

    def test_zero_deployments_returns_na(self):
        """Test that zero deployments returns N/A, not Elite."""
        calculator = DORACalculator()
        result = calculator.calculate_change_failure_rate([], [])
        assert result['level'] == 'N/A'
        assert result['insufficient_data'] is True

    def test_incident_correlation_by_time_window(self):
        """Test that incidents are correlated to deployments within 24h."""
        calculator = DORACalculator()

        deployments = [
            {
                'id': 'deploy1',
                'deployed_at': '2024-01-01T10:00:00Z',
                'status': 'success'
            },
            {
                'id': 'deploy2',
                'deployed_at': '2024-01-02T10:00:00Z',
                'status': 'success'
            }
        ]

        incidents = [
            {
                'created_at': '2024-01-01T12:00:00Z',  # 2 hours after deploy1
            }
        ]

        result = calculator.calculate_change_failure_rate(deployments, incidents)
        assert result['failed_deployments'] == 1
        assert result['total_deployments'] == 2
        assert result['failure_rate_pct'] == 50.0

    def test_elite_cfr_under_15_percent(self):
        """Test that CFR <= 15% = Elite."""
        calculator = DORACalculator()

        deployments = [{'id': f'deploy{i}', 'deployed_at': f'2024-01-{i:02d}T10:00:00Z', 'status': 'success'} for i in range(1, 11)]
        incidents = [{'created_at': '2024-01-01T12:00:00Z'}]  # 1 failure out of 10

        result = calculator.calculate_change_failure_rate(deployments, incidents)
        assert result['failure_rate_pct'] == 10.0
        assert result['level'] == 'Elite'

    def test_failed_deployment_status(self):
        """Test that deployments with status='failure' are counted."""
        calculator = DORACalculator()

        deployments = [
            {'id': 'deploy1', 'deployed_at': '2024-01-01T10:00:00Z', 'status': 'failure'},
            {'id': 'deploy2', 'deployed_at': '2024-01-02T10:00:00Z', 'status': 'success'}
        ]

        result = calculator.calculate_change_failure_rate(deployments, [])
        assert result['failed_deployments'] == 1
        assert result['failure_rate_pct'] == 50.0


class TestOverallPerformance:
    """Tests for overall performance level calculation."""

    def test_all_na_returns_na(self):
        """Test that all N/A metrics returns N/A overall."""
        calculator = DORACalculator()
        metrics = {
            'deployment_frequency': {'level': 'N/A'},
            'lead_time_for_changes': {'level': 'N/A'},
            'mean_time_to_restore': {'level': 'N/A'},
            'change_failure_rate': {'level': 'N/A'}
        }
        result = calculator.get_overall_performance_level(metrics)
        assert result['overall_level'] == 'N/A'
        assert result['score'] == 0

    def test_mixed_na_and_valid_levels(self):
        """Test that N/A levels are excluded from average."""
        calculator = DORACalculator()
        metrics = {
            'deployment_frequency': {'level': 'Elite'},
            'lead_time_for_changes': {'level': 'N/A'},
            'mean_time_to_restore': {'level': 'Elite'},
            'change_failure_rate': {'level': 'High'}
        }
        result = calculator.get_overall_performance_level(metrics)
        # Should average Elite (4) + Elite (4) + High (3) = 11/3 = 3.67
        assert result['overall_level'] == 'Elite'
        assert '1 metric(s) have insufficient data' in result['description']

    def test_all_elite_returns_elite(self):
        """Test that all Elite metrics = Elite overall."""
        calculator = DORACalculator()
        metrics = {
            'deployment_frequency': {'level': 'Elite'},
            'lead_time_for_changes': {'level': 'Elite'},
            'mean_time_to_restore': {'level': 'Elite'},
            'change_failure_rate': {'level': 'Elite'}
        }
        result = calculator.get_overall_performance_level(metrics)
        assert result['overall_level'] == 'Elite'
        assert result['score'] == 4.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

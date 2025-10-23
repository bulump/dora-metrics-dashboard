"""
AI-Powered Insights Generator
Uses Claude AI to generate actionable insights from DORA metrics.
"""
from typing import Dict, Any, Optional
import os
from anthropic import Anthropic


class AIInsightsGenerator:
    """Generates AI-powered insights from DORA metrics."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI insights generator.

        Args:
            api_key: Anthropic API key (optional, uses env var if not provided)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"

    def generate_insights(
        self,
        metrics: Dict[str, Any],
        repo_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights from DORA metrics.

        Args:
            metrics: Calculated DORA metrics
            repo_stats: Repository statistics

        Returns:
            AI-generated insights and recommendations
        """
        prompt = self._build_insights_prompt(metrics, repo_stats)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            insights_text = response.content[0].text

            return {
                'success': True,
                'insights': insights_text,
                'metrics_summary': self._summarize_metrics(metrics)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'insights': 'Could not generate AI insights. Please check your API key.'
            }

    def _build_insights_prompt(
        self,
        metrics: Dict[str, Any],
        repo_stats: Dict[str, Any]
    ) -> str:
        """Build prompt for Claude AI."""
        deployment_freq = metrics['deployment_frequency']
        lead_time = metrics['lead_time_for_changes']
        mttr = metrics['mean_time_to_restore']
        change_failure = metrics['change_failure_rate']

        prompt = f"""You are an engineering metrics analyst. Analyze these DORA metrics and provide actionable insights for improving software delivery performance.

Repository: {repo_stats.get('full_name', 'Unknown')}
Period: Last {metrics.get('period_days', 30)} days

DORA METRICS:

1. Deployment Frequency: {deployment_freq['level']}
   - Rate: {deployment_freq['deploys_per_week']:.1f} deploys/week
   - Total deployments: {deployment_freq['total_deployments']}

2. Lead Time for Changes: {lead_time['level']}
   - Median: {lead_time['median_hours']:.1f} hours
   - Mean: {lead_time['mean_hours']:.1f} hours
   - P95: {lead_time['p95_hours']:.1f} hours

3. Mean Time to Restore (MTTR): {mttr['level']}
   - Median: {mttr['median_hours']:.1f} hours
   - Total incidents: {mttr['total_incidents']}

4. Change Failure Rate: {change_failure['level']}
   - Failure rate: {change_failure['failure_rate_pct']:.1f}%
   - Failed deployments: {change_failure['failed_deployments']}/{change_failure['total_deployments']}

Please provide:

1. **Overall Assessment** (2-3 sentences)
   - What's the overall DORA performance level?
   - What does this say about the team's software delivery capabilities?

2. **Key Strengths** (2-3 bullet points)
   - Which metrics are performing well?
   - What is the team doing right?

3. **Areas for Improvement** (2-3 bullet points)
   - Which metrics need attention?
   - What specific problems do these indicate?

4. **Actionable Recommendations** (3-5 specific recommendations)
   - Concrete steps to improve the weakest metrics
   - Process improvements, tooling, or practices to adopt
   - Prioritize by impact

Keep the tone professional and constructive. Focus on practical, actionable advice that an engineering manager can implement."""

        return prompt

    def _summarize_metrics(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Create a simple summary of metrics levels."""
        return {
            'deployment_frequency': metrics['deployment_frequency']['level'],
            'lead_time': metrics['lead_time_for_changes']['level'],
            'mttr': metrics['mean_time_to_restore']['level'],
            'change_failure_rate': metrics['change_failure_rate']['level']
        }

    def generate_comparison_insights(
        self,
        current_metrics: Dict[str, Any],
        previous_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate insights comparing current vs previous period.

        Args:
            current_metrics: Metrics for current period
            previous_metrics: Metrics for previous period

        Returns:
            Comparison insights
        """
        prompt = f"""Compare these two DORA metrics periods and identify trends.

CURRENT PERIOD:
- Deployment Frequency: {current_metrics['deployment_frequency']['level']} ({current_metrics['deployment_frequency']['deploys_per_week']:.1f}/week)
- Lead Time: {current_metrics['lead_time_for_changes']['level']} ({current_metrics['lead_time_for_changes']['median_hours']:.1f}h median)
- MTTR: {current_metrics['mean_time_to_restore']['level']} ({current_metrics['mean_time_to_restore']['median_hours']:.1f}h median)
- Change Failure Rate: {current_metrics['change_failure_rate']['level']} ({current_metrics['change_failure_rate']['failure_rate_pct']:.1f}%)

PREVIOUS PERIOD:
- Deployment Frequency: {previous_metrics['deployment_frequency']['level']} ({previous_metrics['deployment_frequency']['deploys_per_week']:.1f}/week)
- Lead Time: {previous_metrics['lead_time_for_changes']['level']} ({previous_metrics['lead_time_for_changes']['median_hours']:.1f}h median)
- MTTR: {previous_metrics['mean_time_to_restore']['level']} ({previous_metrics['mean_time_to_restore']['median_hours']:.1f}h median)
- Change Failure Rate: {previous_metrics['change_failure_rate']['level']} ({previous_metrics['change_failure_rate']['failure_rate_pct']:.1f}%)

Provide:
1. Key trends (improving, declining, stable)
2. Most significant changes
3. What might be causing these changes
4. Recommendations based on trends

Keep it concise (3-4 paragraphs)."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return {
                'success': True,
                'comparison': response.content[0].text
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'comparison': 'Could not generate comparison insights.'
            }

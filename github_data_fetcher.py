"""
GitHub Data Fetcher for DORA Metrics
Fetches deployment and incident data from GitHub.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from github import Github
import os


class GitHubDataFetcher:
    """Fetches deployment and incident data from GitHub."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub data fetcher.

        Args:
            token: GitHub token (optional, uses env var if not provided)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GITHUB_TOKEN must be set")

        self.client = Github(self.token)

    def fetch_all_data(
        self,
        repo_name: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Fetch all data needed for DORA metrics.

        Args:
            repo_name: Repository name (owner/repo)
            days_back: Number of days to fetch

        Returns:
            Dictionary containing deployments, PRs, and incidents
        """
        since_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        return {
            'deployments': self.fetch_deployments(repo_name, since_date),
            'pull_requests': self.fetch_pull_requests(repo_name, since_date),
            'incidents': self.fetch_incidents(repo_name, since_date),
            'repository': repo_name,
            'fetched_at': datetime.now(timezone.utc).isoformat(),
            'days_analyzed': days_back
        }

    def fetch_deployments(
        self,
        repo_name: str,
        since_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch deployment data from GitHub.

        Uses GitHub deployment API and workflow runs as fallback.

        Args:
            repo_name: Repository name (owner/repo)
            since_date: Start date for fetching

        Returns:
            List of deployment events
        """
        try:
            repo = self.client.get_repo(repo_name)
            deployments = []

            # Method 1: GitHub Deployments API
            try:
                gh_deployments = repo.get_deployments()
                for deploy in gh_deployments:
                    if deploy.created_at >= since_date.replace(tzinfo=None):
                        # Get deployment status
                        statuses = list(deploy.get_statuses())
                        latest_status = statuses[0] if statuses else None

                        deployments.append({
                            'id': deploy.id,
                            'environment': deploy.environment,
                            'deployed_at': deploy.created_at.isoformat() + 'Z',
                            'status': latest_status.state if latest_status else 'unknown',
                            'sha': deploy.sha,
                            'creator': deploy.creator.login if deploy.creator else 'unknown',
                            'source': 'deployments_api'
                        })
            except Exception as e:
                print(f"Warning: Could not fetch from deployments API: {e}")

            # Method 2: Workflow runs (deploy workflows)
            try:
                workflows = repo.get_workflows()
                for workflow in workflows:
                    # Look for deploy/deployment workflows
                    if any(keyword in workflow.name.lower() for keyword in ['deploy', 'release', 'production']):
                        runs = workflow.get_runs(created=f">={since_date.strftime('%Y-%m-%d')}")
                        for run in runs:
                            if run.conclusion == 'success':
                                deployments.append({
                                    'id': f"workflow_{run.id}",
                                    'environment': workflow.name,
                                    'deployed_at': run.created_at.isoformat() + 'Z',
                                    'status': 'success',
                                    'sha': run.head_sha,
                                    'creator': run.actor.login if run.actor else 'unknown',
                                    'source': 'workflow_runs',
                                    'workflow_name': workflow.name
                                })
            except Exception as e:
                print(f"Warning: Could not fetch from workflow runs: {e}")

            # Method 3: Infer from merged PRs with deployment labels
            if not deployments:
                print("No deployments found via API. Inferring from merged PRs...")
                deployments = self._infer_deployments_from_prs(repo, since_date)

            return sorted(deployments, key=lambda x: x['deployed_at'], reverse=True)

        except Exception as e:
            print(f"Error fetching deployments: {e}")
            return []

    def _infer_deployments_from_prs(
        self,
        repo,
        since_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Infer deployments from merged PRs.

        Assumes each merged PR to main is a deployment.

        Args:
            repo: GitHub repository object
            since_date: Start date

        Returns:
            List of inferred deployments
        """
        deployments = []
        try:
            # Get merged PRs to main branch
            pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')

            for pr in pulls:
                if pr.merged and pr.merged_at and pr.merged_at >= since_date.replace(tzinfo=None):
                    # Check if merged to main/master
                    if pr.base.ref in ['main', 'master']:
                        deployments.append({
                            'id': f"pr_{pr.number}",
                            'environment': 'production',
                            'deployed_at': pr.merged_at.isoformat() + 'Z',
                            'status': 'success',
                            'sha': pr.merge_commit_sha,
                            'creator': pr.user.login,
                            'source': 'inferred_from_pr',
                            'pr_number': pr.number,
                            'pr_title': pr.title
                        })

        except Exception as e:
            print(f"Error inferring deployments from PRs: {e}")

        return deployments

    def fetch_pull_requests(
        self,
        repo_name: str,
        since_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch merged pull requests for lead time calculation.

        Args:
            repo_name: Repository name (owner/repo)
            since_date: Start date for fetching

        Returns:
            List of merged PRs
        """
        try:
            repo = self.client.get_repo(repo_name)
            prs = []

            pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')

            for pr in pulls:
                if pr.merged and pr.merged_at and pr.merged_at >= since_date.replace(tzinfo=None):
                    prs.append({
                        'number': pr.number,
                        'title': pr.title,
                        'created_at': pr.created_at.isoformat() + 'Z',
                        'merged_at': pr.merged_at.isoformat() + 'Z',
                        'author': pr.user.login,
                        'additions': pr.additions,
                        'deletions': pr.deletions,
                        'changed_files': pr.changed_files,
                        'commits': pr.commits
                    })

            return prs

        except Exception as e:
            print(f"Error fetching pull requests: {e}")
            return []

    def fetch_incidents(
        self,
        repo_name: str,
        since_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch incidents from GitHub issues.

        Looks for issues with labels like 'incident', 'bug', 'production', 'outage'.

        Args:
            repo_name: Repository name (owner/repo)
            since_date: Start date for fetching

        Returns:
            List of incidents
        """
        try:
            repo = self.client.get_repo(repo_name)
            incidents = []

            # Define incident labels
            incident_labels = ['incident', 'production', 'outage', 'critical', 'p0', 'sev1']

            # Fetch issues with incident labels
            issues = repo.get_issues(state='all', since=since_date.replace(tzinfo=None))

            for issue in issues:
                # Check if issue has incident-related labels
                issue_labels = [label.name.lower() for label in issue.labels]

                if any(inc_label in issue_labels for inc_label in incident_labels):
                    # Determine if resolved
                    resolved_at = issue.closed_at.isoformat() + 'Z' if issue.closed_at else None

                    incidents.append({
                        'number': issue.number,
                        'title': issue.title,
                        'created_at': issue.created_at.isoformat() + 'Z',
                        'resolved_at': resolved_at,
                        'state': issue.state,
                        'labels': issue_labels,
                        'creator': issue.user.login if issue.user else 'unknown'
                    })

            return incidents

        except Exception as e:
            print(f"Error fetching incidents: {e}")
            return []

    def get_repository_stats(self, repo_name: str) -> Dict[str, Any]:
        """
        Get general repository statistics.

        Args:
            repo_name: Repository name (owner/repo)

        Returns:
            Repository statistics
        """
        try:
            repo = self.client.get_repo(repo_name)

            return {
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'open_issues': repo.open_issues_count,
                'default_branch': repo.default_branch,
                'created_at': repo.created_at.isoformat() + 'Z',
                'updated_at': repo.updated_at.isoformat() + 'Z',
                'language': repo.language,
                'size': repo.size
            }

        except Exception as e:
            print(f"Error fetching repository stats: {e}")
            return {}

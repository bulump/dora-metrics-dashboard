"""
GitHub Data Fetcher for DORA Metrics
Fetches deployment and incident data from GitHub.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from github import Github, GithubException, RateLimitExceededException, BadCredentialsException
import os
import time


class GitHubDataFetcher:
    """Fetches deployment and incident data from GitHub."""

    def __init__(
        self,
        token: Optional[str] = None,
        incident_labels: Optional[List[str]] = None,
        deployment_branches: Optional[List[str]] = None,
        workflow_keywords: Optional[List[str]] = None
    ):
        """
        Initialize GitHub data fetcher.

        Args:
            token: GitHub token (optional, uses env var if not provided)
            incident_labels: Custom labels for incident detection (default: ['incident', 'production', 'outage', 'critical', 'p0', 'sev1'])
            deployment_branches: Branch names to consider for deployments (default: ['main', 'master'])
            workflow_keywords: Keywords in workflow names to identify deployments (default: ['deploy', 'release', 'production'])
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GITHUB_TOKEN must be set")

        self.client = Github(self.token)

        # Configuration with sensible defaults
        self.incident_labels = incident_labels or ['incident', 'production', 'outage', 'critical', 'p0', 'sev1']
        self.deployment_branches = deployment_branches or ['main', 'master']
        self.workflow_keywords = workflow_keywords or ['deploy', 'release', 'production']

    def _handle_github_exception(self, e: Exception, context: str) -> None:
        """
        Handle GitHub API exceptions with informative error messages.

        Args:
            e: The exception that occurred
            context: Context string describing what operation failed
        """
        if isinstance(e, RateLimitExceededException):
            reset_time = e.headers.get('X-RateLimit-Reset', 'unknown')
            if reset_time != 'unknown':
                reset_dt = datetime.fromtimestamp(int(reset_time))
                raise Exception(
                    f"GitHub API rate limit exceeded. "
                    f"Resets at {reset_dt.strftime('%H:%M:%S')}. "
                    f"Try using Demo Data mode or wait until the limit resets."
                )
            else:
                raise Exception(
                    f"GitHub API rate limit exceeded. "
                    f"Try using Demo Data mode or wait ~1 hour for rate limit reset."
                )
        elif isinstance(e, BadCredentialsException):
            raise Exception(
                f"GitHub authentication failed. "
                f"Please check your GITHUB_TOKEN in .env file."
            )
        elif isinstance(e, GithubException):
            if e.status == 404:
                raise Exception(
                    f"Repository not found or you don't have access to it. "
                    f"Check the repository name format (owner/repo)."
                )
            elif e.status == 403:
                raise Exception(
                    f"Access forbidden (403). This could be a rate limit or permissions issue. "
                    f"Try using Demo Data mode."
                )
            else:
                raise Exception(
                    f"GitHub API error ({e.status}): {e.data.get('message', str(e))}"
                )
        else:
            raise Exception(f"Error {context}: {str(e)}")

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
                print("Fetching deployments from GitHub API...")
                gh_deployments = repo.get_deployments()
                deploy_count = 0
                for deploy in gh_deployments:
                    deploy_count += 1
                    if deploy.created_at.replace(tzinfo=None) >= since_date.replace(tzinfo=None):
                        # Get deployment status
                        try:
                            statuses = list(deploy.get_statuses())
                            latest_status = statuses[0] if statuses else None
                        except (RateLimitExceededException, GithubException) as e:
                            # If we hit rate limit getting statuses, use default
                            latest_status = None

                        deployments.append({
                            'id': deploy.id,
                            'environment': deploy.environment,
                            'deployed_at': deploy.created_at.isoformat() + 'Z',
                            'status': latest_status.state if latest_status else 'unknown',
                            'sha': deploy.sha,
                            'creator': deploy.creator.login if deploy.creator else 'unknown',
                            'source': 'deployments_api'
                        })
            except (RateLimitExceededException, BadCredentialsException, GithubException) as e:
                self._handle_github_exception(e, "fetching deployments")
            except Exception as e:
                print(f"Warning: Could not fetch from deployments API: {e}")

            # Method 2: Workflow runs (deploy workflows)
            try:
                print(f"Checking workflow runs... (found {len(deployments)} deployments so far)")
                workflows = repo.get_workflows()
                for workflow in workflows:
                    # Look for deploy/deployment workflows using configured keywords
                    if any(keyword in workflow.name.lower() for keyword in self.workflow_keywords):
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
            else:
                print(f"Found {len(deployments)} total deployments")

            return sorted(deployments, key=lambda x: x['deployed_at'], reverse=True)

        except (RateLimitExceededException, BadCredentialsException, GithubException) as e:
            self._handle_github_exception(e, "fetching deployments")
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
                if pr.merged and pr.merged_at and pr.merged_at.replace(tzinfo=None) >= since_date.replace(tzinfo=None):
                    # Check if merged to configured deployment branches
                    if pr.base.ref in self.deployment_branches:
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

            print("Fetching pull requests...")
            pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')

            pr_count = 0
            for pr in pulls:
                pr_count += 1
                if pr_count % 20 == 0:
                    print(f"Processed {pr_count} PRs...")
                if pr.merged and pr.merged_at and pr.merged_at.replace(tzinfo=None) >= since_date.replace(tzinfo=None):
                    prs.append({
                        'number': pr.number,
                        'title': pr.title,
                        'created_at': pr.created_at.isoformat() + 'Z',
                        'merged_at': pr.merged_at.isoformat() + 'Z',
                        'merge_commit_sha': pr.merge_commit_sha,  # CRITICAL: needed for lead time calculation
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

            # Fetch issues with incident labels
            print(f"Fetching incidents (looking for labels: {', '.join(self.incident_labels)})...")
            issues = repo.get_issues(state='all', since=since_date.replace(tzinfo=None))

            for issue in issues:
                # Check if issue has incident-related labels
                issue_labels = [label.name.lower() for label in issue.labels]

                if any(inc_label in issue_labels for inc_label in self.incident_labels):
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

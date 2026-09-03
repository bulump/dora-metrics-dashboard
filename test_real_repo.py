"""
Test DORA metrics with a real repository.
"""
from dotenv import load_dotenv
from github_data_fetcher import GitHubDataFetcher
from dora_calculator import DORACalculator

# Load environment variables
load_dotenv()

def test_real_repo():
    """Test with a real repository."""
    print("🧪 Testing DORA Metrics with Real Repository\n")

    # Test with a smaller repo that should have activity
    repo_name = "bulump/sprint-analytics"
    days_back = 30

    print(f"Repository: {repo_name}")
    print(f"Period: Last {days_back} days\n")

    try:
        # Fetch data
        print("📊 Fetching data from GitHub...\n")
        fetcher = GitHubDataFetcher()
        data = fetcher.fetch_all_data(repo_name, days_back)

        print("=" * 60)
        print("DATA FETCHED")
        print("=" * 60)
        print(f"\nDeployments found: {len(data['deployments'])}")
        if data['deployments']:
            print("\nDeployment sources:")
            sources = {}
            for d in data['deployments']:
                source = d.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
            for source, count in sources.items():
                print(f"  - {source}: {count}")
            print("\nFirst 3 deployments:")
            for d in data['deployments'][:3]:
                print(f"  - {d.get('deployed_at')} | {d.get('environment')} | {d.get('source')}")

        print(f"\nPull Requests found: {len(data['pull_requests'])}")
        if data['pull_requests']:
            print("\nFirst 3 PRs:")
            for pr in data['pull_requests'][:3]:
                print(f"  - PR #{pr['number']}: {pr['title'][:50]}")
                print(f"    Created: {pr['created_at']}")
                print(f"    Merged: {pr['merged_at']}")

        print(f"\nIncidents found: {len(data['incidents'])}")
        if data['incidents']:
            print("\nFirst 3 incidents:")
            for inc in data['incidents'][:3]:
                print(f"  - Issue #{inc['number']}: {inc['title'][:50]}")
                print(f"    Labels: {', '.join(inc['labels'])}")

        # Calculate metrics
        print("\n" + "=" * 60)
        print("CALCULATING METRICS")
        print("=" * 60)

        calculator = DORACalculator()
        metrics = calculator.calculate_all_metrics(
            deployments=data['deployments'],
            pull_requests=data['pull_requests'],
            incidents=data['incidents'],
            days_back=days_back
        )

        # Display results
        print("\n1️⃣ Deployment Frequency:", metrics['deployment_frequency']['level'])
        print(f"   Deploys/week: {metrics['deployment_frequency']['deploys_per_week']}")

        print("\n2️⃣ Lead Time for Changes:", metrics['lead_time_for_changes']['level'])
        print(f"   Median: {metrics['lead_time_for_changes']['median_hours']} hours")

        print("\n3️⃣ Mean Time to Restore:", metrics['mean_time_to_restore']['level'])
        print(f"   Median: {metrics['mean_time_to_restore']['median_hours']} hours")

        print("\n4️⃣ Change Failure Rate:", metrics['change_failure_rate']['level'])
        print(f"   Rate: {metrics['change_failure_rate']['failure_rate_pct']}%")

        overall = calculator.get_overall_performance_level(metrics)
        print("\n" + "=" * 60)
        print(f"OVERALL: {overall['overall_level']} ({overall['score']}/4.0)")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_real_repo()
    exit(0 if success else 1)

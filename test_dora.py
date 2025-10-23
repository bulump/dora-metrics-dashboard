"""
Test DORA metrics calculator with sample data.
"""
from datetime import datetime, timedelta, timezone
from dora_calculator import DORACalculator

def test_dora_metrics():
    """Test DORA metrics calculation with sample data."""
    print("🧪 Testing DORA Metrics Calculator\n")

    calculator = DORACalculator()

    # Sample data
    now = datetime.now(timezone.utc)

    # Deployments - 10 in last 30 days
    deployments = []
    for i in range(10):
        deployments.append({
            'deployed_at': (now - timedelta(days=i*3)).isoformat(),
            'status': 'success'
        })

    # Pull requests - 15 merged PRs
    pull_requests = []
    for i in range(15):
        created = now - timedelta(days=i*2, hours=48)
        merged = created + timedelta(hours=24)  # 24 hour lead time
        pull_requests.append({
            'created_at': created.isoformat(),
            'merged_at': merged.isoformat()
        })

    # Incidents - 2 incidents
    incidents = [
        {
            'created_at': (now - timedelta(days=5)).isoformat(),
            'resolved_at': (now - timedelta(days=5, hours=-2)).isoformat()  # 2 hours to resolve
        },
        {
            'created_at': (now - timedelta(days=10)).isoformat(),
            'resolved_at': (now - timedelta(days=10, hours=-3)).isoformat()  # 3 hours to resolve
        }
    ]

    # Calculate metrics
    print("📊 Calculating DORA Metrics...\n")
    metrics = calculator.calculate_all_metrics(
        deployments=deployments,
        pull_requests=pull_requests,
        incidents=incidents,
        days_back=30
    )

    # Display results
    print("=" * 60)
    print("DORA METRICS RESULTS")
    print("=" * 60)

    # Deployment Frequency
    df = metrics['deployment_frequency']
    print(f"\n1️⃣ Deployment Frequency: {df['level']}")
    print(f"   • Deploys per day: {df['deploys_per_day']}")
    print(f"   • Deploys per week: {df['deploys_per_week']}")
    print(f"   • Total: {df['total_deployments']}")
    print(f"   • {df['description']}")

    # Lead Time
    lt = metrics['lead_time_for_changes']
    print(f"\n2️⃣ Lead Time for Changes: {lt['level']}")
    print(f"   • Median: {lt['median_hours']:.1f} hours")
    print(f"   • Mean: {lt['mean_hours']:.1f} hours")
    print(f"   • P95: {lt['p95_hours']:.1f} hours")
    print(f"   • {lt['description']}")

    # MTTR
    mttr = metrics['mean_time_to_restore']
    print(f"\n3️⃣ Mean Time to Restore: {mttr['level']}")
    print(f"   • Median: {mttr['median_hours']:.1f} hours")
    print(f"   • Mean: {mttr['mean_hours']:.1f} hours")
    print(f"   • Total incidents: {mttr['total_incidents']}")
    print(f"   • {mttr['description']}")

    # Change Failure Rate
    cfr = metrics['change_failure_rate']
    print(f"\n4️⃣ Change Failure Rate: {cfr['level']}")
    print(f"   • Failure rate: {cfr['failure_rate_pct']:.1f}%")
    print(f"   • Failed/Total: {cfr['failed_deployments']}/{cfr['total_deployments']}")
    print(f"   • {cfr['description']}")

    # Overall performance
    overall = calculator.get_overall_performance_level(metrics)
    print(f"\n" + "=" * 60)
    print(f"OVERALL PERFORMANCE: {overall['overall_level']}")
    print(f"Score: {overall['score']}/4.0")
    print(f"{overall['description']}")
    print("=" * 60)

    print("\n✅ All DORA metrics calculated successfully!")
    print("\n📝 Next steps:")
    print("   1. Set up .env with GITHUB_TOKEN and ANTHROPIC_API_KEY")
    print("   2. Run the dashboard: streamlit run app.py")
    print("   3. Enter a repository and analyze real data")

    return True


if __name__ == "__main__":
    success = test_dora_metrics()
    exit(0 if success else 1)

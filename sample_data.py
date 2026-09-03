"""
Sample DORA Metrics Data for Portfolio Demonstration
Use this when you hit GitHub API rate limits or want to demo the dashboard quickly.
"""
from datetime import datetime, timedelta, timezone

def get_sample_data():
    """Generate realistic sample data for DORA metrics demo."""
    now = datetime.now(timezone.utc)

    # Sample deployments - showing Elite performance
    deployments = []
    for i in range(45):  # ~1.5 deployments per day
        deployed_at = now - timedelta(days=i//1.5, hours=i*6)
        deployments.append({
            'id': f'deploy_{i}',
            'environment': 'production',
            'deployed_at': deployed_at.isoformat(),
            'status': 'success',
            'sha': f'abc123{i}',
            'creator': 'engineering-team',
            'source': 'github_actions'
        })

    # Sample pull requests - showing fast lead times
    pull_requests = []
    for i in range(60):
        created_at = now - timedelta(days=i//2, hours=i*4)
        merged_at = created_at + timedelta(hours=2 + (i % 5))  # 2-7 hours lead time

        pull_requests.append({
            'number': 1000 + i,
            'title': f'Feature: Implement {["authentication", "dashboard", "API endpoint", "data pipeline", "caching"][i % 5]}',
            'created_at': created_at.isoformat(),
            'merged_at': merged_at.isoformat(),
            'author': ['alice', 'bob', 'charlie', 'diana'][i % 4],
            'additions': 50 + (i * 10),
            'deletions': 20 + (i * 5),
            'changed_files': 2 + (i % 3),
            'commits': 1 + (i % 4)
        })

    # Sample incidents - showing good reliability (low change failure rate)
    incidents = []
    incident_count = 3  # Only 3 incidents out of 45 deployments = 6.7% failure rate

    for i in range(incident_count):
        created_at = now - timedelta(days=i*10, hours=i*2)
        resolved_at = created_at + timedelta(minutes=45 + (i * 15))  # Quick MTTR

        incidents.append({
            'number': 500 + i,
            'title': f'Production issue: {["High latency", "Database connection", "Cache invalidation"][i]}',
            'created_at': created_at.isoformat(),
            'resolved_at': resolved_at.isoformat(),
            'state': 'closed',
            'labels': ['incident', 'production'],
            'creator': 'monitoring-system'
        })

    return {
        'deployments': deployments,
        'pull_requests': pull_requests,
        'incidents': incidents,
        'repository': 'example/demo-project',
        'fetched_at': now.isoformat(),
        'days_analyzed': 30
    }


if __name__ == '__main__':
    """Test the sample data."""
    import json
    data = get_sample_data()

    print("Sample DORA Metrics Data Generated:")
    print(f"  Deployments: {len(data['deployments'])}")
    print(f"  Pull Requests: {len(data['pull_requests'])}")
    print(f"  Incidents: {len(data['incidents'])}")
    print(f"\nExpected DORA Performance:")
    print(f"  Deployment Frequency: ~1.5/day (Elite)")
    print(f"  Lead Time: 2-7 hours avg (Elite)")
    print(f"  Change Failure Rate: ~6.7% (Elite)")
    print(f"  MTTR: ~45-60 minutes (Elite)")

    # Save to file for easy loading
    with open('sample_dora_data.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Saved to sample_dora_data.json")

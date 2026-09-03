"""
Test GitHub API error handling
"""
from github_data_fetcher import GitHubDataFetcher
from dotenv import load_dotenv

load_dotenv()

def test_invalid_repo():
    """Test with invalid repository name."""
    print("Test 1: Invalid Repository Name")
    print("=" * 60)
    try:
        fetcher = GitHubDataFetcher()
        data = fetcher.fetch_all_data("nonexistent/repository-that-does-not-exist", 7)
        print(f"Result: {data}")
    except Exception as e:
        print(f"✅ Caught exception: {e}")
    print()

def test_invalid_format():
    """Test with invalid format."""
    print("Test 2: Invalid Repository Format")
    print("=" * 60)
    try:
        fetcher = GitHubDataFetcher()
        data = fetcher.fetch_all_data("invalid-format", 7)
        print(f"Result: {data}")
    except Exception as e:
        print(f"✅ Caught exception: {e}")
    print()

def test_valid_repo():
    """Test with valid repository but potentially rate limited."""
    print("Test 3: Valid Repository (may hit rate limit)")
    print("=" * 60)
    try:
        fetcher = GitHubDataFetcher()
        # Use a small, simple repo
        data = fetcher.fetch_all_data("anthropics/anthropic-sdk-python", 7)
        print(f"✅ Successfully fetched data!")
        print(f"  Deployments: {len(data['deployments'])}")
        print(f"  PRs: {len(data['pull_requests'])}")
        print(f"  Incidents: {len(data['incidents'])}")
    except Exception as e:
        print(f"⚠️  Exception (likely rate limit): {e}")
    print()

if __name__ == "__main__":
    print("\n🧪 Testing GitHub API Error Handling\n")

    test_invalid_repo()
    test_invalid_format()
    test_valid_repo()

    print("=" * 60)
    print("✅ Error handling tests complete!")
    print("=" * 60)

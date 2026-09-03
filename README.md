# DORA Metrics Dashboard

Production-ready dashboard for tracking the four key DORA (DevOps Research and Assessment) metrics that measure software delivery performance.

## Features

- **📊 Accurate DORA Metrics**: Deployment Frequency, Lead Time (commit→production), MTTR, Change Failure Rate
- **🎯 Data Quality Tracking**: Clear provenance indicators showing data sources and calculation methods
- **🔍 Process Compliance**: Detects direct commits bypassing PR workflow
- **🤖 AI-Powered Insights**: Claude-generated recommendations for improving metrics
- **📈 Interactive Visualizations**: Radar charts, timelines, distributions, and performance tracking
- **⚡ Real-time Analysis**: Configurable time periods (7-90 days)
- **✅ N/A Handling**: Honest "insufficient data" reporting instead of false positives
- **🔄 GitHub Integration**: Fetches real data from deployments, PRs, and incidents
- **🧪 Comprehensive Tests**: 17 pytest tests validating metric correctness

## Why This Project?

As an engineering manager, understanding and improving software delivery performance is critical. The DORA metrics provide a research-backed framework for measuring DevOps effectiveness.

## Recent Improvements

### Metric Validity Fixes (v2.0)
✅ **Lead Time** - Now calculates actual commit→production time, not PR cycle time
✅ **Change Failure Rate** - Correlates incidents to deployments within 24h window
✅ **Zero-Data Handling** - Returns N/A instead of misleading Elite ratings
✅ **Data Provenance** - Shows deployment sources and calculation methods
✅ **Professional Code** - Refactored 1200+ lines into modular architecture

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for detailed technical breakdown.

## The Four DORA Metrics

### 1. Deployment Frequency 🚀
How often you deploy to production
- **Elite**: Multiple times per day
- **High**: Once per day to once per week
- **Medium**: Once per week to once per month
- **Low**: Less than once per month

### 2. Lead Time for Changes ⏱️
Time from **first commit to production deployment**
- **Elite**: Less than one hour
- **High**: One day to one week
- **Medium**: One week to one month
- **Low**: More than one month

**Implementation**: Matches PR SHAs with deployment SHAs to calculate true commit→production time. Falls back to PR cycle time with clear labeling.

### 3. Mean Time to Restore (MTTR) 🔧
How quickly you recover from production failures
- **Elite**: Less than one hour
- **High**: Less than one day
- **Medium**: One day to one week
- **Low**: More than one week

### 4. Change Failure Rate ❌
Percentage of deployments causing production failures
- **Elite**: 0-15%
- **High**: 16-30%
- **Medium**: 31-45%
- **Low**: 46-100%

**Implementation**: Correlates incidents to deployments using:
1. Explicit deployment failure status
2. Time-window matching (incidents within 24h of deployment)

## Installation

```bash
git clone https://github.com/bulump/dora-metrics-dashboard.git
cd dora-metrics-dashboard
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your API keys:

```bash
GITHUB_TOKEN=your_github_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional - for AI insights
```

**Get your API keys:**
- GitHub Token: https://github.com/settings/tokens (needs `repo` scope)
- Anthropic API Key: https://console.anthropic.com (optional)

## Usage

### Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

### Using Demo Data

Click "Use Demo Data" checkbox to test without GitHub API calls. Demo data showcases Elite-level performance with realistic deployment patterns.

### Understanding Your Results

**Data Quality Indicators:**
- 🟢 **High** - 80%+ from GitHub Deployments API
- 🟡 **Medium** - 50-80% from API
- 🟠 **Low** - Mostly inferred from PRs/workflows

**Calculation Methods:**
- ✅ **commit_to_production** - True DORA lead time
- ⚠️ **pr_cycle_time_approximation** - Fallback when deployments don't match PRs

**N/A Levels:**
- Displayed when insufficient data (e.g., 0 deployments, 0 incidents)
- Excluded from overall performance calculation
- Prevents false "Elite" ratings on inactive repos

## How It Works

### Data Collection

The dashboard fetches data from three sources:

1. **Deployments** (3-tier detection system)
   - ✅ **Method 1: GitHub Deployments API** (most reliable)
     - Uses official GitHub deployment events
     - Requires GitHub Actions with `environment:` configuration
   - ✅ **Method 2: Workflow Runs** (good fallback)
     - Detects successful workflows with keywords: `deploy`, `release`, or `production` in name
     - Customizable via Advanced Settings
   - ⚠️ **Method 3: Inferred from PRs** (last resort)
     - Assumes merged PRs to `main`/`master` = deployments
     - Lower confidence, only used when Methods 1 & 2 find nothing

2. **Pull Requests**
   - Merged PRs for lead time calculation
   - **SHA matching** with deployments for true commit→production time
   - Falls back to PR cycle time (created→merged) when SHAs don't match
   - Created and merged timestamps

3. **Incidents**
   - GitHub issues with labels: `incident`, `production`, `outage`, `critical`, `p0`, `sev1`
   - **Customizable** via Advanced Settings for your team's labels
   - Created and resolved timestamps
   - Correlated to deployments via 24-hour time window

### Setting Up Your Repository for Accurate Metrics

For the best data quality, configure your repository to use GitHub deployment events:

#### Option 1: GitHub Environments (Recommended)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Creates deployment records
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        run: ./deploy.sh
```

#### Option 2: Deployment Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: chrnorm/deployment-action@v2
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          environment: production

      - name: Deploy
        run: ./deploy.sh
```

#### Option 3: Workflow Naming (Minimum)

If you can't use deployment events, name your workflows with keywords like:
- `Deploy to Production`
- `Release Pipeline`
- `Production Deployment`

The dashboard will detect these as deployments based on successful runs.

### Customizing Detection Settings

Use the **⚙️ Advanced Settings** in the sidebar to customize:

- **Incident Labels**: Change from default `incident, production, outage, critical, p0, sev1` to match your team's labels (e.g., `bug, hotfix, emergency`)
- **Deployment Branches**: Add branches beyond `main, master` (e.g., `production, release, stable`)
- **Workflow Keywords**: Customize keywords beyond `deploy, release, production` (e.g., `ship, publish, cd`)

### Architecture

```
dora-metrics-dashboard/
├── app.py                    # Main application (530 lines)
├── dora_calculator.py        # DORA metrics calculation logic
├── github_data_fetcher.py    # GitHub data fetching
├── ai_insights.py            # AI-powered insights generation
├── ui/                       # Modular UI components
│   ├── styles.py            # CSS styling
│   ├── metrics_display.py   # Metric display components
│   ├── charts.py            # Plotly visualizations
│   ├── data_tables.py       # Data tables & compliance
│   └── insights.py          # AI insights & summaries
├── test_dora_metrics.py     # Unit tests (17 tests)
├── requirements.txt         # Python dependencies
├── IMPROVEMENTS.md          # Technical improvements log
└── REFACTORING.md          # Code refactoring documentation
```

## Testing

Run the comprehensive test suite:

```bash
pytest test_dora_metrics.py -v
```

**Test Coverage:**
- Deployment Frequency (3 tests)
- Lead Time calculation (4 tests, including commit→production)
- MTTR (3 tests)
- Change Failure Rate (4 tests, including correlation)
- Overall Performance (3 tests, including N/A handling)

**All 17 tests passing ✅**

## Technology Stack

- **Python 3.9+** - Core language
- **Streamlit** - Interactive web dashboard
- **Claude AI (Anthropic)** - AI-powered insights (optional)
- **PyGithub** - GitHub API integration
- **Plotly** - Interactive visualizations
- **pytest** - Unit testing

## License

MIT License - free to use for your team!

## About

**Tech Stack:** Python · GitHub API · Streamlit · Claude AI · Plotly · pytest

"I wish I'd had this tool in my previous engineering leadership roles - it would have made performance measurement and improvement so much more **data-driven**, **accurate**, and **actionable**."

---

**Questions?** Open an issue on GitHub or reach out on LinkedIn.

**Documentation:**
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Technical improvements and metric fixes
- [REFACTORING.md](REFACTORING.md) - Code architecture and modularity

# DORA Metrics Dashboard

AI-powered dashboard for tracking the four key DORA (DevOps Research and Assessment) metrics that measure software delivery performance.

## Features

- **📊 Four Key DORA Metrics**: Deployment Frequency, Lead Time for Changes, MTTR, Change Failure Rate
- **🤖 AI-Powered Insights**: Claude-generated recommendations for improving your metrics
- **📈 Interactive Visualizations**: Radar charts, trend analysis, and performance comparisons
- **🎯 Performance Levels**: Automatic classification (Elite, High, Medium, Low) based on DORA research
- **🔄 GitHub Integration**: Fetches real data from deployments, PRs, and incidents
- **⚡ Real-time Analysis**: Configurable time periods (7-90 days)

## Why This Project?

As an engineering manager, understanding and improving software delivery performance is critical. The DORA metrics provide a research-backed framework for measuring DevOps effectiveness. However, calculating these metrics manually is time-consuming and error-prone.

This tool automates DORA metrics calculation and provides AI-powered insights to help engineering leaders:
1. **Measure performance** objectively across teams
2. **Identify bottlenecks** in the delivery pipeline
3. **Track improvement** over time
4. **Benchmark** against industry standards (Elite, High, Medium, Low)

## The Four DORA Metrics

### 1. Deployment Frequency 🚀
How often you deploy to production
- **Elite**: Multiple times per day
- **High**: Once per day to once per week
- **Medium**: Once per week to once per month
- **Low**: Less than once per month

### 2. Lead Time for Changes ⏱️
Time from commit to production deployment
- **Elite**: Less than one hour
- **High**: One day to one week
- **Medium**: One week to one month
- **Low**: More than one month

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

## Installation

```bash
git clone https://github.com/bulump/dora-metrics-dashboard.git
cd dora-metrics-dashboard
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your API keys:

```bash
GITHUB_TOKEN=your_github_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**Get your API keys:**
- GitHub Token: https://github.com/settings/tokens (needs `repo` scope)
- Anthropic API Key: https://console.anthropic.com

## Usage

### Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

### Using the Dashboard

1. **Enter Repository**: Format `owner/repo` (e.g., `bulump/dora-metrics-dashboard`)
2. **Select Time Period**: Choose 7-90 days for analysis
3. **Enable AI Insights**: Toggle for AI-powered recommendations
4. **Click "Fetch & Analyze"**: Dashboard will fetch and display metrics

### Understanding Your Results

The dashboard shows:
- **Overall DORA Performance**: Aggregate score (Elite/High/Medium/Low)
- **Individual Metric Cards**: Detailed breakdowns with performance levels
- **Radar Chart**: Visual comparison across all four metrics
- **AI Insights**: Specific recommendations for improvement

## How It Works

### Data Collection

The dashboard fetches data from three sources:

1. **Deployments**
   - GitHub Deployments API
   - Workflow runs (deploy/release workflows)
   - Inferred from merged PRs (fallback)

2. **Pull Requests**
   - Merged PRs for lead time calculation
   - Created and merged timestamps
   - Commit and change data

3. **Incidents**
   - GitHub issues with labels: `incident`, `production`, `outage`, `critical`, `p0`, `sev1`
   - Created and resolved timestamps

### Metric Calculation

**dora_calculator.py** implements the official DORA metrics calculations:

- **Deployment Frequency**: Deployments per day/week
- **Lead Time**: Median time from PR creation to merge
- **MTTR**: Median time from incident creation to resolution
- **Change Failure Rate**: Incidents per deployment

### AI Insights

**ai_insights.py** uses Claude AI to analyze metrics and generate:
- Overall performance assessment
- Key strengths identification
- Areas for improvement
- Specific, actionable recommendations

## Components

### Core Modules

**dora_calculator.py** - DORA Metrics Calculator
- Calculates all four DORA metrics
- Determines performance levels (Elite/High/Medium/Low)
- Computes overall performance score
- Statistical analysis (median, mean, P95)

**github_data_fetcher.py** - GitHub Data Fetcher
- Fetches deployments from multiple sources
- Retrieves merged PRs for lead time
- Collects incident data from issues
- Repository statistics

**ai_insights.py** - AI Insights Generator
- Claude AI integration
- Context-aware analysis
- Actionable recommendations
- Performance comparisons

**app.py** - Streamlit Dashboard
- Interactive web interface
- Plotly visualizations
- Real-time data fetching
- Configurable time periods

## Example Use Cases

### For Engineering Managers

**Scenario:** Quarterly performance review

1. Run DORA analysis for last 90 days
2. Review overall performance level (currently High)
3. Identify weakest metric (Lead Time: Medium)
4. Read AI recommendations: "Implement automated testing to reduce review cycles"
5. Set goals for next quarter: Move Lead Time from Medium to High

**Benefits:**
- Data-driven performance discussions
- Objective metrics for team improvements
- Clear benchmarking against industry standards
- Actionable improvement roadmap

### For DevOps Teams

**Scenario:** CI/CD pipeline optimization

1. Analyze current DORA metrics
2. Deployment Frequency: Low (monthly)
3. AI recommendation: "Implement feature flags to enable more frequent deployments"
4. After changes, track improvement over time
5. Compare before/after metrics

**Benefits:**
- Quantifiable improvement measurement
- Prioritized optimization efforts
- Evidence-based decision making

## Technology Stack

- **Python 3.9+** - Core language
- **Streamlit** - Interactive web dashboard
- **Claude AI (Anthropic)** - AI-powered insights
- **PyGithub** - GitHub API integration
- **Plotly** - Interactive visualizations

## Architecture

```
dora-metrics-dashboard/
├── app.py                    # Streamlit dashboard (main entry point)
├── dora_calculator.py        # DORA metrics calculation logic
├── github_data_fetcher.py    # GitHub data fetching
├── ai_insights.py            # AI-powered insights generation
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Customization

### Adding Custom Deployment Detection

Edit `github_data_fetcher.py`:

```python
def fetch_deployments(self, repo_name, since_date):
    # Add custom deployment detection logic
    # For example, detect from commit messages
    if 'deploy:' in commit.message:
        deployments.append({...})
```

### Changing Incident Labels

Edit `github_data_fetcher.py`:

```python
incident_labels = ['incident', 'production', 'outage', 'critical', 'p0', 'sev1']
# Add your custom labels
incident_labels.append('emergency')
```

### Adjusting Performance Thresholds

Edit `dora_calculator.py` to customize DORA level thresholds based on your organization's standards.

## Metrics & Impact

Based on DORA research (Accelerate State of DevOps Report):

- **Elite performers** deploy 208x more frequently than low performers
- **Elite performers** have 106x faster lead times
- **Elite performers** recover from incidents 2,604x faster
- **Elite performers** have 7x lower change failure rates

This dashboard helps teams measure and improve toward Elite performance.

## Future Enhancements

- [ ] Historical trend tracking (store metrics over time)
- [ ] Team comparison (compare multiple repositories)
- [ ] Slack/email alerts for metric degradation
- [ ] Integration with PagerDuty for incident data
- [ ] Custom metric definitions
- [ ] Export to CSV/PDF reports
- [ ] Multi-repository aggregation

## Use in Interviews

This project demonstrates:

**Engineering Management Skills**
- Understanding of DevOps metrics and best practices
- Data-driven decision making
- Process improvement mindset
- Industry research knowledge (DORA)

**Technical Skills**
- Python development
- API integration (GitHub)
- AI integration (Claude)
- Data visualization
- Web development (Streamlit)

**Business Value**
- Measurable impact on delivery performance
- Objective performance tracking
- Evidence-based improvement recommendations
- Industry benchmarking

**Interview Talking Points:**
- "I built this to help engineering teams measure and improve their software delivery performance using industry-standard DORA metrics..."
- "In my previous role, we struggled to objectively measure deployment velocity - this tool would have provided clear data for improvement..."
- "The AI insights feature generates specific, actionable recommendations based on your current metrics..."

## Contributing

This is a portfolio project, but suggestions are welcome! Open an issue or submit a pull request.

## License

MIT License - free to use for your team!

## About

Built by Chris Bielinski as a portfolio project demonstrating:
- Engineering management expertise in DevOps metrics
- AI integration capabilities with Claude
- Data visualization and dashboard development
- Software delivery performance optimization

I wish I'd had this tool in my previous engineering leadership roles - it would have made performance measurement and improvement so much more data-driven and actionable.

---

**Questions?** Open an issue on GitHub or reach out on LinkedIn.

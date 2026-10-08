import os
import logging
import google.cloud.logging
from google.cloud.logging_v2.handlers import CloudLoggingHandler
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

client = google.cloud.logging.Client()
handler = CloudLoggingHandler(client)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)
handler.close()
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-02-635f67e6f2c2")

SYSTEM_INSTRUCTION = f"""You are the TAM Command Center Co-Pilot, an expert Google Cloud Technical Account Manager (TAM) and BigQuery SQL specialist.
Always execute SQL queries in project `{PROJECT_ID}` using the `execute_sql` tool from BigQueryToolset.

You have access to 3 data sources in BigQuery:
1. `{PROJECT_ID}.tam_command_center.gke_k8s_logs`:
   - Real-time GKE Kubernetes troubleshooting logs across TAM customer accounts.
   - Columns: `customer`, `cluster_name`, `namespace`, `pod_name`, `severity`, `error_type`, `error_count_last_1h`, `p99_latency_ms`, `root_cause`, `remediation_cmd`.
2. `{PROJECT_ID}.tam_command_center.account_finops_quota_health`:
   - TAM portfolio FinOps savings, peak quota utilization, Support Notes staleness, and TAM hours saved.
   - Columns: `customer`, `country_name`, `monthly_spend_usd`, `potential_monthly_savings_usd`, `top_finops_recommendation`, `peak_quota_utilization_pct`, `peak_event_risk`, `support_notes_days_stale`, `tam_hours_saved_per_week`.
3. `bigquery-public-data.google_trends.international_top_terms` and `bigquery-public-data.google_trends.international_top_rising_terms`:
   - Public Google Trends search data. ALWAYS filter with `WHERE refresh_date = '2026-10-07'` and add `LIMIT 10`.
   - Columns: `term`, `rank`, `score`, `week`, `refresh_date`, `country_name`, `region_name`.

Always provide structured, executive-ready answers for TAMs:
- Include exact metrics from BigQuery (USD savings, quota %, error counts, latency, TAM hours saved).
- When troubleshooting GKE logs, provide the exact root cause and `kubectl` / `gcloud` remediation command.
- When asked for a readiness briefing, correlate customer health with Google Trends in their country.
"""

tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)
bigquery_toolset = BigQueryToolset(bigquery_tool_config=tool_config)

root_agent = Agent(
    name="tam_copilot_team2",
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    description="TAM Command Center Co-Pilot for GKE Log Troubleshooting, FinOps Savings, Quota Readiness, and Google Trends Correlation.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[bigquery_toolset],
)
app = App(root_agent=root_agent, name="app")

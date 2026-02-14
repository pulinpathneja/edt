"""
GCP Cost Monitoring Dashboard for EDT Project

Usage:
    python -m scripts.cost_monitor
    python -m scripts.cost_monitor --dashboard  # Start web dashboard

Requirements:
    pip install google-cloud-billing google-cloud-bigquery flask
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Google Cloud
try:
    from google.cloud import bigquery
    from google.cloud import billing_v1
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    print("Install: pip install google-cloud-billing google-cloud-bigquery")


@dataclass
class ServiceCost:
    """Cost breakdown by service."""
    service: str
    cost: float
    currency: str = "USD"
    period: str = "current_month"


@dataclass
class CostSummary:
    """Overall cost summary."""
    project_id: str
    total_cost: float
    currency: str
    period_start: str
    period_end: str
    services: List[ServiceCost]
    budget_limit: Optional[float] = None
    budget_used_percent: Optional[float] = None


class GCPCostMonitor:
    """Monitor GCP costs for the EDT project."""

    def __init__(self, project_id: str = None, billing_account: str = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "gen-lang-client-0518072406")
        self.billing_account = billing_account or os.getenv("GCP_BILLING_ACCOUNT", "0181EB-93E3BB-C2A9CC")

        # Budget configuration
        self.monthly_budget = float(os.getenv("MONTHLY_BUDGET", "100"))

        # Service cost estimates (Cloud Run pricing)
        self.estimated_costs = {
            "cloud_run": {
                "cpu_per_vcpu_second": 0.00002400,  # $0.024 per vCPU-hour
                "memory_per_gb_second": 0.00000250,  # $0.0025 per GB-hour
                "requests_per_million": 0.40,  # $0.40 per million requests
            },
            "cloud_sql": {
                "db_instance_per_hour": 0.0150,  # db-f1-micro
                "storage_per_gb_month": 0.17,
            },
            "cloud_build": {
                "build_minute": 0.003,  # $0.003 per build-minute
            },
            "container_registry": {
                "storage_per_gb_month": 0.026,
                "network_egress_per_gb": 0.12,
            },
        }

    def get_current_month_dates(self) -> tuple:
        """Get current month start and end dates."""
        today = datetime.now()
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    def estimate_cloud_run_cost(
        self,
        requests_per_day: int = 1000,
        avg_duration_ms: int = 200,
        memory_mb: int = 512,
        vcpus: int = 1,
    ) -> Dict:
        """Estimate Cloud Run costs based on usage."""
        days_in_month = 30

        # Requests
        total_requests = requests_per_day * days_in_month
        request_cost = (total_requests / 1_000_000) * self.estimated_costs["cloud_run"]["requests_per_million"]

        # CPU time
        total_cpu_seconds = total_requests * (avg_duration_ms / 1000) * vcpus
        cpu_cost = total_cpu_seconds * self.estimated_costs["cloud_run"]["cpu_per_vcpu_second"]

        # Memory time
        memory_gb = memory_mb / 1024
        total_memory_gb_seconds = total_requests * (avg_duration_ms / 1000) * memory_gb
        memory_cost = total_memory_gb_seconds * self.estimated_costs["cloud_run"]["memory_per_gb_second"]

        total = request_cost + cpu_cost + memory_cost

        return {
            "service": "Cloud Run",
            "requests": total_requests,
            "request_cost": round(request_cost, 2),
            "cpu_cost": round(cpu_cost, 2),
            "memory_cost": round(memory_cost, 2),
            "total_estimated": round(total, 2),
        }

    def estimate_cloud_sql_cost(
        self,
        hours_per_day: int = 24,
        storage_gb: int = 10,
    ) -> Dict:
        """Estimate Cloud SQL costs."""
        days_in_month = 30

        # Instance hours
        total_hours = hours_per_day * days_in_month
        instance_cost = total_hours * self.estimated_costs["cloud_sql"]["db_instance_per_hour"]

        # Storage
        storage_cost = storage_gb * self.estimated_costs["cloud_sql"]["storage_per_gb_month"]

        total = instance_cost + storage_cost

        return {
            "service": "Cloud SQL",
            "instance_hours": total_hours,
            "instance_cost": round(instance_cost, 2),
            "storage_gb": storage_gb,
            "storage_cost": round(storage_cost, 2),
            "total_estimated": round(total, 2),
        }

    def get_cost_summary(self) -> CostSummary:
        """Get overall cost summary with estimates."""
        start_date, end_date = self.get_current_month_dates()

        # Estimate costs
        cloud_run = self.estimate_cloud_run_cost(
            requests_per_day=500,  # Conservative estimate
            avg_duration_ms=300,
            memory_mb=4096,  # 4GB as configured
            vcpus=2,
        )

        cloud_sql = self.estimate_cloud_sql_cost(
            hours_per_day=24,
            storage_gb=10,
        )

        cloud_build = {
            "service": "Cloud Build",
            "total_estimated": 2.00,  # ~10 builds/month at 5 min each
        }

        services = [
            ServiceCost(
                service="Cloud Run (EDT API)",
                cost=cloud_run["total_estimated"],
            ),
            ServiceCost(
                service="Cloud SQL (PostgreSQL)",
                cost=cloud_sql["total_estimated"],
            ),
            ServiceCost(
                service="Cloud Build",
                cost=cloud_build["total_estimated"],
            ),
            ServiceCost(
                service="Container Registry",
                cost=1.00,  # Minimal storage
            ),
        ]

        total_cost = sum(s.cost for s in services)
        budget_percent = (total_cost / self.monthly_budget) * 100 if self.monthly_budget else None

        return CostSummary(
            project_id=self.project_id,
            total_cost=round(total_cost, 2),
            currency="USD",
            period_start=start_date,
            period_end=end_date,
            services=services,
            budget_limit=self.monthly_budget,
            budget_used_percent=round(budget_percent, 1) if budget_percent else None,
        )

    def print_dashboard(self):
        """Print cost dashboard to console."""
        summary = self.get_cost_summary()

        print("\n" + "=" * 60)
        print("EDT PROJECT - GCP COST DASHBOARD")
        print("=" * 60)
        print(f"\nProject: {summary.project_id}")
        print(f"Period: {summary.period_start} to {summary.period_end}")
        print(f"Monthly Budget: ${summary.budget_limit:.2f}")
        print("")

        # Budget bar
        if summary.budget_used_percent:
            bar_width = 40
            filled = int(bar_width * min(summary.budget_used_percent, 100) / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            status = "OK" if summary.budget_used_percent < 80 else "WARNING" if summary.budget_used_percent < 100 else "OVER"
            print(f"Budget Usage: [{bar}] {summary.budget_used_percent}% ({status})")

        print("")
        print("-" * 60)
        print("ESTIMATED COSTS BY SERVICE")
        print("-" * 60)

        for service in summary.services:
            print(f"  {service.service:<30} ${service.cost:>8.2f}")

        print("-" * 60)
        print(f"  {'TOTAL ESTIMATED':<30} ${summary.total_cost:>8.2f}")
        print("=" * 60)

        # Cost optimization tips
        print("\nCOST OPTIMIZATION TIPS:")
        print("  - Set min-instances=0 for Cloud Run (pay only when used)")
        print("  - Use db-f1-micro for development")
        print("  - Enable Cloud SQL auto-pause if available")
        print("  - Clean up unused container images")

        # Links
        print("\nUSEFUL LINKS:")
        print(f"  Billing: https://console.cloud.google.com/billing/0181EB-93E3BB-C2A9CC/reports?project={summary.project_id}")
        print(f"  Budgets: https://console.cloud.google.com/billing/0181EB-93E3BB-C2A9CC/budgets?project={summary.project_id}")
        print(f"  Cloud Run: https://console.cloud.google.com/run?project={summary.project_id}")
        print("")


def create_flask_dashboard():
    """Create a simple Flask dashboard for cost monitoring."""
    try:
        from flask import Flask, render_template_string, jsonify
    except ImportError:
        print("Install Flask: pip install flask")
        return None

    app = Flask(__name__)
    monitor = GCPCostMonitor()

    DASHBOARD_HTML = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EDT - GCP Cost Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            .card { background: white; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #333; }
            .budget-bar { background: #e0e0e0; border-radius: 10px; height: 30px; overflow: hidden; }
            .budget-fill { height: 100%; transition: width 0.3s; }
            .budget-fill.ok { background: #4caf50; }
            .budget-fill.warning { background: #ff9800; }
            .budget-fill.danger { background: #f44336; }
            .cost-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
            .cost-item:last-child { border-bottom: none; }
            .total { font-weight: bold; font-size: 1.2em; color: #333; }
            .links a { display: block; color: #1976d2; margin: 5px 0; }
            .refresh-btn { background: #1976d2; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>EDT - GCP Cost Dashboard</h1>
            <p>Project: {{ summary.project_id }}</p>
        </div>

        <div class="card">
            <h3>Monthly Budget: ${{ summary.budget_limit }}</h3>
            <div class="budget-bar">
                <div class="budget-fill {{ 'ok' if summary.budget_used_percent < 80 else 'warning' if summary.budget_used_percent < 100 else 'danger' }}"
                     style="width: {{ min(summary.budget_used_percent, 100) }}%">
                </div>
            </div>
            <p style="text-align: center; margin-top: 10px;">
                {{ summary.budget_used_percent }}% used (${{ summary.total_cost }} of ${{ summary.budget_limit }})
            </p>
        </div>

        <div class="card">
            <h3>Cost Breakdown (Estimated)</h3>
            {% for service in summary.services %}
            <div class="cost-item">
                <span>{{ service.service }}</span>
                <span>${{ "%.2f"|format(service.cost) }}</span>
            </div>
            {% endfor %}
            <div class="cost-item total">
                <span>TOTAL</span>
                <span>${{ "%.2f"|format(summary.total_cost) }}</span>
            </div>
        </div>

        <div class="card links">
            <h3>Quick Links</h3>
            <a href="https://console.cloud.google.com/billing/0181EB-93E3BB-C2A9CC/reports?project={{ summary.project_id }}" target="_blank">View Billing Reports</a>
            <a href="https://console.cloud.google.com/billing/0181EB-93E3BB-C2A9CC/budgets?project={{ summary.project_id }}" target="_blank">Manage Budgets</a>
            <a href="https://console.cloud.google.com/run?project={{ summary.project_id }}" target="_blank">Cloud Run Services</a>
            <a href="https://console.cloud.google.com/sql/instances?project={{ summary.project_id }}" target="_blank">Cloud SQL Instances</a>
        </div>

        <div style="text-align: center; margin-top: 20px;">
            <button class="refresh-btn" onclick="location.reload()">Refresh</button>
        </div>
    </body>
    </html>
    """

    @app.route("/")
    def dashboard():
        summary = monitor.get_cost_summary()
        return render_template_string(DASHBOARD_HTML, summary=summary)

    @app.route("/api/costs")
    def api_costs():
        summary = monitor.get_cost_summary()
        return jsonify({
            "project_id": summary.project_id,
            "total_cost": summary.total_cost,
            "budget_limit": summary.budget_limit,
            "budget_used_percent": summary.budget_used_percent,
            "services": [asdict(s) for s in summary.services],
            "period": {
                "start": summary.period_start,
                "end": summary.period_end,
            }
        })

    return app


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GCP Cost Monitor for EDT")
    parser.add_argument("--dashboard", action="store_true", help="Start web dashboard")
    parser.add_argument("--port", type=int, default=5050, help="Dashboard port")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    monitor = GCPCostMonitor()

    if args.dashboard:
        app = create_flask_dashboard()
        if app:
            print(f"\nStarting Cost Dashboard at http://localhost:{args.port}")
            app.run(host="0.0.0.0", port=args.port, debug=True)
    elif args.json:
        summary = monitor.get_cost_summary()
        print(json.dumps({
            "project_id": summary.project_id,
            "total_cost": summary.total_cost,
            "budget_limit": summary.budget_limit,
            "budget_used_percent": summary.budget_used_percent,
            "services": [asdict(s) for s in summary.services],
        }, indent=2))
    else:
        monitor.print_dashboard()


if __name__ == "__main__":
    main()

#!/bin/bash
# Set up GCP Budget and Alerts for EDT Project

set -e

PROJECT_ID="${GCP_PROJECT_ID:-reinovate-363109}"
BILLING_ACCOUNT="0181EB-93E3BB-C2A9CC"  # My Billing Account 2 (OPEN)
BUDGET_NAME="EDT-Monthly-Budget"
BUDGET_AMOUNT="${BUDGET_AMOUNT:-100}"  # Default $100/month
ALERT_EMAIL="${ALERT_EMAIL:-pulinpathneja@gmail.com}"

echo "========================================"
echo "Setting up GCP Budget for EDT Project"
echo "========================================"
echo ""
echo "Project: ${PROJECT_ID}"
echo "Budget: \$${BUDGET_AMOUNT}/month"
echo "Alerts: 50%, 80%, 100%"
echo ""

# Enable billing budget API
echo "Enabling Billing Budget API..."
gcloud services enable billingbudgets.googleapis.com --project=${PROJECT_ID} --quiet 2>/dev/null || true

# Create budget using gcloud (requires beta)
echo "Creating budget..."

# Note: Creating budgets via CLI requires the billingbudgets API
# For now, we'll provide the console URL and a script to check costs

echo ""
echo "========================================"
echo "Budget Setup Instructions"
echo "========================================"
echo ""
echo "To create a budget via GCP Console:"
echo "1. Go to: https://console.cloud.google.com/billing/${BILLING_ACCOUNT}/budgets?project=${PROJECT_ID}"
echo "2. Click 'CREATE BUDGET'"
echo "3. Set budget name: ${BUDGET_NAME}"
echo "4. Set budget amount: \$${BUDGET_AMOUNT}"
echo "5. Set thresholds: 50%, 80%, 100%"
echo "6. Add email alerts to: ${ALERT_EMAIL}"
echo ""

# Get current month's costs
echo "========================================"
echo "Current Cost Summary"
echo "========================================"

# Check if billing export is configured
echo ""
echo "To view current costs:"
echo "  https://console.cloud.google.com/billing/${BILLING_ACCOUNT}/reports?project=${PROJECT_ID}"
echo ""
echo "To set up cost export to BigQuery:"
echo "  https://console.cloud.google.com/billing/${BILLING_ACCOUNT}/export?project=${PROJECT_ID}"
echo ""

# List services and their costs (via Cost Management API)
echo "========================================"
echo "Active Services in Project"
echo "========================================"
gcloud services list --enabled --project=${PROJECT_ID} --format="table(config.name)" 2>/dev/null | head -20

echo ""
echo "========================================"
echo "Cost Monitoring Dashboard"
echo "========================================"
echo ""
echo "View costs at:"
echo "  https://console.cloud.google.com/billing/${BILLING_ACCOUNT}/reports?project=${PROJECT_ID}"
echo ""
echo "Cloud Run costs:"
echo "  https://console.cloud.google.com/run?project=${PROJECT_ID}"
echo ""
echo "Cloud SQL costs:"
echo "  https://console.cloud.google.com/sql/instances?project=${PROJECT_ID}"
echo ""

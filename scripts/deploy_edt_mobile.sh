#!/bin/bash

# Deploy EDT Mobile (Expo) Web App to Cloud Run
# Run: ./scripts/deploy_edt_mobile.sh

set -e

echo "========================================"
echo "EDT Mobile App - Cloud Run Deployment"
echo "========================================"

PROJECT_ID="gen-lang-client-0518072406"
REGION="us-central1"
SERVICE_NAME="edt-mobile-app"
APP_DIR="edt-mobile"

# Check if we're in the right directory
if [ ! -d "$APP_DIR" ]; then
    echo "Error: edt-mobile directory not found"
    echo "Run this script from the EDT project root"
    exit 1
fi

echo ""
echo "Step 1: Building Expo web export..."
cd $APP_DIR
npx expo export --platform web

echo ""
echo "Step 2: Building Docker image via Cloud Build..."
gcloud builds submit \
    --project=$PROJECT_ID \
    --tag=gcr.io/$PROJECT_ID/$SERVICE_NAME \
    .

echo ""
echo "Step 3: Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --project=$PROJECT_ID \
    --region=$REGION \
    --image=gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform=managed \
    --allow-unauthenticated \
    --port=8080 \
    --memory=256Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3

echo ""
echo "========================================"
echo "DEPLOYMENT COMPLETE!"
echo "========================================"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --project=$PROJECT_ID \
    --region=$REGION \
    --format='value(status.url)')

echo ""
echo "Your EDT Mobile app is live at:"
echo "  $SERVICE_URL"
echo ""

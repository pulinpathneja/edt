#!/bin/bash

# Deploy Flutter Web App to Cloud Run
# Run: ./scripts/deploy_flutter_cloudrun.sh

set -e

echo "========================================"
echo "EDT Flutter App - Cloud Run Deployment"
echo "========================================"

PROJECT_ID="gen-lang-client-0518072406"
REGION="us-central1"
SERVICE_NAME="edt-flutter-app"
FLUTTER_APP_DIR="flutter_app"

# Check if we're in the right directory
if [ ! -d "$FLUTTER_APP_DIR" ]; then
    echo "Error: flutter_app directory not found"
    echo "Run this script from the EDT project root"
    exit 1
fi

echo ""
echo "Step 1: Building Flutter web app..."
cd $FLUTTER_APP_DIR
flutter build web --release

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
echo "Your Flutter app is live at:"
echo "  $SERVICE_URL"
echo ""

#!/bin/bash

# Deploy Flutter Web App to Firebase Hosting
# Run: ./scripts/deploy_flutter.sh

set -e

echo "========================================"
echo "EDT Flutter App Deployment"
echo "========================================"

PROJECT_ID="gen-lang-client-0518072406"
FLUTTER_APP_DIR="flutter_app"

# Check if we're in the right directory
if [ ! -d "$FLUTTER_APP_DIR" ]; then
    echo "Error: flutter_app directory not found"
    echo "Run this script from the EDT project root"
    exit 1
fi

echo ""
echo "Step 1: Getting Flutter dependencies..."
cd $FLUTTER_APP_DIR
flutter pub get

echo ""
echo "Step 2: Building Flutter web app..."
flutter build web --release

echo ""
echo "Step 3: Deploying to Firebase Hosting..."
cd ..
firebase deploy --only hosting --project $PROJECT_ID

echo ""
echo "========================================"
echo "DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "Your app is live at:"
echo "  https://${PROJECT_ID}.web.app"
echo "  https://${PROJECT_ID}.firebaseapp.com"
echo ""

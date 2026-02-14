#!/bin/bash
# Deploy EDT Travel Itinerary API to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-gen-lang-client-0518072406}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="edt-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploying EDT Travel Itinerary API${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 > /dev/null 2>&1; then
    echo -e "${RED}Error: Not authenticated with gcloud. Run: gcloud auth login${NC}"
    exit 1
fi

# Set the project
echo -e "${YELLOW}Setting GCP project...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet

# Build the Docker image using Cloud Build
echo -e "${YELLOW}Building Docker image with Cloud Build...${NC}"
gcloud builds submit --tag ${IMAGE_NAME}:latest .

# Get database URL from environment or use default
DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://edt_user:EdtSecure2024@34.46.220.220:5432/edt_db}"

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 4Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300 \
    --cpu-boost \
    --execution-environment gen2 \
    --set-env-vars "DATABASE_URL=${DATABASE_URL}" \
    --set-env-vars "APP_NAME=EDT Itinerary System" \
    --set-env-vars "DEBUG=false" \
    --set-env-vars "EMBEDDING_MODEL=BAAI/bge-small-en-v1.5" \
    --set-env-vars "EMBEDDING_DIMENSION=384"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format="value(status.url)")

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Service URL: ${GREEN}${SERVICE_URL}${NC}"
echo -e "API Docs: ${GREEN}${SERVICE_URL}/docs${NC}"
echo -e "Health Check: ${GREEN}${SERVICE_URL}/health${NC}"
echo ""
echo "To view logs:"
echo "  gcloud run logs read --service ${SERVICE_NAME} --region ${REGION}"
echo ""
echo "To update the service:"
echo "  ./deploy_gcp.sh"

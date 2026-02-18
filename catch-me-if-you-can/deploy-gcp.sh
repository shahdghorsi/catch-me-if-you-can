#!/bin/bash
set -e

# ============================================================
# GCP Cloud Run Deployment Script
# Catch Me If You Can - Office Serendipity App
# ============================================================

# CONFIGURATION - Update these values
PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
REGION="europe-west2"
SERVICE_NAME="catch-me-if-you-can"
REPO_NAME="catch-me-if-you-can"
IMAGE_NAME="app"
COMPANY_DOMAIN="virginmediao2.co.uk"

echo "============================================"
echo "Deploying $SERVICE_NAME to GCP Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "============================================"

# ------------------------------------------------------------
# STEP 1: Set project
# ------------------------------------------------------------
echo ""
echo "[1/7] Setting GCP project..."
gcloud config set project $PROJECT_ID

# ------------------------------------------------------------
# STEP 2: Enable required APIs
# ------------------------------------------------------------
echo ""
echo "[2/7] Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    iap.googleapis.com

# ------------------------------------------------------------
# STEP 3: Create Artifact Registry repository (if not exists)
# ------------------------------------------------------------
echo ""
echo "[3/7] Creating Artifact Registry repository..."
gcloud artifacts repositories describe $REPO_NAME \
    --location=$REGION \
    --project=$PROJECT_ID 2>/dev/null || \
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Catch Me If You Can container images"

# ------------------------------------------------------------
# STEP 4: Configure Docker authentication
# ------------------------------------------------------------
echo ""
echo "[4/7] Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# ------------------------------------------------------------
# STEP 5: Build and push container image
# ------------------------------------------------------------
echo ""
echo "[5/7] Building and pushing container image..."
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest"

docker build -t $IMAGE_URI .
docker push $IMAGE_URI

# ------------------------------------------------------------
# STEP 6: Deploy to Cloud Run
# ------------------------------------------------------------
echo ""
echo "[6/7] Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_URI \
    --region=$REGION \
    --platform=managed \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3 \
    --port=8080 \
    --timeout=300 \
    --session-affinity \
    --ingress=internal-and-cloud-load-balancing \
    --no-allow-unauthenticated \
    --set-env-vars="FLASK_DEBUG=false,SECRET_KEY=$(openssl rand -hex 32)"

# ------------------------------------------------------------
# STEP 7: Restrict access to company domain
# ------------------------------------------------------------
echo ""
echo "[7/7] Configuring IAM access for $COMPANY_DOMAIN..."

# Grant access to all authenticated users from the company domain
gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --region=$REGION \
    --member="domain:$COMPANY_DOMAIN" \
    --role="roles/run.invoker"

# ------------------------------------------------------------
# COMPLETE
# ------------------------------------------------------------
echo ""
echo "============================================"
echo "DEPLOYMENT COMPLETE"
echo "============================================"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "Access restricted to: *@$COMPANY_DOMAIN"
echo ""
echo "Users must authenticate with their Google Workspace"
echo "account to access the application."
echo "============================================"

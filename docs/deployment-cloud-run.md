# Google Cloud Run Deployment Setup

This document provides step-by-step instructions to configure Google Cloud for deploying your application using the Cloud Run GitHub Actions workflow.

## Prerequisites

- Google Cloud Project with billing enabled
- `gcloud` CLI installed and authenticated
- GitHub repository with the deployment workflow

## Required Placeholders

Replace these placeholders in `.github/workflows/deploy-cloud-run.yml` and in the commands below:

- `REPLACE_WITH_GCP_PROJECT_ID`: Your Google Cloud Project ID
- `REPLACE_WITH_GCP_PROJECT_NUMBER`: Your Google Cloud Project Number
- `REPLACE_WITH_CLOUD_RUN_REGION`: Target region (e.g., `us-central1`, `europe-west1`)
- `REPLACE_WITH_CLOUD_RUN_SERVICE_NAME`: Name for your Cloud Run service
- `REPLACE_WITH_SERVICE_ACCOUNT_EMAIL`: Email of the service account for deployment
- `REPLACE_WITH_WIF_POOL_ID`: Workload Identity Pool ID (for WIF setup)
- `REPLACE_WITH_WIF_PROVIDER_ID`: Workload Identity Provider ID (for WIF setup)

## Step 1: Enable Required APIs

```bash
# Enable necessary Google Cloud APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  iamcredentials.googleapis.com \
  --project=REPLACE_WITH_GCP_PROJECT_ID
```

## Step 2: Create Artifact Registry Repository

```bash
# Create Docker repository in Artifact Registry
gcloud artifacts repositories create contenedores \
  --repository-format=docker \
  --location=REPLACE_WITH_CLOUD_RUN_REGION \
  --description="Container images for Cloud Run deployment" \
  --project=REPLACE_WITH_GCP_PROJECT_ID
```

## Step 3: Create Service Account

```bash
# Create service account for deployment
gcloud iam service-accounts create cloud-run-deployer \
  --display-name="Cloud Run Deployer" \
  --description="Service account for GitHub Actions Cloud Run deployment" \
  --project=REPLACE_WITH_GCP_PROJECT_ID
```

## Step 4: Grant Required IAM Roles

```bash
# Set variables for convenience
export PROJECT_ID="REPLACE_WITH_GCP_PROJECT_ID"
export SA_EMAIL="cloud-run-deployer@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant minimum required roles for Cloud Run deployment
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Optional: If using Cloud Build
# gcloud projects add-iam-policy-binding $PROJECT_ID \
#   --member="serviceAccount:${SA_EMAIL}" \
#   --role="roles/cloudbuild.builds.editor"
```

## Step 5: Authentication Setup

### Option A: Workload Identity Federation (RECOMMENDED)

Workload Identity Federation allows GitHub Actions to authenticate without storing long-lived JSON keys.

```bash
# Set variables
export PROJECT_ID="REPLACE_WITH_GCP_PROJECT_ID"
export PROJECT_NUMBER="REPLACE_WITH_GCP_PROJECT_NUMBER"
export POOL_ID="github-pool"
export PROVIDER_ID="github-provider"
export SA_EMAIL="cloud-run-deployer@${PROJECT_ID}.iam.gserviceaccount.com"
export REPO="emerrbdva/sga-iso14001-2026"  # Replace with your GitHub repo

# Create Workload Identity Pool
gcloud iam workload-identity-pools create $POOL_ID \
  --project=$PROJECT_ID \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create Workload Identity Provider
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_ID \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool=$POOL_ID \
  --display-name="GitHub Actions Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Allow GitHub Actions to impersonate the service account
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --project=$PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/attribute.repository/$REPO"

# Get the Workload Identity Provider resource name
echo "Workload Identity Provider:"
echo "projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/providers/$PROVIDER_ID"
```

**Update your workflow file** with these values:
- `REPLACE_WITH_WIF_POOL_ID`: Use `$POOL_ID` (e.g., `github-pool`)
- `REPLACE_WITH_WIF_PROVIDER_ID`: Use `$PROVIDER_ID` (e.g., `github-provider`)
- `REPLACE_WITH_SERVICE_ACCOUNT_EMAIL`: Use `$SA_EMAIL`

### Option B: JSON Key Authentication (NOT RECOMMENDED)

Only use this if Workload Identity Federation is not suitable for your setup.

```bash
# Create and download service account key
gcloud iam service-accounts keys create key.json \
  --iam-account=cloud-run-deployer@REPLACE_WITH_GCP_PROJECT_ID.iam.gserviceaccount.com \
  --project=REPLACE_WITH_GCP_PROJECT_ID

# Add the contents of key.json as a GitHub secret named GCP_SA_KEY
echo "Add the contents of key.json as a GitHub repository secret named 'GCP_SA_KEY'"
echo "Then delete the local key file for security"
```

**Important**: 
1. Add the JSON key content as a GitHub repository secret named `GCP_SA_KEY`
2. Delete the local `key.json` file
3. Uncomment the JSON key authentication section in the workflow
4. Comment out or remove the Workload Identity Federation section

## Step 6: Configure GitHub Repository

1. Go to your GitHub repository settings
2. Navigate to **Settings > Secrets and variables > Actions**
3. If using JSON key authentication (Option B), add `GCP_SA_KEY` secret
4. Update the workflow file placeholders with your actual values

## Step 7: Test Deployment

1. Update all placeholders in `.github/workflows/deploy-cloud-run.yml`
2. Remove or comment out the unused authentication option
3. Commit and push to the `main` branch, or manually trigger the workflow
4. Monitor the workflow execution in the GitHub Actions tab

## Multi-Service Deployment

This repository contains multiple services in the `services/` directory. The current workflow defaults to deploying the `core_sga` service. To deploy a different service:

1. Modify the build logic in the workflow file
2. Update the `DOCKERFILE_PATH` and potentially the `CONTEXT_PATH`
3. Consider creating separate workflows for each service
4. Use different service names and image repositories for each service

Available services:
- `core_sga` (port 8000)
- `ai_engine` (port 8001)
- `risk_engine` (port 8002)
- `compliance_engine` (port 8003)
- `objectives_engine` (port 8004)
- `ghg_engine` (port 8005)
- `reporting_engine`
- `audit_engine`

## Security Best Practices

1. **Use Workload Identity Federation** instead of JSON keys
2. **Apply principle of least privilege** - grant only necessary IAM roles
3. **Use environments** for production deployments to add approval gates
4. **Scope deployment triggers** appropriately (e.g., deploy only from main branch)
5. **Review and audit** service account permissions regularly
6. **Monitor deployment logs** and set up alerting for failures

## Troubleshooting

### Common Issues

1. **Authentication failures**: Verify service account permissions and WIF configuration
2. **Image push failures**: Check Artifact Registry permissions and repository existence
3. **Deployment failures**: Review Cloud Run service configuration and resource limits
4. **Build failures**: Ensure Dockerfile path is correct for multi-service repository

### Debug Commands

```bash
# Check current gcloud configuration
gcloud config list

# Test authentication
gcloud auth list

# Verify Artifact Registry repository
gcloud artifacts repositories list --location=REPLACE_WITH_CLOUD_RUN_REGION

# Check Cloud Run services
gcloud run services list --region=REPLACE_WITH_CLOUD_RUN_REGION

# View service logs
gcloud logs read --resource="cloud_run_revision" --limit=50
```

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GitHub Actions for Google Cloud](https://github.com/google-github-actions)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
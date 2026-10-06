#!/usr/bin/env bash
# Idempotent GCP bootstrap for stack-pulse. Safe to re-run.
#
# Creates: required APIs, BigQuery dataset `raw`, pipeline service account,
# and a Workload Identity Federation pool so GitHub Actions can impersonate
# that service account without any JSON key.
#
# Usage: GCP_PROJECT_ID=my-project ./scripts/bootstrap_gcp.sh
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
LOCATION="${BQ_LOCATION:-US}"
RAW_DATASET="${BQ_RAW_DATASET:-raw}"
GITHUB_REPO="${GITHUB_REPO:-max-mena/stack-pulse}"
SA_NAME="stack-pulse-pipeline"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
POOL_ID="github"
PROVIDER_ID="stack-pulse"

step() { printf '\n==> %s\n' "$*"; }

gcloud config set project "$PROJECT_ID" >/dev/null
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"

step "Enabling APIs"
gcloud services enable \
  bigquery.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com

step "BigQuery dataset ${RAW_DATASET} (${LOCATION})"
if bq --project_id="$PROJECT_ID" show --dataset "${PROJECT_ID}:${RAW_DATASET}" >/dev/null 2>&1; then
  echo "exists"
else
  bq --project_id="$PROJECT_ID" --location="$LOCATION" mk --dataset \
    --description "Raw API payloads landed by stack-pulse ingestion" \
    "${PROJECT_ID}:${RAW_DATASET}"
fi

step "Service account ${SA_EMAIL}"
if gcloud iam service-accounts describe "$SA_EMAIL" >/dev/null 2>&1; then
  echo "exists"
else
  gcloud iam service-accounts create "$SA_NAME" --display-name "stack-pulse pipeline"
fi
for role in roles/bigquery.dataEditor roles/bigquery.jobUser; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:${SA_EMAIL}" --role "$role" --condition=None >/dev/null
  echo "granted $role"
done

step "Workload Identity pool ${POOL_ID}"
if gcloud iam workload-identity-pools describe "$POOL_ID" --location global >/dev/null 2>&1; then
  echo "exists"
else
  gcloud iam workload-identity-pools create "$POOL_ID" --location global \
    --display-name "GitHub Actions"
fi

step "OIDC provider ${PROVIDER_ID} (only ${GITHUB_REPO})"
if gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
    --workload-identity-pool "$POOL_ID" --location global >/dev/null 2>&1; then
  echo "exists"
else
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
    --workload-identity-pool "$POOL_ID" --location global \
    --issuer-uri "https://token.actions.githubusercontent.com" \
    --attribute-mapping "google.subject=assertion.sub,attribute.repository=assertion.repository" \
    --attribute-condition "assertion.repository == '${GITHUB_REPO}'"
fi

step "Allow ${GITHUB_REPO} to impersonate ${SA_NAME}"
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --role roles/iam.workloadIdentityUser \
  --member "principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${GITHUB_REPO}" \
  >/dev/null
echo "granted roles/iam.workloadIdentityUser"

cat <<EOF

Done. Add these as GitHub repository *Variables* (not secrets; they are not sensitive):

  gh variable set GCP_PROJECT_ID   --body "${PROJECT_ID}"
  gh variable set GCP_SA_EMAIL     --body "${SA_EMAIL}"
  gh variable set GCP_WIF_PROVIDER --body "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
EOF

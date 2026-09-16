#!/usr/bin/env bash
# ============================================================
# SolveNow — PostgreSQL Backup Script
# ============================================================
# Backs up the production database and uploads to S3.
# Designed to be run as a daily cron job.
#
# Required environment variables (same as .env.production):
#   POSTGRES_SERVER, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
#   S3_ENDPOINT_URL, S3_BUCKET_NAME, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY
#
# Cron example (daily at 02:00 UTC):
#   0 2 * * * /opt/solvenow/infrastructure/scripts/backup.sh >> /var/log/solvenow-backup.log 2>&1
# ============================================================
set -euo pipefail

# --- Configuration ---
TIMESTAMP=$(date -u +"%Y-%m-%dT%H-%M-%SZ")
BACKUP_FILENAME="solvenow-db-${TIMESTAMP}.dump"
BACKUP_PATH="/tmp/${BACKUP_FILENAME}"
S3_KEY="backups/postgres/${BACKUP_FILENAME}"
RETENTION_DAYS=30

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting database backup..."

# --- Validate required environment variables ---
: "${POSTGRES_SERVER:?POSTGRES_SERVER must be set}"
: "${POSTGRES_USER:?POSTGRES_USER must be set}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}"
: "${POSTGRES_DB:?POSTGRES_DB must be set}"
: "${S3_BUCKET_NAME:?S3_BUCKET_NAME must be set}"

# --- Create backup using pg_dump custom format (compressed, parallel-restoreable) ---
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    --host="${POSTGRES_SERVER}" \
    --port="${POSTGRES_PORT:-5432}" \
    --username="${POSTGRES_USER}" \
    --dbname="${POSTGRES_DB}" \
    --format=custom \
    --compress=9 \
    --verbose \
    --file="${BACKUP_PATH}"

BACKUP_SIZE=$(du -sh "${BACKUP_PATH}" | cut -f1)
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Backup created: ${BACKUP_FILENAME} (${BACKUP_SIZE})"

# --- Upload to S3-compatible storage ---
AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY_ID}" \
AWS_SECRET_ACCESS_KEY="${S3_SECRET_ACCESS_KEY}" \
aws s3 cp \
    "${BACKUP_PATH}" \
    "s3://${S3_BUCKET_NAME}/${S3_KEY}" \
    ${S3_ENDPOINT_URL:+--endpoint-url "${S3_ENDPOINT_URL}"} \
    --region "${S3_REGION:-us-east-1}" \
    --storage-class STANDARD_IA

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Upload complete: s3://${S3_BUCKET_NAME}/${S3_KEY}"

# --- Cleanup local temp file ---
rm -f "${BACKUP_PATH}"

# --- Prune old backups from S3 (older than RETENTION_DAYS) ---
CUTOFF_DATE=$(date -u -d "-${RETENTION_DAYS} days" +"%Y-%m-%d" 2>/dev/null || date -u -v"-${RETENTION_DAYS}d" +"%Y-%m-%d")
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Pruning backups older than ${RETENTION_DAYS} days (before ${CUTOFF_DATE})..."

AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY_ID}" \
AWS_SECRET_ACCESS_KEY="${S3_SECRET_ACCESS_KEY}" \
aws s3 ls \
    "s3://${S3_BUCKET_NAME}/backups/postgres/" \
    ${S3_ENDPOINT_URL:+--endpoint-url "${S3_ENDPOINT_URL}"} \
    | awk '{print $4}' \
    | while read -r key; do
        file_date=$(echo "${key}" | grep -oP '\d{4}-\d{2}-\d{2}' | head -1 || true)
        if [[ -n "${file_date}" && "${file_date}" < "${CUTOFF_DATE}" ]]; then
            echo "Deleting old backup: ${key}"
            AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY_ID}" \
            AWS_SECRET_ACCESS_KEY="${S3_SECRET_ACCESS_KEY}" \
            aws s3 rm \
                "s3://${S3_BUCKET_NAME}/backups/postgres/${key}" \
                ${S3_ENDPOINT_URL:+--endpoint-url "${S3_ENDPOINT_URL}"}
        fi
    done

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Backup job complete. ✅"


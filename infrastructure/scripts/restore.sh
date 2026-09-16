#!/usr/bin/env bash
# ============================================================
# SolveNow — PostgreSQL Point-in-Time Restore Script
# ============================================================
# Downloads a specific backup from S3 and restores it.
# WARNING: This will DROP AND RECREATE the target database.
#
# Usage:
#   ./restore.sh solvenow-db-2026-09-15T02-00-00Z.dump
#
# The script will prompt for confirmation before destructive steps.
# ============================================================
set -euo pipefail

BACKUP_FILENAME="${1:?Usage: restore.sh <backup-filename>}"
BACKUP_PATH="/tmp/${BACKUP_FILENAME}"
S3_KEY="backups/postgres/${BACKUP_FILENAME}"

echo ""
echo "┌─────────────────────────────────────────────────────┐"
echo "│         SolveNow — DATABASE RESTORE TOOL           │"
echo "└─────────────────────────────────────────────────────┘"
echo ""
echo "  Backup file : ${BACKUP_FILENAME}"
echo "  Target DB   : ${POSTGRES_DB:-solvenow_production}"
echo "  Target host : ${POSTGRES_SERVER:-postgres}"
echo ""
echo "  ⚠️  WARNING: This will DROP the target database and"
echo "  restore it from the selected backup. This is irreversible."
echo ""
read -rp "  Type 'YES I AM SURE' to continue: " confirmation

if [[ "${confirmation}" != "YES I AM SURE" ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "[$(date -u)] Downloading backup from S3..."

AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY_ID}" \
AWS_SECRET_ACCESS_KEY="${S3_SECRET_ACCESS_KEY}" \
aws s3 cp \
    "s3://${S3_BUCKET_NAME}/${S3_KEY}" \
    "${BACKUP_PATH}" \
    ${S3_ENDPOINT_URL:+--endpoint-url "${S3_ENDPOINT_URL}"}

echo "[$(date -u)] Download complete. Starting restore..."

# Terminate all existing connections to the database
PGPASSWORD="${POSTGRES_PASSWORD}" psql \
    --host="${POSTGRES_SERVER}" \
    --port="${POSTGRES_PORT:-5432}" \
    --username="${POSTGRES_USER}" \
    --dbname="postgres" \
    --command="SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${POSTGRES_DB}' AND pid <> pg_backend_pid();"

# Drop and recreate database
PGPASSWORD="${POSTGRES_PASSWORD}" psql \
    --host="${POSTGRES_SERVER}" \
    --port="${POSTGRES_PORT:-5432}" \
    --username="${POSTGRES_USER}" \
    --dbname="postgres" \
    --command="DROP DATABASE IF EXISTS \"${POSTGRES_DB}\"; CREATE DATABASE \"${POSTGRES_DB}\" OWNER \"${POSTGRES_USER}\";"

# Restore
PGPASSWORD="${POSTGRES_PASSWORD}" pg_restore \
    --host="${POSTGRES_SERVER}" \
    --port="${POSTGRES_PORT:-5432}" \
    --username="${POSTGRES_USER}" \
    --dbname="${POSTGRES_DB}" \
    --verbose \
    --no-owner \
    --no-privileges \
    "${BACKUP_PATH}"

rm -f "${BACKUP_PATH}"

echo "[$(date -u)] Restore complete. ✅"
echo ""
echo "  IMPORTANT: Run 'alembic upgrade head' to apply any"
echo "  migrations that occurred after this backup was taken."


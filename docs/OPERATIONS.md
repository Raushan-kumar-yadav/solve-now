# SolveNow — Operations Runbook

This document covers the complete lifecycle of operating SolveNow in production: deployment, backups, incident response, and secret rotation.

---

## Table of Contents
1. [First Deployment](#1-first-deployment)
2. [Routine Deployment](#2-routine-deployment)
3. [Database Backup](#3-database-backup)
4. [Database Restore](#4-database-restore)
5. [Secret Rotation](#5-secret-rotation)
6. [Environment Separation](#6-environment-separation)
7. [Monitoring & Alerting](#7-monitoring--alerting)
8. [Incident Response](#8-incident-response)

---

## 1. First Deployment

### Prerequisites on the server
- Docker Engine ≥ 24.x and Docker Compose plugin
- AWS CLI (`aws`) installed and on `PATH`
- Git installed
- Firewall configured to accept only Cloudflare IPs on ports 80/443

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_ORG/solvenow /opt/solvenow
cd /opt/solvenow

# 2. Create production environment file
cp .env.production.example .env.production
# Edit .env.production with real values — NEVER commit this file
nano .env.production

# 3. Log in to GitHub Container Registry
echo "$GHCR_PAT" | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin

# 4. Pull images
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  --env-file .env.production pull

# 5. Run database migrations
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  --env-file .env.production run --rm migrate

# 6. Start all services
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  --env-file .env.production up -d

# 7. Verify health
curl -f https://api.yourdomain.com/health
curl -f https://api.yourdomain.com/ready
```

---

## 2. Routine Deployment

All production deployments are executed automatically by the **GitHub Actions deploy workflow** when a commit is merged to `main`.

To trigger a manual deploy (e.g., to staging):
1. Go to **GitHub → Actions → Deploy**
2. Click **Run workflow**
3. Select `staging` or `production`

The workflow:
- Builds and pushes new Docker images to GHCR
- SSHes into the server
- Runs `alembic upgrade head` (via the `migrate` service)
- Performs a rolling `docker compose up -d`
- Verifies the `/health` endpoint

---

## 3. Database Backup

**Automatic**: A cron job on the server runs `backup.sh` daily at 02:00 UTC:
```bash
# /etc/cron.d/solvenow-backup
0 2 * * * root /opt/solvenow/infrastructure/scripts/backup.sh >> /var/log/solvenow-backup.log 2>&1
```

**Manual backup**:
```bash
# Source environment variables
set -a && source /opt/solvenow/.env.production && set +a

# Run backup
/opt/solvenow/infrastructure/scripts/backup.sh
```

**Verify backups are working**:
```bash
# List recent backups in S3
aws s3 ls s3://${S3_BUCKET_NAME}/backups/postgres/ --endpoint-url ${S3_ENDPOINT_URL} | sort | tail -5
```

Retention policy: **30 days**. Backups older than 30 days are automatically deleted by the script.

---

## 4. Database Restore

> ⚠️ **DESTRUCTIVE OPERATION** — Drops and recreates the database. Always verify the backup file before proceeding.

```bash
# 1. List available backups
aws s3 ls s3://${S3_BUCKET_NAME}/backups/postgres/ | sort

# 2. Run the restore script with the chosen filename
set -a && source /opt/solvenow/.env.production && set +a
/opt/solvenow/infrastructure/scripts/restore.sh solvenow-db-2026-09-15T02-00-00Z.dump

# 3. After restore, apply any pending migrations
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  --env-file .env.production run --rm migrate
```

---

## 5. Secret Rotation

### Rotating SECRET_KEY (JWT signing key)

> ⚠️ Rotating `SECRET_KEY` immediately invalidates **all active user sessions**.

1. Generate a new key: `openssl rand -hex 64`
2. Update `SECRET_KEY` in `/opt/solvenow/.env.production`
3. Redeploy: `docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up -d api`
4. Clear the `token_denylist` table to avoid orphaned entries (optional)

### Rotating Database Password

1. Log into PostgreSQL: `docker compose exec postgres psql -U postgres`
2. `ALTER USER solvenow PASSWORD 'new_strong_password';`
3. Update `POSTGRES_PASSWORD` in `.env.production`
4. Redeploy api and worker services

---

## 6. Environment Separation

| Environment | Branch   | Server            | Secrets          |
|-------------|----------|-------------------|------------------|
| Development | any      | Local Docker       | `.env` (dev defaults) |
| Staging     | `main`   | Separate VPS       | GitHub Env: `staging` |
| Production  | `main` (tagged) | Production VPS | GitHub Env: `production` |

**Rule**: Production secrets exist **only** in the GitHub `production` environment and on the production server's `.env.production`. They are never stored in the repository, staging servers, or developer machines.

---

## 7. Monitoring & Alerting

### Checking service health
```bash
# All services running?
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

# API logs (last 100 lines)
docker compose logs --tail=100 api

# Worker logs
docker compose logs --tail=100 worker

# API error count (last hour)
docker compose logs api --since 1h | grep '"severity": "ERROR"' | wc -l
```

### Metrics Dashboard
- Prometheus: `http://your-server:9090` (restrict to internal IP)
- Grafana: `http://your-server:3001`

### Alert channels
Configure Alertmanager to notify via Slack, PagerDuty, or email for:
- Error rate > 5%
- P95 latency > 2s
- PostgreSQL down
- Redis down
- Worker stopped processing

---

## 8. Incident Response

### API is returning 5xx errors
1. `docker compose logs --tail=200 api` — check for exceptions
2. `curl https://api.yourdomain.com/ready` — check DB connectivity
3. Check Sentry for grouped error reports
4. If OOM: `docker stats` — scale `WEB_CONCURRENCY` down or add memory
5. If DB overloaded: check `pg_stat_activity` for long-running queries

### Worker is not processing jobs
1. `docker compose logs --tail=100 worker`
2. Check Redis connectivity: `docker compose exec redis redis-cli -a $REDIS_PASSWORD ping`
3. Check Celery queue length: `docker compose exec worker celery -A worker.celery inspect active`
4. Restart worker: `docker compose restart worker`

### Database disk full
1. Check disk: `df -h`
2. Identify large tables: `SELECT pg_size_pretty(pg_total_relation_size(relname::text)) AS size, relname FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relname::text) DESC LIMIT 10;`
3. Run `VACUUM FULL` on large tables
4. Expand VPS disk via provider console and extend the volume


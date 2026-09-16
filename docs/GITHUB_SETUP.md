# SolveNow — GitHub Actions Secrets

## Required Secrets

Configure these in your GitHub repository under:
**Settings → Secrets and variables → Actions**

### Global Secrets (all environments)

| Secret              | Description                                      |
|---------------------|--------------------------------------------------|
| `DEPLOY_SSH_KEY`    | Private SSH key that has access to the server    |
| `DEPLOY_HOST`       | VPS IP address or hostname                       |
| `DEPLOY_USER`       | SSH username (e.g. `deploy` or `ubuntu`)         |

### Environment: `staging`

| Secret                    | Value                                    |
|---------------------------|------------------------------------------|
| `NEXT_PUBLIC_API_URL`     | `https://api.staging.yourdomain.com`     |
| `API_DOMAIN`              | `api.staging.yourdomain.com`             |

### Environment: `production`

| Secret                    | Value                                    |
|---------------------------|------------------------------------------|
| `NEXT_PUBLIC_API_URL`     | `https://api.yourdomain.com`             |
| `API_DOMAIN`              | `api.yourdomain.com`                     |

## Server-side `.env.production`

The full set of secrets (DB password, Redis password, AI key, etc.) live in
`/opt/solvenow/.env.production` on the VPS itself and are **never stored in GitHub**.

The CI/CD workflow only SSHes into the server and runs `docker compose` commands —
it never reads or transmits the production secrets.

## Branch Protection Rules

Enforce these on the `main` branch to prevent merging failing PRs:

1. **Require status checks to pass before merging**:
   - `API — Lint`
   - `API — Tests`
   - `API — Security Audit`
   - `Web — Lint`
   - `Web — Typecheck`
   - `Web — Security Audit`
   - `Docker — Build Images`
2. **Require branches to be up to date before merging** ✅
3. **Restrict who can push to matching branches** (admins only)


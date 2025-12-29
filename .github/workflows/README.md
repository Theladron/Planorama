# GitHub Actions Workflows

This directory contains GitHub Actions workflows for CI/CD.

## Workflows

### `ci.yml` - Continuous Integration

Runs on every push and pull request to `main` and `develop` branches.

**Jobs:**
- **backend-tests**: Runs pytest with coverage
- **backend-lint**: Runs pylint and enforces minimum score of 8.0/10
- **frontend-tests**: Runs Jest tests with coverage
- **frontend-lint**: Runs ESLint

### `deploy.yml` - Deployment to AWS EC2

Runs automatically after the CI workflow completes successfully on `main` branch, or can be manually triggered (which bypasses the CI check).

**Uses GitHub Environment:** `Planorama`

**Configuration Requirements:**

This workflow uses a GitHub Environment (Settings → Environments → Planorama). Configure the following:

*Environment Variables (Non-Sensitive):*
- `AWS_EC2_HOST`: EC2 instance hostname or IP
- `AWS_EC2_USER`: SSH username (typically `ec2-user` or `ubuntu`)
- `AWS_EC2_APP_PATH`: (Optional) Path to app on EC2 (defaults to `/opt/planorama`)
- `POSTGRESQL_USERNAME`: PostgreSQL database username
- `POSTGRESQL_SERVER`: PostgreSQL server host (use `postgres` for Docker Compose)
- `POSTGRESQL_PORT`: PostgreSQL port (usually `5432`)
- `POSTGRESQL_DATABASE`: PostgreSQL database name
- `ENVIRONMENT`: Environment name (`local`, `staging`, or `production`)
- `DOMAIN`: Domain name for the application
- `BACKEND_CORS_ORIGINS`: Comma-separated list of allowed CORS origins
- `DEBUG`: (Optional) Debug mode (`True` or `False`, defaults to `False`)
- `ADMIN_EMAIL`: Admin user email for seeding
- `ADMIN_USERNAME`: Admin user username for seeding
- `AUTH0_DOMAIN`: Auth0 tenant domain (e.g., `dev-xxxxx.us.auth0.com`)
- `AUTH0_AUDIENCE`: Auth0 API identifier (e.g., `https://api.planorama`)
- `AUTH0_CONNECTION_NAME`: (Optional) Auth0 database connection name (defaults to `Username-Password-Authentication`)
- `VITE_BACKEND_URL`: (Optional) Backend URL for frontend build. Should include port 8000 (e.g., `http://13.51.172.110:8000`). Defaults to `http://localhost:8000`

**Note:** The `VITE_AUTH0_*` variables are automatically derived from `AUTH0_*` variables by `docker-compose.yml` during the frontend build process, so you don't need to set them separately.

*Environment Secrets (Sensitive - store as Secrets, not Variables):*
- `AWS_EC2_SSH_PRIVATE_KEY`: Private SSH key for EC2 access (entire `.pem` file content, including `-----BEGIN` and `-----END` lines with all newlines preserved)
- `POSTGRESQL_PASSWORD`: PostgreSQL database password
- `ORS_API_KEY`: OpenRouteService API key
- `AI_API_KEY`: AI service API key
- `ADMIN_PASSWORD`: Admin user password for seeding
- `AUTH0_CLIENT_ID`: Auth0 SPA application client ID
- `AUTH0_CLIENT_SECRET`: Auth0 SPA application client secret
- `AUTH0_MANAGEMENT_CLIENT_ID`: Auth0 Management API M2M application client ID
- `AUTH0_MANAGEMENT_CLIENT_SECRET`: Auth0 Management API M2M application client secret

**Note:** PostgreSQL server host should be `postgres` for Docker Compose deployments (this is the Docker service name that containers use to communicate. **Do not use `localhost`** when running in Docker, as `localhost` inside a container refers to that container itself.)

**What it does:**
1. Runs automatically after CI workflow completes successfully on `main` branch
2. Creates a `.env` file from GitHub Environment variables/secrets and uploads it to EC2 (always overwrites with latest values)
3. SSH into EC2 instance
4. Clone repository if needed, or pull latest code from `main` branch
5. Verify `.env` file exists
6. Rebuild Docker containers (ensures build-time variables like `VITE_BACKEND_URL` are updated)
7. Restart services

**Note:** If you change environment variables in GitHub Environment settings, you need to trigger a new deployment (push to `main` or manually trigger the workflow) for the changes to take effect, as the `.env` file is recreated and containers are rebuilt on each deployment.

## Setup

### Configure GitHub Environment

1. Go to your GitHub repository → Settings → Environments
2. Click "New environment" and name it `Planorama`
3. Add all required **Variables** (non-sensitive) listed above
4. Add all required **Secrets** (sensitive) listed above

**Important Notes:**
- Store sensitive data (passwords, API keys, SSH keys) as **Secrets**, not Variables
- Store non-sensitive data (usernames, ports, domains) as **Variables**
- The `.env` file is created automatically during deployment - you don't need to create it manually on EC2
- Never commit `.env` files to the repository (they're in `.gitignore`)
- All secrets and variables are securely stored in GitHub and only used during deployment

## Notes

- The `.env` file is automatically created during deployment - don't create it manually
- **EC2 Security Group**: Must allow SSH (port 22) from GitHub Actions IP ranges (see https://api.github.com/meta for current IPs) or use 0.0.0.0/0 for testing
- **Port Configuration**:
  - Frontend: Accessible on port 80 (standard HTTP). Update `docker-compose.yml` frontend service to map `"80:80"` instead of `"5173:80"` for production
  - Backend: Accessible on port 8000. `VITE_BACKEND_URL` must include the port: `http://YOUR_EC2_IP:8000`
- For production, configure SSL/TLS termination using AWS Application Load Balancer or nginx reverse proxy
- `ENVIRONMENT=production` changes URL generation to use `https://` but doesn't enable HTTPS on the server
- Update `BACKEND_CORS_ORIGINS` to use HTTPS URLs in production


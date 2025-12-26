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
- `ACCESS_TOKEN_EXPIRE_MINUTES`: (Optional) Token expiration in minutes (defaults to `30`)
- `ALGORITHM`: (Optional) JWT algorithm (defaults to `HS256`)
- `ENVIRONMENT`: Environment name (`local`, `staging`, or `production`)
- `DOMAIN`: Domain name for the application
- `BACKEND_CORS_ORIGINS`: Comma-separated list of allowed CORS origins
- `DEBUG`: (Optional) Debug mode (`True` or `False`, defaults to `False`)
- `ADMIN_EMAIL`: Admin user email for seeding
- `ADMIN_USERNAME`: Admin user username for seeding
- `VITE_BACKEND_URL`: (Optional) Backend URL for frontend build

*Environment Secrets (Sensitive - store as Secrets, not Variables):*
- `AWS_EC2_SSH_PRIVATE_KEY`: Private SSH key for EC2 access (entire `.pem` file content)
- `POSTGRESQL_PASSWORD`: PostgreSQL database password
- `ORS_API_KEY`: OpenRouteService API key
- `AI_API_KEY`: AI service API key
- `JWT_SECRET_KEY`: Secret key for JWT token signing (use strong random string)
- `ADMIN_PASSWORD`: Admin user password for seeding

**Note:** PostgreSQL server host should be `postgres` for Docker Compose deployments (this is the Docker service name that containers use to communicate. **Do not use `localhost`** when running in Docker, as `localhost` inside a container refers to that container itself.)

**What it does:**
1. Runs automatically after CI workflow completes successfully on `main` branch
2. Creates a `.env` file from GitHub Environment variables/secrets and uploads it to EC2
3. SSH into EC2 instance
4. Clone repository if needed, or pull latest code from `main` branch
5. Verify `.env` file exists
6. Rebuild Docker containers
7. Restart services

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

### EC2 Setup

See [EC2_DEPLOYMENT_CHECKLIST.md](./EC2_DEPLOYMENT_CHECKLIST.md) for detailed EC2 setup instructions.

## Production HTTPS Setup

For production deployments with HTTPS, see [PRODUCTION_SETUP.md](./PRODUCTION_SETUP.md) for detailed instructions on setting up SSL/TLS termination using AWS Application Load Balancer or nginx reverse proxy.

### EC2 Setup Requirements

1. Install Docker and Docker Compose on EC2
2. Clone your repository to the deployment path
3. Configure SSH access (copy your public key to EC2)
4. The `.env` file will be automatically created during deployment - no manual setup needed

### Production HTTPS Setup

When setting `ENVIRONMENT=production`, the application generates HTTPS URLs, but you need to configure SSL/TLS termination:

**Option 1: AWS Application Load Balancer (Recommended)**
- Set up an AWS ALB with SSL certificate (ACM)
- Point your domain to the ALB
- Configure ALB to forward traffic to EC2 instance (port 80/443 → port 80/5173)
- Containers serve HTTP internally; ALB handles HTTPS termination

**Option 2: Nginx Reverse Proxy in Docker**
- Add an nginx service to `docker-compose.yml` that handles SSL
- Mount SSL certificates into the nginx container
- Update port mappings so nginx is the entry point

**Important Notes:**
- `ENVIRONMENT=production` changes URL generation to use `https://` but doesn't enable HTTPS on the server
- Docker containers can still serve HTTP internally - SSL termination happens at the reverse proxy/load balancer
- Update `BACKEND_CORS_ORIGINS` to use HTTPS URLs in production
- Update `DOMAIN` to your actual production domain (e.g., `api.yourdomain.com`)


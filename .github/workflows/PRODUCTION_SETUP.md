# Production Deployment Guide

This guide explains how to set up production deployment with HTTPS on AWS EC2.

## Overview

When `ENVIRONMENT=production`, the application generates HTTPS URLs, but the Docker containers still serve HTTP internally. SSL/TLS termination is handled by a reverse proxy (recommended: AWS Application Load Balancer).

## Architecture

```
Internet (HTTPS)
    ↓
AWS Application Load Balancer (SSL Termination)
    ↓
EC2 Instance (HTTP)
    ↓
Docker Compose
    ├── Frontend (nginx, port 80)
    └── Backend (FastAPI, port 8000)
```

## Step-by-Step Setup

### 1. Configure GitHub Secrets

Set the following secrets with production values:

```
ENVIRONMENT=production
DOMAIN=api.yourdomain.com  # Your actual domain
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
POSTGRESQL_SERVER=postgres  # Keep as 'postgres' for Docker Compose
```

### 2. Set Up AWS Application Load Balancer

1. **Create SSL Certificate in AWS Certificate Manager (ACM)**
   - Request a certificate for your domain (`*.yourdomain.com` or `yourdomain.com`)
   - Validate the certificate

2. **Create Application Load Balancer**
   - Target type: Instances
   - Scheme: Internet-facing
   - Security groups: Allow HTTPS (443) and HTTP (80) from internet

3. **Configure Listeners**
   - **HTTPS (443)**: Use your ACM certificate, forward to target group
   - **HTTP (80)**: Redirect to HTTPS (optional but recommended)

4. **Create Target Group**
   - Protocol: HTTP
   - Port: 80 (for frontend nginx) or 5173 (if exposing frontend directly)
   - Health check: Configure appropriate path (e.g., `/api/health`)

5. **Register EC2 Instance**
   - Register your EC2 instance in the target group

6. **Update DNS**
   - Point your domain to the ALB's DNS name

### 3. EC2 Security Group Configuration

Ensure your EC2 security group allows:
- Inbound: HTTP (80) and HTTPS (443) from ALB security group
- Outbound: All traffic (or restrict as needed)

### 4. Update docker-compose.yml (if needed)

For production, you might want to:
- Remove port mappings from backend (only expose via nginx/ALB)
- Keep frontend port mapping for ALB target group
- Or use internal networking and expose only frontend

Example production `docker-compose.yml` changes:

```yaml
backend:
  # Remove or comment out:
  # ports:
  #   - "8000:8000"
  # ALB will access via internal Docker network

frontend:
  ports:
    - "80:80"  # ALB will forward to this
```

### 5. Environment Variables

The deployment workflow automatically creates `.env` from GitHub Secrets. Ensure:

- `ENVIRONMENT=production`
- `DOMAIN` matches your actual domain
- `BACKEND_CORS_ORIGINS` uses HTTPS URLs
- All secrets are properly configured

## Alternative: Nginx Reverse Proxy in Docker

If you prefer to handle SSL in Docker instead of using ALB:

1. Add nginx service to `docker-compose.yml`
2. Configure SSL certificates (mount from host or use Let's Encrypt)
3. Update nginx config to proxy to backend/frontend
4. Expose only nginx on ports 80/443

This approach is more complex but gives you full control over SSL configuration.

## Testing

After deployment:

1. Verify HTTPS works: `https://yourdomain.com`
2. Check API endpoints: `https://api.yourdomain.com/api/health`
3. Verify CORS headers allow your frontend domain
4. Test frontend can connect to backend

## Troubleshooting

- **502 Bad Gateway**: Check ALB target group health checks, ensure containers are running
- **CORS errors**: Verify `BACKEND_CORS_ORIGINS` includes your frontend domain with `https://`
- **SSL certificate errors**: Ensure ACM certificate is validated and attached to ALB listener
- **Connection refused**: Check EC2 security group allows traffic from ALB security group



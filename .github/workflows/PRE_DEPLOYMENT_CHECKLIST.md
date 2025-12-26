# Pre-Deployment Checklist

Use this checklist before pushing to `main` to ensure your deployment will succeed.

## ✅ GitHub Environment Configuration

- [ ] **Environment Created**: GitHub Environment named `Planorama` exists
- [ ] **All Variables Set**: All non-sensitive variables are configured in Environment Variables
- [ ] **All Secrets Set**: All sensitive values are configured in Environment Secrets

### Required Environment Variables (Non-Sensitive)
- [ ] `AWS_EC2_HOST` - Your EC2 instance IP or hostname
- [ ] `AWS_EC2_USER` - SSH username (ec2-user or ubuntu)
- [ ] `AWS_EC2_APP_PATH` - Deployment path (e.g., `/opt/planorama`)
- [ ] `POSTGRESQL_USERNAME` - Database username
- [ ] `POSTGRESQL_SERVER` - Database host (`postgres` for Docker Compose)
- [ ] `POSTGRESQL_PORT` - Database port (`5432`)
- [ ] `POSTGRESQL_DATABASE` - Database name
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: `30`)
- [ ] `ALGORITHM` - JWT algorithm (default: `HS256`)
- [ ] `ENVIRONMENT` - Environment type (`production`, `staging`, or `local`)
- [ ] `DOMAIN` - Your domain name
- [ ] `BACKEND_CORS_ORIGINS` - Comma-separated CORS origins
- [ ] `DEBUG` - Debug mode (`False` for production)
- [ ] `ADMIN_EMAIL` - Admin user email
- [ ] `ADMIN_USERNAME` - Admin username
- [ ] `VITE_BACKEND_URL` - Backend URL for frontend

### Required Environment Secrets (Sensitive)
- [ ] `AWS_EC2_SSH_PRIVATE_KEY` - Full content of your `.pem` file
- [ ] `POSTGRESQL_PASSWORD` - Database password
- [ ] `ORS_API_KEY` - OpenRouteService API key
- [ ] `AI_API_KEY` - AI service API key
- [ ] `JWT_SECRET_KEY` - Strong random secret (at least 32 characters)
- [ ] `ADMIN_PASSWORD` - Admin user password

## ✅ EC2 Instance Setup

- [ ] **Docker Installed**: `docker --version` works
- [ ] **Docker Compose Installed**: `docker-compose --version` works
- [ ] **Git Installed**: `git --version` works
- [ ] **User in Docker Group**: User has permission to run Docker without sudo
- [ ] **Repository Cloned** (optional): If private repo, clone manually once (workflow will handle updates)
- [ ] **Security Groups Configured**: 
  - [ ] SSH (port 22) - Restricted to your IP or GitHub Actions IPs
  - [ ] HTTP (port 80) - Open for frontend
  - [ ] Backend API (port 8000) - Open or restricted as needed
- [ ] **SSH Access Tested**: Can SSH into instance from local machine

## ✅ Code Readiness

- [ ] **All changes committed**: Ready to push to `main`
- [ ] **Environment files created**: `.env.example` and `.env.local.example` exist
- [ ] **Workflow file updated**: `.github/workflows/deploy.yml` uses GitHub Environment
- [ ] **No sensitive data in code**: No API keys, passwords, or secrets committed

## 🚀 Deployment Steps

1. **Push to main**:
   ```bash
   git push origin main
   ```

2. **Or manually trigger workflow**:
   - Go to GitHub → Actions → Deploy to AWS
   - Click "Run workflow"

3. **Monitor deployment**:
   - Watch the GitHub Actions workflow logs
   - Check EC2 instance logs if needed: `docker compose logs -f`

4. **Verify deployment**:
   - Frontend: `http://YOUR_EC2_IP:5173`
   - Backend API: `http://YOUR_EC2_IP:8000`
   - API Docs: `http://YOUR_EC2_IP:8000/api/docs`

## 🔍 Troubleshooting

If deployment fails:

1. **Check GitHub Actions logs** for specific error messages
2. **Verify SSH connection**: Ensure `AWS_EC2_SSH_PRIVATE_KEY` contains entire key (including `-----BEGIN` and `-----END` lines)
3. **Check Security Groups**: Ensure SSH port is open
4. **Verify Environment Variables**: Double-check all variables and secrets are set correctly
5. **Check EC2 logs**: SSH into instance and run `docker compose logs`

## 📝 Notes

- The `.env` file is created automatically by the workflow - don't create it manually
- For private repositories, you may need to clone manually once, then the workflow handles updates
- First deployment may take longer due to Docker image builds
- Database will be initialized automatically by Docker Compose


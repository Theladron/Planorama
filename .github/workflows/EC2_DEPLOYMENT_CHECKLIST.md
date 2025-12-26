# EC2 Deployment Checklist

This checklist ensures your EC2 instance and GitHub repository are properly configured for automated deployment.

## ✅ Prerequisites Completed

- [x] Created GitHub Environment named "Planorama"
- [x] Created EC2 instance
- [x] Created EC2 key pairs

## 📋 GitHub Environment Configuration

### Required Environment Variables (Non-Sensitive)

Configure these in your GitHub Environment (Settings → Environments → Planorama → Variables):

- [ ] `AWS_EC2_HOST` - EC2 instance public IP or hostname (e.g., `ec2-1-2-3-4.compute-1.amazonaws.com`)
- [ ] `AWS_EC2_USER` - SSH username (e.g., `ec2-user` for Amazon Linux, `ubuntu` for Ubuntu)
- [ ] `AWS_EC2_APP_PATH` - Path where app will be deployed (e.g., `/opt/planorama`)
- [ ] `POSTGRESQL_USERNAME` - PostgreSQL username (e.g., `postgres`)
- [ ] `POSTGRESQL_SERVER` - PostgreSQL host (use `postgres` for Docker Compose)
- [ ] `POSTGRESQL_PORT` - PostgreSQL port (usually `5432`)
- [ ] `POSTGRESQL_DATABASE` - Database name (e.g., `Planorama`)
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: `30`)
- [ ] `ALGORITHM` - JWT algorithm (default: `HS256`)
- [ ] `ENVIRONMENT` - Environment type: `production`, `staging`, or `local`
- [ ] `DOMAIN` - Your domain name (e.g., `api.yourdomain.com` or `yourdomain.com`)
- [ ] `BACKEND_CORS_ORIGINS` - Comma-separated CORS origins (e.g., `https://yourdomain.com,https://www.yourdomain.com`)
- [ ] `DEBUG` - Debug mode: `False` for production, `True` for development
- [ ] `ADMIN_EMAIL` - Admin user email (e.g., `admin@yourdomain.com`)
- [ ] `ADMIN_USERNAME` - Admin username (e.g., `admin`)
- [ ] `VITE_BACKEND_URL` - Backend URL for frontend (e.g., `https://api.yourdomain.com`)

### Required Environment Secrets (Sensitive)

Configure these in your GitHub Environment (Settings → Environments → Planorama → Secrets):

- [ ] `AWS_EC2_SSH_PRIVATE_KEY` - Private SSH key content (entire content of your `.pem` file)
- [ ] `POSTGRESQL_PASSWORD` - PostgreSQL password
- [ ] `ORS_API_KEY` - OpenRouteService API key
- [ ] `AI_API_KEY` - AI service API key
- [ ] `JWT_SECRET_KEY` - Secret key for JWT token signing (use a strong random string)
- [ ] `ADMIN_PASSWORD` - Admin user password

**Note:** The workflow uses `vars.*` for non-sensitive variables and `secrets.*` for sensitive data.

## 🖥️ EC2 Instance Setup

### 1. Install Required Software

SSH into your EC2 instance and run:

```bash
# Update package manager
sudo yum update -y  # For Amazon Linux
# OR
sudo apt-get update && sudo apt-get upgrade -y  # For Ubuntu

# Install Docker
sudo yum install -y docker  # For Amazon Linux
# OR
sudo apt-get install -y docker.io  # For Ubuntu

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (replace ec2-user with your username)
sudo usermod -aG docker ec2-user
# OR
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git (if not already installed)
sudo yum install -y git  # For Amazon Linux
# OR
sudo apt-get install -y git  # For Ubuntu

# Log out and log back in for docker group changes to take effect
```

### 2. Create App Directory (Optional - workflow will create it)

The GitHub workflow will automatically create the directory and clone the repository on first deployment. However, if you want to create it manually:

```bash
# Create app directory
sudo mkdir -p /opt/planorama
sudo chown $USER:$USER /opt/planorama
```

**Note:** You don't need to clone the repository manually - the deployment workflow handles this automatically. The workflow will:
- Create the directory if it doesn't exist
- Clone the repository on first deployment (for public repos)
- Pull latest code on subsequent deployments

**Important - For Private Repositories:** 
If your repository is private, the automatic clone will fail. You have two options:
1. **Clone manually once** (then the workflow will handle all future updates):
   ```bash
   cd /opt/planorama
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git .
   # Or use SSH if you've set up keys:
   # git clone git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git .
   ```
2. **Set up authentication** so the workflow can clone automatically:
   - Configure git credentials on EC2 for HTTPS access, OR
   - Add EC2's SSH public key to GitHub as a deploy key

Since you've already cloned it, you can leave it as-is - the workflow will pull updates automatically on each deployment.

### 4. Configure Security Groups

In AWS Console → EC2 → Security Groups:

- [ ] **Inbound Rules:**
  - Port `22` (SSH) - From your IP or 0.0.0.0/0 (temporary, restrict later)
  - Port `80` (HTTP) - From 0.0.0.0/0 (for frontend)
  - Port `8000` (Backend API) - From 0.0.0.0/0 (or restrict to your ALB/IPs)
  - Port `443` (HTTPS) - From 0.0.0.0/0 (if using direct HTTPS)

- [ ] **Outbound Rules:**
  - Allow all (default)

### 5. Test Docker Installation

```bash
# Test Docker
docker --version
docker ps

# Test Docker Compose
docker-compose --version

# If you get permission errors, log out and log back in
```

### 6. Verify SSH Access from GitHub Actions

You should be able to SSH into your EC2 instance using the private key. Test locally:

```bash
# On your local machine
ssh -i /path/to/your-key.pem ec2-user@YOUR_EC2_IP

# If this works, GitHub Actions should be able to connect
```

## 🔒 Security Recommendations

1. **Restrict SSH Access:**
   - Limit Security Group port 22 to your IP address only
   - Use a bastion host or VPN for production

2. **Use AWS Systems Manager:**
   - Consider using AWS Systems Manager Session Manager instead of SSH
   - More secure and audit-friendly

3. **Strong Passwords:**
   - Generate strong random strings for:
     - `JWT_SECRET_KEY` (at least 32 characters)
     - `POSTGRESQL_PASSWORD` (complex password)
     - `ADMIN_PASSWORD` (strong password)

4. **HTTPS Setup:**
   - For production, set up an Application Load Balancer with SSL certificate
   - Or use nginx reverse proxy with SSL
   - See `PRODUCTION_SETUP.md` for details

## 🚀 First Deployment

After completing all checklist items:

1. Push code to `main` branch
2. GitHub Actions workflow will automatically:
   - SSH into EC2
   - Pull latest code
   - Create `.env` file from environment variables
   - Build and start Docker containers
   - Run database migrations (if enabled)

3. Monitor deployment:
   ```bash
   # On EC2 instance
   cd /opt/planorama
   docker compose logs -f
   ```

4. Verify services are running:
   ```bash
   docker compose ps
   ```

5. Check application health:
   - Frontend: `http://YOUR_EC2_IP:5173`
   - Backend API: `http://YOUR_EC2_IP:8000`
   - API Docs: `http://YOUR_EC2_IP:8000/api/docs`

## 🔍 Troubleshooting

### GitHub Actions Fails to Connect
- Verify `AWS_EC2_SSH_PRIVATE_KEY` contains the entire private key (including `-----BEGIN` and `-----END` lines)
- Check Security Group allows SSH from GitHub Actions IPs (or 0.0.0.0/0 for testing)
- Verify `AWS_EC2_HOST` is correct (public IP or hostname)
- Verify `AWS_EC2_USER` matches your AMI (ec2-user for Amazon Linux, ubuntu for Ubuntu)

### Docker Permission Denied
- Ensure user is in docker group: `sudo usermod -aG docker $USER`
- Log out and log back in
- Or use `sudo docker` (not recommended for production)

### Containers Won't Start
- Check `.env` file exists: `cat /opt/planorama/.env`
- Check Docker logs: `docker compose logs`
- Verify all required environment variables are set
- Check database connection (if using external database)

### Database Connection Issues
- For Docker Compose: Ensure `POSTGRESQL_SERVER=postgres` (service name)
- Verify database credentials are correct
- Check database container is healthy: `docker compose ps`

## 📝 Notes

- The `.env` file is automatically created during deployment - don't create it manually
- The workflow pulls from `origin/main` - ensure your main branch is up to date
- Database migrations are commented out by default - uncomment when ready
- For production, consider using AWS RDS instead of containerized PostgreSQL
- Regular backups are recommended for production databases


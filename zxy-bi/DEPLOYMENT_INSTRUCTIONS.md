
# ZXY Business Intelligence Dashboard Deployment Instructions

## Server Requirements
- Ubuntu/Debian Linux server
- Python 3.8+ installed
- Nginx (optional, for reverse proxy)
- Systemd (for service management)

## Deployment Steps

### 1. Upload Files to Server
```bash
# Upload the deployment archive to your server
scp zxy-dashboard-deployment.zip user@18.140.79.12:/tmp/

# Connect to server
ssh user@18.140.79.12

# Create application directory
sudo mkdir -p /var/www/zxy-dashboard
cd /var/www/zxy-dashboard

# Extract deployment files
sudo unzip /tmp/zxy-dashboard-deployment.zip -d .
sudo chown -R www-data:www-data /var/www/zxy-dashboard
```

### 2. Install Dependencies
```bash
# Install Python and pip (if not already installed)
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Create virtual environment
sudo -u www-data python3 -m venv venv
sudo -u www-data venv/bin/pip install -r requirements.txt
```

### 3. Configure and Start Application
```bash
# Make startup script executable
chmod +x start_dashboard.sh

# Start the application
sudo -u www-data ./start_dashboard.sh
```

### 4. Optional: Setup Nginx Reverse Proxy
```bash
# Copy Nginx configuration
sudo cp zxy-dashboard.nginx /etc/nginx/sites-available/zxy-dashboard
sudo ln -s /etc/nginx/sites-available/zxy-dashboard /etc/nginx/sites-enabled/

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Optional: Setup Systemd Service
```bash
# Copy service file
sudo cp zxy-dashboard.service /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable zxy-dashboard
sudo systemctl start zxy-dashboard

# Check status
sudo systemctl status zxy-dashboard
```

## Access Your Dashboard
- Direct access: http://18.140.79.12:80
- With Nginx: http://18.140.79.12

## Troubleshooting
- Check application logs: `sudo journalctl -u zxy-dashboard -f`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- Verify port is open: `sudo netstat -tlnp | grep 80`

## Security Notes
- Change the SECRET_KEY in .env file
- Configure firewall to allow only necessary ports
- Consider setting up SSL/TLS certificates
- Regularly update dependencies

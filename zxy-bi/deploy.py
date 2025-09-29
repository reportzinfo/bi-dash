#!/usr/bin/env python3
"""
ZXY Business Intelligence Dashboard Deployment Script
Deploys the Flask application to a remote server
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path
import argparse

class DashboardDeployer:
    def __init__(self, target_server="18.140.79.12", target_port=80):
        self.target_server = target_server
        self.target_port = target_port
        self.project_root = Path(__file__).parent
        self.deployment_files = [
            'app.py',
            'requirements.txt',
            'templates/',
            'static/',
            'app/',
            'config/',
            'data/',
            '.env.example'
        ]
    
    def create_deployment_package(self):
        """Create a deployment package with all necessary files"""
        print("📦 Creating deployment package...")
        
        # Create deployment directory
        deploy_dir = self.project_root / 'deployment'
        if deploy_dir.exists():
            shutil.rmtree(deploy_dir)
        deploy_dir.mkdir()
        
        # Copy files to deployment directory
        for item in self.deployment_files:
            source = self.project_root / item
            if source.exists():
                if source.is_file():
                    shutil.copy2(source, deploy_dir)
                    print(f"   ✅ Copied {item}")
                elif source.is_dir():
                    shutil.copytree(source, deploy_dir / item)
                    print(f"   ✅ Copied directory {item}")
            else:
                print(f"   ⚠️  Warning: {item} not found")
        
        # Create production environment file
        self.create_production_env(deploy_dir)
        
        # Create deployment archive
        archive_path = self.project_root / 'zxy-dashboard-deployment.zip'
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(deploy_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(deploy_dir)
                    zipf.write(file_path, arcname)
        
        print(f"   ✅ Created deployment archive: {archive_path}")
        return archive_path
    
    def create_production_env(self, deploy_dir):
        """Create production environment configuration"""
        env_content = f"""# ZXY Business Intelligence Dashboard - Production Configuration
SECRET_KEY=zxy-bi-production-secret-key-{os.urandom(16).hex()}
FLASK_DEBUG=False
PORT={self.target_port}

# Database Configuration
DATABASE_URL=sqlite:///dashboard.db

# Logging Configuration
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
"""
        
        env_file = deploy_dir / '.env'
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("   ✅ Created production .env file")
    
    def create_startup_script(self):
        """Create startup script for the server"""
        startup_script = f"""#!/bin/bash
# ZXY Dashboard Startup Script

echo "🚀 Starting ZXY Business Intelligence Dashboard..."

# Navigate to application directory
cd /var/www/zxy-dashboard

# Activate virtual environment (if exists)
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "   ✅ Activated virtual environment"
fi

# Install/update dependencies
pip install -r requirements.txt
echo "   ✅ Dependencies installed"

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Start the application with Gunicorn
echo "   🌐 Starting server on http://{self.target_server}:{self.target_port}"
gunicorn -w 4 -b 0.0.0.0:{self.target_port} app:app --daemon

echo "   ✅ ZXY Dashboard started successfully!"
echo "   🌐 Access at: http://{self.target_server}:{self.target_port}"
"""
        
        script_path = self.project_root / 'start_dashboard.sh'
        with open(script_path, 'w') as f:
            f.write(startup_script)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        print(f"   ✅ Created startup script: {script_path}")
        return script_path
    
    def create_nginx_config(self):
        """Create Nginx configuration for reverse proxy"""
        nginx_config = f"""# ZXY Dashboard Nginx Configuration
server {{
    listen 80;
    server_name {self.target_server};
    
    location / {{
        proxy_pass http://127.0.0.1:{self.target_port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Static files
    location /static {{
        alias /var/www/zxy-dashboard/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}
"""
        
        config_path = self.project_root / 'zxy-dashboard.nginx'
        with open(config_path, 'w') as f:
            f.write(nginx_config)
        print(f"   ✅ Created Nginx config: {config_path}")
        return config_path
    
    def create_systemd_service(self):
        """Create systemd service file for auto-start"""
        service_config = f"""[Unit]
Description=ZXY Business Intelligence Dashboard
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/zxy-dashboard
Environment=PATH=/var/www/zxy-dashboard/venv/bin
ExecStart=/var/www/zxy-dashboard/venv/bin/gunicorn -w 4 -b 0.0.0.0:{self.target_port} app:app --daemon
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
"""
        
        service_path = self.project_root / 'zxy-dashboard.service'
        with open(service_path, 'w') as f:
            f.write(service_config)
        print(f"   ✅ Created systemd service: {service_path}")
        return service_path
    
    def generate_deployment_instructions(self):
        """Generate deployment instructions"""
        instructions = f"""
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
scp zxy-dashboard-deployment.zip user@{self.target_server}:/tmp/

# Connect to server
ssh user@{self.target_server}

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
- Direct access: http://{self.target_server}:{self.target_port}
- With Nginx: http://{self.target_server}

## Troubleshooting
- Check application logs: `sudo journalctl -u zxy-dashboard -f`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- Verify port is open: `sudo netstat -tlnp | grep {self.target_port}`

## Security Notes
- Change the SECRET_KEY in .env file
- Configure firewall to allow only necessary ports
- Consider setting up SSL/TLS certificates
- Regularly update dependencies
"""
        
        instructions_path = self.project_root / 'DEPLOYMENT_INSTRUCTIONS.md'
        with open(instructions_path, 'w') as f:
            f.write(instructions)
        print(f"   ✅ Created deployment instructions: {instructions_path}")
        return instructions_path
    
    def deploy(self):
        """Main deployment function"""
        print(f"🚀 ZXY Dashboard Deployment to {self.target_server}:{self.target_port}")
        print("=" * 60)
        
        try:
            # Create deployment package
            archive_path = self.create_deployment_package()
            
            # Create additional deployment files
            startup_script = self.create_startup_script()
            nginx_config = self.create_nginx_config()
            systemd_service = self.create_systemd_service()
            instructions = self.generate_deployment_instructions()
            
            print("\n✅ Deployment package created successfully!")
            print(f"\nFiles created:")
            print(f"   📦 Deployment archive: {archive_path}")
            print(f"   🚀 Startup script: {startup_script}")
            print(f"   🌐 Nginx config: {nginx_config}")
            print(f"   ⚙️  Systemd service: {systemd_service}")
            print(f"   📋 Instructions: {instructions}")
            
            print(f"\n🎯 Next steps:")
            print(f"   1. Upload {archive_path.name} to your server")
            print(f"   2. Follow the instructions in {instructions.name}")
            print(f"   3. Access your dashboard at http://{self.target_server}:{self.target_port}")
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Deploy ZXY Dashboard')
    parser.add_argument('--server', default='18.140.79.12', help='Target server IP')
    parser.add_argument('--port', type=int, default=80, help='Target port')
    
    args = parser.parse_args()
    
    deployer = DashboardDeployer(args.server, args.port)
    deployer.deploy()

if __name__ == '__main__':
    main()
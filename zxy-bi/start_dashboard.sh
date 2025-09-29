#!/bin/bash
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
echo "   🌐 Starting server on http://18.140.79.12:80"
gunicorn -w 4 -b 0.0.0.0:80 app:app --daemon

echo "   ✅ ZXY Dashboard started successfully!"
echo "   🌐 Access at: http://18.140.79.12:80"

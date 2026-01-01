#!/bin/bash

# Production environment setup script for dhii-mail
# This script helps configure the application for production deployment

set -e

echo "🔧 Setting up production environment for dhii-mail..."

# Create data and logs directories
mkdir -p data logs ssl

# Generate secure keys if not provided
if [ -z "$JWT_SECRET_KEY" ]; then
    echo "🔑 Generating JWT secret key..."
    export JWT_SECRET_KEY=$(openssl rand -base64 32)
    echo "JWT_SECRET_KEY generated and exported"
fi

if [ -z "$ENCRYPTION_KEY" ]; then
    echo "🔐 Generating encryption key..."
    export ENCRYPTION_KEY=$(openssl rand -base64 24)
    echo "ENCRYPTION_KEY generated and exported"
fi

# Create production .env file if it doesn't exist
if [ ! -f ".env.production" ]; then
    echo "📝 Creating production environment file..."
    cat > .env.production << EOF
# Production Environment Configuration
# Generated on $(date)

# Google API Configuration
GOOGLE_API_KEY=${GOOGLE_API_KEY:-your_google_api_key_here}

# JWT Configuration
JWT_SECRET_KEY=${JWT_SECRET_KEY}

# Database Configuration
DATABASE_URL=sqlite:///./data/dhii_mail_production.db

# Email Configuration
SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}
SMTP_PORT=${SMTP_PORT:-587}
SMTP_USERNAME=${SMTP_USERNAME:-your_email@gmail.com}
SMTP_PASSWORD=${SMTP_PASSWORD:-your_app_password_here}

# Security Configuration
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Application Configuration
DEBUG=false
LOG_LEVEL=INFO
MAX_WORKERS=4
ENVIRONMENT=production

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Security Headers
ENABLE_CORS=true
CORS_ORIGINS=${CORS_ORIGINS:-https://yourdomain.com}

# A2UI Configuration
A2UI_ENABLED=true
A2UI_CLIENT_URL=${A2UI_CLIENT_URL:-https://yourdomain.com}
A2UI_BACKEND_URL=${A2UI_BACKEND_URL:-https://api.yourdomain.com}
A2UI_WEBSOCKET_URL=${A2UI_WEBSOCKET_URL:-wss://api.yourdomain.com}

# Production Settings
UVICORN_WORKERS=4
UVICORN_PORT=8005
UVICORN_HOST=0.0.0.0
EOF
    echo "✅ Production environment file created: .env.production"
fi

# Create production database if it doesn't exist
if [ ! -f "data/dhii_mail_production.db" ]; then
    echo "🗄️  Creating production database..."
    python -c "
from database import DatabaseManager
db = DatabaseManager('sqlite:///./data/dhii_mail_production.db')
# Database will be created automatically when needed
print('Production database ready')
"
fi

# Create SSL directory and self-signed certificate for development
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo "🔒 Creating SSL certificates..."
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    echo "✅ SSL certificates created in ssl/ directory"
fi

# Set proper file permissions
chmod 600 .env.production ssl/key.pem
chmod 644 ssl/cert.pem
chmod 755 data logs

echo ""
echo "🎉 Production environment setup completed!"
echo ""
echo "Next steps:"
echo "1. Update .env.production with your actual values"
echo "2. Configure your domain and SSL certificates"
echo "3. Run: ./deploy.sh to deploy the application"
echo "4. Monitor logs: docker-compose logs -f"
echo ""
echo "⚠️  Important: Keep your .env.production file secure and never commit it to version control!"
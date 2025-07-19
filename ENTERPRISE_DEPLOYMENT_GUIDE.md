# Enterprise Deployment Guide

## Vessel Maintenance AI System - Enterprise Edition

This guide provides comprehensive instructions for deploying the Vessel Maintenance AI System with enterprise features including multi-tenancy, advanced security, monitoring, and compliance capabilities.

## Table of Contents

1. [Overview](#overview)
2. [Enterprise Features](#enterprise-features)
3. [System Requirements](#system-requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Database Setup](#database-setup)
7. [Security Setup](#security-setup)
8. [Monitoring Setup](#monitoring-setup)
9. [Deployment Options](#deployment-options)
10. [Troubleshooting](#troubleshooting)

## Overview

The Enterprise Edition of the Vessel Maintenance AI System provides comprehensive features for large-scale maritime operations:

- **Multi-tenant Architecture**: Support for multiple fleet operators with complete data isolation
- **Advanced Security**: JWT authentication, API keys, RBAC, and comprehensive audit logging
- **Enterprise Analytics**: Trend analysis, predictive insights, and custom reporting
- **Real-time Monitoring**: Health checks, metrics collection, and alerting
- **Compliance**: GDPR compliance, data retention policies, and maritime standards
- **Scalability**: Horizontal scaling, caching, and load balancing support

## Enterprise Features

### Multi-tenant Architecture
- **Tenant Isolation**: Database-level, schema-level, or row-level isolation
- **Tenant Management**: Create, update, and manage tenant configurations
- **Data Routing**: Automatic tenant identification and data routing
- **Resource Limits**: Configurable quotas and usage limits per tenant

### Advanced Security
- **Authentication**: JWT tokens, API keys, and SSO integration ready
- **Authorization**: Role-based access control (RBAC) with fine-grained permissions
- **Audit Logging**: Comprehensive audit trails for all system activities
- **Data Encryption**: End-to-end encryption for sensitive data
- **Rate Limiting**: Configurable request throttling and quota management

### Enterprise Analytics
- **Trend Analysis**: Historical data analysis and trend identification
- **Predictive Insights**: ML-powered predictions for maintenance and alerts
- **Custom Reports**: Configurable reporting with export capabilities
- **Real-time Dashboards**: Live monitoring and visualization

### Monitoring & Alerting
- **Health Monitoring**: Comprehensive system health checks
- **Metrics Collection**: Performance and usage metrics
- **Real-time Alerts**: Configurable alerting via multiple channels
- **Notification Channels**: Email, Slack, Teams, Discord, and webhooks

### Compliance & Governance
- **GDPR Compliance**: Data subject rights and privacy controls
- **Data Retention**: Configurable retention policies
- **Audit Trails**: Complete activity logging for compliance
- **Maritime Standards**: IMO and industry best practices alignment

## System Requirements

### Minimum Requirements
- **CPU**: 4 cores (8+ recommended for production)
- **RAM**: 8GB (16GB+ recommended for production)
- **Storage**: 100GB SSD (500GB+ recommended for production)
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.9+

### Production Requirements
- **CPU**: 8+ cores
- **RAM**: 32GB+
- **Storage**: 1TB+ SSD with RAID
- **Network**: High-speed internet connection
- **Load Balancer**: HAProxy or nginx
- **Database**: PostgreSQL 13+ or MySQL 8+
- **Cache**: Redis 6+
- **Monitoring**: Prometheus + Grafana

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/fusionpact/vessel-ai-enterprise.git
cd vessel-ai-enterprise
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

## Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# Application Settings
APP_NAME="Vessel Maintenance AI System"
APP_VERSION="1.0.0"
DEBUG=false

# Multi-tenancy Configuration
MULTI_TENANT_ENABLED=true
TENANT_ISOLATION_LEVEL=database
DEFAULT_TENANT_ID=default

# Database Configuration
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/vessel_ai
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Authentication & Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENCRYPTION_LEVEL=enterprise
ENCRYPTION_KEY=your-encryption-key

# Rate Limiting
RATE_LIMITING_ENABLED=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Caching Configuration
CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# Background Processing
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Monitoring & Logging
LOGGING_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENABLED=true

# Analytics & ML
ANALYTICS_ENABLED=true
ML_MODEL_CACHE_SIZE=100
PREDICTION_BATCH_SIZE=50

# Notifications
NOTIFICATIONS_ENABLED=true
EMAIL_ENABLED=true
SMS_ENABLED=false
WEBHOOK_ENABLED=true

# Compliance & Audit
AUDIT_LOGGING_ENABLED=true
GDPR_COMPLIANCE_ENABLED=true
DATA_RETENTION_DAYS=2555

# API Configuration
API_VERSION=v1
CORS_ORIGINS=["https://yourdomain.com"]
API_DOCUMENTATION_ENABLED=true

# Performance & Scaling
WORKER_PROCESSES=4
MAX_CONCURRENT_REQUESTS=1000
REQUEST_TIMEOUT=300

# Feature Flags
ADVANCED_ANALYTICS_ENABLED=true
CUSTOM_MODELS_ENABLED=true
BATCH_PROCESSING_ENABLED=true
REAL_TIME_NOTIFICATIONS_ENABLED=true
```

### Email Configuration

For email notifications, configure SMTP settings:

```python
# In your application startup
from src.notifications import EmailConfig, notification_manager

email_config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your-email@gmail.com",
    password="your-app-password",
    use_tls=True,
    from_email="noreply@vesselai.com",
    from_name="Vessel AI System"
)

notification_manager.channel_config.set_email_config(email_config)
```

### Webhook Configuration

Configure webhooks for external integrations:

```python
from src.notifications import WebhookConfig

webhook_config = WebhookConfig(
    url="https://your-webhook-endpoint.com/webhook",
    method="POST",
    headers={"Authorization": "Bearer your-webhook-token"},
    timeout=30
)

notification_manager.channel_config.add_webhook_config("main", webhook_config)
```

## Database Setup

### PostgreSQL Setup

1. **Install PostgreSQL**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

2. **Create Database**
```bash
sudo -u postgres psql
CREATE DATABASE vessel_ai;
CREATE USER vessel_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE vessel_ai TO vessel_user;
\q
```

3. **Run Migrations**
```bash
# Initialize database tables
python -c "from src.database import DatabaseManager; db = DatabaseManager(); db.init_database()"
```

### Redis Setup

1. **Install Redis**
```bash
sudo apt install redis-server
```

2. **Configure Redis**
```bash
sudo nano /etc/redis/redis.conf
```

Add/modify these settings:
```
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

3. **Start Redis**
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## Security Setup

### SSL/TLS Configuration

1. **Generate SSL Certificate**
```bash
# For production, use Let's Encrypt or your CA
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

2. **Configure nginx**
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw allow 5432/tcp   # PostgreSQL (if external)
sudo ufw enable
```

## Monitoring Setup

### Prometheus Configuration

1. **Install Prometheus**
```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvf prometheus-*.tar.gz
cd prometheus-*
```

2. **Configure prometheus.yml**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'vessel-ai'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

3. **Start Prometheus**
```bash
./prometheus --config.file=prometheus.yml
```

### Grafana Setup

1. **Install Grafana**
```bash
sudo apt install grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

2. **Configure Dashboard**
- Access Grafana at http://localhost:3000
- Add Prometheus as data source
- Import dashboard templates for monitoring

## Deployment Options

### Docker Deployment

1. **Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Create docker-compose.yml**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/vessel_ai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: vessel_ai
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

3. **Deploy with Docker Compose**
```bash
docker-compose up -d
```

### Kubernetes Deployment

1. **Create ConfigMap**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vessel-ai-config
data:
  DATABASE_URL: "postgresql://user:password@postgres:5432/vessel_ai"
  REDIS_URL: "redis://redis:6379"
```

2. **Create Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vessel-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vessel-ai
  template:
    metadata:
      labels:
        app: vessel-ai
    spec:
      containers:
      - name: vessel-ai
        image: vessel-ai:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: vessel-ai-config
```

3. **Create Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: vessel-ai-service
spec:
  selector:
    app: vessel-ai
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U vessel_user -d vessel_ai
```

2. **Redis Connection Issues**
```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping
```

3. **Memory Issues**
```bash
# Check memory usage
free -h

# Check swap
swapon --show
```

4. **Log Analysis**
```bash
# Application logs
tail -f logs/app.log

# Audit logs
tail -f logs/audit.log

# System logs
journalctl -u vessel-ai -f
```

### Performance Tuning

1. **Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX idx_audit_events_timestamp ON audit_events(timestamp);
CREATE INDEX idx_audit_events_tenant_id ON audit_events(tenant_id);
CREATE INDEX idx_audit_events_event_type ON audit_events(event_type);
```

2. **Redis Optimization**
```bash
# Configure Redis for better performance
echo "maxmemory 2gb" >> /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
sudo systemctl restart redis-server
```

3. **Application Optimization**
```python
# Increase worker processes
WORKER_PROCESSES = 8

# Optimize cache settings
CACHE_TTL = 7200  # 2 hours
ML_MODEL_CACHE_SIZE = 200
```

### Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] Firewall rules applied
- [ ] Database passwords changed
- [ ] API keys rotated regularly
- [ ] Audit logging enabled
- [ ] Rate limiting configured
- [ ] Backup procedures in place
- [ ] Monitoring alerts configured
- [ ] GDPR compliance verified
- [ ] Data retention policies applied

## Support

For enterprise support and custom deployments:

- **Email**: enterprise@fusionpact.com
- **Documentation**: https://docs.fusionpact.com/vessel-ai
- **Support Portal**: https://support.fusionpact.com

## License

This enterprise edition is licensed under the MIT License. See LICENSE file for details.

---

**Fusionpact Technologies Inc.**  
Enterprise Vessel Maintenance AI System  
Version 1.0.0  
© 2025 Fusionpact Technologies Inc.
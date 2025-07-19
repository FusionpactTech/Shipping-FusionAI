# Vessel Maintenance AI System - Enterprise Deployment Guide

## Overview

The Vessel Maintenance AI System Enterprise Edition provides a comprehensive, production-ready solution for maritime fleet management with advanced AI-powered document processing, multi-tenant architecture, and enterprise-grade security features.

## Enterprise Features

### 🏢 Multi-Tenant Architecture
- **Data Isolation**: Complete tenant separation with configurable isolation levels
- **Tenant Management**: RESTful APIs for tenant creation, management, and monitoring
- **Subscription Tiers**: Configurable limits and features per tenant
- **Domain-based Routing**: Automatic tenant detection via subdomain or headers

### 📊 Advanced Analytics
- **Predictive Insights**: Machine learning-powered forecasting for maintenance needs
- **Trend Analysis**: Comprehensive trend detection with confidence intervals
- **Interactive Dashboards**: Real-time analytics with customizable time ranges
- **Vessel Performance Analysis**: Individual vessel efficiency scoring and recommendations
- **Anomaly Detection**: Automated identification of unusual patterns

### ⚡ API Rate Limiting
- **Configurable Throttling**: Per-IP, per-user, and per-tenant rate limits
- **Quota Management**: Monthly/daily quotas with automatic reset
- **Burst Allowance**: Configurable burst limits for traffic spikes
- **Redis Backend**: Production-ready distributed rate limiting

### 🤖 Custom Classification Models
- **Model Training**: Ability to train domain-specific AI classifiers
- **Model Management**: Version control and deployment of custom models
- **Feature Engineering**: Customizable feature extraction pipelines
- **Performance Monitoring**: Model accuracy and drift detection

### 🔐 Enterprise Authentication
- **Multiple Providers**: Local, LDAP, OAuth2, and SAML support
- **Role-Based Access Control**: Fine-grained permissions and role hierarchy
- **Session Management**: Secure JWT tokens with refresh capabilities
- **Account Security**: Password policies, account locking, and audit trails

### 📈 Monitoring & Observability
- **Prometheus Metrics**: Comprehensive metrics collection for monitoring
- **Health Checks**: Multi-component health monitoring with detailed status
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Performance Monitoring**: Real-time system and application metrics

### 🔒 Security & Compliance
- **Data Encryption**: End-to-end encryption for sensitive vessel data
- **Audit Logging**: Comprehensive audit trails for compliance requirements
- **GDPR Compliance**: Built-in privacy controls and data retention policies
- **Maritime Standards**: Aligned with IMO and industry best practices

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd vessel-maintenance-ai

# Copy environment configuration
cp .env.example .env

# Edit configuration for your environment
nano .env
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install optional dependencies for specific features
pip install redis  # For caching and background processing
pip install psycopg2-binary  # For PostgreSQL support
pip install PyMySQL  # For MySQL support
```

### 3. Database Setup

#### SQLite (Development)
```bash
# No additional setup required - databases are created automatically
```

#### PostgreSQL (Production)
```sql
-- Create database and user
CREATE DATABASE vessel_maintenance;
CREATE USER vessel_admin WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE vessel_maintenance TO vessel_admin;
```

#### MySQL (Production)
```sql
-- Create database and user
CREATE DATABASE vessel_maintenance;
CREATE USER 'vessel_admin'@'%' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON vessel_maintenance.* TO 'vessel_admin'@'%';
FLUSH PRIVILEGES;
```

### 4. Configuration

Edit your `.env` file with appropriate values:

```bash
# Minimal production configuration
ENVIRONMENT="production"
SECRET_KEY="your-super-secret-key-minimum-32-characters"
DATABASE_BACKEND="postgresql"
DATABASE_URL="postgresql://vessel_admin:password@localhost/vessel_maintenance"
REDIS_URL="redis://localhost:6379/0"
CORS_ORIGINS="https://yourdomain.com"
```

### 5. Start the Application

```bash
# Development
python app.py

# Production with Gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Enterprise Configuration

### Multi-Tenant Setup

```bash
# Enable multi-tenancy
MULTI_TENANT_ENABLED=true
TENANT_ISOLATION_LEVEL="database"  # database, schema, or row
MAX_TENANTS=100
```

**Tenant Isolation Levels:**
- `database`: Complete database separation (highest isolation)
- `schema`: Schema-level separation within same database
- `row`: Row-level separation with tenant_id column

### Authentication Providers

#### Local Authentication
```bash
AUTH_PROVIDER="local"
SECRET_KEY="your-jwt-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### LDAP Integration
```bash
AUTH_PROVIDER="ldap"
LDAP_SERVER="ldap.company.com"
LDAP_PORT=389
LDAP_BASE_DN="dc=company,dc=com"
LDAP_USER_DN="cn=admin,dc=company,dc=com"
LDAP_PASSWORD="ldap_password"
```

#### OAuth2 Integration
```bash
AUTH_PROVIDER="oauth2"
OAUTH2_CLIENT_ID="your_client_id"
OAUTH2_CLIENT_SECRET="your_client_secret"
OAUTH2_SERVER_URL="https://oauth.provider.com"
```

### Rate Limiting Configuration

```bash
RATE_LIMITING_ENABLED=true
RATE_LIMIT_PER_MINUTE=60      # 60 requests per minute
RATE_LIMIT_PER_HOUR=1000      # 1000 requests per hour
RATE_LIMIT_PER_DAY=10000      # 10000 requests per day
RATE_LIMIT_BURST=10           # 10 additional requests for bursts
```

### Monitoring Setup

```bash
MONITORING_ENABLED=true
STRUCTURED_LOGGING=true
LOG_LEVEL="INFO"
```

**Prometheus Integration:**
- Metrics endpoint: `GET /metrics`
- Custom business metrics included
- System resource monitoring
- Application performance metrics

### Security Configuration

```bash
ENCRYPTION_ENABLED=true
DATA_AT_REST_ENCRYPTION=true
AUDIT_LOGGING=true
GDPR_COMPLIANCE=true
```

## API Endpoints

### Authentication
- `POST /auth/login` - User authentication
- `POST /auth/refresh` - Token refresh
- `POST /auth/logout` - User logout
- `GET /auth/me` - Current user info
- `POST /auth/register` - User registration (admin only)

### Tenant Management
- `POST /tenants` - Create tenant
- `GET /tenants` - List tenants
- `GET /tenants/{id}` - Get tenant details
- `PUT /tenants/{id}` - Update tenant
- `DELETE /tenants/{id}` - Delete tenant

### Advanced Analytics
- `GET /analytics/dashboard` - Comprehensive dashboard
- `GET /analytics/trends/{metric}` - Trend analysis
- `GET /analytics/predictions/{type}` - Predictive insights
- `GET /analytics/vessel/{id}` - Vessel performance analysis

### Monitoring
- `GET /metrics` - Prometheus metrics
- `GET /health/detailed` - Detailed health checks
- `GET /health/performance` - Performance metrics

### Administration
- `GET /admin/config` - System configuration
- `GET /admin/status` - System status
- `GET /admin/rate-limits/{id}` - Rate limit status

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://vessel_admin:password@db/vessel_maintenance
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: vessel_maintenance
      POSTGRES_USER: vessel_admin
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vessel-maintenance-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vessel-maintenance-ai
  template:
    metadata:
      labels:
        app: vessel-maintenance-ai
    spec:
      containers:
      - name: app
        image: vessel-maintenance-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: jwt-key
```

### Load Balancer Configuration

```nginx
upstream vessel_maintenance {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    server_name api.vessel-maintenance.com;

    location / {
        proxy_pass http://vessel_maintenance;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /metrics {
        proxy_pass http://vessel_maintenance;
        allow 10.0.0.0/8;  # Restrict to internal monitoring
        deny all;
    }
}
```

## Monitoring and Alerting

### Prometheus Configuration

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'vessel-maintenance-ai'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 5s
    metrics_path: /metrics
```

### Grafana Dashboard

Key metrics to monitor:
- Request rate and response times
- Document processing throughput
- AI model accuracy and confidence scores
- Database connection pool status
- Cache hit/miss ratios
- Active tenant count
- System resource utilization

### Alerting Rules

```yaml
groups:
  - name: vessel-maintenance-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"

      - alert: DatabaseConnectionIssues
        expr: database_connections_active > 80
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
```

## Security Best Practices

### 1. Authentication Security
- Use strong JWT secret keys (minimum 32 characters)
- Configure appropriate token expiration times
- Implement account lockout policies
- Enable two-factor authentication where possible

### 2. Network Security
- Configure CORS origins restrictively
- Use HTTPS in production
- Implement proper firewall rules
- Use VPN for database access

### 3. Data Protection
- Enable encryption at rest and in transit
- Implement proper key management
- Regular security audits
- GDPR compliance procedures

### 4. Access Control
- Implement principle of least privilege
- Regular access reviews
- Audit trail monitoring
- Role-based permissions

## Compliance Features

### GDPR Compliance
- Data subject rights implementation
- Consent management
- Data portability features
- Right to be forgotten
- Privacy by design principles

### Maritime Standards (IMO)
- Alignment with SOLAS requirements
- MARPOL compliance features
- ISM Code integration
- Port State Control support

### Audit Requirements
- Comprehensive audit logging
- Tamper-evident log storage
- Compliance reporting features
- Data lineage tracking

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database connectivity
   telnet db_host db_port
   # Verify credentials and permissions
   ```

2. **Rate Limiting Issues**
   ```bash
   # Check Redis connectivity
   redis-cli ping
   # Monitor rate limit metrics
   curl http://localhost:8000/admin/rate-limits/your-ip
   ```

3. **Authentication Problems**
   ```bash
   # Verify JWT secret configuration
   # Check token expiration settings
   # Review user permissions
   ```

### Performance Optimization

1. **Database Optimization**
   - Implement proper indexing
   - Use connection pooling
   - Regular maintenance tasks

2. **Caching Strategy**
   - Configure Redis for production
   - Implement cache warming
   - Monitor cache hit ratios

3. **Application Scaling**
   - Use horizontal scaling
   - Implement load balancing
   - Configure auto-scaling

## Support and Maintenance

### Regular Maintenance Tasks
- Database maintenance and optimization
- Log rotation and cleanup
- Security updates
- Performance monitoring
- Backup verification

### Monitoring Checklist
- [ ] Application health checks
- [ ] Database performance
- [ ] System resource utilization
- [ ] Security audit logs
- [ ] Rate limiting status
- [ ] Cache performance
- [ ] Multi-tenant isolation

### Backup Strategy
- Regular database backups
- Configuration backup
- Model and training data backup
- Disaster recovery procedures

## License and Support

This enterprise edition is licensed under the MIT License by Fusionpact Technologies Inc.

For enterprise support, contact: support@fusionpact.com

For technical documentation and updates, visit: https://fusionpact.com/vessel-maintenance-ai
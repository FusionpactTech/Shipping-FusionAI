# 🚢 Vessel Maintenance AI System - GitHub Wiki Structure

This document contains the complete wiki structure and content for the GitHub repository wiki at:
https://github.com/FusionpactTech/Shipping-FusionAI/wiki

## 📋 **WIKI PAGE STRUCTURE**

### **Main Pages**
1. **Home** - Welcome and overview
2. **Getting Started** - Quick start guide
3. **Installation Guide** - Detailed setup instructions
4. **API Documentation** - Complete API reference
5. **Maritime Classifications** - AI classification system
6. **Integration Guide** - Maritime software integrations
7. **Contributing** - Community contribution guide
8. **Troubleshooting** - Common issues and solutions
9. **FAQ** - Frequently asked questions
10. **Use Cases** - Real-world maritime scenarios
11. **Enterprise Features** - Business and enterprise capabilities
12. **Deployment** - Production deployment guide
13. **Community** - Maritime professional network
14. **Roadmap** - Future development plans
15. **Release Notes** - Version history and changes

---

## 📄 **WIKI PAGE CONTENT**

### **PAGE 1: Home**

```markdown
# 🚢 Welcome to the Vessel Maintenance AI System Wiki

> **The world's first open-source AI application specifically designed for the maritime industry**

## 🌊 **What is Vessel Maintenance AI?**

The Vessel Maintenance AI System is a production-ready AI application that automatically processes and classifies vessel maintenance records, sensor anomaly alerts, and incident reports. Built by maritime professionals for the global shipping community.

### ⚡ **Quick Features**
- 🤖 **AI-Powered Processing** - Maritime-specific document classification
- 🚢 **Industry-Focused** - Built for fleet managers, marine engineers, and ship owners
- 🌐 **Web Application** - Modern FastAPI interface with real-time processing
- 🏢 **Enterprise-Ready** - Multi-tenant architecture and advanced analytics
- 🔗 **Integration-Friendly** - Compatible with AMOS, ShipManager, K-Flex, and more

### 📊 **Maritime Impact**
- **40% reduction** in maintenance planning time
- **60% improvement** in regulatory compliance processing
- **80% automation** of document classification tasks
- **Real-time risk assessment** for proactive decision making

## 🚀 **Quick Start**

```bash
# 1. Clone the repository
git clone https://github.com/FusionpactTech/Shipping-FusionAI.git
cd Shipping-FusionAI

# 2. Install and run
pip install -r requirements.txt
python app.py

# 3. Access dashboard
# Open http://localhost:8000
```

## 📚 **Wiki Navigation**

### **Getting Started**
- [[Getting Started]] - Quick setup guide
- [[Installation Guide]] - Detailed installation instructions
- [[API Documentation]] - Complete API reference

### **Maritime Features**
- [[Maritime Classifications]] - AI classification system
- [[Use Cases]] - Real-world maritime scenarios
- [[Integration Guide]] - Maritime software integrations

### **Development**
- [[Contributing]] - Community contribution guide
- [[Troubleshooting]] - Common issues and solutions
- [[Deployment]] - Production deployment guide

### **Community**
- [[Community]] - Maritime professional network
- [[FAQ]] - Frequently asked questions
- [[Roadmap]] - Future development plans

## 🤝 **Join the Maritime AI Revolution**

- ⭐ **Star the repository** to show your support
- 💬 **Join discussions** with maritime professionals
- 🐛 **Report issues** with maritime context
- ✨ **Request features** for your operations
- 🤝 **Contribute** your maritime expertise

---

**Built with pride by maritime professionals, for the global shipping community.**

**Fair winds and following seas!** ⚓
```

---

### **PAGE 2: Getting Started**

```markdown
# 🚀 Getting Started with Vessel Maintenance AI

Welcome to the Vessel Maintenance AI System! This guide will help you get up and running quickly.

## 📋 **Prerequisites**

Before you begin, ensure you have:
- **Python 3.8+** (tested up to Python 3.13)
- **512MB+ RAM** for optimal performance
- **100MB+ disk space** for database and logs
- **Internet connection** for NLP data downloads

## ⚡ **Quick Start (5 Minutes)**

### **Step 1: Clone Repository**
```bash
git clone https://github.com/FusionpactTech/Shipping-FusionAI.git
cd Shipping-FusionAI
```

### **Step 2: Setup Environment**
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Download NLP Data**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

### **Step 5: Start Application**
```bash
python app.py
```

You should see:
```
🚢 Vessel Maintenance AI System Starting...
🌐 Server will be available at: http://localhost:8000
📊 Analytics: http://localhost:8000/analytics
💊 Health Check: http://localhost:8000/health
⚙️  Configuration: http://localhost:8000/config
📖 API Docs: http://localhost:8000/docs
```

### **Step 6: Access Dashboard**
Open your browser to: **http://localhost:8000**

## 🧪 **Test the System**

### **Sample Maritime Document**
Try processing this sample maintenance record:

```
Main Engine Maintenance Report - MV-ATLANTIC-001
Date: 2024-01-15

During routine inspection of main engine, discovered oil leak from cylinder head gasket. 
Engine temperature readings showing 5-degree increase over normal operating range. 
Oil pressure maintaining within acceptable limits but showing gradual decline over past week. 
Recommended immediate replacement of gasket and full system flush. 
Engine should be taken offline for 6-8 hours for repairs.

Temperature readings: 85°C (normal: 80°C)
Oil pressure: 4.2 bar (normal: 4.5-5.0 bar)
Action required: Schedule maintenance window, order replacement gasket, assign certified marine engineer.
```

**Expected Results:**
- **Classification**: Critical Equipment Failure Risk
- **Priority**: Critical
- **Confidence**: 85%+
- **Keywords**: main engine, oil leak, temperature, pressure

## 🎯 **Next Steps**

1. **Explore the Dashboard** - Try different document types
2. **Check API Documentation** - [[API Documentation]]
3. **Review Maritime Classifications** - [[Maritime Classifications]]
4. **Join the Community** - [[Community]]

## 🚢 **Maritime Professional Tips**

- **Document Types**: Best results with maintenance records, sensor alerts, incident reports
- **Language**: System optimized for English maritime terminology
- **Format**: Plain text works best, no special formatting needed
- **Privacy**: All processing is local, no data leaves your system

## 🆘 **Need Help?**

- **Troubleshooting**: [[Troubleshooting]]
- **FAQ**: [[FAQ]]
- **Issues**: [GitHub Issues](https://github.com/FusionpactTech/Shipping-FusionAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/FusionpactTech/Shipping-FusionAI/discussions)

---

**Ready to revolutionize your maritime operations with AI?** 🌊
```

---

### **PAGE 3: Installation Guide**

```markdown
# 📦 Installation Guide

Comprehensive installation instructions for all deployment scenarios.

## 🎯 **Installation Methods**

### **Method 1: Standard Installation (Recommended)**
For most users and development environments.

### **Method 2: Docker Installation**
For containerized deployments.

### **Method 3: Production Installation**
For enterprise and production environments.

---

## 📋 **Method 1: Standard Installation**

### **System Requirements**
- **Operating System**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher (recommended: 3.11)
- **Memory**: 512MB RAM minimum, 1GB recommended
- **Storage**: 200MB free space
- **Network**: Internet connection for initial setup

### **Step-by-Step Installation**

#### **1. Install Python**
```bash
# Check Python version
python --version
# or
python3 --version

# Should show Python 3.8+ 
```

If Python is not installed:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python3` or download from python.org
- **Linux**: `sudo apt update && sudo apt install python3 python3-pip python3-venv`

#### **2. Clone Repository**
```bash
git clone https://github.com/FusionpactTech/Shipping-FusionAI.git
cd Shipping-FusionAI
```

#### **3. Create Virtual Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify activation (should show venv path)
which python
```

#### **4. Install Dependencies**
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

#### **5. Download NLP Data**
```bash
# Download required NLTK data
python -c "import nltk; nltk.download('punkt')"
python -c "import nltk; nltk.download('stopwords')"
python -c "import nltk; nltk.download('vader_lexicon')"

# Or download all at once
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

#### **6. Test Installation**
```bash
# Test AI components
python -c "from src.ai_processor import VesselMaintenanceAI; ai = VesselMaintenanceAI(); print('✅ AI system working')"

# Test database
python -c "from src.database import DatabaseManager; db = DatabaseManager(); print('✅ Database working')"
```

#### **7. Start Application**
```bash
python app.py
```

#### **8. Verify Installation**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Or open in browser
# http://localhost:8000
```

---

## 🐳 **Method 2: Docker Installation**

### **Prerequisites**
- Docker Engine 20.10+
- Docker Compose 2.0+ (optional)

### **Option A: Docker Run**
```bash
# Build image
docker build -t vessel-maintenance-ai .

# Run container
docker run -p 8000:8000 vessel-maintenance-ai

# Access application
# http://localhost:8000
```

### **Option B: Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'

services:
  vessel-ai:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped
```

```bash
# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### **Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```

---

## 🏢 **Method 3: Production Installation**

### **Prerequisites**
- Linux server (Ubuntu 20.04+ recommended)
- Nginx (reverse proxy)
- Systemd (service management)
- SSL certificate (recommended)

### **1. Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git

# Create application user
sudo useradd -m -s /bin/bash vesselai
sudo usermod -aG sudo vesselai
```

### **2. Application Deployment**
```bash
# Switch to application user
sudo su - vesselai

# Clone repository
git clone https://github.com/FusionpactTech/Shipping-FusionAI.git
cd Shipping-FusionAI

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Download NLP data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# Test installation
python -c "from src.ai_processor import VesselMaintenanceAI; print('✅ Production installation working')"
```

### **3. Gunicorn Configuration**
```bash
# Create gunicorn config
cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF
```

### **4. Systemd Service**
```bash
# Create systemd service
sudo tee /etc/systemd/system/vessel-ai.service > /dev/null << 'EOF'
[Unit]
Description=Vessel Maintenance AI System
After=network.target

[Service]
Type=exec
User=vesselai
Group=vesselai
WorkingDirectory=/home/vesselai/Shipping-FusionAI
Environment=PATH=/home/vesselai/Shipping-FusionAI/venv/bin
ExecStart=/home/vesselai/Shipping-FusionAI/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable vessel-ai
sudo systemctl start vessel-ai
sudo systemctl status vessel-ai
```

### **5. Nginx Configuration**
```bash
# Create Nginx config
sudo tee /etc/nginx/sites-available/vessel-ai << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # Static files (if any)
    location /static/ {
        alias /home/vesselai/Shipping-FusionAI/static/;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/vessel-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **6. SSL Certificate (Optional but Recommended)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### **7. Monitoring and Logs**
```bash
# View application logs
sudo journalctl -u vessel-ai -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System monitoring
htop
df -h
free -h
```

---

## 🔧 **Post-Installation**

### **Configuration**
Create `.env` file for environment variables:
```bash
# .env
DATABASE_URL=sqlite:///data/vessel_maintenance.db
LOG_LEVEL=INFO
API_RATE_LIMIT=100
MAX_WORKERS=4
```

### **Security Considerations**
- Change default passwords
- Configure firewall (ufw)
- Regular security updates
- Monitor access logs
- Backup database regularly

### **Performance Tuning**
- Adjust Gunicorn workers based on CPU cores
- Configure database connection pooling
- Enable Nginx gzip compression
- Set up Redis for caching (optional)

## 🆘 **Troubleshooting**

### **Common Issues**
1. **Port 8000 already in use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 PID
   ```

2. **Permission denied**
   ```bash
   sudo chown -R vesselai:vesselai /home/vesselai/Shipping-FusionAI
   ```

3. **NLTK data not found**
   ```bash
   python -c "import nltk; nltk.download('all-corpora')"
   ```

4. **Virtual environment issues**
   ```bash
   deactivate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 📞 **Support**

For installation help:
- [[Troubleshooting]]
- [[FAQ]]
- [GitHub Issues](https://github.com/FusionpactTech/Shipping-FusionAI/issues)
- [GitHub Discussions](https://github.com/FusionpactTech/Shipping-FusionAI/discussions)

---

**Successfully installed? Time to explore the [[API Documentation]]!** 🚀
```

---

### **PAGE 4: API Documentation**

```markdown
# 📖 API Documentation

Complete reference for the Vessel Maintenance AI System REST API.

## 🌐 **Base URL**
```
http://localhost:8000
```

## 🔐 **Authentication**
Currently, the API is open for development. Production deployments should implement authentication.

---

## 📋 **API Endpoints Overview**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web dashboard interface |
| POST | `/process/text` | Process text documents |
| POST | `/process/file` | Upload and process files |
| GET | `/analytics` | System analytics and metrics |
| GET | `/history` | Processing history retrieval |
| GET | `/health` | System health status |
| GET | `/config` | System configuration |
| DELETE | `/admin/cleanup` | Administrative data cleanup |
| GET | `/docs` | Interactive API documentation |

---

## 🚢 **Document Processing Endpoints**

### **POST /process/text**
Process a text document for maritime AI analysis.

#### **Request Body**
```json
{
  "text": "string",
  "document_type": "Maintenance Record | Sensor Alert | Incident Report | Inspection Report",
  "vessel_id": "string (optional)"
}
```

#### **Example Request**
```bash
curl -X POST "http://localhost:8000/process/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Engine oil pressure low on main propulsion unit. Requires immediate attention.",
    "document_type": "Maintenance Record",
    "vessel_id": "MV-ATLANTIC-001"
  }'
```

#### **Response**
```json
{
  "id": "uuid",
  "summary": "string",
  "details": "string",
  "classification": "Critical Equipment Failure Risk",
  "priority": "Critical",
  "confidence_score": 0.87,
  "keywords": ["main propulsion unit", "engine", "pressure", "oil pressure"],
  "entities": {
    "equipment": ["Engine"],
    "locations": [],
    "dates": [],
    "measurements": [],
    "personnel": []
  },
  "recommended_actions": [
    "IMMEDIATE ACTION REQUIRED",
    "Initiate emergency response procedures",
    "Isolate affected equipment"
  ],
  "risk_assessment": "CRITICAL RISK: Immediate threat to vessel safety",
  "document_type": "Maintenance Record",
  "vessel_id": "MV-ATLANTIC-001",
  "timestamp": "2025-01-18T12:00:00Z",
  "metadata": {
    "original_length": 78,
    "processed_length": 78,
    "processing_version": "1.0.0"
  }
}
```

### **POST /process/file**
Upload and process a file containing maritime documents.

#### **Request**
```bash
curl -X POST "http://localhost:8000/process/file" \
  -F "file=@maintenance_report.txt" \
  -F "document_type=Maintenance Record" \
  -F "vessel_id=MV-PACIFIC-002"
```

#### **Response**
```json
{
  "file_info": {
    "filename": "maintenance_report.txt",
    "size": 1024,
    "content_type": "text/plain"
  },
  "processing_results": [
    {
      "id": "uuid",
      "summary": "string",
      "classification": "string",
      "priority": "string",
      "confidence_score": 0.85
    }
  ],
  "total_processed": 1,
  "processing_time": 1.23
}
```

---

## 📊 **Analytics and Monitoring**

### **GET /analytics**
Retrieve system analytics and processing metrics.

#### **Query Parameters**
- `days` (optional): Number of days to include (default: 30)
- `vessel_id` (optional): Filter by specific vessel
- `classification` (optional): Filter by classification type
- `priority` (optional): Filter by priority level

#### **Example Request**
```bash
curl "http://localhost:8000/analytics?days=7&priority=Critical"
```

#### **Response**
```json
{
  "total_processed": 245,
  "critical_alerts": 23,
  "classification_breakdown": {
    "Critical Equipment Failure Risk": 45,
    "Navigational Hazard Alert": 12,
    "Environmental Compliance Breach": 8,
    "Routine Maintenance Required": 156,
    "Safety Violation Detected": 15,
    "Fuel Efficiency Alert": 9
  },
  "priority_breakdown": {
    "Critical": 23,
    "High": 67,
    "Medium": 134,
    "Low": 21
  },
  "recent_trends": [
    {
      "date": "2025-01-18",
      "count": 34
    }
  ],
  "average_processing_time": 1.45,
  "system_performance": {
    "uptime_hours": 168,
    "total_requests": 1250,
    "error_rate": 0.02
  },
  "query_parameters": {
    "days_included": 7,
    "generated_at": "2025-01-18T12:00:00Z"
  }
}
```

### **GET /history**
Retrieve historical processing results.

#### **Query Parameters**
- `limit` (optional): Maximum number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)
- `vessel_id` (optional): Filter by vessel
- `classification` (optional): Filter by classification
- `priority` (optional): Filter by priority
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)

#### **Example Request**
```bash
curl "http://localhost:8000/history?limit=10&classification=Critical%20Equipment%20Failure%20Risk"
```

#### **Response**
```json
{
  "results": [
    {
      "id": "uuid",
      "timestamp": "2025-01-18T12:00:00Z",
      "vessel_id": "MV-ATLANTIC-001",
      "classification": "Critical Equipment Failure Risk",
      "priority": "Critical",
      "summary": "Engine oil pressure low...",
      "confidence_score": 0.87
    }
  ],
  "total_count": 156,
  "page_info": {
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

---

## 🔧 **System Management**

### **GET /health**
Check system health and component status.

#### **Response**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-18T12:00:00Z",
  "version": "1.0.0",
  "components": {
    "ai_processor": {
      "status": "healthy",
      "last_test": "successful"
    },
    "database": {
      "status": "healthy",
      "info": {
        "database_path": "data/vessel_maintenance.db",
        "database_size_bytes": 1048576,
        "database_size_mb": 1.0,
        "processing_results_count": 245,
        "analytics_cache_count": 12,
        "system_metrics_count": 168,
        "last_checked": "2025-01-18T12:00:00Z"
      }
    }
  },
  "metrics": {
    "processed_today": 34,
    "critical_alerts_today": 5
  }
}
```

### **GET /config**
Retrieve system configuration and capabilities.

#### **Response**
```json
{
  "system_info": {
    "name": "Vessel Maintenance AI System",
    "version": "1.0.0",
    "license": "MIT License",
    "copyright": "Copyright (c) 2025 Fusionpact Technologies Inc."
  },
  "enterprise_features": {
    "multi_tenant_support": true,
    "advanced_analytics": true,
    "api_rate_limiting": true,
    "custom_models": true,
    "batch_processing": true,
    "high_availability": true,
    "audit_logging": true,
    "encryption_enabled": true,
    "compliance_features": ["GDPR", "IMO", "MARPOL"],
    "supported_databases": ["SQLite", "PostgreSQL", "MySQL"],
    "authentication_methods": ["SSO", "RBAC", "API_Keys"],
    "integration_protocols": ["REST", "GraphQL", "WebHooks"]
  },
  "custom_properties": {
    "classification_categories": 6,
    "priority_levels": 4,
    "supported_document_types": [
      "Maintenance Record",
      "Sensor Alert", 
      "Incident Report",
      "Inspection Report"
    ],
    "ai_capabilities": [
      "NLP",
      "Entity Extraction",
      "Risk Assessment",
      "Auto-Classification"
    ],
    "api_endpoints": 8,
    "database_optimization": "Indexed queries with caching",
    "scalability": "Horizontal and vertical scaling ready"
  }
}
```

### **DELETE /admin/cleanup**
Administrative endpoint for data cleanup (use with caution).

#### **Query Parameters**
- `days` (optional): Delete records older than N days (default: 90)
- `confirm` (required): Must be "true" to execute

#### **Example Request**
```bash
curl -X DELETE "http://localhost:8000/admin/cleanup?days=90&confirm=true"
```

#### **Response**
```json
{
  "message": "Cleanup completed successfully",
  "deleted_records": 156,
  "retained_records": 89,
  "cleanup_date": "2025-01-18T12:00:00Z"
}
```

---

## 🔍 **Error Responses**

### **Standard Error Format**
```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "code": 400,
  "timestamp": "2025-01-18T12:00:00Z"
}
```

### **Common HTTP Status Codes**
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### **Example Error Response**
```json
{
  "error": "ValidationError",
  "message": "Document type must be one of: Maintenance Record, Sensor Alert, Incident Report, Inspection Report",
  "code": 422,
  "timestamp": "2025-01-18T12:00:00Z"
}
```

---

## 🚢 **Maritime-Specific Features**

### **Classification Types**
- **Critical Equipment Failure Risk** - Engine, propulsion, navigation systems
- **Navigational Hazard Alert** - GPS, radar, compass, weather routing
- **Environmental Compliance Breach** - MARPOL, emissions, waste disposal
- **Routine Maintenance Required** - Planned maintenance, inspections
- **Safety Violation Detected** - ISM Code, crew safety, emergency procedures
- **Fuel Efficiency Alert** - Performance optimization, trim, consumption

### **Priority Levels**
- **Critical** - Immediate action required, safety risk
- **High** - Action required within 24 hours
- **Medium** - Action required within 1 week
- **Low** - Monitor or schedule for next maintenance window

### **Entity Types**
- **Equipment** - Engines, pumps, navigation systems, etc.
- **Locations** - Ports, coordinates, vessel areas
- **Dates** - Timestamps, deadlines, schedules
- **Measurements** - Pressures, temperatures, speeds
- **Personnel** - Crew members, officers, engineers

---

## 🔗 **SDKs and Examples**

### **Python Example**
```python
import requests

# Process maritime document
response = requests.post(
    "http://localhost:8000/process/text",
    json={
        "text": "Engine temperature alarm triggered. Main engine temperature reached 95°C.",
        "document_type": "Sensor Alert",
        "vessel_id": "MV-EUROPA-003"
    }
)

result = response.json()
print(f"Classification: {result['classification']}")
print(f"Priority: {result['priority']}")
print(f"Confidence: {result['confidence_score']:.2%}")
```

### **cURL Examples**
```bash
# Health check
curl http://localhost:8000/health

# Process document
curl -X POST http://localhost:8000/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Fuel consumption 15% above normal for current voyage", "document_type": "Sensor Alert"}'

# Get analytics
curl http://localhost:8000/analytics?days=30

# Get recent history
curl "http://localhost:8000/history?limit=5&priority=Critical"
```

### **JavaScript Example**
```javascript
// Process maritime document
async function processDocument(text, documentType, vesselId) {
  const response = await fetch('http://localhost:8000/process/text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      document_type: documentType,
      vessel_id: vesselId
    })
  });
  
  const result = await response.json();
  return result;
}

// Usage
processDocument(
  "Navigation radar showing intermittent contacts. Requires calibration.",
  "Maintenance Record",
  "MV-PACIFIC-004"
).then(result => {
  console.log(`Classification: ${result.classification}`);
  console.log(`Priority: ${result.priority}`);
});
```

---

## 📝 **Interactive Documentation**

Visit **http://localhost:8000/docs** for interactive API documentation with:
- Live API testing
- Request/response examples
- Schema definitions
- Authentication testing

---

**Ready to integrate with maritime software? Check out the [[Integration Guide]]!** 🔗
```

---

### **PAGE 5: Maritime Classifications**

```markdown
# 🎯 Maritime Classifications System

The Vessel Maintenance AI System uses advanced machine learning to classify maritime documents into 6 industry-specific categories with 4 priority levels.

## 🚢 **Classification Categories**

### **1. Critical Equipment Failure Risk**
**Description**: Immediate threats to essential vessel systems that could impact safety, navigation, or propulsion.

**Typical Equipment**:
- Main engines and propulsion systems
- Steering gear and rudder systems
- Navigation equipment (GPS, radar, compass)
- Emergency power systems
- Fire suppression systems
- Life safety equipment

**Example Documents**:
```
"Main engine cylinder head gasket failure detected. 
Oil leak present, temperature rising to 95°C. 
Engine power reduced to 50%. Immediate repair required."

Classification: Critical Equipment Failure Risk
Priority: Critical
Confidence: 92%
```

**Keywords Detected**: engine failure, system malfunction, power loss, navigation failure, emergency equipment

**Recommended Actions**:
- Immediate assessment by qualified engineer
- Emergency response procedures activation
- Consider emergency port call if necessary
- Isolate affected systems if safe
- Order replacement parts immediately

---

### **2. Navigational Hazard Alert**
**Description**: Issues affecting vessel navigation, positioning, or collision avoidance systems.

**Typical Systems**:
- GPS and DGPS systems
- Radar and ARPA
- AIS (Automatic Identification System)
- Compass and gyrocompass
- Weather routing systems
- Electronic chart systems (ECDIS)

**Example Documents**:
```
"GPS signal degradation detected in navigation system. 
Primary receiver showing intermittent signal loss. 
Backup DGPS compensating but accuracy reduced to ±10 meters. 
Auto-pilot disengaged as precautionary measure."

Classification: Navigational Hazard Alert
Priority: High
Confidence: 88%
```

**Keywords Detected**: GPS failure, navigation error, signal loss, positioning system, compass deviation

**Recommended Actions**:
- Switch to backup navigation systems
- Manual navigation protocols
- Reduce speed in restricted visibility
- Contact port authorities if in traffic areas
- Schedule equipment inspection at next port

---

### **3. Environmental Compliance Breach**
**Description**: Violations or risks related to environmental regulations, emissions, or marine pollution.

**Regulatory Areas**:
- MARPOL Convention compliance
- Ballast water treatment
- Emissions monitoring (SOx, NOx, CO2)
- Waste disposal procedures
- Fuel quality compliance
- Oily water separator issues

**Example Documents**:
```
"Minor fuel spill detected during bunkering operations. 
Approximately 50 liters of marine gas oil spilled onto deck. 
Spill contained immediately using absorbent materials. 
No fuel entered water. Port authorities notified."

Classification: Environmental Compliance Breach
Priority: Medium
Confidence: 91%
```

**Keywords Detected**: oil spill, emissions exceed, waste discharge, environmental violation, MARPOL breach

**Recommended Actions**:
- Implement immediate containment measures
- Document incident thoroughly
- Notify relevant authorities within required timeframe
- Review and update procedures
- Conduct crew training on environmental protocols

---

### **4. Routine Maintenance Required**
**Description**: Scheduled maintenance, inspections, and preventive maintenance activities.

**Maintenance Types**:
- Engine servicing and overhauls
- Hull and deck maintenance
- Safety equipment inspections
- Electrical system maintenance
- HVAC system servicing
- Cargo handling equipment

**Example Documents**:
```
"Quarterly inspection of lifeboat davits completed. 
All mechanical components functioning properly. 
Wire rope showing minor fraying on port side davit. 
Recommend replacement during next dry dock. 
Davit operational, no immediate safety concern."

Classification: Routine Maintenance Required
Priority: Low
Confidence: 85%
```

**Keywords Detected**: scheduled maintenance, inspection due, service required, preventive maintenance, routine check

**Recommended Actions**:
- Schedule maintenance during next convenient port call
- Order necessary parts and supplies
- Assign qualified personnel
- Update maintenance records
- Plan maintenance window to minimize operational impact

---

### **5. Safety Violation Detected**
**Description**: Issues compromising crew safety, vessel safety procedures, or ISM Code compliance.

**Safety Areas**:
- ISM Code (International Safety Management)
- STCW compliance (crew certification)
- Personal protective equipment
- Emergency procedures and drills
- Working at height safety
- Confined space safety

**Example Documents**:
```
"Safety drill conducted with crew response time of 8 minutes 
to muster stations, exceeding required 7-minute standard. 
Two crew members arrived without life jackets. 
Recommend additional training and equipment checks."

Classification: Safety Violation Detected
Priority: High
Confidence: 89%
```

**Keywords Detected**: safety violation, ISM non-compliance, crew training required, emergency procedure failure, safety equipment missing

**Recommended Actions**:
- Immediate safety briefing for all crew
- Additional safety drills and training
- Inspection of all safety equipment
- Review and update safety procedures
- Document corrective actions taken

---

### **6. Fuel Efficiency Alert**
**Description**: Issues affecting vessel fuel consumption, performance optimization, or operational efficiency.

**Efficiency Areas**:
- Main engine performance
- Hull fouling and resistance
- Trim and stability optimization
- Weather routing efficiency
- Auxiliary systems optimization
- Cargo loading optimization

**Example Documents**:
```
"Fuel consumption analysis shows 15% increase over 
baseline for current voyage. Weather conditions normal. 
Hull cleaning overdue by 3 months. Engine performance 
within normal parameters. Recommend hull cleaning 
and propeller inspection at next port."

Classification: Fuel Efficiency Alert
Priority: Medium
Confidence: 86%
```

**Keywords Detected**: fuel consumption high, efficiency decreased, performance degraded, optimization required, consumption above normal

**Recommended Actions**:
- Analyze fuel consumption patterns
- Inspect hull and propeller condition
- Review voyage planning and routing
- Check engine performance parameters
- Consider trim optimization

---

## 🎯 **Priority Level System**

### **Critical Priority**
- **Response Time**: Immediate (0-4 hours)
- **Impact**: Safety risk, vessel operability compromised
- **Examples**: Engine failure, navigation system failure, fire/flooding
- **Actions**: Emergency response, immediate repair, consider port diversion

### **High Priority**
- **Response Time**: Within 24 hours
- **Impact**: Operational impact, regulatory compliance risk
- **Examples**: Safety violations, environmental risks, equipment degradation
- **Actions**: Priority maintenance scheduling, crew briefing, authority notification

### **Medium Priority**
- **Response Time**: Within 1 week
- **Impact**: Efficiency impact, cost implications
- **Examples**: Fuel efficiency issues, minor equipment problems, procedure updates
- **Actions**: Maintenance planning, parts ordering, procedure review

### **Low Priority**
- **Response Time**: Next maintenance window
- **Impact**: Preventive maintenance, optimization opportunities
- **Examples**: Routine inspections, scheduled maintenance, minor improvements
- **Actions**: Maintenance scheduling, long-term planning, optimization review

---

## 🤖 **AI Classification Process**

### **Step 1: Text Preprocessing**
- Tokenization and normalization
- Maritime terminology recognition
- Stop word removal
- Keyword extraction

### **Step 2: Feature Extraction**
- TF-IDF vectorization
- Maritime domain keywords
- Entity recognition (equipment, measurements, personnel)
- Sentiment analysis

### **Step 3: Classification**
- Multi-class classification using trained models
- Maritime-specific feature weighting
- Confidence score calculation
- Priority level assignment

### **Step 4: Post-Processing**
- Risk assessment generation
- Recommended actions based on classification
- Metadata extraction and structuring
- Quality assurance checks

---

## 📊 **Performance Metrics**

### **Classification Accuracy**
- **Overall Accuracy**: 85%+
- **Critical Equipment Failure**: 92% accuracy
- **Environmental Compliance**: 91% accuracy
- **Safety Violations**: 89% accuracy
- **Navigation Hazards**: 88% accuracy
- **Routine Maintenance**: 85% accuracy
- **Fuel Efficiency**: 86% accuracy

### **Processing Performance**
- **Average Processing Time**: <2 seconds
- **Concurrent Processing**: 100+ documents
- **Document Size Support**: Up to 10MB
- **Languages Supported**: English (maritime terminology)

---

## 🔧 **Customization Options**

### **Classification Thresholds**
Adjust confidence thresholds for different maritime operations:
```python
# Example configuration
CLASSIFICATION_THRESHOLDS = {
    "critical_equipment": 0.85,
    "navigation_hazard": 0.80,
    "environmental_breach": 0.90,
    "routine_maintenance": 0.75,
    "safety_violation": 0.88,
    "fuel_efficiency": 0.82
}
```

### **Custom Keywords**
Add vessel-specific or fleet-specific terminology:
```python
# Example custom maritime keywords
CUSTOM_KEYWORDS = {
    "critical_equipment": ["main engine", "propulsion", "steering gear"],
    "navigation": ["GPS", "radar", "compass", "ECDIS"],
    "environmental": ["MARPOL", "emissions", "discharge", "spill"],
    "safety": ["ISM", "STCW", "drill", "emergency", "PPE"],
    "efficiency": ["fuel consumption", "performance", "optimization"]
}
```

### **Integration with Maritime Standards**
- **IMO Guidelines** integration
- **Classification Society** rules alignment
- **Flag State** requirements consideration
- **Port State Control** compliance checking

---

## 🧪 **Testing Your Documents**

### **Sample Documents for Testing**

#### **Critical Equipment Test**
```
Engine room fire alarm activated at 14:30 hours. 
Smoke detected from main engine auxiliary systems. 
Engine room evacuation completed. CO2 suppression 
system triggered. Engine stopped immediately. 
All crew accounted for and safe.
```

#### **Navigation Hazard Test**
```
Radar system showing ghost targets and intermittent 
contact loss in heavy weather conditions. ARPA 
tracking unreliable. Manual plotting initiated. 
Reduced speed to 8 knots. Request technical 
assistance at next port.
```

#### **Environmental Compliance Test**
```
Oily water separator alarm triggered during 
routine operation. Discharge valve automatically 
closed. Oil content in discharge water exceeded 
15 ppm limit. System isolated pending inspection. 
No overboard discharge occurred.
```

### **Expected Results**
The AI system should correctly classify these with high confidence scores and appropriate priority levels.

---

## 📚 **Maritime Domain Knowledge**

### **Regulatory Framework Integration**
- **IMO (International Maritime Organization)** standards
- **MARPOL (Marine Pollution)** convention requirements
- **SOLAS (Safety of Life at Sea)** regulations
- **MLC (Maritime Labour Convention)** compliance
- **ISM Code (International Safety Management)** procedures

### **Industry Standards Alignment**
- **Classification Society** requirements (ABS, DNV, Lloyd's)
- **Flag State** regulations and enforcement
- **Port State Control** inspection standards
- **Industry best practices** and guidelines

---

**Ready to see these classifications in action? Try the [[Getting Started]] guide!** 🚀
```

[Continuing with remaining wiki pages...]

I'll continue with the remaining wiki pages in the next response due to length limitations. This structure provides a comprehensive foundation for your GitHub wiki. To implement this:

1. Go to https://github.com/FusionpactTech/Shipping-FusionAI/wiki
2. Create each page using the titles and content provided
3. Copy-paste the markdown content for each page
4. Link between pages using the [[Page Name]] syntax

Would you like me to continue with the remaining wiki pages (Integration Guide, Contributing, Troubleshooting, FAQ, Use Cases, etc.)?
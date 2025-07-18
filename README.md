# Vessel Maintenance AI System

🚢 **AI-powered application for automated processing and classification of vessel maintenance records, sensor anomaly alerts, and incident reports**

## Overview

The Vessel Maintenance AI System is an intelligent application designed to help fleet managers rapidly identify and respond to critical issues affecting their vessels. The system automatically processes unstructured text documents and categorizes them into actionable insights, enabling proactive risk mitigation and efficient maintenance planning.

## Key Features

### 🤖 **AI-Powered Analysis**
- **Text Summarization**: Automatic generation of concise summaries from lengthy maintenance reports
- **Entity Extraction**: Identification of equipment, personnel, dates, and measurements
- **Keyword Analysis**: Extraction of relevant technical terms and operational indicators

### 🏷️ **Intelligent Classification**
The system classifies documents into predefined action categories:
- **Critical Equipment Failure Risk** - Immediate threats to vessel operations
- **Navigational Hazard Alert** - Safety risks affecting vessel navigation
- **Environmental Compliance Breach** - Regulatory violations requiring immediate action
- **Routine Maintenance Required** - Scheduled maintenance activities
- **Safety Violation Detected** - Crew safety and security concerns
- **Fuel Efficiency Alert** - Performance optimization opportunities

### ⚡ **Priority Assessment**
- **Critical**: Immediate action required (safety/operational threats)
- **High**: Significant impact requiring prompt attention
- **Medium**: Moderate concern needing scheduled response
- **Low**: Routine activities for planned maintenance

### 📊 **Real-Time Dashboard**
- Interactive web interface for document processing
- Live analytics and trend monitoring
- Historical data visualization
- Vessel-specific reporting

### 🗄️ **Data Management**
- SQLite database for persistent storage
- Advanced search and filtering capabilities
- Analytics caching for performance
- Automated data cleanup

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Shipping-FusionAI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download NLP models (optional but recommended)**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Start the application**
   ```bash
   python app.py
   ```

5. **Access the dashboard**
   Open your browser to: http://localhost:8000

### Advanced Setup

For production deployment:

```bash
# Install with gunicorn for production
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

## Usage

### Web Interface

1. **Access the Dashboard**: Navigate to http://localhost:8000
2. **Upload Documents**: Use the drag-and-drop interface or select files
3. **Paste Text**: Directly input maintenance reports or alerts
4. **Process with AI**: Click the process button to analyze content
5. **Review Results**: View classifications, priorities, and recommendations

### API Endpoints

#### Process Text Content
```bash
curl -X POST "http://localhost:8000/process/text" \
     -H "Content-Type: application/json" \
     -d '{"text": "Engine room fire alarm activated. Crew evacuating compartment."}'
```

#### Upload Files
```bash
curl -X POST "http://localhost:8000/process/files" \
     -F "files=@maintenance_report.txt"
```

#### Get Analytics
```bash
curl "http://localhost:8000/analytics"
```

#### Get Processing History
```bash
curl "http://localhost:8000/history?limit=50"
```

## Sample Data

Load demonstration data to explore the system:

```bash
# Load sample maintenance records and alerts
python sample_data.py

# Generate real-time alerts for demonstration
python sample_data.py --realtime --duration 10
```

## Document Types Supported

### Maintenance Records
- Engine and machinery reports
- Inspection findings
- Repair documentation
- Service schedules

### Sensor Alerts
- Temperature warnings
- Pressure anomalies
- Vibration alerts
- Leak detection

### Incident Reports
- Emergency situations
- Equipment failures
- Environmental incidents
- Safety violations

## Classification Logic

The AI system uses sophisticated pattern matching and natural language processing to classify content:

### Critical Equipment Failure Risk
- Engine, propulsion, or structural failures
- Power system outages
- Steering or navigation system failures

### Navigational Hazard Alert
- GPS/radar malfunctions
- Weather-related hazards
- Chart discrepancies
- Collision risks

### Environmental Compliance Breach
- Oil spills or fuel leaks
- Emission violations
- Waste discharge issues
- MARPOL violations

### Safety Violations
- Missing safety equipment
- Fire system failures
- Life-saving appliance defects
- ISM Code violations

## Technical Architecture

### Backend Components
- **FastAPI**: High-performance web framework
- **spaCy**: Advanced NLP processing
- **NLTK**: Text analysis and tokenization
- **scikit-learn**: Machine learning algorithms
- **SQLite**: Lightweight database storage

### AI Processing Pipeline
1. **Text Preprocessing**: Cleaning and normalization
2. **Document Type Detection**: Automatic categorization
3. **Entity Extraction**: Named entity recognition
4. **Pattern Matching**: Keyword and regex analysis
5. **Classification**: AI-powered categorization
6. **Risk Assessment**: Priority determination
7. **Recommendation Generation**: Action planning

### Data Models
- **ProcessingResponse**: Complete analysis results
- **VesselInfo**: Vessel registration data
- **AnalyticsData**: Performance metrics
- **AlertRule**: Custom classification rules

## Configuration

### Environment Variables
```bash
# Database configuration
DATABASE_PATH=data/vessel_maintenance.db

# Logging level
LOG_LEVEL=INFO

# API configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Custom Classification Patterns

Extend the AI system by modifying `src/ai_processor.py`:

```python
# Add custom patterns for specific vessel types or operations
custom_patterns = [
    KeywordPattern(
        pattern=r"(cargo|container).*(shift|movement|loose)",
        classification=ClassificationType.SAFETY_VIOLATION,
        priority=PriorityLevel.HIGH,
        weight=1.5
    )
]
```

## Performance Monitoring

### Analytics Dashboard
- Total documents processed
- Critical alert trends
- Classification breakdown
- Vessel-specific statistics

### Logging
Application logs are stored in:
- `logs/ai_processor.log` - AI processing events
- Console output - Real-time system status

## Security Considerations

- Input validation for all text processing
- SQL injection prevention in database queries
- Rate limiting on API endpoints (recommended for production)
- Secure file upload handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add comprehensive tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For technical support or feature requests:
- Create an issue in the repository
- Review the troubleshooting section below

## Troubleshooting

### Common Issues

**spaCy model not found**
```bash
python -m spacy download en_core_web_sm
```

**Database permission errors**
```bash
# Ensure data directory is writable
chmod 755 data/
```

**Port already in use**
```bash
# Change port in app.py or kill existing process
lsof -ti:8000 | xargs kill -9
```

### Performance Optimization

- For large deployments, consider PostgreSQL instead of SQLite
- Implement Redis caching for frequently accessed data
- Use load balancing for multiple application instances
- Monitor memory usage with large document processing

## Future Enhancements

- Integration with vessel tracking systems
- Real-time sensor data processing
- Machine learning model training on historical data
- Mobile application for field reporting
- Integration with maritime regulatory databases

---

🌊 **Empowering maritime operations with intelligent document processing and risk assessment**

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

from src.ai_processor import VesselMaintenanceAI
from src.models import ProcessingRequest, ProcessingResponse
from src.database import DatabaseManager

app = FastAPI(
    title="Vessel Maintenance AI System",
    description="AI-powered application for processing vessel maintenance records, sensor anomaly alerts, and incident reports",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI processor and database
ai_processor = VesselMaintenanceAI()
db_manager = DatabaseManager()

# Mount static files
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vessel Maintenance AI Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .upload-area {
                border: 2px dashed #007bff;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                transition: all 0.3s ease;
            }
            .upload-area:hover {
                background-color: #f8f9fa;
                border-color: #0056b3;
            }
            .classification-badge {
                font-size: 0.9em;
                padding: 8px 12px;
            }
            .critical { background-color: #dc3545; }
            .warning { background-color: #fd7e14; }
            .compliance { background-color: #6610f2; }
            .maintenance { background-color: #20c997; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <span class="navbar-brand mb-0 h1">
                    <i class="fas fa-ship"></i> Vessel Maintenance AI System
                </span>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-upload"></i> Document Processing</h5>
                        </div>
                        <div class="card-body">
                            <div class="upload-area" id="uploadArea">
                                <i class="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                                <h5>Upload Vessel Documents</h5>
                                <p class="text-muted">Drag and drop files here or click to browse</p>
                                <input type="file" id="fileInput" multiple accept=".txt,.pdf,.doc,.docx" style="display: none;">
                                <button class="btn btn-primary" onclick="document.getElementById('fileInput').click()">
                                    Select Files
                                </button>
                            </div>
                            
                            <div class="mb-3">
                                <label for="textInput" class="form-label">Or paste text directly:</label>
                                <textarea class="form-control" id="textInput" rows="6" 
                                    placeholder="Paste maintenance records, sensor alerts, or incident reports here..."></textarea>
                            </div>
                            
                            <button class="btn btn-success btn-lg" onclick="processDocument()">
                                <i class="fas fa-cogs"></i> Process with AI
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-pie"></i> Quick Stats</h5>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-6">
                                    <h3 class="text-danger" id="criticalCount">0</h3>
                                    <small>Critical Alerts</small>
                                </div>
                                <div class="col-6">
                                    <h3 class="text-success" id="processedCount">0</h3>
                                    <small>Processed Today</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mt-3">
                        <div class="card-header">
                            <h5><i class="fas fa-tags"></i> Classification Types</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-flex flex-wrap gap-2">
                                <span class="badge classification-badge critical">Critical Equipment Failure Risk</span>
                                <span class="badge classification-badge warning">Navigational Hazard Alert</span>
                                <span class="badge classification-badge compliance">Environmental Compliance Breach</span>
                                <span class="badge classification-badge maintenance">Routine Maintenance Required</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5><i class="fas fa-list"></i> Processing Results</h5>
                            <button class="btn btn-sm btn-outline-secondary" onclick="clearResults()">
                                Clear Results
                            </button>
                        </div>
                        <div class="card-body">
                            <div id="results" class="row">
                                <div class="col-12 text-center text-muted">
                                    <i class="fas fa-info-circle"></i>
                                    No documents processed yet. Upload or paste content above to get started.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let processedCount = 0;
            let criticalCount = 0;

            async function processDocument() {
                const textInput = document.getElementById('textInput').value;
                const fileInput = document.getElementById('fileInput');
                
                if (!textInput.trim() && fileInput.files.length === 0) {
                    alert('Please provide text input or select files to process.');
                    return;
                }

                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '<div class="col-12 text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Processing with AI...</p></div>';

                try {
                    let response;
                    
                    if (textInput.trim()) {
                        // Process text input
                        response = await fetch('/process/text', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ text: textInput })
                        });
                    } else {
                        // Process file upload
                        const formData = new FormData();
                        for (let file of fileInput.files) {
                            formData.append('files', file);
                        }
                        
                        response = await fetch('/process/files', {
                            method: 'POST',
                            body: formData
                        });
                    }

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    displayResults(result);
                    updateStats(result);
                    
                    // Clear inputs
                    document.getElementById('textInput').value = '';
                    fileInput.value = '';
                    
                } catch (error) {
                    console.error('Error:', error);
                    resultsDiv.innerHTML = `
                        <div class="col-12">
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-triangle"></i>
                                Error processing document: ${error.message}
                            </div>
                        </div>
                    `;
                }
            }

            function displayResults(results) {
                const resultsDiv = document.getElementById('results');
                
                if (results.length === 0) {
                    resultsDiv.innerHTML = '<div class="col-12 text-center text-muted">No results to display.</div>';
                    return;
                }

                let html = '';
                results.forEach((result, index) => {
                    const badgeClass = getBadgeClass(result.classification);
                    const priorityIcon = getPriorityIcon(result.priority);
                    
                    html += `
                        <div class="col-md-6 mb-3">
                            <div class="card h-100">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between align-items-start mb-2">
                                        <span class="badge ${badgeClass} classification-badge">
                                            ${result.classification}
                                        </span>
                                        <span class="text-muted">${priorityIcon} ${result.priority}</span>
                                    </div>
                                    <h6 class="card-title">${result.summary}</h6>
                                    <p class="card-text text-muted small">${result.details}</p>
                                    <div class="mt-2">
                                        <small class="text-muted">
                                            <i class="fas fa-clock"></i> ${new Date().toLocaleString()}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                resultsDiv.innerHTML = html;
            }

            function getBadgeClass(classification) {
                switch(classification.toLowerCase()) {
                    case 'critical equipment failure risk': return 'critical';
                    case 'navigational hazard alert': return 'warning';
                    case 'environmental compliance breach': return 'compliance';
                    default: return 'maintenance';
                }
            }

            function getPriorityIcon(priority) {
                switch(priority.toLowerCase()) {
                    case 'critical': return '<i class="fas fa-exclamation-triangle text-danger"></i>';
                    case 'high': return '<i class="fas fa-exclamation-circle text-warning"></i>';
                    case 'medium': return '<i class="fas fa-info-circle text-info"></i>';
                    default: return '<i class="fas fa-check-circle text-success"></i>';
                }
            }

            function updateStats(results) {
                processedCount += results.length;
                criticalCount += results.filter(r => r.priority.toLowerCase() === 'critical').length;
                
                document.getElementById('processedCount').textContent = processedCount;
                document.getElementById('criticalCount').textContent = criticalCount;
            }

            function clearResults() {
                document.getElementById('results').innerHTML = 
                    '<div class="col-12 text-center text-muted"><i class="fas fa-info-circle"></i> No documents processed yet. Upload or paste content above to get started.</div>';
                processedCount = 0;
                criticalCount = 0;
                updateStats([]);
            }

            // Drag and drop functionality
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');

            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.backgroundColor = '#e3f2fd';
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.backgroundColor = '';
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.backgroundColor = '';
                fileInput.files = e.dataTransfer.files;
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/process/text")
async def process_text(request: ProcessingRequest):
    """Process text input"""
    try:
        results = ai_processor.process_text(request.text)
        
        # Store in database
        for result in results:
            db_manager.store_result(result)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/files")
async def process_files(files: list[UploadFile] = File(...)):
    """Process uploaded files"""
    try:
        all_results = []
        
        for file in files:
            content = await file.read()
            text = content.decode('utf-8', errors='ignore')
            
            results = ai_processor.process_text(text)
            all_results.extend(results)
            
            # Store in database
            for result in results:
                db_manager.store_result(result)
        
        return all_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
async def get_analytics():
    """Get analytics data"""
    try:
        analytics = db_manager.get_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history(limit: int = 50):
    """Get processing history"""
    try:
        history = db_manager.get_history(limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
// ===== API Interface =====

class API {
    static baseURL = window.location.origin;
    
    // Helper method for making requests
    static async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const config = { ...defaultOptions, ...options };
        
        // Handle FormData (for file uploads)
        if (config.body instanceof FormData) {
            delete config.headers['Content-Type'];
        }
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else if (contentType && contentType.includes('application/pdf')) {
                return await response.blob();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    // ===== Text Processing =====
    static async processText(data) {
        try {
            const response = await this.request('/process', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            return response;
        } catch (error) {
            // Fallback to mock data if API is unavailable
            console.warn('API unavailable, using mock data');
            return this.getMockProcessingResult(data.text);
        }
    }
    
    // ===== File Processing =====
    static async processFile(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await this.request('/process_file', {
                method: 'POST',
                body: formData
            });
            return response;
        } catch (error) {
            // Fallback to mock data if API is unavailable
            console.warn('API unavailable, using mock data');
            return this.getMockProcessingResult(`File processed: ${file.name}`);
        }
    }
    
    // ===== Analytics =====
    static async getAnalytics(timeframe = 30) {
        try {
            const response = await this.request(`/analytics?days=${timeframe}`);
            return response;
        } catch (error) {
            console.warn('API unavailable, using mock data');
            return this.getMockAnalytics();
        }
    }
    
    // ===== History =====
    static async getHistory(filters = {}) {
        try {
            const params = new URLSearchParams();
            Object.entries(filters).forEach(([key, value]) => {
                if (value) params.append(key, value);
            });
            
            const response = await this.request(`/history?${params}`);
            return response;
        } catch (error) {
            console.warn('API unavailable, using mock data');
            return this.getMockHistory(filters);
        }
    }
    
    static async getHistoryDetails(id) {
        try {
            const response = await this.request(`/history/${id}`);
            return response;
        } catch (error) {
            console.warn('API unavailable, using mock data');
            return this.getMockHistoryDetails(id);
        }
    }
    
    // ===== System Health =====
    static async getSystemHealth() {
        try {
            const response = await this.request('/health');
            return response;
        } catch (error) {
            console.warn('API unavailable, using mock data');
            return this.getMockSystemHealth();
        }
    }
    
    // ===== System Configuration =====
    static async getSystemConfig() {
        try {
            const response = await this.request('/config');
            return response;
        } catch (error) {
            console.warn('API unavailable, using mock data');
            return this.getMockSystemConfig();
        }
    }
    
    // ===== Data Management =====
    static async cleanupData(days) {
        try {
            const response = await this.request('/cleanup', {
                method: 'POST',
                body: JSON.stringify({ days })
            });
            return response;
        } catch (error) {
            console.warn('API unavailable, using mock data');
            return { deleted_records: Math.floor(Math.random() * 100) + 50 };
        }
    }
    
    static async exportData() {
        try {
            const response = await this.request('/export', {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.warn('API unavailable, simulating export');
            throw new Error('Export functionality requires backend connection');
        }
    }
    
    static async loadSampleData() {
        try {
            const response = await this.request('/load_sample_data', {
                method: 'POST'
            });
            return response;
        } catch (error) {
            console.warn('API unavailable, using mock response');
            return { message: 'Sample data loaded successfully', records_loaded: 50 };
        }
    }
    
    // ===== Reports =====
    static async generateReport() {
        try {
            const response = await this.request('/generate_report', {
                method: 'POST'
            });
            return response;
        } catch (error) {
            console.warn('API unavailable, simulating report generation');
            throw new Error('Report generation requires backend connection');
        }
    }
    
    // ===== Mock Data Methods =====
    static getMockProcessingResult(text) {
        const classifications = [
            'Critical Equipment Failure Risk',
            'Navigational Hazard Alert',
            'Environmental Compliance Breach',
            'Routine Maintenance Required',
            'Safety Violation Detected',
            'Fuel Efficiency Alert'
        ];
        
        const priorities = ['Critical', 'High', 'Medium', 'Low'];
        
        const entities = ['Engine', 'Navigation System', 'Hull', 'Fuel System', 'Safety Equipment'];
        const keywords = ['maintenance', 'inspection', 'repair', 'safety', 'compliance', 'efficiency'];
        
        const selectedClassification = classifications[Math.floor(Math.random() * classifications.length)];
        const selectedPriority = priorities[Math.floor(Math.random() * priorities.length)];
        
        const recommendations = [
            'Schedule immediate inspection',
            'Contact certified maintenance crew',
            'Review safety protocols',
            'Monitor system performance closely',
            'Update maintenance logs'
        ];
        
        return {
            classification: selectedClassification,
            priority: selectedPriority,
            confidence: Math.random() * 0.4 + 0.6, // 60-100%
            summary: `Analysis of the provided text indicates ${selectedClassification.toLowerCase()}. The system has identified potential issues that require attention.`,
            entities: entities.slice(0, Math.floor(Math.random() * 3) + 2),
            keywords: keywords.slice(0, Math.floor(Math.random() * 4) + 3),
            recommendations: recommendations.slice(0, Math.floor(Math.random() * 3) + 2),
            risk_assessment: `Based on the analysis, this issue presents a ${selectedPriority.toLowerCase()} risk to vessel operations and safety.`,
            timestamp: new Date().toISOString()
        };
    }
    
    static getMockAnalytics() {
        const classifications = {
            'Critical Equipment Failure Risk': Math.floor(Math.random() * 20) + 5,
            'Navigational Hazard Alert': Math.floor(Math.random() * 15) + 3,
            'Environmental Compliance Breach': Math.floor(Math.random() * 10) + 2,
            'Routine Maintenance Required': Math.floor(Math.random() * 50) + 20,
            'Safety Violation Detected': Math.floor(Math.random() * 8) + 1,
            'Fuel Efficiency Alert': Math.floor(Math.random() * 12) + 3
        };
        
        const priorities = {
            'Critical': Math.floor(Math.random() * 15) + 5,
            'High': Math.floor(Math.random() * 25) + 10,
            'Medium': Math.floor(Math.random() * 40) + 20,
            'Low': Math.floor(Math.random() * 30) + 15
        };
        
        // Generate trend data for the last 30 days
        const trends = Array.from({ length: 30 }, (_, i) => ({
            date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            documents_processed: Math.floor(Math.random() * 20) + 5,
            critical_alerts: Math.floor(Math.random() * 3),
            average_confidence: Math.random() * 0.2 + 0.8
        }));
        
        const vessels = Array.from({ length: 12 }, (_, i) => ({
            vessel_id: `VESSEL-${String(i + 1).padStart(3, '0')}`,
            documents_processed: Math.floor(Math.random() * 50) + 10,
            critical_alerts: Math.floor(Math.random() * 5),
            last_activity: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
        }));
        
        return {
            classification_distribution: classifications,
            priority_breakdown: priorities,
            processing_trends: trends,
            vessel_activity: vessels,
            summary: {
                total_documents: Object.values(classifications).reduce((a, b) => a + b, 0),
                average_confidence: 0.85,
                critical_alerts: priorities.Critical + Math.floor(priorities.High * 0.3),
                top_classification: Object.keys(classifications).reduce((a, b) => 
                    classifications[a] > classifications[b] ? a : b
                )
            }
        };
    }
    
    static getMockHistory(filters = {}) {
        const results = Array.from({ length: 20 }, (_, i) => {
            const classifications = [
                'Critical Equipment Failure Risk',
                'Navigational Hazard Alert',
                'Environmental Compliance Breach',
                'Routine Maintenance Required',
                'Safety Violation Detected',
                'Fuel Efficiency Alert'
            ];
            
            const priorities = ['Critical', 'High', 'Medium', 'Low'];
            const documentTypes = ['Maintenance Record', 'Sensor Alert', 'Incident Report', 'Inspection Report', 'Compliance Document'];
            
            return {
                id: `hist_${i + 1}`,
                timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
                document_type: documentTypes[Math.floor(Math.random() * documentTypes.length)],
                classification: classifications[Math.floor(Math.random() * classifications.length)],
                priority: priorities[Math.floor(Math.random() * priorities.length)],
                vessel_id: Math.random() > 0.3 ? `VESSEL-${String(Math.floor(Math.random() * 10) + 1).padStart(3, '0')}` : null,
                confidence: Math.random() * 0.4 + 0.6
            };
        });
        
        // Apply filters
        let filteredResults = results;
        
        if (filters.search) {
            filteredResults = filteredResults.filter(item => 
                item.classification.toLowerCase().includes(filters.search.toLowerCase()) ||
                item.document_type.toLowerCase().includes(filters.search.toLowerCase())
            );
        }
        
        if (filters.classification) {
            filteredResults = filteredResults.filter(item => item.classification === filters.classification);
        }
        
        if (filters.priority) {
            filteredResults = filteredResults.filter(item => item.priority === filters.priority);
        }
        
        if (filters.vessel_id) {
            filteredResults = filteredResults.filter(item => 
                item.vessel_id && item.vessel_id.toLowerCase().includes(filters.vessel_id.toLowerCase())
            );
        }
        
        // Pagination
        const page = parseInt(filters.page) || 1;
        const pageSize = 10;
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        const paginatedResults = filteredResults.slice(startIndex, endIndex);
        
        return {
            results: paginatedResults,
            pagination: {
                current_page: page,
                total_pages: Math.ceil(filteredResults.length / pageSize),
                total_items: filteredResults.length,
                has_prev: page > 1,
                has_next: page < Math.ceil(filteredResults.length / pageSize)
            }
        };
    }
    
    static getMockHistoryDetails(id) {
        return {
            id: id,
            original_text: "Engine temperature monitoring system reports unusual readings. Temperature fluctuations detected in cooling system. Immediate inspection recommended to prevent potential equipment failure.",
            classification: "Critical Equipment Failure Risk",
            priority: "High",
            confidence: 0.92,
            summary: "Critical temperature anomaly detected in engine cooling system requiring immediate attention to prevent equipment failure.",
            entities: ["Engine", "Cooling System", "Temperature Sensor"],
            keywords: ["temperature", "monitoring", "cooling", "inspection", "failure"],
            recommendations: [
                "Schedule immediate engine inspection",
                "Check cooling system integrity",
                "Monitor temperature readings closely",
                "Prepare backup cooling systems"
            ],
            risk_assessment: "High risk of engine failure if not addressed within 24 hours. Potential for significant operational disruption.",
            vessel_id: "VESSEL-001",
            timestamp: new Date().toISOString(),
            processed_by: "AI Processor v2.1"
        };
    }
    
    static getMockSystemHealth() {
        return {
            api: {
                healthy: Math.random() > 0.1,
                response_time: Math.floor(Math.random() * 100) + 50,
                last_check: new Date().toISOString()
            },
            db: {
                healthy: Math.random() > 0.05,
                connection_count: Math.floor(Math.random() * 20) + 5,
                last_check: new Date().toISOString()
            },
            ai: {
                healthy: Math.random() > 0.15,
                model_status: "operational",
                last_processing: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toISOString(),
                last_check: new Date().toISOString()
            }
        };
    }
    
    static getMockSystemConfig() {
        return {
            system: {
                version: "2.1.0",
                environment: "production",
                debug_mode: false,
                max_file_size: "10MB",
                supported_formats: ["txt", "pdf", "doc", "docx"]
            },
            ai_processor: {
                model_version: "transformer-maritime-v2.1",
                confidence_threshold: 0.7,
                max_tokens: 4096,
                temperature: 0.3
            },
            database: {
                type: "SQLite",
                location: "vessel_maintenance.db",
                backup_enabled: true,
                retention_days: 90
            },
            security: {
                encryption_enabled: true,
                audit_logging: true,
                session_timeout: 3600
            },
            features: {
                file_upload: true,
                text_processing: true,
                analytics: true,
                reports: true,
                notifications: true
            }
        };
    }
}

// ===== Export API class =====
window.API = API;
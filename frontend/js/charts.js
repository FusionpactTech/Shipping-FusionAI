// ===== Charts and Data Visualization =====

class Charts {
    static charts = {};
    
    static init() {
        // Set default Chart.js configuration
        Chart.defaults.font.family = 'Inter, sans-serif';
        Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim();
        Chart.defaults.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim();
    }
    
    static getColors() {
        const root = getComputedStyle(document.documentElement);
        return {
            primary: root.getPropertyValue('--primary-color').trim(),
            secondary: root.getPropertyValue('--secondary-color').trim(),
            critical: root.getPropertyValue('--critical-color').trim(),
            high: root.getPropertyValue('--high-color').trim(),
            medium: root.getPropertyValue('--medium-color').trim(),
            low: root.getPropertyValue('--low-color').trim(),
            gray: root.getPropertyValue('--gray-400').trim()
        };
    }
    
    static createClassificationChart(data) {
        const ctx = document.getElementById('classificationChart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.charts.classification) {
            this.charts.classification.destroy();
        }
        
        const colors = this.getColors();
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        // Generate colors for each classification
        const backgroundColors = labels.map((_, index) => {
            const colorKeys = ['primary', 'secondary', 'critical', 'high', 'medium', 'low'];
            return colors[colorKeys[index % colorKeys.length]];
        });
        
        this.charts.classification = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: backgroundColors,
                    borderWidth: 2,
                    borderColor: getComputedStyle(document.documentElement).getPropertyValue('--bg-primary').trim()
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    static createPriorityChart(data) {
        const ctx = document.getElementById('priorityChart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.charts.priority) {
            this.charts.priority.destroy();
        }
        
        const colors = this.getColors();
        const priorityColors = {
            'Critical': colors.critical,
            'High': colors.high,
            'Medium': colors.medium,
            'Low': colors.low
        };
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        const backgroundColors = labels.map(label => priorityColors[label] || colors.gray);
        
        this.charts.priority = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Documents',
                    data: values,
                    backgroundColor: backgroundColors,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim()
                        },
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
    
    static createTrendsChart(data) {
        const ctx = document.getElementById('trendsChart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.charts.trends) {
            this.charts.trends.destroy();
        }
        
        const colors = this.getColors();
        
        // Prepare data
        const labels = data.map(item => {
            const date = new Date(item.date);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });
        
        const documentsData = data.map(item => item.documents_processed);
        const alertsData = data.map(item => item.critical_alerts);
        const confidenceData = data.map(item => item.average_confidence * 100);
        
        this.charts.trends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Documents Processed',
                        data: documentsData,
                        borderColor: colors.primary,
                        backgroundColor: colors.primary + '20',
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Critical Alerts',
                        data: alertsData,
                        borderColor: colors.critical,
                        backgroundColor: colors.critical + '20',
                        tension: 0.4,
                        fill: false,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Avg Confidence (%)',
                        data: confidenceData,
                        borderColor: colors.secondary,
                        backgroundColor: colors.secondary + '20',
                        tension: 0.4,
                        fill: false,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `Date: ${context[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        grid: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim()
                        },
                        title: {
                            display: true,
                            text: 'Count'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        min: 70,
                        max: 100,
                        grid: {
                            drawOnChartArea: false,
                        },
                        title: {
                            display: true,
                            text: 'Confidence (%)'
                        }
                    }
                }
            }
        });
    }
    
    static createVesselChart(data) {
        const ctx = document.getElementById('vesselChart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.charts.vessel) {
            this.charts.vessel.destroy();
        }
        
        const colors = this.getColors();
        
        // Take top 10 vessels by document count
        const sortedData = data.sort((a, b) => b.documents_processed - a.documents_processed).slice(0, 10);
        
        const labels = sortedData.map(item => item.vessel_id);
        const documentsData = sortedData.map(item => item.documents_processed);
        const alertsData = sortedData.map(item => item.critical_alerts);
        
        this.charts.vessel = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Documents Processed',
                        data: documentsData,
                        backgroundColor: colors.primary,
                        borderRadius: 4,
                        borderSkipped: false
                    },
                    {
                        label: 'Critical Alerts',
                        data: alertsData,
                        backgroundColor: colors.critical,
                        borderRadius: 4,
                        borderSkipped: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `Vessel: ${context[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 45
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim()
                        },
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
    
    static updateCharts(analyticsData) {
        if (analyticsData.classification_distribution) {
            this.createClassificationChart(analyticsData.classification_distribution);
        }
        
        if (analyticsData.priority_breakdown) {
            this.createPriorityChart(analyticsData.priority_breakdown);
        }
        
        if (analyticsData.processing_trends) {
            this.createTrendsChart(analyticsData.processing_trends);
        }
        
        if (analyticsData.vessel_activity) {
            this.createVesselChart(analyticsData.vessel_activity);
        }
    }
    
    static generateInsights(analyticsData) {
        const insights = [];
        const colors = this.getColors();
        
        if (analyticsData.summary) {
            const summary = analyticsData.summary;
            
            // Total documents insight
            insights.push({
                icon: 'fas fa-file-alt',
                color: colors.primary,
                title: 'Document Processing',
                description: `Processed ${summary.total_documents} documents with ${(summary.average_confidence * 100).toFixed(1)}% average confidence.`
            });
            
            // Critical alerts insight
            if (summary.critical_alerts > 0) {
                insights.push({
                    icon: 'fas fa-exclamation-triangle',
                    color: colors.critical,
                    title: 'Critical Alerts',
                    description: `${summary.critical_alerts} critical alerts require immediate attention.`
                });
            }
            
            // Top classification insight
            insights.push({
                icon: 'fas fa-chart-pie',
                color: colors.secondary,
                title: 'Top Issue Type',
                description: `Most common issue: ${summary.top_classification.replace(/([A-Z])/g, ' $1').trim()}.`
            });
        }
        
        // Trend analysis
        if (analyticsData.processing_trends && analyticsData.processing_trends.length > 0) {
            const trends = analyticsData.processing_trends;
            const recent = trends.slice(-7); // Last 7 days
            const avgRecent = recent.reduce((sum, item) => sum + item.documents_processed, 0) / recent.length;
            const older = trends.slice(-14, -7); // Previous 7 days
            const avgOlder = older.reduce((sum, item) => sum + item.documents_processed, 0) / older.length;
            
            const change = ((avgRecent - avgOlder) / avgOlder * 100).toFixed(1);
            
            if (Math.abs(change) > 5) {
                insights.push({
                    icon: change > 0 ? 'fas fa-trending-up' : 'fas fa-trending-down',
                    color: change > 0 ? colors.low : colors.high,
                    title: 'Processing Trend',
                    description: `Document processing ${change > 0 ? 'increased' : 'decreased'} by ${Math.abs(change)}% this week.`
                });
            }
        }
        
        // Confidence analysis
        if (analyticsData.processing_trends) {
            const confidenceData = analyticsData.processing_trends.map(item => item.average_confidence);
            const avgConfidence = confidenceData.reduce((a, b) => a + b, 0) / confidenceData.length;
            
            if (avgConfidence < 0.8) {
                insights.push({
                    icon: 'fas fa-exclamation-circle',
                    color: colors.medium,
                    title: 'Confidence Level',
                    description: `Average confidence is ${(avgConfidence * 100).toFixed(1)}%. Consider reviewing classification models.`
                });
            } else if (avgConfidence > 0.9) {
                insights.push({
                    icon: 'fas fa-check-circle',
                    color: colors.low,
                    title: 'High Confidence',
                    description: `Excellent average confidence of ${(avgConfidence * 100).toFixed(1)}%. System is performing well.`
                });
            }
        }
        
        return insights;
    }
    
    static displayInsights(insights) {
        const container = document.getElementById('analyticsInsights');
        if (!container) return;
        
        container.innerHTML = insights.map(insight => `
            <div class="insight-item animate-fade-in">
                <div class="insight-header">
                    <i class="${insight.icon}" style="color: ${insight.color}"></i>
                    <h4>${insight.title}</h4>
                </div>
                <p>${insight.description}</p>
            </div>
        `).join('');
    }
    
    static destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
    
    static resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }
}

// ===== Analytics Functions =====
async function loadAnalytics() {
    const timeFilter = document.getElementById('timeFilter');
    const timeframe = timeFilter ? timeFilter.value : 30;
    
    showAnalyticsLoading();
    
    try {
        const analyticsData = await API.getAnalytics(timeframe);
        
        // Update charts
        Charts.updateCharts(analyticsData);
        
        // Generate and display insights
        const insights = Charts.generateInsights(analyticsData);
        Charts.displayInsights(insights);
        
        hideAnalyticsLoading();
    } catch (error) {
        console.error('Analytics loading error:', error);
        VesselApp.showNotification('Error loading analytics data.', 'error');
        hideAnalyticsLoading();
    }
}

function showAnalyticsLoading() {
    const chartContainers = document.querySelectorAll('.chart-container canvas');
    chartContainers.forEach(canvas => {
        const container = canvas.parentElement;
        if (!container.querySelector('.loading-skeleton')) {
            const skeleton = document.createElement('div');
            skeleton.className = 'loading-skeleton';
            skeleton.style.height = '300px';
            skeleton.style.borderRadius = '8px';
            container.appendChild(skeleton);
        }
    });
}

function hideAnalyticsLoading() {
    const skeletons = document.querySelectorAll('.chart-container .loading-skeleton');
    skeletons.forEach(skeleton => skeleton.remove());
}

// Setup analytics refresh
function setupAnalyticsRefresh() {
    const refreshBtn = document.getElementById('refreshAnalytics');
    const timeFilter = document.getElementById('timeFilter');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadAnalytics);
    }
    
    if (timeFilter) {
        timeFilter.addEventListener('change', loadAnalytics);
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Charts.init();
    setupAnalyticsRefresh();
});

// Handle window resize
window.addEventListener('resize', () => {
    Charts.resizeCharts();
});

// Handle theme changes
document.addEventListener('themeChanged', () => {
    Charts.destroyAllCharts();
    setTimeout(() => {
        if (VesselApp.AppState.currentSection === 'analytics') {
            loadAnalytics();
        }
    }, 100);
});

// Export for global access
window.Charts = Charts;
window.loadAnalytics = loadAnalytics;
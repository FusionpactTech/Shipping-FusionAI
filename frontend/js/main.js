// ===== Main Application JavaScript =====

// Application State
const AppState = {
    currentSection: 'dashboard',
    theme: 'light',
    notifications: [],
    isLoading: false,
    charts: {}
};

// DOM Elements
const elements = {
    navLinks: document.querySelectorAll('.nav-link'),
    sections: document.querySelectorAll('.section'),
    themeToggle: document.getElementById('themeToggle'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    notificationToast: document.getElementById('notificationToast'),
    toastMessage: document.getElementById('toastMessage'),
    toastClose: document.getElementById('toastClose'),
    modal: document.getElementById('resultModal'),
    modalBody: document.getElementById('modalBody'),
    modalClose: document.querySelector('.modal-close')
};

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    loadDashboardData();
    checkSystemHealth();
});

function initializeApp() {
    // Initialize theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // Initialize navigation
    const savedSection = localStorage.getItem('currentSection') || 'dashboard';
    navigateToSection(savedSection);
    
    // Initialize mobile menu
    setupMobileMenu();
    
    // Load user preferences
    loadUserPreferences();
    
    console.log('Vessel Maintenance AI System initialized');
}

// ===== Navigation =====
function setupEventListeners() {
    // Navigation links
    elements.navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            navigateToSection(section);
        });
    });

    // Theme toggle
    elements.themeToggle?.addEventListener('click', toggleTheme);

    // Modal close
    elements.modalClose?.addEventListener('click', closeModal);
    elements.modal?.addEventListener('click', (e) => {
        if (e.target === elements.modal) closeModal();
    });

    // Toast close
    elements.toastClose?.addEventListener('click', hideNotification);

    // Form submissions
    setupFormHandlers();

    // Action buttons
    setupActionButtons();

    // File upload
    setupFileUpload();

    // Settings
    setupSettings();

    // Keyboard shortcuts
    setupKeyboardShortcuts();
}

function navigateToSection(sectionName) {
    // Update navigation state
    elements.navLinks.forEach(link => {
        link.classList.toggle('active', link.dataset.section === sectionName);
    });

    // Update sections
    elements.sections.forEach(section => {
        section.classList.toggle('active', section.id === sectionName);
    });

    // Update app state
    AppState.currentSection = sectionName;
    localStorage.setItem('currentSection', sectionName);

    // Load section-specific data
    loadSectionData(sectionName);

    // Update URL without reload
    window.history.pushState({section: sectionName}, '', `#${sectionName}`);
}

function loadSectionData(sectionName) {
    switch (sectionName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'history':
            loadHistory();
            break;
        case 'settings':
            loadSettings();
            break;
    }
}

// ===== Theme Management =====
function toggleTheme() {
    const newTheme = AppState.theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

function setTheme(theme) {
    AppState.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update theme toggle icon
    const themeIcon = elements.themeToggle?.querySelector('i');
    if (themeIcon) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// ===== Mobile Menu =====
function setupMobileMenu() {
    // Create mobile menu toggle if it doesn't exist
    let mobileToggle = document.querySelector('.mobile-menu-toggle');
    if (!mobileToggle) {
        mobileToggle = document.createElement('button');
        mobileToggle.className = 'mobile-menu-toggle desktop-only';
        mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
        
        const navContainer = document.querySelector('.nav-container');
        navContainer.insertBefore(mobileToggle, navContainer.firstChild);
    }

    mobileToggle.addEventListener('click', () => {
        const navMenu = document.querySelector('.nav-menu');
        navMenu.classList.toggle('active');
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        const navMenu = document.querySelector('.nav-menu');
        const mobileToggle = document.querySelector('.mobile-menu-toggle');
        
        if (!navMenu.contains(e.target) && !mobileToggle.contains(e.target)) {
            navMenu.classList.remove('active');
        }
    });
}

// ===== Dashboard Functions =====
function loadDashboardData() {
    updateDashboardStats();
    loadRecentActivity();
}

function updateDashboardStats() {
    // Simulate API call
    showLoading();
    
    setTimeout(() => {
        const stats = {
            criticalAlerts: Math.floor(Math.random() * 5),
            totalProcessed: Math.floor(Math.random() * 1000) + 500,
            activeVessels: Math.floor(Math.random() * 50) + 10,
            efficiency: (Math.random() * 5 + 95).toFixed(1) + '%'
        };

        // Update DOM
        document.getElementById('criticalAlerts').textContent = stats.criticalAlerts;
        document.getElementById('totalProcessed').textContent = stats.totalProcessed;
        document.getElementById('activeVessels').textContent = stats.activeVessels;
        document.getElementById('efficiency').textContent = stats.efficiency;

        // Update notification badge
        document.getElementById('notificationCount').textContent = stats.criticalAlerts;

        hideLoading();
    }, 1000);
}

function loadRecentActivity() {
    const activities = [
        {
            type: 'critical',
            icon: 'fas fa-exclamation-triangle',
            title: 'Critical Equipment Alert',
            description: 'Engine temperature exceeded threshold on VESSEL-001',
            time: '5 minutes ago',
            color: 'var(--critical-color)'
        },
        {
            type: 'processed',
            icon: 'fas fa-file-alt',
            title: 'Document Processed',
            description: 'Maintenance report analyzed with 95% confidence',
            time: '12 minutes ago',
            color: 'var(--primary-color)'
        },
        {
            type: 'maintenance',
            icon: 'fas fa-wrench',
            title: 'Routine Maintenance',
            description: 'Scheduled maintenance completed on VESSEL-003',
            time: '1 hour ago',
            color: 'var(--low-color)'
        },
        {
            type: 'inspection',
            icon: 'fas fa-search',
            title: 'Safety Inspection',
            description: 'Quarterly safety inspection report submitted',
            time: '2 hours ago',
            color: 'var(--secondary-color)'
        }
    ];

    const activityContainer = document.getElementById('recentActivity');
    activityContainer.innerHTML = activities.map(activity => `
        <div class="activity-item animate-fade-in">
            <div class="activity-icon" style="background: ${activity.color}">
                <i class="${activity.icon}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <p class="activity-description">${activity.description}</p>
            </div>
            <div class="activity-time">${activity.time}</div>
        </div>
    `).join('');
}

// ===== Form Handlers =====
function setupFormHandlers() {
    const textForm = document.getElementById('textProcessingForm');
    if (textForm) {
        textForm.addEventListener('submit', handleTextProcessing);
    }
}

async function handleTextProcessing(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        text: formData.get('text'),
        document_type: formData.get('document_type'),
        vessel_id: formData.get('vessel_id')
    };

    if (!data.text.trim()) {
        showNotification('Please enter some text to process', 'error');
        return;
    }

    showLoading();
    
    try {
        const response = await API.processText(data);
        displayProcessingResults(response);
        showNotification('Document processed successfully!', 'success');
    } catch (error) {
        console.error('Processing error:', error);
        showNotification('Error processing document. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function displayProcessingResults(results) {
    const resultsSection = document.getElementById('processingResults');
    
    // Update classification
    const classificationBadge = document.getElementById('classificationResult');
    classificationBadge.textContent = results.classification;
    classificationBadge.className = `classification-badge ${results.priority.toLowerCase()}`;

    // Update priority
    const priorityBadge = document.getElementById('priorityResult');
    priorityBadge.textContent = results.priority;
    priorityBadge.className = `priority-badge ${results.priority}`;

    // Update confidence score
    const confidenceContainer = document.getElementById('confidenceScore');
    const confidencePercentage = Math.round(results.confidence * 100);
    confidenceContainer.innerHTML = `
        <div class="confidence-meter">
            <div class="confidence-bar" style="width: ${confidencePercentage}%"></div>
            <div class="confidence-text">${confidencePercentage}%</div>
        </div>
    `;

    // Update details
    document.getElementById('summaryText').textContent = results.summary;
    
    // Update entities
    const entitiesContainer = document.getElementById('entitiesContainer');
    entitiesContainer.innerHTML = results.entities.map(entity => 
        `<span class="entity-tag">${entity}</span>`
    ).join('');

    // Update keywords
    const keywordsContainer = document.getElementById('keywordsContainer');
    keywordsContainer.innerHTML = results.keywords.map(keyword => 
        `<span class="keyword-tag">${keyword}</span>`
    ).join('');

    // Update recommendations
    const recommendationsContainer = document.getElementById('recommendationsContainer');
    recommendationsContainer.innerHTML = results.recommendations.map(rec => 
        `<li>${rec}</li>`
    ).join('');

    // Update risk assessment
    document.getElementById('riskAssessment').textContent = results.risk_assessment;

    // Show results
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// ===== File Upload =====
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');

    if (!uploadArea || !fileInput) return;

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        handleFileSelect(files);
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files);
    });

    function handleFileSelect(files) {
        Array.from(files).forEach(file => {
            if (file.size > 10 * 1024 * 1024) { // 10MB limit
                showNotification(`File ${file.name} is too large. Maximum size is 10MB.`, 'error');
                return;
            }

            addFileToList(file);
        });
    }

    function addFileToList(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item animate-fade-in';
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file file-icon"></i>
                <span class="file-name">${file.name}</span>
                <span class="file-size">(${formatFileSize(file.size)})</span>
            </div>
            <button class="file-remove" onclick="removeFile(this)">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        fileList.appendChild(fileItem);
        
        // Process file automatically
        processFile(file);
    }

    async function processFile(file) {
        showLoading();
        
        try {
            const response = await API.processFile(file);
            displayProcessingResults(response);
            showNotification(`File ${file.name} processed successfully!`, 'success');
        } catch (error) {
            console.error('File processing error:', error);
            showNotification(`Error processing ${file.name}. Please try again.`, 'error');
        } finally {
            hideLoading();
        }
    }
}

window.removeFile = function(button) {
    button.parentElement.remove();
};

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ===== Action Buttons =====
function setupActionButtons() {
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            handleQuickAction(action);
        });
    });
}

function handleQuickAction(action) {
    switch (action) {
        case 'process-document':
            navigateToSection('process');
            break;
        case 'view-analytics':
            navigateToSection('analytics');
            break;
        case 'generate-report':
            generateReport();
            break;
        case 'system-health':
            checkSystemHealth();
            break;
    }
}

async function generateReport() {
    showLoading();
    
    try {
        const response = await API.generateReport();
        
        // Create download link
        const blob = new Blob([response], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `vessel-maintenance-report-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showNotification('Report generated successfully!', 'success');
    } catch (error) {
        console.error('Report generation error:', error);
        showNotification('Error generating report. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// ===== Settings =====
function setupSettings() {
    // System health check
    const healthBtn = document.getElementById('checkHealth');
    if (healthBtn) {
        healthBtn.addEventListener('click', checkSystemHealth);
    }

    // Load config
    const configBtn = document.getElementById('loadConfig');
    if (configBtn) {
        configBtn.addEventListener('click', loadSystemConfig);
    }

    // Data management
    const cleanupBtn = document.getElementById('cleanupData');
    if (cleanupBtn) {
        cleanupBtn.addEventListener('click', cleanupData);
    }

    const exportBtn = document.getElementById('exportData');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportData);
    }

    const sampleDataBtn = document.getElementById('loadSampleData');
    if (sampleDataBtn) {
        sampleDataBtn.addEventListener('click', loadSampleData);
    }

    // Notification settings
    setupNotificationSettings();
}

async function checkSystemHealth() {
    const statusElements = {
        api: document.getElementById('apiStatus'),
        db: document.getElementById('dbStatus'),
        ai: document.getElementById('aiStatus')
    };

    // Set all to checking
    Object.values(statusElements).forEach(el => {
        if (el) {
            el.textContent = 'Checking...';
            el.className = 'status-indicator checking';
        }
    });

    try {
        const health = await API.getSystemHealth();
        
        Object.entries(health).forEach(([key, status]) => {
            const element = statusElements[key];
            if (element) {
                element.textContent = status.healthy ? 'Healthy' : 'Unhealthy';
                element.className = `status-indicator ${status.healthy ? 'healthy' : 'unhealthy'}`;
            }
        });

        const allHealthy = Object.values(health).every(status => status.healthy);
        showNotification(
            allHealthy ? 'All systems are healthy!' : 'Some systems need attention.',
            allHealthy ? 'success' : 'warning'
        );
    } catch (error) {
        console.error('Health check error:', error);
        Object.values(statusElements).forEach(el => {
            if (el) {
                el.textContent = 'Error';
                el.className = 'status-indicator unhealthy';
            }
        });
        showNotification('Error checking system health.', 'error');
    }
}

async function loadSystemConfig() {
    try {
        const config = await API.getSystemConfig();
        const configContainer = document.getElementById('systemConfig');
        if (configContainer) {
            configContainer.innerHTML = `<pre>${JSON.stringify(config, null, 2)}</pre>`;
        }
    } catch (error) {
        console.error('Config loading error:', error);
        showNotification('Error loading system configuration.', 'error');
    }
}

async function cleanupData() {
    const days = document.getElementById('cleanupDays')?.value || 90;
    
    if (!confirm(`Are you sure you want to delete data older than ${days} days?`)) {
        return;
    }

    showLoading();
    
    try {
        const result = await API.cleanupData(days);
        showNotification(`Cleaned up ${result.deleted_records} records.`, 'success');
    } catch (error) {
        console.error('Cleanup error:', error);
        showNotification('Error during data cleanup.', 'error');
    } finally {
        hideLoading();
    }
}

function setupNotificationSettings() {
    const settings = ['criticalNotifications', 'processingNotifications', 'systemNotifications'];
    
    settings.forEach(settingId => {
        const checkbox = document.getElementById(settingId);
        if (checkbox) {
            // Load saved setting
            const saved = localStorage.getItem(settingId);
            if (saved !== null) {
                checkbox.checked = saved === 'true';
            }

            // Save on change
            checkbox.addEventListener('change', () => {
                localStorage.setItem(settingId, checkbox.checked);
                showNotification('Notification settings updated.', 'success');
            });
        }
    });
}

// ===== History Functions =====
function loadHistory() {
    setupHistoryFilters();
    loadHistoryData();
}

function setupHistoryFilters() {
    const searchInput = document.getElementById('historySearch');
    const classificationFilter = document.getElementById('classificationFilter');
    const priorityFilter = document.getElementById('priorityFilter');
    const vesselFilter = document.getElementById('vesselFilter');

    [searchInput, classificationFilter, priorityFilter, vesselFilter].forEach(element => {
        if (element) {
            element.addEventListener('input', () => {
                debounce(loadHistoryData, 300)();
            });
        }
    });
}

async function loadHistoryData(page = 1) {
    const filters = {
        search: document.getElementById('historySearch')?.value || '',
        classification: document.getElementById('classificationFilter')?.value || '',
        priority: document.getElementById('priorityFilter')?.value || '',
        vessel_id: document.getElementById('vesselFilter')?.value || '',
        page: page
    };

    showLoading();

    try {
        const data = await API.getHistory(filters);
        displayHistoryData(data.results);
        setupPagination(data.pagination);
    } catch (error) {
        console.error('History loading error:', error);
        showNotification('Error loading history data.', 'error');
    } finally {
        hideLoading();
    }
}

function displayHistoryData(results) {
    const tbody = document.getElementById('historyTableBody');
    if (!tbody) return;

    tbody.innerHTML = results.map(item => `
        <tr class="animate-fade-in">
            <td data-label="Timestamp">${formatDate(item.timestamp)}</td>
            <td data-label="Document Type">${item.document_type}</td>
            <td data-label="Classification">
                <span class="classification-badge ${item.priority.toLowerCase()}">${item.classification}</span>
            </td>
            <td data-label="Priority">
                <span class="priority-badge ${item.priority}">${item.priority}</span>
            </td>
            <td data-label="Vessel ID">${item.vessel_id || 'N/A'}</td>
            <td data-label="Confidence">${Math.round(item.confidence * 100)}%</td>
            <td data-label="Actions">
                <button class="btn btn-outline btn-sm" onclick="viewHistoryDetails('${item.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        </tr>
    `).join('');
}

window.viewHistoryDetails = async function(id) {
    try {
        const details = await API.getHistoryDetails(id);
        showModal('Processing Details', `
            <div class="result-details">
                <div class="detail-section">
                    <h4>Original Text</h4>
                    <p>${details.original_text}</p>
                </div>
                <div class="detail-section">
                    <h4>Classification</h4>
                    <span class="classification-badge ${details.priority.toLowerCase()}">${details.classification}</span>
                </div>
                <div class="detail-section">
                    <h4>Summary</h4>
                    <p>${details.summary}</p>
                </div>
                <div class="detail-section">
                    <h4>Entities</h4>
                    <div>${details.entities.map(e => `<span class="entity-tag">${e}</span>`).join('')}</div>
                </div>
                <div class="detail-section">
                    <h4>Keywords</h4>
                    <div>${details.keywords.map(k => `<span class="keyword-tag">${k}</span>`).join('')}</div>
                </div>
            </div>
        `);
    } catch (error) {
        console.error('Error loading details:', error);
        showNotification('Error loading details.', 'error');
    }
};

function setupPagination(pagination) {
    const container = document.getElementById('historyPagination');
    if (!container) return;

    const { current_page, total_pages, has_prev, has_next } = pagination;
    
    let paginationHTML = '';
    
    // Previous button
    paginationHTML += `
        <button ${!has_prev ? 'disabled' : ''} onclick="loadHistoryData(${current_page - 1})">
            <i class="fas fa-chevron-left"></i>
        </button>
    `;
    
    // Page numbers
    for (let i = Math.max(1, current_page - 2); i <= Math.min(total_pages, current_page + 2); i++) {
        paginationHTML += `
            <button class="${i === current_page ? 'active' : ''}" onclick="loadHistoryData(${i})">
                ${i}
            </button>
        `;
    }
    
    // Next button
    paginationHTML += `
        <button ${!has_next ? 'disabled' : ''} onclick="loadHistoryData(${current_page + 1})">
            <i class="fas fa-chevron-right"></i>
        </button>
    `;
    
    container.innerHTML = paginationHTML;
}

// ===== Utility Functions =====
function showLoading() {
    AppState.isLoading = true;
    elements.loadingOverlay?.classList.add('active');
}

function hideLoading() {
    AppState.isLoading = false;
    elements.loadingOverlay?.classList.remove('active');
}

function showNotification(message, type = 'info') {
    elements.toastMessage.textContent = message;
    elements.notificationToast.className = `notification-toast show alert-${type}`;
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        hideNotification();
    }, 5000);
}

function hideNotification() {
    elements.notificationToast?.classList.remove('show');
}

function showModal(title, content) {
    elements.modalBody.innerHTML = `
        <h2>${title}</h2>
        ${content}
    `;
    elements.modal?.classList.add('active');
}

function closeModal() {
    elements.modal?.classList.remove('active');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function loadUserPreferences() {
    // Load notification settings
    const notificationSettings = {
        critical: localStorage.getItem('criticalNotifications') !== 'false',
        processing: localStorage.getItem('processingNotifications') !== 'false',
        system: localStorage.getItem('systemNotifications') === 'true'
    };
    
    // Apply settings
    Object.entries(notificationSettings).forEach(([key, value]) => {
        const element = document.getElementById(`${key}Notifications`);
        if (element) {
            element.checked = value;
        }
    });
}

// ===== Keyboard Shortcuts =====
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + number keys for navigation
        if ((e.ctrlKey || e.metaKey) && e.key >= '1' && e.key <= '5') {
            e.preventDefault();
            const sections = ['dashboard', 'process', 'analytics', 'history', 'settings'];
            const index = parseInt(e.key) - 1;
            if (sections[index]) {
                navigateToSection(sections[index]);
            }
        }
        
        // Escape to close modal
        if (e.key === 'Escape') {
            closeModal();
            hideNotification();
        }
        
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('historySearch');
            if (searchInput && AppState.currentSection === 'history') {
                searchInput.focus();
            }
        }
    });
}

// ===== Browser History =====
window.addEventListener('popstate', (e) => {
    if (e.state && e.state.section) {
        navigateToSection(e.state.section);
    }
});

// ===== Error Handling =====
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    showNotification('An unexpected error occurred. Please refresh the page.', 'error');
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
    showNotification('An error occurred while processing your request.', 'error');
});

// ===== Export for global access =====
window.VesselApp = {
    navigateToSection,
    showNotification,
    showLoading,
    hideLoading,
    showModal,
    closeModal,
    AppState
};
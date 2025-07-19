// ===== Reusable UI Components =====

class UIComponents {
    // ===== Notification System =====
    static createNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification-item notification-${type} animate-slide-in-right`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <div class="notification-content">
                <i class="${icons[type] || icons.info}"></i>
                <span>${message}</span>
                <button class="notification-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add to container
        let container = document.querySelector('.notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Setup close button
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => this.removeNotification(notification));
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => this.removeNotification(notification), duration);
        }
        
        return notification;
    }
    
    static removeNotification(notification) {
        notification.classList.add('animate-slide-out-right');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
    
    // ===== Loading Components =====
    static createLoadingSpinner(size = 'md') {
        const spinner = document.createElement('div');
        spinner.className = `spinner spinner-${size}`;
        return spinner;
    }
    
    static createLoadingSkeleton(type = 'text', width = '100%') {
        const skeleton = document.createElement('div');
        skeleton.className = `loading-skeleton skeleton-${type}`;
        skeleton.style.width = width;
        return skeleton;
    }
    
    static showElementLoading(element) {
        if (!element) return;
        
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'element-loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="element-loading-content">
                ${this.createLoadingSpinner().outerHTML}
                <span>Loading...</span>
            </div>
        `;
        
        element.style.position = 'relative';
        element.appendChild(loadingOverlay);
        
        return loadingOverlay;
    }
    
    static hideElementLoading(element) {
        if (!element) return;
        
        const overlay = element.querySelector('.element-loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
    
    // ===== Modal Components =====
    static createModal(title, content, options = {}) {
        const modal = document.createElement('div');
        modal.className = 'modal custom-modal';
        
        const defaultOptions = {
            closable: true,
            backdrop: true,
            size: 'md',
            buttons: []
        };
        
        const config = { ...defaultOptions, ...options };
        
        modal.innerHTML = `
            <div class="modal-content modal-${config.size}">
                <div class="modal-header">
                    <h3>${title}</h3>
                    ${config.closable ? '<button class="modal-close"><i class="fas fa-times"></i></button>' : ''}
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                ${config.buttons.length > 0 ? `
                    <div class="modal-footer">
                        ${config.buttons.map(btn => `
                            <button class="btn btn-${btn.type || 'secondary'}" data-action="${btn.action || ''}">
                                ${btn.text}
                            </button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Setup event listeners
        if (config.closable) {
            const closeBtn = modal.querySelector('.modal-close');
            closeBtn.addEventListener('click', () => this.closeModal(modal));
        }
        
        if (config.backdrop) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        }
        
        // Setup button actions
        config.buttons.forEach(button => {
            if (button.action && button.handler) {
                const btn = modal.querySelector(`[data-action="${button.action}"]`);
                btn.addEventListener('click', () => button.handler(modal));
            }
        });
        
        // Show modal
        setTimeout(() => modal.classList.add('active'), 10);
        
        return modal;
    }
    
    static closeModal(modal) {
        modal.classList.remove('active');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }
    
    // ===== Confirmation Dialog =====
    static showConfirmDialog(message, options = {}) {
        return new Promise((resolve) => {
            const defaultOptions = {
                title: 'Confirm Action',
                confirmText: 'Confirm',
                cancelText: 'Cancel',
                type: 'warning'
            };
            
            const config = { ...defaultOptions, ...options };
            
            const modal = this.createModal(config.title, `
                <div class="confirm-dialog">
                    <div class="confirm-icon">
                        <i class="fas fa-exclamation-triangle" style="color: var(--medium-color)"></i>
                    </div>
                    <div class="confirm-message">
                        <p>${message}</p>
                    </div>
                </div>
            `, {
                buttons: [
                    {
                        text: config.cancelText,
                        type: 'secondary',
                        action: 'cancel',
                        handler: () => {
                            this.closeModal(modal);
                            resolve(false);
                        }
                    },
                    {
                        text: config.confirmText,
                        type: config.type === 'danger' ? 'danger' : 'primary',
                        action: 'confirm',
                        handler: () => {
                            this.closeModal(modal);
                            resolve(true);
                        }
                    }
                ]
            });
        });
    }
    
    // ===== Dropdown Component =====
    static createDropdown(trigger, items, options = {}) {
        const defaultOptions = {
            position: 'bottom-left',
            closeOnClick: true
        };
        
        const config = { ...defaultOptions, ...options };
        
        const dropdown = document.createElement('div');
        dropdown.className = 'dropdown-menu';
        dropdown.style.position = 'absolute';
        dropdown.style.zIndex = '1000';
        
        dropdown.innerHTML = items.map(item => {
            if (item.divider) {
                return '<div class="dropdown-divider"></div>';
            }
            return `
                <button class="dropdown-item" data-value="${item.value || ''}">
                    ${item.icon ? `<i class="${item.icon}"></i>` : ''}
                    ${item.text}
                </button>
            `;
        }).join('');
        
        // Position dropdown
        const triggerRect = trigger.getBoundingClientRect();
        dropdown.style.top = `${triggerRect.bottom + window.scrollY}px`;
        dropdown.style.left = `${triggerRect.left + window.scrollX}px`;
        
        document.body.appendChild(dropdown);
        
        // Setup item click handlers
        dropdown.addEventListener('click', (e) => {
            const item = e.target.closest('.dropdown-item');
            if (item) {
                const value = item.dataset.value;
                const text = item.textContent.trim();
                
                if (config.onSelect) {
                    config.onSelect(value, text, item);
                }
                
                if (config.closeOnClick) {
                    this.closeDropdown(dropdown);
                }
            }
        });
        
        // Close dropdown when clicking outside
        setTimeout(() => {
            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target) && !trigger.contains(e.target)) {
                    this.closeDropdown(dropdown);
                }
            }, { once: true });
        }, 10);
        
        return dropdown;
    }
    
    static closeDropdown(dropdown) {
        dropdown.classList.add('closing');
        setTimeout(() => {
            if (dropdown.parentNode) {
                dropdown.parentNode.removeChild(dropdown);
            }
        }, 150);
    }
    
    // ===== Tooltip Component =====
    static initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            if (element.dataset.tooltipInitialized) return;
            
            element.dataset.tooltipInitialized = 'true';
            
            let tooltip = null;
            
            element.addEventListener('mouseenter', () => {
                tooltip = this.createTooltip(element.dataset.tooltip, element);
            });
            
            element.addEventListener('mouseleave', () => {
                if (tooltip) {
                    this.removeTooltip(tooltip);
                    tooltip = null;
                }
            });
        });
    }
    
    static createTooltip(text, targetElement) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip-popup';
        tooltip.textContent = text;
        
        document.body.appendChild(tooltip);
        
        // Position tooltip
        const targetRect = targetElement.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        tooltip.style.position = 'absolute';
        tooltip.style.top = `${targetRect.top + window.scrollY - tooltipRect.height - 8}px`;
        tooltip.style.left = `${targetRect.left + window.scrollX + (targetRect.width - tooltipRect.width) / 2}px`;
        tooltip.style.zIndex = '9999';
        
        // Add arrow
        const arrow = document.createElement('div');
        arrow.className = 'tooltip-arrow';
        tooltip.appendChild(arrow);
        
        // Animate in
        setTimeout(() => tooltip.classList.add('visible'), 10);
        
        return tooltip;
    }
    
    static removeTooltip(tooltip) {
        tooltip.classList.remove('visible');
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        }, 200);
    }
    
    // ===== Progress Bar Component =====
    static createProgressBar(value = 0, options = {}) {
        const defaultOptions = {
            max: 100,
            showText: true,
            animated: false,
            color: 'primary'
        };
        
        const config = { ...defaultOptions, ...options };
        
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        
        const progressFill = document.createElement('div');
        progressFill.className = `progress-fill progress-${config.color}`;
        if (config.animated) {
            progressFill.classList.add('progress-animated');
        }
        
        const percentage = Math.round((value / config.max) * 100);
        progressFill.style.width = `${percentage}%`;
        
        if (config.showText) {
            const progressText = document.createElement('div');
            progressText.className = 'progress-text';
            progressText.textContent = `${percentage}%`;
            progressFill.appendChild(progressText);
        }
        
        progressBar.appendChild(progressFill);
        
        // Method to update progress
        progressBar.updateProgress = function(newValue) {
            const newPercentage = Math.round((newValue / config.max) * 100);
            progressFill.style.width = `${newPercentage}%`;
            if (config.showText) {
                progressFill.querySelector('.progress-text').textContent = `${newPercentage}%`;
            }
        };
        
        return progressBar;
    }
    
    // ===== Tabs Component =====
    static initTabs(tabContainer) {
        const tabButtons = tabContainer.querySelectorAll('.tab-button');
        const tabPanels = tabContainer.querySelectorAll('.tab-panel');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetPanel = button.dataset.tab;
                
                // Remove active class from all buttons and panels
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabPanels.forEach(panel => panel.classList.remove('active'));
                
                // Add active class to clicked button and corresponding panel
                button.classList.add('active');
                const panel = tabContainer.querySelector(`#${targetPanel}`);
                if (panel) {
                    panel.classList.add('active');
                }
            });
        });
    }
    
    // ===== Search Component =====
    static createSearchInput(placeholder = 'Search...', options = {}) {
        const defaultOptions = {
            debounce: 300,
            minLength: 2,
            showClear: true
        };
        
        const config = { ...defaultOptions, ...options };
        
        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-input-container';
        
        searchContainer.innerHTML = `
            <div class="search-input-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input type="text" class="search-input" placeholder="${placeholder}">
                ${config.showClear ? '<button class="search-clear"><i class="fas fa-times"></i></button>' : ''}
            </div>
            <div class="search-results-container"></div>
        `;
        
        const input = searchContainer.querySelector('.search-input');
        const clearBtn = searchContainer.querySelector('.search-clear');
        const resultsContainer = searchContainer.querySelector('.search-results-container');
        
        let debounceTimer;
        
        // Search input handler
        input.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            
            const query = e.target.value.trim();
            
            // Show/hide clear button
            if (clearBtn) {
                clearBtn.style.display = query ? 'block' : 'none';
            }
            
            if (query.length >= config.minLength) {
                debounceTimer = setTimeout(() => {
                    if (config.onSearch) {
                        config.onSearch(query, resultsContainer);
                    }
                }, config.debounce);
            } else {
                resultsContainer.innerHTML = '';
                resultsContainer.style.display = 'none';
            }
        });
        
        // Clear button handler
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                input.value = '';
                clearBtn.style.display = 'none';
                resultsContainer.innerHTML = '';
                resultsContainer.style.display = 'none';
                input.focus();
            });
        }
        
        return searchContainer;
    }
    
    // ===== File Upload Component =====
    static createFileUpload(options = {}) {
        const defaultOptions = {
            multiple: false,
            accept: '*/*',
            maxSize: 10 * 1024 * 1024, // 10MB
            dragDrop: true
        };
        
        const config = { ...defaultOptions, ...options };
        
        const uploadContainer = document.createElement('div');
        uploadContainer.className = 'file-upload-container';
        
        uploadContainer.innerHTML = `
            <div class="file-upload-area">
                <input type="file" class="file-input" ${config.multiple ? 'multiple' : ''} accept="${config.accept}">
                <div class="upload-content">
                    <i class="fas fa-cloud-upload-alt upload-icon"></i>
                    <h4>Drop files here or click to browse</h4>
                    <p>Max file size: ${this.formatFileSize(config.maxSize)}</p>
                </div>
            </div>
            <div class="file-list"></div>
        `;
        
        const uploadArea = uploadContainer.querySelector('.file-upload-area');
        const fileInput = uploadContainer.querySelector('.file-input');
        const fileList = uploadContainer.querySelector('.file-list');
        
        // File input change handler
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files, config, fileList);
        });
        
        // Drag and drop handlers
        if (config.dragDrop) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                this.handleFileSelection(e.dataTransfer.files, config, fileList);
            });
        }
        
        // Click to browse
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        return uploadContainer;
    }
    
    static handleFileSelection(files, config, fileList) {
        Array.from(files).forEach(file => {
            if (file.size > config.maxSize) {
                VesselApp.showNotification(`File ${file.name} is too large`, 'error');
                return;
            }
            
            this.addFileToList(file, fileList, config);
        });
    }
    
    static addFileToList(file, fileList, config) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file file-icon"></i>
                <div class="file-details">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${this.formatFileSize(file.size)}</div>
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-sm btn-outline file-remove">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Remove button handler
        const removeBtn = fileItem.querySelector('.file-remove');
        removeBtn.addEventListener('click', () => {
            fileItem.remove();
        });
        
        fileList.appendChild(fileItem);
        
        // Trigger upload callback
        if (config.onFileAdd) {
            config.onFileAdd(file, fileItem);
        }
    }
    
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// ===== Initialize Components =====
document.addEventListener('DOMContentLoaded', () => {
    // Initialize tooltips
    UIComponents.initTooltips();
    
    // Initialize tabs
    document.querySelectorAll('.tabs').forEach(tabContainer => {
        UIComponents.initTabs(tabContainer);
    });
    
    // Re-initialize tooltips when new content is added
    const observer = new MutationObserver(() => {
        UIComponents.initTooltips();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// ===== Add missing export data function =====
async function exportData() {
    try {
        const confirmed = await UIComponents.showConfirmDialog(
            'This will export all your data. Continue?',
            { title: 'Export Data', confirmText: 'Export' }
        );
        
        if (!confirmed) return;
        
        VesselApp.showLoading();
        
        const data = await API.exportData();
        
        // Create download
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `vessel-data-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        VesselApp.showNotification('Data exported successfully!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        VesselApp.showNotification('Error exporting data.', 'error');
    } finally {
        VesselApp.hideLoading();
    }
}

async function loadSampleData() {
    try {
        const confirmed = await UIComponents.showConfirmDialog(
            'This will load sample data into the system. Continue?',
            { title: 'Load Sample Data', confirmText: 'Load Data' }
        );
        
        if (!confirmed) return;
        
        VesselApp.showLoading();
        
        const result = await API.loadSampleData();
        VesselApp.showNotification(result.message, 'success');
        
        // Refresh current section data
        if (VesselApp.AppState.currentSection === 'dashboard') {
            loadDashboardData();
        } else if (VesselApp.AppState.currentSection === 'history') {
            loadHistoryData();
        }
    } catch (error) {
        console.error('Sample data loading error:', error);
        VesselApp.showNotification('Error loading sample data.', 'error');
    } finally {
        VesselApp.hideLoading();
    }
}

// ===== CSS for components =====
const componentStyles = `
    .notifications-container {
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 10000;
        pointer-events: none;
    }

    .notification-item {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-left: 4px solid;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        margin-bottom: var(--space-sm);
        max-width: 400px;
        pointer-events: auto;
    }

    .notification-success { border-left-color: var(--low-color); }
    .notification-error { border-left-color: var(--critical-color); }
    .notification-warning { border-left-color: var(--medium-color); }
    .notification-info { border-left-color: var(--primary-color); }

    .notification-content {
        display: flex;
        align-items: center;
        gap: var(--space-sm);
        padding: var(--space-md);
    }

    .notification-close {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        margin-left: auto;
        padding: var(--space-xs);
    }

    .element-loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }

    .element-loading-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-sm);
    }

    .tooltip-popup {
        background: var(--gray-900);
        color: white;
        padding: var(--space-xs) var(--space-sm);
        border-radius: var(--radius-sm);
        font-size: var(--font-size-xs);
        white-space: nowrap;
        opacity: 0;
        transition: opacity var(--transition-fast);
    }

    .tooltip-popup.visible {
        opacity: 1;
    }

    .confirm-dialog {
        text-align: center;
        padding: var(--space-lg);
    }

    .confirm-icon {
        font-size: var(--font-size-4xl);
        margin-bottom: var(--space-lg);
    }

    .search-input-container {
        position: relative;
    }

    .search-input-wrapper {
        position: relative;
        display: flex;
        align-items: center;
    }

    .search-icon {
        position: absolute;
        left: var(--space-md);
        color: var(--text-secondary);
        z-index: 1;
    }

    .search-input {
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }

    .search-clear {
        position: absolute;
        right: var(--space-md);
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        display: none;
    }

    .file-upload-area {
        border: 2px dashed var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--space-2xl);
        text-align: center;
        cursor: pointer;
        transition: all var(--transition-normal);
    }

    .file-upload-area:hover,
    .file-upload-area.dragover {
        border-color: var(--primary-color);
        background: rgba(37, 99, 235, 0.05);
    }

    .upload-icon {
        font-size: var(--font-size-4xl);
        color: var(--primary-color);
        margin-bottom: var(--space-md);
    }

    .file-input {
        position: absolute;
        opacity: 0;
        pointer-events: none;
    }
`;

// Inject component styles
const styleSheet = document.createElement('style');
styleSheet.textContent = componentStyles;
document.head.appendChild(styleSheet);

// Export for global access
window.UIComponents = UIComponents;
window.exportData = exportData;
window.loadSampleData = loadSampleData;
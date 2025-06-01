/**
 * SkillForge Admin Base JavaScript
 * Common functionality across all admin pages
 */

class AdminBase {
    constructor() {
        this.init();
    }

    init() {
        console.log('SkillForge Admin Base initialized');
        this.setupGlobalEventListeners();
        this.initializeTooltips();
        this.setupFormValidation();
    }

    /**
     * Setup global event listeners
     */
    setupGlobalEventListeners() {
        // Auto-dismiss alerts after 5 seconds
        this.setupAlertAutoDismiss();
        
        // Setup CSRF token for AJAX requests
        this.setupCSRFToken();
        
        // Setup responsive navigation
        this.setupResponsiveNav();
    }

    /**
     * Auto-dismiss alerts
     */
    setupAlertAutoDismiss() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            // Only auto-dismiss success and info alerts
            if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
                setTimeout(() => {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }, 5000);
            }
        });
    }

    /**
     * Setup CSRF token for AJAX requests
     */
    setupCSRFToken() {
        // Get CSRF token from cookie
        const csrfToken = this.getCookie('csrftoken');
        
        // Setup jQuery AJAX if available
        if (typeof $ !== 'undefined') {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrfToken);
                    }
                }
            });
        }
        
        // Setup fetch defaults
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            if (!options.headers) {
                options.headers = {};
            }
            
            if (!options.headers['X-CSRFToken']) {
                options.headers['X-CSRFToken'] = csrfToken;
            }
            
            return originalFetch(url, options);
        };
    }

    /**
     * Initialize Bootstrap tooltips
     */
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }

    /**
     * Setup responsive navigation
     */
    setupResponsiveNav() {
        const navbar = document.querySelector('.navbar-collapse');
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        // Close mobile menu when clicking on a link
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navbar.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(navbar);
                    bsCollapse.hide();
                }
            });
        });
    }

    /**
     * Get cookie value by name
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Show loading state on element
     */
    showLoading(element, text = 'Loading...') {
        element.classList.add('loading');
        const originalText = element.textContent;
        element.setAttribute('data-original-text', originalText);
        
        if (element.tagName === 'BUTTON') {
            element.disabled = true;
            element.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i>${text}`;
        }
    }

    /**
     * Hide loading state from element
     */
    hideLoading(element) {
        element.classList.remove('loading');
        const originalText = element.getAttribute('data-original-text');
        
        if (element.tagName === 'BUTTON') {
            element.disabled = false;
            if (originalText) {
                element.textContent = originalText;
                element.removeAttribute('data-original-text');
            }
        }
    }

    /**
     * Show notification toast
     */
    showToast(message, type = 'info', duration = 5000) {
        const toastContainer = this.getOrCreateToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${this.getIconForType(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    /**
     * Get or create toast container
     */
    getOrCreateToastContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    }

    /**
     * Get icon for toast type
     */
    getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'primary': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Confirm action with modal
     */
    confirmAction(message, callback, title = 'Confirm Action') {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content bg-admin-gray">
                    <div class="modal-header border-admin">
                        <h5 class="modal-title text-white">${title}</h5>
                        <button type="button" class="btn-close btn-close-white" 
                                data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-white">
                        ${message}
                    </div>
                    <div class="modal-footer border-admin">
                        <button type="button" class="btn btn-secondary" 
                                data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" 
                                id="confirm-action">Confirm</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Handle confirm click
        modal.querySelector('#confirm-action').addEventListener('click', () => {
            callback();
            bsModal.hide();
        });
        
        // Remove from DOM after hiding
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
}

// Utility functions
const AdminUtils = {
    /**
     * Format date for display
     */
    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return new Date(date).toLocaleDateString('en-US', {
            ...defaultOptions,
            ...options
        });
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function
     */
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.adminBase = new AdminBase();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AdminBase, AdminUtils };
}
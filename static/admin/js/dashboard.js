/**
 * SkillForge Admin Dashboard JavaScript
 * Handles real-time updates, animations, and interactions
 */

class AdminDashboard {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }

    init() {
        console.log('SkillForge Admin Dashboard initialized');
        this.animateCards();
        this.setupTooltips();
    }

    /**
     * Animate dashboard cards on page load
     */
    animateCards() {
        const cards = document.querySelectorAll('.dashboard-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    /**
     * Setup event listeners for dashboard interactions
     */
    setupEventListeners() {
        // Quick action buttons
        const quickActionBtns = document.querySelectorAll('.quick-action-btn');
        quickActionBtns.forEach(btn => {
            btn.addEventListener('click', this.handleQuickAction.bind(this));
        });

        // Dashboard card clicks
        const dashboardCards = document.querySelectorAll('.dashboard-card');
        dashboardCards.forEach(card => {
            card.addEventListener('click', this.handleCardClick.bind(this));
            card.style.cursor = 'pointer';
        });

        // Refresh button if exists
        const refreshBtn = document.querySelector('[data-action="refresh"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', this.refreshStats.bind(this));
        }
    }

    /**
     * Handle quick action button clicks
     */
    handleQuickAction(event) {
        const btn = event.currentTarget;
        const action = btn.getAttribute('data-action');
        
        // Add loading state
        btn.classList.add('loading');
        const icon = btn.querySelector('i');
        const originalIcon = icon.className;
        icon.className = 'fas fa-spinner fa-spin';
        
        // Remove loading state after a short delay
        setTimeout(() => {
            btn.classList.remove('loading');
            icon.className = originalIcon;
        }, 1000);
    }

    /**
     * Handle dashboard card clicks
     */
    handleCardClick(event) {
        const card = event.currentTarget;
        const cardType = this.getCardType(card);
        
        // Navigate to appropriate page based on card type
        switch (cardType) {
            case 'users':
                window.location.href = '/panel/users/';
                break;
            case 'contacts':
                window.location.href = '/panel/contacts/';
                break;
            case 'sessions':
                // Handle sessions view
                break;
            case 'status':
                // Handle system status
                break;
        }
    }

    /**
     * Get card type from CSS classes
     */
    getCardType(card) {
        if (card.classList.contains('users')) return 'users';
        if (card.classList.contains('contacts')) return 'contacts';
        if (card.classList.contains('sessions')) return 'sessions';
        if (card.classList.contains('status')) return 'status';
        return null;
    }

    /**
     * Setup tooltips for dashboard elements
     */
    setupTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(
                document.querySelectorAll('[data-bs-toggle="tooltip"]')
            );
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    /**
     * Start real-time updates for dashboard statistics
     */
    startRealTimeUpdates() {
        // Update stats every 30 seconds
        this.updateInterval = setInterval(() => {
            this.fetchLatestStats();
        }, 30000);
    }

    /**
     * Fetch latest statistics from the server
     */
    async fetchLatestStats() {
        try {
            const response = await fetch('/panel/stats/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateStatsDisplay(data);
            }
        } catch (error) {
            console.error('Failed to fetch latest stats:', error);
        }
    }

    /**
     * Update statistics display with new data
     */
    updateStatsDisplay(data) {
        // Update user count
        const totalUsersElement = document.querySelector('.users .card-number');
        if (totalUsersElement && data.total_users !== undefined) {
            this.animateNumber(totalUsersElement, data.total_users);
        }

        // Update contact count
        const totalContactsElement = document.querySelector('.contacts .card-number');
        if (totalContactsElement && data.total_contacts !== undefined) {
            this.animateNumber(totalContactsElement, data.total_contacts);
        }

        // Update active users
        const activeUsersElement = document.querySelector('.sessions .card-number');
        if (activeUsersElement && data.active_users !== undefined) {
            this.animateNumber(activeUsersElement, data.active_users);
        }
    }

    /**
     * Animate number changes in dashboard cards
     */
    animateNumber(element, newValue) {
        const currentValue = parseInt(element.textContent) || 0;
        
        if (currentValue === newValue) return;

        const duration = 1000; // 1 second
        const steps = 30;
        const stepValue = (newValue - currentValue) / steps;
        let currentStep = 0;

        const interval = setInterval(() => {
            currentStep++;
            const value = Math.round(currentValue + (stepValue * currentStep));
            element.textContent = value;

            if (currentStep >= steps) {
                clearInterval(interval);
                element.textContent = newValue;
            }
        }, duration / steps);
    }

    /**
     * Manually refresh dashboard statistics
     */
    async refreshStats() {
        const refreshBtn = document.querySelector('[data-action="refresh"]');
        if (refreshBtn) {
            refreshBtn.classList.add('loading');
            const icon = refreshBtn.querySelector('i');
            icon.classList.add('fa-spin');
        }

        await this.fetchLatestStats();

        if (refreshBtn) {
            setTimeout(() => {
                refreshBtn.classList.remove('loading');
                const icon = refreshBtn.querySelector('i');
                icon.classList.remove('fa-spin');
            }, 1000);
        }
    }

    /**
     * Cleanup when page is unloaded
     */
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.adminDashboard = new AdminDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.adminDashboard) {
        window.adminDashboard.destroy();
    }
});

// Utility functions for dashboard
const DashboardUtils = {
    /**
     * Format numbers with commas for better readability
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    /**
     * Show notification toast
     */
    showToast(message, type = 'info') {
        // Implementation depends on your toast library
        console.log(`[${type.toUpperCase()}] ${message}`);
    },

    /**
     * Handle API errors gracefully
     */
    handleApiError(error) {
        console.error('API Error:', error);
        this.showToast('An error occurred while updating data', 'error');
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AdminDashboard, DashboardUtils };
}
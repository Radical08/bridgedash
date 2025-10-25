// Main application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize HTMX configuration
    document.body.addEventListener('htmx:configRequest', (event) => {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            event.detail.headers['X-CSRFToken'] = csrfToken.value;
        }
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            // Simple tooltip implementation
            const tooltipText = this.getAttribute('title');
            if (tooltipText) {
                const tooltipEl = document.createElement('div');
                tooltipEl.className = 'custom-tooltip';
                tooltipEl.textContent = tooltipText;
                document.body.appendChild(tooltipEl);
                
                const rect = this.getBoundingClientRect();
                tooltipEl.style.left = rect.left + 'px';
                tooltipEl.style.top = (rect.top - tooltipEl.offsetHeight - 5) + 'px';
                
                this._tooltip = tooltipEl;
            }
        });
        
        tooltip.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });
});

// Utility functions
const BridgeDash = {
    // Format currency
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Format distance
    formatDistance: (km) => {
        return `${parseFloat(km).toFixed(1)} km`;
    },

    // Format time
    formatTime: (timestamp) => {
        return new Date(timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Calculate ETA
    calculateETA: (distanceKm, speedKmh = 15) => {
        const minutes = Math.round((distanceKm / speedKmh) * 60);
        return minutes > 0 ? minutes : 5; // Minimum 5 minutes
    }
};

// Export for global use
window.BridgeDash = BridgeDash;
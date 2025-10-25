// Notifications system for BridgeDash
class NotificationManager {
    constructor() {
        this.permission = null;
        this.soundEnabled = true;
        this.init();
    }

    async init() {
        // Check notification permission
        if ('Notification' in window) {
            this.permission = Notification.permission;
            
            if (this.permission === 'default') {
                this.permission = await Notification.requestPermission();
            }
        }

        // Listen for online/offline events
        window.addEventListener('online', this.handleOnline.bind(this));
        window.addEventListener('offline', this.handleOffline.bind(this));
    }

    // Show browser notification
    showBrowserNotification(title, options = {}) {
        if (!('Notification' in window) || this.permission !== 'granted') {
            return false;
        }

        const notificationOptions = {
            icon: '/static/images/logo.png',
            badge: '/static/images/logo.png',
            ...options
        };

        const notification = new Notification(title, notificationOptions);
        
        notification.onclick = () => {
            window.focus();
            notification.close();
            
            if (options.clickUrl) {
                window.location.href = options.clickUrl;
            }
        };

        // Auto-close after 5 seconds
        setTimeout(() => {
            notification.close();
        }, 5000);

        return true;
    }

    // Show in-app notification
    showInAppNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-icon">${this.getIcon(type)}</div>
            <div class="notification-content">
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;

        // Add styles if not already added
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border-radius: 10px;
                    padding: 15px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    max-width: 400px;
                    z-index: 10000;
                    animation: slideIn 0.3s ease;
                }
                .notification-icon { font-size: 1.5em; }
                .notification-content { flex: 1; }
                .notification-close {
                    background: none;
                    border: none;
                    font-size: 1.2em;
                    cursor: pointer;
                    padding: 0;
                    width: 25px;
                    height: 25px;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); }
                    to { transform: translateX(0); }
                }
            `;
            document.head.appendChild(styles);
        }

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getIcon(type) {
        const icons = {
            info: 'ℹ️',
            success: '✅',
            warning: '⚠️',
            error: '❌',
            delivery: '📦',
            message: '💬'
        };
        return icons[type] || icons.info;
    }

    // Play notification sound
    playSound(type = 'default') {
        if (!this.soundEnabled) return;

        // Simple sound using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.type = 'sine';
            
            switch(type) {
                case 'success':
                    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
                    break;
                case 'warning':
                    oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
                    break;
                case 'error':
                    oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
                    break;
                default:
                    oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
            }

            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.warn('Audio not supported:', error);
        }
    }

    // Handle online event
    handleOnline() {
        this.showInAppNotification('🔗 Connection restored', 'success');
        this.playSound('success');
    }

    // Handle offline event
    handleOffline() {
        this.showInAppNotification('🔌 You are offline', 'warning');
        this.playSound('warning');
    }

    // Delivery-specific notifications
    notifyDeliveryAccepted(delivery) {
        const message = `✅ ${delivery.driverName} accepted your delivery`;
        this.showInAppNotification(message, 'success');
        this.showBrowserNotification('Delivery Accepted', {
            body: message,
            clickUrl: `/deliveries/customer/active/${delivery.id}/`
        });
        this.playSound('success');
    }

    notifyNewMessage(sender, preview) {
        const message = `💬 New message from ${sender}`;
        this.showInAppNotification(message, 'message');
        this.showBrowserNotification('New Message', {
            body: preview,
            clickUrl: '/chat/'
        });
        this.playSound('default');
    }

    notifyDriverAssigned(delivery) {
        const message = `🚴 You have a new delivery from ${delivery.customerName}`;
        this.showInAppNotification(message, 'delivery');
        this.showBrowserNotification('New Delivery', {
            body: message,
            clickUrl: `/deliveries/driver/`
        });
        this.playSound('default');
    }
}

// Initialize notification manager
const notificationManager = new NotificationManager();
window.notificationManager = notificationManager;
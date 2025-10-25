// Map utilities for BridgeDash
class BridgeDashMap {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.map = null;
        this.markers = {};
        this.options = {
            zoom: 13,
            center: [-22.2167, 30.0000], // Beitbridge coordinates
            ...options
        };
    }

    init() {
        if (!this.container) {
            console.error('Map container not found');
            return;
        }

        // Initialize Leaflet map
        this.map = L.map(this.container).setView(this.options.center, this.options.zoom);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);

        return this;
    }

    addMarker(id, latlng, options = {}) {
        const markerOptions = {
            title: options.title || 'Location',
            ...options
        };

        const marker = L.marker(latlng, markerOptions);
        
        if (options.popup) {
            marker.bindPopup(options.popup);
        }

        marker.addTo(this.map);
        this.markers[id] = marker;

        return marker;
    }

    updateMarker(id, latlng) {
        if (this.markers[id]) {
            this.markers[id].setLatLng(latlng);
        }
    }

    removeMarker(id) {
        if (this.markers[id]) {
            this.map.removeLayer(this.markers[id]);
            delete this.markers[id];
        }
    }

    addPickupLocation(latlng, address) {
        return this.addMarker('pickup', latlng, {
            title: 'Pickup Location',
            popup: `🏠 Pickup<br>${address}`,
            icon: L.divIcon({
                className: 'pickup-marker',
                html: '🏠',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            })
        });
    }

    addDeliveryLocation(latlng, address) {
        return this.addMarker('delivery', latlng, {
            title: 'Delivery Location',
            popup: `📍 Delivery<br>${address}`,
            icon: L.divIcon({
                className: 'delivery-marker',
                html: '📍',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            })
        });
    }

    addDriverLocation(latlng, driverName) {
        return this.addMarker('driver', latlng, {
            title: `Driver: ${driverName}`,
            popup: `🚴 ${driverName}`,
            icon: L.divIcon({
                className: 'driver-marker',
                html: '🚴',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            })
        });
    }

    fitToMarkers(padding = 0.1) {
        const group = new L.FeatureGroup(Object.values(this.markers));
        if (Object.keys(this.markers).length > 0) {
            this.map.fitBounds(group.getBounds().pad(padding));
        }
    }

    getCurrentLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    });
                },
                (error) => {
                    reject(error);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
    }

    watchLocation(callback) {
        if (!navigator.geolocation) {
            console.error('Geolocation is not supported');
            return null;
        }

        return navigator.geolocation.watchPosition(
            (position) => {
                const location = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                callback(location);
            },
            (error) => {
                console.error('Geolocation error:', error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    stopWatching(watchId) {
        if (watchId) {
            navigator.geolocation.clearWatch(watchId);
        }
    }
}

// Export for global use
window.BridgeDashMap = BridgeDashMap;
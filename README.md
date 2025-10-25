# 🚲 BridgeDash - Bike Delivery App

Instant bike delivery service for Beitbridge, Zimbabwe. Built with Django, real-time features, and modern web technologies.

## 🌟 Features

- **Real-time Delivery Tracking** - Live GPS tracking of deliveries
- **Instant Chat** - Real-time messaging between customers and drivers
- **Push Notifications** - In-app and browser notifications
- **Admin Dashboard** - Complete management interface
- **Mobile Responsive** - Works on all devices
- **PWA Ready** - Install as mobile app

## 🛠️ Tech Stack

- **Backend**: Django 4.2, Django Channels
- **Database**: PostgreSQL (production), SQLite (development)
- **Real-time**: WebSockets, Redis
- **Frontend**: HTML, CSS, JavaScript, HTMX
- **Maps**: Leaflet.js with OpenStreetMap
- **Deployment**: Railway.app

## 🚀 Quick Start

### Development
```bash
# Clone repository
git clone https://github.com/yourusername/bridgedash.git
cd bridgedash

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
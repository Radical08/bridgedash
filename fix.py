import os
import subprocess
import secrets

def run_command(command, description):
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

def delete_old_files():
    """Delete all old deployment files"""
    files_to_delete = [
        'railway.json',
        'nixpacks.toml', 
        'runtime.txt',
        'Procfile',
        'Dockerfile',
        '.dockerignore',
        'fix_and_deploy.py',
        'final_fix.py'
    ]
    
    print("🗑️  Deleting old deployment files...")
    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Deleted {file}")
        else:
            print(f"ℹ️  {file} not found (already deleted)")

def create_nixpacks_config():
    """Create the correct nixpacks.toml"""
    print("📄 Creating nixpacks.toml...")
    
    content = """[phases.setup]
cmds = [
    "python -m pip install --upgrade pip",
    "pip install -r requirements.txt"
]

[phases.build]
cmds = [
    "python manage.py collectstatic --noinput"
]

[start]
cmd = "python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT bridgedash.asgi:application"
"""
    
    with open('nixpacks.toml', 'w') as f:
        f.write(content)
    print("✅ Created nixpacks.toml")

def create_railway_config():
    """Create minimal railway.json"""
    print("📄 Creating railway.json...")
    
    content = """{
    "$schema": "https://railway.app/railway.schema.json",
    "build": {
        "builder": "NIXPACKS"
    }
}"""
    
    with open('railway.json', 'w') as f:
        f.write(content)
    print("✅ Created railway.json")

def update_requirements():
    """Ensure requirements.txt has all needed packages"""
    print("📦 Updating requirements.txt...")
    
    requirements = """Django==4.2.7
channels==4.0.0
channels-redis==4.1.0
daphne==4.0.0
celery==5.3.4
redis==5.0.1
psycopg2-binary==2.9.7
python-decouple==3.8
whitenoise==6.5.0
django-crispy-forms==2.0
crispy-bootstrap5==0.7
pillow==10.0.1
geopy==2.3.0
requests==2.31.0
gunicorn==21.2.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("✅ Updated requirements.txt")

def create_env_example():
    """Create .env.example for Railway variables"""
    print("🔧 Creating .env.example...")
    
    secret_key = secrets.token_urlsafe(50)
    content = f"""DEBUG=False
SECRET_KEY={secret_key}
ALLOWED_HOSTS=.railway.app,localhost,127.0.0.1
BRIDGEDASH_COMMISSION_RATE=0.15
BRIDGEDASH_BASE_FARE=5.00
BRIDGEDASH_PER_KM_RATE=2.00
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# Railway automatically provides:
# DATABASE_URL=postgresql://...
# REDIS_URL=redis://...
"""
    
    with open('.env.example', 'w') as f:
        f.write(content)
    print("✅ Created .env.example")

def update_django_settings():
    """Add production settings to Django"""
    print("⚙️  Updating Django settings for production...")
    
    production_settings = '''

# Railway Production Settings
import dj_database_url

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }

if 'RAILWAY_STATIC_URL' in os.environ:
    STATIC_URL = os.environ.get('RAILWAY_STATIC_URL')

if 'RAILWAY_ENVIRONMENT' in os.environ:
    DEBUG = False
    ALLOWED_HOSTS = ['.railway.app', 'localhost', '127.0.0.1']
    CSRF_TRUSTED_ORIGINS = ['https://*.railway.app']
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
'''
    
    # Read current settings
    try:
        with open('bridgedash/settings.py', 'r') as f:
            settings_content = f.read()
        
        # Only add if not already there
        if 'Railway Production Settings' not in settings_content:
            with open('bridgedash/settings.py', 'a') as f:
                f.write(production_settings)
            print("✅ Updated bridgedash/settings.py")
        else:
            print("✅ Production settings already exist")
    except Exception as e:
        print(f"⚠️  Could not update settings: {e}")

def push_to_github():
    """Push all changes to GitHub"""
    print("📤 Pushing to GitHub...")
    
    commands = [
        'git add .',
        'git commit -m "FINAL FIX: Correct Railway deployment with nixpacks.toml"',
        'git push origin main'
    ]
    
    for cmd in commands:
        if not run_command(cmd, cmd):
            return False
    
    return True

def main():
    print("🎯 BRIDGEDASH - FINAL DEPLOYMENT FIX")
    print("=" * 50)
    
    # Step 1: Delete all old files
    delete_old_files()
    
    # Step 2: Create new deployment files
    create_nixpacks_config()
    create_railway_config()
    update_requirements()
    create_env_example()
    
    # Step 3: Update Django settings
    update_django_settings()
    
    # Step 4: Push to GitHub
    print("\\n" + "=" * 50)
    print("🚀 DEPLOYING TO RAILWAY")
    print("=" * 50)
    
    if push_to_github():
        print("\\n🎉 SUCCESS! Everything fixed and pushed!")
        print("📋 Railway will automatically deploy with:")
        print("   ✅ Correct pip installation (python -m pip)")
        print("   ✅ Django Channels with Daphne")
        print("   ✅ PostgreSQL database")
        print("   ✅ Redis for real-time features")
        print("   ✅ Production security settings")
        print("\\n🌐 Check deployment at: https://railway.app")
        print("📞 Contact: 0781874006")
    else:
        print("\\n❌ Failed to push to GitHub")

if __name__ == "__main__":
    main()
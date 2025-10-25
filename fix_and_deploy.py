import os
import subprocess
import json
import secrets

def run_command(command, description):
    print(f"Running: {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed: {description} - {e}")
        return False

def main():
    print("Starting BridgeDash deployment fix...")
    
    # Create railway.json
    railway_config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT bridgedash.asgi:application"
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=4)
    print("Created railway.json")
    
    # Create nixpacks.toml
    nixpacks_content = '''[phases.setup]
cmds = [
    "pip install -r requirements.txt"
]

[phases.build]
cmds = [
    "python manage.py collectstatic --noinput"
]

[start]
cmd = "python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT bridgedash.asgi:application"
'''
    
    with open('nixpacks.toml', 'w') as f:
        f.write(nixpacks_content)
    print("Created nixpacks.toml")
    
    # Create runtime.txt
    with open('runtime.txt', 'w') as f:
        f.write("python-3.11.0\n")
    print("Created runtime.txt")
    
    # Update requirements.txt
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
    print("Updated requirements.txt")
    
    # Create .env.example
    secret_key = secrets.token_urlsafe(50)
    env_content = f"""DEBUG=False
SECRET_KEY={secret_key}
ALLOWED_HOSTS=.railway.app,localhost,127.0.0.1
BRIDGEDASH_COMMISSION_RATE=0.15
BRIDGEDASH_BASE_FARE=5.00
BRIDGEDASH_PER_KM_RATE=2.00
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    print("Created .env.example")
    
    # Create simple README
    readme_content = "# BridgeDash - Bike Delivery App\n\nReal-time delivery app for Beitbridge, Zimbabwe.\n\n## Quick Start\n\n1. Clone repo\n2. Install requirements\n3. Run migrations\n4. Start server\n\n## Deployment\n\nDeploy on Railway with PostgreSQL and Redis.\n\nContact: 0781874006"
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("Created README.md")
    
    # Push to GitHub
    print("Pushing to GitHub...")
    commands = [
        'git add .',
        'git commit -m "Fix Railway deployment"',
        'git push origin main'
    ]
    
    for cmd in commands:
        if not run_command(cmd, cmd):
            break
    
    print("Deployment fix completed!")
    print("Visit https://railway.app to check deployment")

if __name__ == "__main__":
    main()
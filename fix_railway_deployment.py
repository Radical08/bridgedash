import os
import subprocess

def create_fix_files():
    """Create corrected Railway deployment files"""
    
    # Create railway.json
    railway_json = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT bridgedash.asgi:application"
        }
    }
    
    import json
    with open('railway.json', 'w') as f:
        json.dump(railway_json, f, indent=4)
    
    # Create nixpacks.toml
    nixpacks_toml = '''[phases.setup]
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
        f.write(nixpacks_toml)
    
    print("✅ Created fixed deployment files")

def push_changes():
    """Push the fixes to GitHub"""
    commands = [
        'git add railway.json nixpacks.toml',
        'git commit -m "🔧 Fix Railway deployment configuration"',
        'git push origin main'
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️  Command failed: {cmd}")
            print(f"Error: {result.stderr}")
        else:
            print(f"✅ {cmd.split()[0]} completed")
    
    print("🎉 Fixes pushed to GitHub! Railway will automatically redeploy.")

if __name__ == "__main__":
    print("🔧 Fixing Railway Deployment Issue...")
    print("=" * 50)
    create_fix_files()
    push_changes()
    print("\n✅ Deployment fix completed!")
    print("📦 Railway will automatically redeploy with the corrected configuration")
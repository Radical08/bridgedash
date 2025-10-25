import subprocess
import os

def run_command(command, description):
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False

print("🔄 Fixing GitHub push issue...")
print("=" * 50)

# Force push solution
commands = [
    ('git add .', 'Adding files'),
    ('git commit -m "🚀 Complete BridgeDash - Real-time Bike Delivery App for Beitbridge"', 'Creating commit'),
    ('git push -u origin main --force', 'Force pushing to GitHub')
]

for cmd, desc in commands:
    if not run_command(cmd, desc):
        break

print("\n🎉 If successful, your code is now on GitHub!")
print("🌐 Check: https://github.com/Radical08/bridgedash")
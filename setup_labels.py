import subprocess
import json

labels = [
    {"name": "area/plugin", "color": "5319e7", "description": "Related to Plugin Ecosystem"},
    {"name": "layer/core", "color": "b60205", "description": "Core OS Plugins"},
    {"name": "layer/bridge", "color": "0e8a16", "description": "Communication Bridges"},
    {"name": "layer/business", "color": "1d76db", "description": "CRM and Business Suite"},
    {"name": "layer/social", "color": "fbca04", "description": "Social OS and Connection"},
    {"name": "layer/creative", "color": "d93f0b", "description": "Creative Studio AI"},
    {"name": "layer/dev", "color": "1d76db", "description": "Developer Tools"},
    {"name": "priority/p0", "color": "b60205", "description": "Critical blocker"},
    {"name": "priority/p1", "color": "d93f0b", "description": "High priority"},
    {"name": "priority/p2", "color": "fbca04", "description": "Medium priority"},
    {"name": "priority/p3", "color": "0052cc", "description": "Low priority"}
]

def create_label(label):
    # check if label exists
    check = subprocess.run(["gh", "label", "list", "--search", label["name"]], capture_output=True, text=True)
    if label["name"] in check.stdout:
        print(f"Skipping {label['name']}, already exists.")
        return

    cmd = [
        "gh", "label", "create", label["name"],
        "--color", label["color"],
        "--description", label["description"],
        "--force"
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Created label: {label['name']}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create label {label['name']}: {e}")

print("🔧 Setting up GitHub Labels...")
for l in labels:
    create_label(l)
print("✨ Label setup complete.")

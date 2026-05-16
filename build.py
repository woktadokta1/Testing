#!/usr/bin/env python3
"""
Anki Add-on Builder
Creates a properly formatted .ankiaddon file compatible with Anki 2.1.50+
"""
import os
import zipfile
import json
import sys

def build_addon():
    addon_name = "heatmap_selector"
    output_file = f"{addon_name}.ankiaddon"
    
    # Files to include in the addon package
    addon_files = [
        "__init__.py",
        "manifest.json",
        "config.json",
        "utils.py",
        "heatmap_widget.py",
        "heatmap_window.py"
    ]
    
    # Check if manifest.json exists and is valid
    if not os.path.exists("manifest.json"):
        print("❌ Error: manifest.json not found!")
        sys.exit(1)
    
    try:
        with open("manifest.json", "r") as f:
            manifest = json.load(f)
            print(f"✓ Manifest loaded: {manifest.get('name', 'Unknown')}")
    except json.JSONDecodeError as e:
        print(f"❌ Error: manifest.json is invalid JSON: {e}")
        sys.exit(1)
    
    # Remove old addon file
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"✓ Removed old {output_file}")
    
    # Create the .ankiaddon file (it's just a zip with a different extension)
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in addon_files:
                if os.path.exists(file):
                    # Files go directly in the addon folder
                    zipf.write(file, arcname=f"{addon_name}/{file}")
                    print(f"✓ Added {file}")
                else:
                    print(f"⚠ Warning: {file} not found, skipping...")
        
        # Verify the zip was created correctly
        if not os.path.exists(output_file):
            print(f"❌ Error: Failed to create {output_file}")
            sys.exit(1)
        
        file_size = os.path.getsize(output_file)
        print(f"\n✅ SUCCESS: Created {output_file} ({file_size} bytes)")
        print("\n📦 Addon Package Ready!")
        print("\nTo install in Anki:")
        print("1. Open Anki")
        print("2. Tools → Add-ons → Install from file")
        print(f"3. Select: {output_file}")
        print("4. Restart Anki")
        print("5. Tools → Show Review Heatmap")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating addon package: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_addon()

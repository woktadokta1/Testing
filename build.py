#!/usr/bin/env python3
import os
import zipfile
import shutil

addon_name = "heatmap_selector"
output_file = f"{addon_name}.ankiaddon"

# Files to include in the addon
files = [
    "__init__.py",
    "manifest.json",
    "config.json",
    "utils.py",
    "heatmap_widget.py",
    "heatmap_window.py"
]

# Remove old addon file if it exists
if os.path.exists(output_file):
    os.remove(output_file)
    print(f"✓ Removed old {output_file}")

# Create the addon zip file
with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in files:
        if os.path.exists(file):
            # Add file to the addon_name folder inside the zip
            zipf.write(file, arcname=f"{addon_name}/{file}")
            print(f"✓ Added {file}")
        else:
            print(f"⚠ Warning: {file} not found")

print(f"\n✅ Created: {output_file}")
print("Ready to import into Anki!")
print("\nInstallation:")
print("1. Open Anki")
print("2. Tools → Add-ons → Install from file")
print(f"3. Select: {output_file}")
print("4. Restart Anki")
print("5. Tools → Show Review Heatmap")

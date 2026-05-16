#!/usr/bin/env python3
import os
import zipfile
import json

addon_name = "heatmap_selector"
output_file = f"{addon_name}.ankiaddon"
files = ["__init__.py", "manifest.json", "config.json", "utils.py", "heatmap_widget.py", "heatmap_window.py"]

if os.path.exists(output_file):
    os.remove(output_file)

with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in files:
        if os.path.exists(file):
            zipf.write(file, f"{addon_name}/{file}")
            print(f"✓ {file}")

print(f"\n✅ Created: {output_file}")
print("Ready to import into Anki!")

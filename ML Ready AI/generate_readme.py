import os

templates_dir = r"d:\Major Projects2025\ML READY AI\ml_ready_ai\templates"
output_file = os.path.join(templates_dir, "README.md")

files = [
    "algorithm.html",
    "cleaning.html",
    "eda.html",
    "feature_engineering.html",
    "final.html",
    "index.html",
    "model.html",
    "result.html",
    "summary.html",
    "upload.html"
]

with open(output_file, "w", encoding="utf-8") as f:
    f.write("# ML Ready AI - Templates Source Code\n\n")
    f.write("This document contains the exact source code for all the HTML template files used in the project.\n\n")
    
    for filename in files:
        filepath = os.path.join(templates_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as html_file:
                content = html_file.read()
                
            f.write(f"## `{filename}`\n")
            f.write("```html\n")
            f.write(content)
            if not content.endswith("\n"):
                f.write("\n")
            f.write("```\n\n")

print(f"Successfully generated {output_file}")
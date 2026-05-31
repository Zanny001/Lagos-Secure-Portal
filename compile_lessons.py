import os
import json
import re

SYLLABUS_BASE_DIR = "academic_syllabus"
OUTPUT_MANIFEST = "lessons_manifest.json"

def parse_markdown_to_html(md_text):
    """
    Converts standard Markdown components into clean HTML elements
    using sequential regex transformation blocks.
    """
    html = md_text
    
    # 1. Strip out Windows style carriage returns
    html = html.replace("\r\n", "\n")
    
    # 2. Parse Blockquotes
    html = re.sub(r'^>\s*(.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    
    # 3. Parse Headings (## and #)
    html = re.sub(r'^##\s*(.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#\s*(.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    
    # 4. Parse Bold Phrases
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # 5. Parse Unordered Lists
    html = re.sub(r'^\*\s*(.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    # Wrap loose consecutive li items in ul blocks
    html = re.sub(r'(<li>.*?</li>)+', r'<ul>\0</ul>', html, flags=re.DOTALL)
    
    # 6. Parse Ordered Lists
    html = re.sub(r'^\d+\.\s*(.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # 7. Convert horizontal rules
    html = html.replace("---", "<hr>")
    
    # 8. Handle basic paragraph splits (consecutive double line breaks)
    paragraphs = html.split("\n\n")
    processed_paragraphs = []
    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue
        # If it's already wrapped in a block element, don't wrap in <p>
        if p_clean.startswith(("<h", "<ul", "<ol", "<block", "<hr")):
            processed_paragraphs.append(p_clean)
        else:
            processed_paragraphs.append(f"<p>{p_clean.replace('\n', '<br>')}</p>")
            
    return "\n".join(processed_paragraphs)

def compile_syllabus_manifest():
    print("\n\033[1m[*] Compiling Markdown Syllabus Templates into HTML Manifest...\033[0m")
    
    if not os.path.exists(SYLLABUS_BASE_DIR):
        print(f"[-] Base directory '{SYLLABUS_BASE_DIR}' not found. Run syllabus_builder.py first.")
        return

    manifest_data = []

    # Walk the directory tree to collect markdown assets
    for root, dirs, files in os.walk(SYLLABUS_BASE_DIR):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                
                # Extract relative details from path tree
                parts = os.path.relpath(file_path, SYLLABUS_BASE_DIR).split(os.sep)
                subject = parts[0] if len(parts) > 0 else "General"
                track = parts[1] if len(parts) > 1 else "Core"
                
                # Derive a human-readable title from the filename
                lesson_title = file.replace("_template.md", "").replace("_", " ").title()
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        md_content = f.read()
                    
                    # Convert raw source text into ready-to-render web markup
                    html_content = parse_markdown_to_html(md_content)
                    
                    manifest_data.append({
                        "title": lesson_title,
                        "subject": subject.capitalize(),
                        "track": track.replace("_", " ").upper(),
                        "content_html": html_content
                    })
                    print(f"    -> Parsed & Staged: {subject}/{track}/{file}")
                except Exception as e:
                    print(f"    [-] Failed parsing execution on {file_path}: {e}")

    # Export compiled output structure to a local JSON file
    try:
        with open(OUTPUT_MANIFEST, "w", encoding="utf-8") as out_f:
            json.dump(manifest_data, out_f, indent=2)
        print(f"\n\033[92m\033[1m[SUCCESS] Unified manifest compiled to '{OUTPUT_MANIFEST}' ({len(manifest_data)} nodes integrated).\033[0m\n")
    except Exception as e:
        print(f"[-] Critical error writing manifest output: {e}")

if __name__ == "__main__":
    compile_syllabus_manifest()


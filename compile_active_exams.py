import json
import os
from generate_pdf import create_assessment_pdf

def load_manifest(manifest_path):
    """Loads the compiled curriculum database nodes."""
    if not os.path.exists(manifest_path):
        print(f"[-] Manifest not found at: {manifest_path}")
        return None
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[-] Failed to read manifest JSON: {e}")
        return None

def generate_student_assessments():
    manifest_file = "/home/userland/Lagos-Secure-Portal/lessons_manifest.json"
    manifest_data = load_manifest(manifest_file)
    
    # Standardize data format depending on how JSON is wrapped
    students_list = []
    
    if isinstance(manifest_data, list):
        # Format is a direct list: [...]
        students_list = manifest_data
    elif isinstance(manifest_data, dict):
        # Format is a wrapped dictionary: {"students": [...]}
        students_list = manifest_data.get("students", [])
    else:
        # Fallback automated configuration if manifest file is unseeded or unreadable
        print("[*] Manifest structure unseeded. Initializing programmatic compilation fallback matrix...")
        students_list = [
            {
                "name": "Kehinde",
                "level": "WAEC Secondary",
                "current_topic": "Nuclear Physics",
                "questions": [
                    "Define radioactive half-life and explain how environmental factors affect the decay constant of a sample.",
                    "Calculate the energy released (in Joules) during a fission reaction where a mass defect of 0.025 kg is recorded. (Speed of light, c = 3 x 10^8 m/s)",
                    "Sketch a labeled diagram showing the deflection of alpha, beta, and gamma radiations passing through a uniform magnetic field."
                ]
            },
            {
                "name": "Tooki",
                "level": "IGCSE Extended",
                "current_topic": "Space Physics",
                "questions": [
                    "Define orbital speed and derive its relationship with gravitational constant (G) and orbital radius (r).",
                    "Explain why a geostationary satellite must be positioned directly above the Earth's equator and state its orbital period.",
                    "Describe the lifecycle stages of a stable star having a mass significantly greater than the mass of our Sun."
                ]
            }
        ]

    # Iterate through tracked student records and compile target PDFs
    for student in students_list:
        # Ensure student is a dictionary object before processing
        if not isinstance(student, dict):
            continue
            
        name = student.get("name", student.get("student_name", "Student"))
        level = student.get("level", student.get("syllabus_type", "Assessment"))
        topic = student.get("current_topic", student.get("topic", "General Revision"))
        questions = student.get("questions", [])
        
        # If no explicit questions array exists in the node, provide fallbacks
        if not questions:
            questions = [
                f"Define the primary foundational principles governing {topic}.",
                f"Solve or explain a multi-step scenario problem demonstrating practical application of {topic} formulas.",
                f"Discuss the experimental observation limits and structural importance of {topic} inside modern frameworks."
            ]
        
        pdf_filename = f"/home/userland/Lagos-Secure-Portal/{name.lower()}_{topic.lower().replace(' ', '_')}_exam.pdf"
        title = f"{level} Assessment - {topic}"
        instructions = f"Hello {name}, please answer all questions thoroughly in the workspaces provided below. Show all algebraic formula steps."
        
        print(f"[*] Processing pipeline for {name} ({level})...")
        create_assessment_pdf(pdf_filename, title, instructions, questions)

if __name__ == "__main__":
    generate_student_assessments()

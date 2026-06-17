import os

# Define the architectural tree for your instructional tracks
SYLLABUS_TREE = {
    "physics": {
        "igcse_extended": [
            "nuclear_physics_fission_fusion",
            "space_physics_orbital_mechanics",
            "thermal_physics_properties"
        ],
        "waec_senior": [
            "ss1_first_term_mechanics",
            "current_electricity_circuits",
            "atomic_energy_levels"
        ]
    },
    "mathematics": {
        "igcse_extended": [
            "probability_independent_events",
            "year_8_cartesian_coordinates",
            "quadratic_functions_graphs"
        ],
        "waec_senior": [
            "matrices_and_determinants",
            "trigonometry_elevations",
            "statistics_grouped_data"
        ]
    }
}

def build_syllabus_framework():
    print("\n\033[1m[*] Launching Academic Syllabus Infrastructure Builder...\033[0m")
    base_dir = "academic_syllabus"
    
    count = 0
    for subject, tracks in SYLLABUS_TREE.items():
        for track_name, modules in tracks.items():
            # Construct localized system folder paths
            folder_path = os.path.join(base_dir, subject, track_name)
            os.makedirs(folder_path, exist_ok=True)
            
            for module in modules:
                file_name = f"{module}_template.md"
                full_file_path = os.path.join(folder_path, file_name)
                
                # Check if the file already exists to preserve existing documentation
                if not os.path.exists(full_file_path):
                    with open(full_file_path, "w") as f:
                        f.write(generate_markdown_template(subject, track_name, module))
                    count += 1
                    print(f"    -> Compiled: {folder_path}/{file_name}")
                    
    print(f"\n\033[92m\033[1m[SUCCESS] Structural directory active. Created {count} new curriculum templates.\033[0m\n")

def generate_markdown_template(subject, track, module):
    """Generates rich instructional boilerplate layouts tailored to specific syllabus requirements."""
    title = module.replace("_", " ").title()
    return f"""# {title}
## Curriculum Reference Node: {subject.upper()} | {track.replace('_', ' ').upper()}

---

### I. Instructional Objectives & Target Standards
* **Objective A:** Core concept mastery and structural variable definition.
* **Objective B:** Mathematical proof execution and system equation derivation.
* **Objective C:** Assessment question evaluation and error analysis tracking.

### II. Core Lesson Documentation Notes
> Write clear, high-standard instructional summaries, definitions, and real-world system applications here.

### III. Core Curricular Formula Registry
Insert target equations using clean system text notation:
* **Equation 1:** [Insert Primary Variable Relations Here]
* **Equation 2:** [Insert Secondary Condition Limits Here]

### IV. Sample High-Fidelity Assessment Bank
1. **[Question Type: Conceptual]** Formulate a comprehensive question matching target examination metrics.
   * *Mark Scheme / Solution Pathway:* Provide explicit step-by-step scoring rules.
   
2. **[Question Type: Calculation]** Formulate a rigorous variable problem requiring precision extraction.
   * *Mark Scheme / Solution Pathway:* Detail systemic computation checkpoints.

---
*Template Node Generated via Zannie Academic Engine Suite.*
"""

if __name__ == "__main__":
    build_syllabus_framework()


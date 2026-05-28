import random
import sys

# Expanded Master Question Bank including both Physics & Mathematics domains
QUESTION_BANK = [
    # --- PHYSICS DOMAINS ---
    {
        "id": 101, "topic": "Dimensions",
        "question": "Which of the following represents the correct dimensional formula for linear momentum?",
        "options": {"A": "MLT⁻¹", "B": "MLT⁻²", "C": "ML²T⁻²", "D": "M²LT⁻¹"}, "correct": "A"
    },
    {
        "id": 102, "topic": "Dimensions",
        "question": "The identity of a dimensionless quantity implies it:",
        "options": {"A": "Has no numerical value", "B": "Is a ratio of two identical physical quantities", "C": "Cannot be measured using instruments", "D": "Exposes zero error limits"}, "correct": "B"
    },
    {
        "id": 201, "topic": "Mechanics",
        "question": "A vehicle accelerating uniformly from rest achieves a velocity of 20 m/s in exactly 5 seconds. Calculate its acceleration.",
        "options": {"A": "4 m/s²", "B": "100 m/s²", "C": "0.25 m/s²", "D": "15 m/s²"}, "correct": "A"
    },
    {
        "id": 203, "topic": "Mechanics",
        "question": "A continuous horizontal force of 15N pushes a mass through 4 meters. Determine the mechanical work done.",
        "options": {"A": "60 J", "B": "3.75 J", "C": "11 J", "D": "19 J"}, "correct": "A"
    },
    {
        "id": 301, "topic": "Circular Motion",
        "question": "The uniform force directed towards the central rotation axis during a circular velocity sweep is called:",
        "options": {"A": "Centrifugal force", "B": "Centripetal force", "C": "Linear inertia", "D": "Tangential torque"}, "correct": "B"
    },
    
    # --- MATHEMATICS DOMAINS ---
    {
        "id": 401, "topic": "Algebra",
        "question": "Solve for 'x' in the linear equation: 3(x - 4) = 2x + 5.",
        "options": {"A": "x = 7", "B": "x = 17", "C": "x = -7", "D": "x = 9"}, "correct": "B"
    },
    {
        "id": 402, "topic": "Algebra",
        "question": "Factorize the quadratic expression completely: x² - 5x + 6.",
        "options": {"A": "(x - 2)(x - 3)", "B": "(x + 2)(x + 3)", "C": "(x - 1)(x - 6)", " matrimonial": "(x + 1)(x - 6)"}, "correct": "A"
    },
    {
        "id": 501, "topic": "Geometry",
        "question": "Calculate the total surface area of a solid cylinder with a base radius of 7cm and a height of 10cm. (Take π = 22/7)",
        "options": {"A": "748 cm²", "B": "440 cm²", "C": "1540 cm²", "D": "308 cm²"}, "correct": "A"
    },
    {
        "id": 502, "topic": "Geometry",
        "question": "The interior angles of a regular polygon sum up to 1080°. Identify the name of this polygon.",
        "options": {"A": "Hexagon", "B": "Heptagon", "C": "Octagon", "D": "Decagon"}, "correct": "C"
    },
    {
        "id": 601, "topic": "Sequences",
        "question": "Determine the 15th term of the Arithmetic Progression (A.P.): 5, 9, 13, 17, ...",
        "options": {"A": "61", "B": "65", "C": "56", "D": "71"}, "correct": "A"
    },
    {
        "id": 602, "topic": "Sequences",
        "question": "Find the sum of the first 20 terms of the arithmetic series whose first term is 3 and common difference is 4.",
        "options": {"A": "820", "B": "780", "C": "850", "D": "910"}, "correct": "A"
    }
]

def compile_practice_sheet(target_topic=None, limit=5, randomize=True):
    """Filters, organizes, and structures clean text question sheets for immediate student delivery."""
    if target_topic:
        pool = [q for q in QUESTION_BANK if q["topic"].lower() == target_topic.lower()]
    else:
        pool = list(QUESTION_BANK)

    if not pool:
        return f"[ERROR] No questions discovered matching the target domain: '{target_topic}'\n"

    if randomize:
        random.shuffle(pool)

    selected_questions = pool[:limit]
    topic_header = target_topic if target_topic else "Comprehensive General Review (Physics & Math)"
    
    output = []
    output.append("============================================================")
    output.append(f"📝 ZANNIE ACADEMIC PORTAL — PRACTICE ASSIGNMENT SHEET")
    output.append(f"Focus Domain: {topic_header.upper()}")
    output.append(f"Total Items : {len(selected_questions)} Multiple-Choice Questions")
    output.append("============================================================\n")

    answer_key_sheet = []

    for index, item in enumerate(selected_questions, 1):
        output.append(f"Question {index} [{item['topic']}]")
        output.append(f"{item['question']}")
        for letter, choice_text in sorted(item['options'].items()):
            output.append(f"  [{letter}] {choice_text}")
        output.append("") 
        
        answer_key_sheet.append(f"Q{index}: {item['correct']}")

    output.append("------------------------------------------------------------")
    output.append("🔑 TUTOR EVALUATION ANSWER MATRIX (DO NOT SEND TO STUDENT)")
    output.append("------------------------------------------------------------")
    output.append(", ".join(answer_key_sheet))
    output.append("============================================================")

    return "\n".join(output)

if __name__ == "__main__":
    topic_filter = sys.argv[1] if len(sys.argv) > 1 else None
    count_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    result_sheet = compile_practice_sheet(target_topic=topic_filter, limit=count_limit)
    print(result_sheet)

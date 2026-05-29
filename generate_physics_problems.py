import os
import random
import time

def generate_random_problems(count=3):
    """
    Generates a structured list of randomized kinematics problems 
    with detailed answer keys for tutorial sheets.
    """
    timestamp = time.strftime('%Y-%m-%d')
    current_dir = os.path.dirname(os.path.abspath('%s' % __file__))
    
    question_paper = f"""==================================================================
              ZANNIE ACADEMIC PREPARATION TUTORIALS
                  DYNAMIC KINEMATICS PROBLEM SET
==================================================================
Curriculum Standards: IGCSE / WAEC / OCR GCSE Physics
Date Generated: {timestamp}
Instructor: Elebute Hassan Oluwafemi

INSTRUCTIONS: 
- Show all formulas used clearly.
- State your answers to 2 decimal places with correct SI units.

------------------------------------------------------------------
"""
    answer_key = f"""==================================================================
                  OFFICIAL SOLUTION METHODOLOGY KEY
==================================================================
"""
    
    # Problem 1 Configuration: Car accelerating from rest (Find distance)
    # v² = u² + 2as  -> s = v² / 2a (since u=0)
    for i in range(1, count + 1):
        car_brand = random.choice(["vehicle", "race car", "motorcycle", "electric sedan"])
        u = 0
        a = round(random.uniform(2.0, 5.5), 1)
        v = random.choice([20, 24, 30, 35, 40])
        
        # Calculate distance
        s = (v**2) / (2 * a)
        
        question_paper += f"""
QUESTION {i} [4 Marks]
A {car_brand} starts from rest and accelerates uniformly down a straight track 
at a rate of {a} m/s². Calculate the total displacement of the {car_brand} 
by the time its speedometer registers exactly {v} m/s.
------------------------------------------------------------------
"""
        answer_key += f"""
SOLUTION FOR QUESTION {i}:
1. Identify Knowns: u = 0 m/s, a = {a} m/s², v = {v} m/s
2. Formula Selection: v² = u² + 2as
3. Algebraic Rearrangement: s = (v² - u²) / 2a
4. Calculation:
   s = ({v}² - 0²) / (2 * {a})
   s = {v**2} / {2 * a}
   s = {s:.2f} meters
[M1 for formula, M1 for substitution, A1 for calculation, A1 for units 'm']
------------------------------------------------------------------
"""

    # Combine document blocks
    full_output = question_paper + "\n\n" + answer_key
    file_path = os.path.join(current_dir, "kinematics_practice_problems.txt")
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_output)
        print(f"[COMPILER SUCCESS] Instantiated randomized problem sheet: kinematics_practice_problems.txt")
        return True
    except Exception as e:
        print(f"[COMPILER ERROR] Failed to write problem sheet: {e}")
        return False

if __name__ == "__main__":
    generate_random_problems()


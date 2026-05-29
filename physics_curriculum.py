import os
import math

def compile_physics_module():
    """
    Generates a structured Physics assessment workbook covering Linear Kinematics
    and Vector Dynamics, complete with an automated step-by-step marking key.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Automated calculation parameters for Problem 2 (Resolving Forces)
    # A box pulled on a frictionless surface by a force at an angle
    force_n = 50.0
    angle_deg = 30.0
    mass_kg = 10.0
    
    # Calculate components programmatically
    angle_rad = math.radians(angle_deg)
    horizontal_force = force_n * math.cos(angle_rad)
    acceleration = horizontal_force / mass_kg
    
    workbook_content = f"""==================================================================
                 ZANY ACADEMIC PREPARATION TUTORIALS
               PHYSICS CURRICULUM SERIES: MECHANICS I
==================================================================
Curriculum Standards: IGCSE Physics (0625) / WAEC Higher Tier
Focus Area: Equations of Motion & Vector Dynamics
Document Reference: PHYS/MEC/01

[SECTION A: LINEAR KINEMATICS - 5 MARKS]
1. A test vehicle starts from rest at a local checkpoint and accelerates 
   uniformly along a straight road at a rate of 3.5 m/s² for a duration 
   of 8.0 seconds. 
   
   Calculate:
   (a) The final velocity attained by the vehicle at the 8.0s mark. [2 Marks]
   (b) The total linear distance covered during this acceleration phase. [3 Marks]

[SECTION B: VECTOR DYNAMICS & FORCES - 5 MARKS]
2. A cargo crate of mass {mass_kg} kg rests on a smooth, frictionless horizontal 
   surface. A haulage rope pulls the crate with a constant force of {force_n} N 
   directed at an angle of {angle_deg}° above the horizontal plane.
   
   Calculate:
   (a) The horizontal component of the pulling force acting on the crate. [2 Marks]
   (b) The resulting horizontal acceleration of the crate across the surface. [3 Marks]

==================================================================
              OFFICIAL MARKING SCHEME & SOLUTION KEY
==================================================================

SOLUTION TO QUESTION 1:
(a) Find final velocity (v) using: v = u + at
    Given: initial velocity (u) = 0 m/s, acceleration (a) = 3.5 m/s², time (t) = 8.0 s
    v = 0 + (3.5 * 8.0)
    v = 28.0 m/s                                         [Formula: C1, Answer: A1]

(b) Find distance (s) using: s = ut + 0.5at²  (or v² = u² + 2as)
    s = (0 * 8.0) + 0.5 * 3.5 * (8.0)²
    s = 0 + 0.5 * 3.5 * 64
    s = 112.0 meters                                     [Formula: C1, Answer: A2]


SOLUTION TO QUESTION 2:
(a) Horizontal Force Component (Fx) = F * cos(θ)
    Fx = {force_n} * cos({angle_deg}°)
    Fx = {force_n} * {math.cos(angle_rad):.4f}
    Fx = {horizontal_force:.2f} N                         [Formula: C1, Answer: A1]

(b) Acceleration (a) using Newton's Second Law: Fx = m * a
    a = Fx / m
    a = {horizontal_force:.2f} / {mass_kg}
    a = {acceleration:.2f} m/s²                           [Formula: C1, Answer: A2]

------------------------------------------------------------------
                     END OF EXAM BLUEPRINT
==================================================================
"""

    file_path = os.path.join(current_dir, "physics_mechanics_workbook.txt")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(workbook_content)
        
    print("[COMPILER SUCCESS] Physics workbook generated: physics_mechanics_workbook.txt")

if __name__ == "__main__":
    compile_physics_module()


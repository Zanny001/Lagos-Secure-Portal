import csv
import os
from flask import Blueprint, render_template 

scholarships_bp = Blueprint('scholarships', __name__) 

# Lock the base pathway to ensure correct file handling in cloud runtimes
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

@scholarships_bp.route('/scholarships')
def view_scholarships():
    leads = []
    csv_path = os.path.join(BASE_DIR, "global_assistantships_leads.csv") 

    if os.path.exists(csv_path):
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                leads.append(row) 

    return render_template("scholarships.html", leads=leads)

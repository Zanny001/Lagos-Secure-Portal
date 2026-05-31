import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_assessment_pdf(filename, assessment_title, instructions, questions):
    """
    Programmatically generates a clean, standardized academic assessment PDF.
    Optimized for mobile compilation environments.
    """
    # 1. Setup Document Layout
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    # 2. Setup Typography Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Centered
        spaceAfter=10
    )
    
    meta_style = ParagraphStyle(
        'MetaText',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )
    
    instruction_style = ParagraphStyle(
        'Instructions',
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=15
    )
    
    question_style = ParagraphStyle(
        'Question',
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=8
    )

    story = []

    # 3. Build Academic Exam Header Block
    story.append(Paragraph(assessment_title.upper(), title_style))
    
    # Student Metadata Table Simulator
    meta_header = """
    <b>STUDENT NAME:</b> ____________________________________ &nbsp;&nbsp;&nbsp;&nbsp; <b>DATE:</b> _______________<br/>
    <b>DURATION:</b> 1 Hour 30 Minutes &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>SCORE:</b> / ______
    """
    story.append(Paragraph(meta_header, meta_style))
    story.append(Spacer(1, 10))
    
    # Decorative Rule separator
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceAfter=15))
    
    # Instructions Block
    story.append(Paragraph(f"<b>Instructions:</b> {instructions}", instruction_style))
    
    # 4. Populate Question Blocks with Work Spaces
    for i, q_text in enumerate(questions, 1):
        question_data = []
        # Question Statement
        question_data.append(Paragraph(f"<b>Q{i}.</b> {q_text}", question_style))
        
        # Add designated blank lines for calculations/writing space
        question_data.append(Spacer(1, 12))
        for _ in range(4):
            question_data.append(Paragraph("<font color='#cbd5e1'>__________________________________________________________________________________________</font>", question_style))
        question_data.append(Spacer(1, 15))
        
        # Keep Together ensures an individual question and its lines don't get split across pages
        story.append(KeepTogether(question_data))

    # 5. Compile and Write PDF out to disk
    doc.build(story)
    print(f"[+] Successfully compiled structural asset: {filename}")

if __name__ == "__main__":
    # Sample Test Rig Mocking Physics Layout Structure
    sample_title = "Physics Session Assessment: Nuclear Reactions"
    sample_instructions = "Answer all questions clearly in the spaces provided. Show all working metrics where calculations are required."
    
    sample_questions = [
        "Distinguish clearly between the processes of nuclear fission and nuclear fusion, giving one practical example or occurrence of each.",
        "A radioactive isotope sample decays from an initial activity count of 1200 Bq down to 150 Bq over a timeframe spanning exactly 24 days. Determine the definitive half-life of this isotope.",
        "State and briefly explain Einstein's mass-energy equivalence principle equation, detailing what each variable element represents structurally."
    ]
    
    output_path = "/home/userland/Lagos-Secure-Portal/nuclear_assessment_sample.pdf"
    create_assessment_pdf(output_path, sample_title, sample_instructions, sample_questions)

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def build_pdf(markdown_path, pdf_path):
    print(f"[*] Starting compilation of {markdown_path} into {pdf_path}...")
    
    # 1. Establish the document template
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    story = []
    
    # 2. Initialize and customize the stylesheet parameters
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=6
    )
    
    h2_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=14,
        spaceAfter=10
    )
    
    h3_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )
    
    formula_style = ParagraphStyle(
        'FormulaText',
        parent=styles['BodyText'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#0284c7'),
        leftIndent=20,
        spaceBefore=6,
        spaceAfter=6
    )

    # 3. Read raw lesson lines and compile into the flowable layout tree
    if not os.path.exists(markdown_path):
        print(f"[-] Source file error: {markdown_path} does not exist.")
        sys.exit(1)
        
    with open(markdown_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_table = False
    table_data = []

    for line in lines:
        stripped = line.strip()
        
        # Handle structural Markdown tables
        if stripped.startswith('|'):
            in_table = True
            # Skip separator row definitions
            if '---' in stripped:
                continue
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            # Convert cells to Paragraph objects to enable auto-wrap inside tables
            p_cells = [Paragraph(cell, body_style) for cell in cells]
            table_data.append(p_cells)
            continue
        elif in_table and not stripped.startswith('|'):
            # Close out table rendering block when table lines end
            in_table = False
            if table_data:
                t = Table(table_data, colWidths=[120, 200, 210])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ]))
                story.append(t)
                story.append(Spacer(1, 10))
                table_data = []

        if not stripped:
            continue
            
        # Parse Document Architecture Headers
        if stripped.startswith('# '):
            story.append(Paragraph(stripped[2:], title_style))
            story.append(Spacer(1, 4))
        elif stripped.startswith('## '):
            story.append(Paragraph(stripped[3:], h2_style))
        elif stripped.startswith('### '):
            story.append(Paragraph(stripped[4:], h3_style))
        # Parse Equation Blocks
        elif stripped.startswith('$$') or stripped.endswith('$$'):
            clean_formula = stripped.replace('$$', '')
            story.append(Paragraph(clean_formula, formula_style))
        # Parse Bullet Configurations
        elif stripped.startswith('* '):
            clean_bullet = f"&bull; {stripped[2:]}"
            story.append(Paragraph(clean_bullet, body_style))
        # Parse Standard Block Paragraphs
        elif not stripped.startswith('---'):
            story.append(Paragraph(stripped, body_style))

    # 4. Generate the final PDF
    doc.build(story)
    print(f"[SUCCESS] PDF asset generated successfully at: {pdf_path}")

if __name__ == "__main__":
    src = "/home/userland/Lagos-Secure-Portal/space_physics_igcse.md"
    dest = "/home/userland/Lagos-Secure-Portal/space_physics_assessment.pdf"
    build_pdf(src, dest)

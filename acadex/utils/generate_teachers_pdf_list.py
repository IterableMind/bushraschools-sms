from fpdf import FPDF
from flask import make_response
import io
from ..models import SchoolBranch

class TeacherListPDF(FPDF):
    def footer(self): 
        self.set_font('Arial', 'I', 9)
        self.set_text_color(128)
        self.set_y(-20)
        self.cell(0, 6, '2025 © Bushra. All rights reserved.(System Generated List)',
                   align='C', ln=True
        )
        self.cell(0,5, f'Page {self.page_no()}', align='C')

def generate_teacher_list_pdf(teachers, branch_name, address):
    pdf = TeacherListPDF('L')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Fonts and Styles
    pdf.set_font("Arial", "B", 16)

    # Title
    title = branch_name if branch_name != 'All' else 'BUSHRA SCHOOLS TEACHERS [ALL]'
    pdf.cell(0, 10, title.upper(), ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 7, address, ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 7, 'Teachers List', ln=True, align='C')
    pdf.ln(2)

    # Horizontal line (centered)
    pdf.set_line_width(1)
    line_width = pdf.w - 20  # 10mm margin on both sides
    start_x = (pdf.w - line_width) / 2
    end_x = start_x + line_width
    pdf.line(start_x, pdf.get_y(), end_x, pdf.get_y())
    pdf.ln(5)

    pdf.set_line_width(0.3)

    # Table Headers
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(10, 8, 'S/N', border=1, align='C')
    pdf.cell(60, 8, 'Teacher Name', 1, 0, 'C')
    pdf.cell(20, 8, 'Gender', 1, 0, 'C')
    pdf.cell(30, 8, 'ID Number', border=1, align='C')
    pdf.cell(32, 8, 'Phone Number', border=1, align='C')
    pdf.cell(26, 8, 'TSC No', border=1, align='C')
    if branch_name == 'All':
        pdf.cell(40, 8, 'Branch', border=1, align='C')
        pdf.cell(30, 8, 'Email', border=1, align='C')
    else:
        pdf.cell(60, 8, 'Email', border=1, align='C')
    pdf.cell(30, 8, 'Salary', border=1, align='C', ln=True)

    # Table Rows
    pdf.set_font("Arial", '', 11) 
    branches = {b.id: b.name for b in SchoolBranch.query.all()}
    for index, teacher in enumerate(teachers, start=1):
        b_name = branches.get(teacher.branch_id, "---")
        pdf.cell(10, 8, str(index), 1, 0, align='C')
        pdf.cell(60, 8, teacher.teacher_name, 1, 0)
        pdf.cell(20, 8, teacher.gender.capitalize(), 1, 0)
        pdf.cell(30, 8, teacher.id_no, border=1)
        pdf.cell(32, 8, str(teacher.phone_no), border=1)
        pdf.cell(26, 8, f'{teacher.tsc_no if teacher.tsc_no else "---"}', border=1)
        if branch_name == 'All':
            pdf.cell(40, 8, f'{b_name if b_name else "---"}', border=1)
            pdf.cell(30, 8, f'{teacher.email[:8] + "..." if teacher.email else "---"}', border=1)
        else:
            pdf.cell(60, 8, f'{teacher.email if teacher.email else "---"}', border=1)
        pdf.cell(30, 8, "Ksh." + "{:,}".format(teacher.salary), border=1, ln=True)

    # Stream response
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    response = make_response(pdf_output.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename="{title.lower().replace(" ", "_")}_list.pdf"'
    return response

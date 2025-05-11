from fpdf import FPDF
import random
from datetime import datetime


class StudentListPDF(FPDF):
    def __init__(self, list_type, branch_name, addr, grade, stream):
        super().__init__()
        self.branch_name = branch_name
        self.addr = addr
        self.grade = grade
        self.stream = stream
        self.list_type = list_type
        self.cell_widths = [] 

    def header(self):
        "Set headers for every page"
        if self.branch_name.upper().endswith('SCHOOL'):
            self.branch_name =  self.branch_name[:-6].rstrip()
        headers = [
            (f'{self.branch_name.upper()} SCHOOL', 17, 8),
            (self.addr, 15, 5),
            (
                f'{self.grade}  {self.stream} Students {"Mark List" if self.list_type == "Mark list" else "Class List"}',
                15,
                6
            )
        ]

        for text, font_size, cell_height in headers:
            self.center_header(text, font_size, cell_hight=cell_height)
        
        self.ln(2)
        
        # Draw horizontal line
        self.set_line_width(1)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)


    def center_header(self, string, font_size, cell_hight=10):
        self.set_font('helvetica', 'B', font_size)
        s_width = self.get_string_width(string) + 6
        self.set_x((self.w - s_width) / 2)
        self.cell(s_width, cell_hight, string, align='C', ln=True)

    def set_table_headers(self, headers):
        self.set_font('helvetica', 'B', 11)
        if self.list_type == 'Mark list':
            header_w = 10
            self.cell(10, 7, '#', border=1, align='C')
            self.cell(54, 7, 'Name', border=1, align='C')
            for header in headers:
                header_w = self.get_string_width(header[:4]) + 6
                self.cell_widths.append(header_w)
                self.cell(header_w, 7, header[:4], border=1, align='C')
            self.ln(7)
        else:
            self.cell(10, 7, '#', border=1, align='C')
            self.cell(18, 7, 'Adm no', border=1, align='C')
            self.cell(60, 7, 'Name', border=1, align='C')
            self.cell(0, 7, '', border=1)
            self.ln(7)


    def display_data(self, students):
        self.set_font('helvetica', '', 10)
        if self.list_type == 'Mark list':
            for index, student in enumerate(students, start=1):
                self.cell(10, 7, str(index), border=1, align='C')
                self.cell(54, 7, student.fullname, border=1)
                for c in self.cell_widths:
                    self.cell(c, 7, border=1)
                self.ln(7)
        else:
            for index, student in enumerate(students, start=1):
                self.cell(10, 7, str(index), border=1, align='C')
                self.cell(18, 7, student.adm_no, border=1)
                self.cell(60, 7, student.fullname, border=1)
                self.cell(0, 7, '', border=1)
                self.ln(7)


    def footer(self):
        "set footer for every page"
        self.set_font('times', '', 10)
        self.set_y(-15)
        # self.cell(0, 8, f'Generated on {str(datetime.now().strftime("%A, %B %d, %Y"))}')
        self.cell(0, 8, f'Generated on {str(datetime.now().strftime("%A, %B %d, %Y"))} © Bushra. All rights reserved', align='C')
        # Page number
        page_text = f'Page {self.page_no()} / {{nb}}'
        self.cell(0, 10, page_text, align='C')
    


def generate_marklist(students, headers, list_type, config=None, output=None):
    """
    Generate a student marklist PDF.

    Args:
        students (list): List of student objects.
        headers (list): List of header strings.
        config (dict, optional): Configuration with 'branch_name', 'addr', and 'grade'.
        output (io.BytesIO, optional): Output buffer to write the PDF to. If None, saves to a file.

    Returns:
        None
    """
    if config is None:
        config = {}

    pdf = StudentListPDF(
        list_type = list_type,
        branch_name=config.get('branch_name', 'Unknown Branch'),
        stream=config.get('stream'),
        addr=config.get('addr', ''),
        grade=config.get('grade', '')
    )
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_table_headers(headers)
    pdf.display_data(students)

    if output:
        pdf.output(output)  # Write to the provided output buffer
    else:
        filename = f"{config.get('branch_name', 'students')}_{random.randint(2, 100)}.pdf"
        pdf.output(filename)

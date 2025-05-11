from fpdf import FPDF

class LetterHead(FPDF):
    def header(self, school_name, address, grade):
        "Set the heading of the document"
        self.set_font("Helvetica", "B", 17)
        self.set_text_color(0, 128, 128)
        self.cell(0, 8, school_name, ln=True, align="C")
        self.set_font("Helvetica", "B", 15)
        self.cell(0, 5, address, ln=True, align="C")
        self.cell(0, 5, grade, ln=True, align="C")
         
        self.ln(3)   

        # Draw horizontal line (X1, Y1, X2, Y2)
        self.set_draw_color(0, 128, 128)  
        self.set_line_width(0.5) 
        self.line(10, self.get_y(), 200, self.get_y())   
        self.ln(4)  # Space after line
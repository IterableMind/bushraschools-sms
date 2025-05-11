from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from pathlib import Path

downloads_path = str(Path.home() / "Downloads")

headers = ['LEARNING AREA', 'SCORE', 'PER. LEVEL', 'GRADE', 'REMARKS', 'INTIALS']
key_headers = ['EXCEED EXPECTATION', 'MEET EXPECTATION', 'APPROACH EXPECTATION', 'BELOW EXPECTATION']


def set_comment(marks):
  if marks is None:
    return '--'  # Return a string when marks is missing

  marks = int(marks)  # Convert to integer

  if marks >= 76:  # Marks greater than or equal to 77
      return 'Excellent'
  elif marks >= 60:  # Marks between 61 and 76 (inclusive)
      return 'Very Good'
  elif marks >= 40:  # Marks between 41 and 60 (inclusive)
      return 'Average'
  else:  # Marks 40 and below
      return 'Can Improve'

def set_grade(marks):
  if marks is None:
    return '--'  # Return a string when marks is missing

  marks = int(marks)  # Convert to integer

  if marks >= 76:  # Marks greater than or equal to 77
      return '4'
  elif marks >= 60:  # Marks between 61 and 76 (inclusive)
      return '3'
  elif marks >= 40:  # Marks between 41 and 60 (inclusive)
      return '2'
  else:  # Marks 40 and below
      return '1'

def set_perf_level(marks):
  if marks is None:
    return '--'  # Return a string when marks is missing

  marks = int(marks)  # Convert to integer

  if marks >= 76:  # Marks greater than or equal to 77
      return 'EE'
  elif marks >= 60:  # Marks between 61 and 76 (inclusive)
      return 'ME'
  elif marks >= 40:  # Marks between 41 and 60 (inclusive)
      return 'AE'
  else:  # Marks 40 and below
      return 'BE'



class ReportCard(FPDF):
  def __init__(self, exam, rank, tot_students):
    super().__init__()
    self.exam = exam
    self.rank = rank
    self.tot_students = tot_students

  def header(self):
    "Set the heading of the report card"
    self.set_font("Helvetica", "B", 17)
    self.set_text_color(0, 128, 128)
    self.cell(0, 8, "BUSHRA ACADEMY", ln=True, align="C")
    self.set_font("Helvetica", "B", 15)
    self.cell(0, 5, "LEARNER'S ASSESSMENT REPORT", ln=True, align="C")
    self.cell(0, 5, f"Exam: {self.exam.name}", ln=True, align="C")
    self.cell(0, 5, f"Term: {self.exam.term}({self.exam.year})", ln=True, align="C")
    self.ln(3)   

    # Draw horizontal line (X1, Y1, X2, Y2)
    self.set_draw_color(0, 128, 128)  
    self.set_line_width(0.5) 
    self.line(10, self.get_y(), 200, self.get_y())   
    self.ln(4)  # Space after line

  def student_details(self, report):
    # Set font for both the label and cell
    self.set_font("Times", "B", 12)
    # Save the current position
    x = self.get_x()
    y = self.get_y()

    # Draw the bordered cell without any text inside
    self.cell(80, 10, '', border=1) 
    self.set_fill_color(255, 255, 255)  
    self.set_xy(x + 2, y - self.font_size/2)
    self.cell(40, self.font_size, "STUDENT'S NAME", border=0, fill=True)
      
    
    # Reset the cursor back to the beginning of the bordered cell
    self.set_xy(x, y)
    self.set_font("Times", "", 12)
    self.cell(80, 10, report['student'].fullname.upper())  
    


    self.set_font("Times", "B", 12)
    # Save the current position
    x = self.get_x()
    y = self.get_y() 

    self.set_x(x + 5)
    # Draw the bordered cell without any text inside
    self.cell(30, 10, '', border=1) 
    self.set_fill_color(255, 255, 255)  
    self.set_xy(x + 7, y - self.font_size/2)
    self.cell(18, self.font_size, "GRADE", border=0, fill=True)
        
    # Reset the cursor back to the beginning of the bordered cell
    self.set_xy(x + 5, y)
    self.set_font("Times", "", 12)
    if report['student'].stream:
      self.cell(5, 10, f"{report['student'].grade[-1]} ({report['student'].stream})")
    else:
      self.cell(5, 10, report['student'].grade[-1])

    if self.rank:
      # rank if necessary
      self.set_x(self.get_x() + 30)
      self.set_font("Times", "B", 12)
      self.cell(5, 10, f"Position: {report['position']} out of {self.tot_students}")

    self.ln(5)
    # Draw table for display marks
  def draw_marks_table(self, th, students):
    self.ln(10)
    # Set column widths (adjust as needed)
    col_widths = [46, 19, 30, 26, 36, 26]
    # Set header background color and font
    self.set_fill_color(200, 220, 255)
    self.set_text_color(0)
    self.set_draw_color(0, 0, 0)
    self.set_line_width(0.3)
    self.set_font("Arial", "B", 12) 

    for i, col_name in enumerate(th):
      self.cell(col_widths[i], 10, col_name, border=1, align="C", fill=True)
    self.ln()

    # Reset font for data rows
    self.set_font("Arial", "", 11)

    # Loop through the subjects dictionary and add rows for each subject
    for subject, details in students.items():
        # Subject name in column 1
        self.cell(col_widths[0], 9, subject, border=1)
        # Score in column 2
        self.cell(col_widths[1], 9, str(details['score']), border=1, align="C")
        # Initial in column 3
        
        self.cell(col_widths[2], 9, set_perf_level(details['score']), border=1, align="C")
        # For the columns we're ignoring, we simply create empty cells
        self.cell(col_widths[3], 9, set_grade(details['score']), border=1, align="C")
        self.cell(col_widths[4], 9, set_comment(details['score']), border=1, align="C")
        self.cell(col_widths[5], 9, details['teacher'], border=1, align="C")
        self.ln()
        
     
    
  def draw_key_table(self, th):
    self.ln(10)
    # self.set_font("Arial", "B", 11)
    # self.cell(0, 10, 'CBC Rubrics Key', align='C') 
    col_widths = [45, 45, 48, 45]
    # Set header background color and font
    self.set_fill_color(248, 248, 248)
    self.set_text_color(0)
    self.set_draw_color(0, 0, 0)
    self.set_line_width(0.3)
    self.set_font("Arial", "B", 10) 


    for i, col_name in enumerate(th):
      self.cell(col_widths[i], 10, col_name, border=1, align="C", fill=True)
    self.ln()

    # Reset font for data rows
    self.set_font("Arial", "", 11)
    for i, data in enumerate(['4 = 76-100', '3 = 60-75', '2 = 40-59', '1 = 0-39']):
       self.cell(col_widths[i], 9, data, border=1)
    self.ln()
    for i, data in enumerate(['EE', 'ME', 'AE', 'BE']):
       self.cell(col_widths[i], 9, data, border=1)

  def add_graph(self, data, dates):
    self.ln(10)   
    subjects = list(data['marks'].keys())  # Extract subjects
    scores = [subject_data['score'] for subject_data in data['marks'].values()]
    
    # Plot the graph
    plt.figure(figsize=(10, 4))
    plt.bar(subjects, scores, color=['blue', 'green', 'red', 'purple', 'pink', 'orange', 'black'])
    plt.xlabel("Subjects", fontsize=14)
    plt.ylabel("Scores", fontsize=14)
    plt.title("Subject Scores", fontsize=14)
    plt.ylim(0, 100)  # Assuming max score is 100
    
    # Rotate subject labels for better visibility
    plt.xticks(rotation=45, ha="right", fontsize=14)  # Rotate and increase font size
    plt.yticks(fontsize=14)  # Increase y-axis tick size
    
    # Save as an image
    graph_path = "graph.png"
    plt.savefig(graph_path, bbox_inches='tight', dpi=100)
    plt.close()
    
    # Insert the image into the PDF
    self.image(graph_path, x=10, y=self.get_y() + 5, w=100)  # Adjust position & width

    x = self.get_x()
    y = self.get_y()
    self.set_xy(x=x+100, y=y+10)
    self.cell(0, 10, f"Closing Date: {dates['closing_date']}" , border=1)
    self.ln()

    x = self.get_x()
    y = self.get_y()
    self.set_xy(x=x+100, y=y+5)
    self.cell(0, 10, f"Opening Date: {dates['opening_date']}" , border=1)

  def comment_section(self):
    self.ln(40)
    self.set_font("Times", "B", 12)

    # Save the current position
    x = self.get_x()
    y = self.get_y()

    # Headteacher's Comment cell
    self.cell(80, 20, '', border=1) 
    self.set_fill_color(255, 255, 255)  
    self.set_xy(x + 2, y - self.font_size/2)
    self.cell(68, self.font_size, "Headteacher's Comment and Stamp", border=0, fill=True)

    # Move to the right for the next cell
    self.set_xy(x + 85, y)  # Shift right

    # Classteacher's Comment cell
    self.cell(80, 20, '', border=1) 
    self.set_fill_color(255, 255, 255)  
    self.set_xy(x + 87, y - self.font_size/2)  # Adjust to match the floating label
    self.cell(48, self.font_size, "Classteacher's Comment", border=0, fill=True)


      

def generate_report_cards_pdf(exam, report_cards, rank, dates, grade):
  pdf = ReportCard(exam, rank, len(report_cards))
  # Generate Report
  for report in report_cards:
    pdf.add_page()
    pdf.student_details(report)
    pdf.draw_marks_table(headers, report['marks'])
    pdf.draw_key_table(key_headers)
    pdf.add_graph(report, dates)
    pdf.comment_section()
  

  file_path = os.path.join(downloads_path, f"{grade}_{exam}_report_forms.pdf")

  # Save PDF in the Downloads folder
  pdf.output(file_path)
  print(f"PDF saved at: {file_path}")
    







 
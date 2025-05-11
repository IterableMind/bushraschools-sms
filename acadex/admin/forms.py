from flask_wtf import FlaskForm
from wtforms.validators import ValidationError
from ..models import Teacher, Student, Staff, SchoolBranch, Grade
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms import (
    StringField, 
    TextAreaField, 
    SubmitField, 
    IntegerField, 
    RadioField, 
    SelectField,
    FileField,
    PasswordField,
    EmailField,
    FileField,
    DateField,
    BooleanField,
    HiddenField
)
from wtforms.validators import (
    DataRequired, 
    Length, 
    Email, 
    NumberRange, 
    Optional, 
    Regexp,
    EqualTo,
    InputRequired
)

class SearchStudent(FlaskForm):
    search_input = StringField(
        validators=[
            DataRequired(message="Please enter ADM No, Name, or UPI No!")
        ]
    )
    search_by = RadioField(
        "Search Student",
        choices=[
            ("Enter adm no", "Adm no"),
            ("Enter name", "Name"),
            ("Enter UPI no", "UPI no")
        ],
        default="Enter adm no"
    )
    search = SubmitField("Search")


class SchoolInfoForm(FlaskForm):
    name = StringField(
        'School Name', 
        validators=[
            DataRequired(
                message='Please provide school name.'
            ), 
            Length(min=3, max=100)
        ],
        render_kw={"placeholder": "Enter school name"}
    )
    address = TextAreaField(
        'Address',
        validators=[
            DataRequired(
                message='Please provide school address.'
            ), 
            Length(max=250)
        ],
        render_kw={"placeholder": "Enter school address"}
    )
    registration_number = StringField(
        'Registration Number (Optional)',
        validators=[
            Length(min=5, max=50), 
            Optional()
        ],
        render_kw={"placeholder": "Enter registration number"}
    )
    contact_email = StringField(
        'Contact Email (Optional)',
        validators=[
            Optional(),
            Email(), 
            Length(max=100)
        ],
        render_kw={"placeholder": "Enter email address"}
    )
    contact_phone = StringField(
        'Contact Phone',
        validators=[
            DataRequired(
                message='Please provide phone number.'
            ), 
            Length(min=10, max=15)
        ],
        render_kw={"placeholder": "Enter contact phone number"}
    )
    submit = SubmitField('Submit')

 
class TeacherForm(FlaskForm):
    teacher_name = StringField(
        'Teacher Name', 
        validators=[
            DataRequired(
                message='You must provide the teacher\'s name.'
            ), 
            Length(min=2, max=100, 
                message="Name must be between 2 and 100 characters."
            )
        ],
        render_kw={"placeholder": "Enter the teacher's full name"}
    )
    tsc_no = IntegerField(
        'TSC No',
        validators=[
            Optional()
        ], 
        render_kw={"placeholder": "Enter the TSC number"}
    )
    id_no = IntegerField(
        'ID No', 
        validators=[DataRequired(
            message="The ID No of the Teacher must be provided.")
        ],
        render_kw={"placeholder": "Enter the ID number"}
    )
    phone_no = StringField(
        'Phone No', 
        validators=[
            DataRequired(message="Phone number is required."),
            Regexp(r'^\d{10}$', message="Enter a valid 10-digit phone number.")
        ],
        render_kw={"placeholder": "Enter a 10-digit phone number"}
    )
    email = StringField(
        'Email', 
        validators=[
            Optional(), 
            Email(message="Enter a valid email address.")
        ],
        render_kw={"placeholder": "Enter email address"}
    )
    gender = SelectField(
        'Gender', 
        validators=[
            DataRequired(
                message='You must select the teacher\'s gender.'
            )
        ],
        choices=[
            ('', 'Select Gender'), 
            ('male', 'Male'),
            ('female', 'Female')
        ], 
        default=''
    )
    branch = SelectField(
        'Branch',
        validators=[
            DataRequired(
                message="You must select the teacher's branch."
            )
        ],
        choices=[]
    )
    salary = IntegerField(
        'Gross Salary',
        validators=[
            DataRequired(
                message="Enter Gross Salary of the teacher."
            )
        ]
    )
    submit = SubmitField('Add Teacher')

    # Custom validators
    def validate_tsc_no(self, field):
        if field.data:
            teacher = Teacher.query.filter_by(tsc_no=field.data).first()
            if teacher:
                raise ValidationError('TSC No already exists.')

    def validate_id_no(self, field):
        teacher = Teacher.query.filter_by(id_no=field.data).first()
        if teacher:
            raise ValidationError('ID No already exists.')

    def validate_phone_no(self, field):
        teacher = Teacher.query.filter_by(phone_no=field.data).first()
        if teacher:
            raise ValidationError('Phone number already exists.')

    def validate_email(self, field):
        if field.data:
            teacher = Teacher.query.filter_by(email=field.data).first()
            if teacher:
                raise ValidationError('Email address already exists.')
    
    def validate_teacher_name(self, field):
        if field.data:
            teacher = Teacher.query.filter_by(teacher_name=field.data).first()
            if teacher:
                raise ValidationError('There is a teacher with that username already.')
            


class UpdateForm(FlaskForm):
    current_password = PasswordField(
        "Current Password",
        render_kw={"placeholder": "Enter current password"}
    )
    new_password = PasswordField(
        'New Password',
        validators=[
            Length(min=4, max=20),
            Optional()
        ],
        render_kw={"placeholder": "Enter new password"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            EqualTo('new_password', message='Passwords must match.')
        ],
        render_kw={"placeholder": "Confirm password"}
    )
    phone_no = StringField(
        'Phone No', 
        validators=[
            Optional(),
            Regexp(r'^\d{10}$', message="Enter a valid 10-digit phone number.")
        ],
        render_kw={"placeholder": "Enter a 10-digit phone number"}
    )
    profile_picture = FileField(
        'Profile Picture',
        validators=[
            Optional(),
        ]
    )
    submit = SubmitField('Update')


class StreamForm(FlaskForm):
    name = StringField(
                'Stream Name', 
                validators=[
                    DataRequired(message='You must enter the name of the stream to add.')
                ]
            )


class GradeForm(FlaskForm):
    grade_name = SelectField(
        'Grade',
        choices=[('', 'Select Grade')] + [(f'Grade {i}', f'Grade {i}') for i in range(1, 10)] +
        [(f'Form {i}', f'Form {i}') for i in range(2, 5)],
        validators=[DataRequired(message='Please select a grade.')]
    )
    branch = SelectField(
        'Branch',
        validators=[
            DataRequired(message='Please select a branch with muiltaple streams.')
        ],
        choices=[]
    )
    stream1 = StringField(
        'Stream 1',
         render_kw={"placeholder": "Enter stream 1 name"}
        )
    stream2 = StringField(
        'Stream 2',
         render_kw={"placeholder": "Enter stream 2 name"}
        )
    stream3 = StringField(
        'Stream 3',
         render_kw={"placeholder": "Enter stream 3 name"}
        )
    
    submit = SubmitField('Add')

    def validate_grade_name(self, field):
        if field.data == '':
            raise ValidationError('Please select a valid grade.')


class StudentRegistrationForm(FlaskForm):
    fullname = StringField(
        "Fullname", 
        validators=[
            DataRequired(message='You must enter the fullname of the student.'),
            Length(
                min=8, 
                max=50,
                message='Student name must be between 8-50 characters long.'
            )
        ],
    render_kw={"placeholder": "Enter student's name"}
    )

    grade = SelectField(
        'Grade',
        choices=[('', 'Select Grade')] + [(f'Grade {i}', f'Grade {i}') for i in range(1, 10)] +
        [(f'Form {i}', f'Form {i}') for i in range(2, 5)],
        validators=[InputRequired(message='Please select a grade.')]
    )

    photo = FileField(
        "Photo", 
        validators=[Optional()]
    )

    adm_no = StringField(
        "Admission Number", 
        validators=[
            DataRequired(
                message='You must enter the student\'s adm no.'
            )
        ],
        render_kw={"placeholder": "Enter Adm no"}
    )

    gender = SelectField(
        "Gender", choices=[
         ("", "Select Gender"),   ("Male", "Male"), ("Female", "Female")
        ], 
        validators=[
            DataRequired(message='You must select student\'s gender')
        ]
    )

    stream = StringField(
        "Stream", 
        validators=[Optional()]
    )

    branch = SelectField(
        "Select Branch", 
        validators=[DataRequired(message="You must select a branch!")],
        choices=[]
    )

    parent_name = StringField(
        "Parent/Guardian Name", 
        validators=[
            DataRequired(
                message='Please provide fullname of the parent/guardian.'
            )
        ],
        render_kw={"placeholder": "Parent/Guardian's name"}
    )

    contact_phone = StringField(
        "Contact Information", 
        validators=[
            DataRequired(
                message='Phone number of the parent/guardian must be provided.'
            )
        ],
        render_kw={"placeholder": "07********"}
    )

    health_info = TextAreaField(
        "Health Information", 
        validators=[Optional()],
        render_kw={"placeholder": "Information about any chronical illiness"}
    )
    submit = SubmitField("Save Data")

    def validate_adm_no(self, field):
        student = Student.query.filter_by(adm_no=field.data).first()
        if student:
            raise ValidationError(f'A student with adm no {field.data} already exist!')


class SubjectForm(FlaskForm):
    subject = StringField(
        'Subject',
        validators=[
            DataRequired(message='Please enter a subject to add.')
        ],
        render_kw={"placeholder": "Enter Subject/Learning Area"}
    )

    sub_short_form = StringField(
        'Short form',
        validators=[
            DataRequired(message="Please enter the subject's short form.")
        ],
        render_kw={"placeholder": "Subject short form"}
    )
    grade_1 = BooleanField('Grade 1', description='Grade 1')
    grade_2 = BooleanField('Grade 2', description='Grade 2')
    grade_3 = BooleanField('Grade 3', description='Grade 3')
    grade_4 = BooleanField('Grade 4', description='Grade 4')
    grade_5 = BooleanField('Grade 5', description='Grade 5')
    grade_6 = BooleanField('Grade 6', description='Grade 6')
    grade_7 = BooleanField('Grade 7', description='Grade 7')
    grade_8 = BooleanField('Grade 8', description='Grade 8')
    grade_9 = BooleanField('Grade 9', description='Grade 9')
    form_2 = BooleanField('Form 2', description='Form 2')
    form_3 = BooleanField('Form 3', description='Form 3')
    form_4 = BooleanField('Form 4', description='Form 4')
    all_classes = BooleanField('All classes', description='All classes')


    add = SubmitField("Add Subject")

    def validate(self, extra_validators=None):
        rv = super().validate(extra_validators=extra_validators)
        if not rv:
            return False

        # Check if at least one checkbox is selected
        checkbox_fields = [field for name, field in self._fields.items() if field.type == 'BooleanField']
        if not any(field.data for field in checkbox_fields):
            self.all_classes.errors.append('Please select at least one class/form.')
            return False

        return True



class ExamForm(FlaskForm):
    exam_name = StringField(
        'Exam Name',
        validators=[DataRequired(message="Please enter the exam name.")],
        render_kw={"placeholder": "Enter exam name"}
    )

    term = SelectField(
        'Term',
        choices=[
            ('', 'Select Term'),
            ('1', 'Term 1'),
            ('2', 'Term 2'),
            ('3', 'Term 3')
        ],
        validators=[DataRequired(message="Please select a term.")]
    )

    year = IntegerField(
        'Year',
        validators=[
            DataRequired(message="Please enter the exam year."),
            NumberRange(min=2000, max=2100, message="Enter a valid year.")
        ],
        render_kw={"placeholder": "Enter Year"}
    )

    exam_type = SelectField(
        'Exam Type',
        choices=[
            ('', 'Select Exam Type'),
            ('opening', 'Opening'),
            ('midterm', 'Midterm'),
            ('endterm', 'End Term'),
            ('mocks', 'Mock Exam'),
            ('assessment', 'Assessment')
        ],
        validators=[DataRequired(message="Please select an exam type.")]
    )

    exam_date = DateField(
        "Exam Date",
        validators=[DataRequired(message="Please select the exam date.")],
        format="%Y-%m-%d"
    )

    submit = SubmitField("Add Exam")

class BranchForm(FlaskForm):
    name = StringField(
        'Branch Name',
        validators=[
           DataRequired(message="You must provide the name of the branch to add!") 
        ],
        render_kw={"placeholder": "Example Branch"}
    )
    manager = StringField(
        'Branch Manager',
        validators=[DataRequired(message="Enter Branch manager.")]
    )
    branch_level = SelectField(
        'Branch Level', 
        choices=[
            ('', 'Select Level'),
            ('Primary', 'Primary'),
            ('High School', 'High School'),
            ('Combined', 'Combined')
        ],
        validators=[DataRequired(message="Please select school level.")]
    )
    branch_head = StringField(
        'Headteacher/Principal', 
        validators=[DataRequired(message="Provide headteacher/principal's name.")]
    )
    branch_id = StringField('branch_id')

class StaffForm(FlaskForm):
    fullname = StringField('Full Name', validators=[
        DataRequired(message='Enter the staff\'s fullname.'), 
        Length(max=100)
        ]
    )
    branch = SelectField('Branch', validators=[
        DataRequired(message='You must select the branch name.')
        ], 
        choices=[]
    )   
    designation = StringField('Designation', validators=[
        DataRequired(message='Please enter the designation of the staff.'), 
        Length(max=50)
        ]
    ) 
    phone_number = StringField('Phone Number', validators=[
        DataRequired(message='You must provide phone number.'),
        Regexp(r'^(07|01)\d{8}$', message='Enter a valid phone number.')
    ])
    
    submit = SubmitField('Submit')

    def validate_phone_number(self, field):
        if field.data:
            staff = Staff.query.filter_by(phone_number=field.data).first()
            if staff:
                raise ValidationError('There is a staff with this phone number already.')

    def validate_fullname(self, field):
        if field.data:
            staff = Staff.query.filter_by(fullname=field.data).first()
            if staff:
                raise ValidationError('There is a staff with that name already.')    

class StudentListForm(FlaskForm):
    branch = SelectField(
        'Branch',
        validators=(
            [DataRequired(message='You must select a branch to continue.')]
         ),
        choices=[]
    )
    grade = SelectField (
        'Grade',
        validators=(
            [DataRequired(message='You must select a grade to continue.')]
         ),
        choices=[('', 'Select Grade')] + [(f'Grade {i}', f'Grade {i}') for i in range(1, 10)] + \
        [(f'Form {i}', f'Form {i}') for i in range(2, 5)]
    )

    stream = StringField(
        'Streams',
         validators=(
            [DataRequired(message='You didn\'t select a stream for the selected grade/form.')]
         )
    )
    
    list_type = SelectField(
        'List Type',
        validators=(
            [DataRequired(message='Please select the list type.')]
         ),
        choices=[
            ('', 'Select list type'),
            ('Class list', 'Class list'),
            ('Mark list', 'Mark list')
        ]
    )

  

# Helper function for branches
def branch_choices():
    return SchoolBranch.query.all()

def grade_choices():
    return Grade.query.all()

class AssignTeacherRoleForm(FlaskForm):
    role = SelectField(
        'Teacher Role',
        choices=[
            ('', 'Select Role'),
            ('teacher', 'Teacher'),
            ('principal', 'Principal'), 
            ('deputy principal', 'Deputy Principal'),
            ('headteacher', 'Headteacher'),
            ('deputy headteacher', 'Deputy Headteacher'),
            ('classteacher', 'Class Teacher'),
            ('senior teacher', 'Senior Teacher'),
            ('system admin', 'System Admin'),
        ],
        # default='teacher',
        validators=[DataRequired()]
    )

    is_center_manager = BooleanField('Assign as Center Manager?')

    center_branch = QuerySelectField(
        'Center Manager Branch',
        query_factory=branch_choices,
        allow_blank=True,
        get_label='name'
    )

    grade = SelectField(
        'Select Grade/Form to assign classteacher Responsibility',
        choices = [('', 'Select Grade')] + [(f'Grade {i}', f'Grade {i}') for i in range(1, 10)] + \
        [(f'Form {i}', f'Form {i}') for i in range(2, 5)]
    )

    submit = SubmitField('Assign Role')

    def validate_center_branch(form, field):
        if form.is_center_manager.data and not field.data:
            raise ValidationError('Please select a center manager branch.')
    
    def validate_grade(form, field):
        if form.role.data == 'classteacher' and not field.data:
            raise ValidationError('Please select a Grade/Form.')
        

# Afande Denno
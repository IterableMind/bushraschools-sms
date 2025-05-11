import traceback
from flask import render_template, url_for, flash, redirect, current_app, jsonify, request
from flask import send_file
import io
from . import admin_bp
from .forms import * 
from ..models import db, SchoolInfo, Teacher, User, Grade, Stream, Student, Subject, Role, SchoolBranch, Staff
from .. models import TeacherSubjectAssignment, Exam, ExamMarks, GradeStreamBranch
from ..utils.utils import generate_username
from ..utils.generate_students_lists import generate_marklist
from ..utils.generate_teachers_pdf_list import generate_teacher_list_pdf
from ..utils.generate_pdf import generate_report_cards_pdf
from ..utils.image_processor import preprocess_image as img_editor 
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_, and_, func, distinct
from werkzeug.exceptions import InternalServerError
from flask_login import login_required, current_user, logout_user



ACTIVE = 'link--active'
HORIZONTAL_ACTIVE = 'sub--link--active'
            

@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = SearchStudent()
    totals = {
        'staff_total': 0,
        'teacher_total': 0,
        'branch_total': 0,
        'student_total': 0
    }
    branch_data = []

    try:
        branches = SchoolBranch.query.all()
        totals = {
            'staff_total': Staff.query.count(),
            'teacher_total': Teacher.query.count(),
            'branch_total': len(branches),
            'student_total': Student.query.count()
        }

        for branch in branches:
            student_count = Student.query.filter_by(branch_id=branch.id).count()
            all_students = Student.query.filter_by(branch_id=branch.id).all()
            male_students = Student.query.filter_by(branch_id=branch.id, gender='Male').count()
            female_students = Student.query.filter_by(branch_id=branch.id, gender='Female').count()
            # assigned_grades = Grades
            teacher_count = Teacher.query.filter_by(branch_id=branch.id).count()
            staff_count = Staff.query.filter_by(branch_id=branch.id).count()

            # Example: get all grades with at least one student in a specific branch
            branch_grades = (
                    db.session.query(distinct(Student.grade))
                    .filter(Student.branch_id == branch.id)
                    .all()
                )
            # Flatten the result because query returns list of tuples
            branch_grades = [g[0] for g in branch_grades]
               
            def format_grades(grades_list):
                form_grades = []
                grade_grades = []
                
                for g in grades_list:
                    if g.startswith('Form'):
                        form_grades.append(g)
                    elif g.startswith('Grade'):
                        grade_grades.append(g)

                # Sort them numerically descending
                form_grades.sort(key=lambda x: int(x.split()[1]), reverse=False)
                grade_grades.sort(key=lambda x: int(x.split()[1]), reverse=False)

                # Combine the two lists
                ordered = grade_grades +  form_grades
                return ordered
            
            # Aggregate students by grade
            grade_distribution = {}
            for student in all_students:
                grade = student.grade
                if grade not in grade_distribution:
                    grade_distribution[grade] = 0
                grade_distribution[grade] += 1

            branch_data.append({
                "id": branch.id,
                "name": branch.name,
                "manager": branch.branch_manager,
                "head": branch.branch_head,
                "level": branch.branch_level,
                "student_count": student_count,
                "teacher_count": teacher_count,
                "staff_count": staff_count,
                "male_students": male_students,
                "female_students": female_students,
                "all_students": all_students,
                "branch_grades": format_grades(branch_grades),
                "grade_distribution": grade_distribution  # Add grade distribution here
            })


    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Error: {e}\nTraceback: {traceback.format_exc()}')
        flash('Sorry, an error was encountered when querying the database! Please try again later.', 'danger')

    return render_template(
        'dashboard.html',
        form=form,
        totals=totals,
        d_active=ACTIVE,
        branches=branch_data,
        title='Admin'
    )


"""
Handle school information update.
"""
@admin_bp.route('/update_sch_info', methods = ['GET', 'POST'])
@login_required
def update_sch_info():
    form = SchoolInfoForm()
    if form.validate_on_submit():
      try: 
        sch = SchoolInfo(
            name = form.name.data.upper(),
            address = form.address.data,
            registration_number = form.registration_number.data or None,
            contact_email = form.contact_email.data or None,
            contact_phone = form.contact_phone.data
        )

        db.session.add(sch)
        db.session.commit()

        prev_info = SchoolInfo.query.first() 

        if prev_info and prev_info.id != sch.id:   
            db.session.delete(prev_info)
            db.session.commit()

        flash('School information updated successfully!', 'success')
        return redirect(
            url_for('admin_bp.update_sch_info')
        )
      
      except Exception as e:
          db.session.rollback()
          flash('An unexpected error occurred. Please try again later.', 'error')
          current_app.logger.error(f'Error: {e}\nTraceback: {traceback.format_exc()}')

    return render_template(
        'update_sch_info.html', 
        form = form,
        d_active = ACTIVE, 
        title = 'Update School Information'
    )


@admin_bp.route('/view-teachers')
@login_required
def view_teachers():
    branches = SchoolBranch.query.all()
    try: 
        all_teachers = Teacher.query.all()[::-1]
        if not all_teachers:
            flash('No records of teachers are present!', 'info')
    except SQLAlchemyError as e: 
        current_app.logger.error(f"Database query error: {e}")
        flash(
            'Oops, something went wrong on our side! Please try again later.',
            'danger'
        )
        all_teachers = []  

    return render_template(
        'manage_teachers/view_teachers.html',
        t_active = ACTIVE,
        title = 'View Teachers',
        teachers = all_teachers,
        branches = branches
    ) 


@admin_bp.route('/add-teacher', methods = ['GET', 'POST'])
@login_required
def add_teacher():
    form = TeacherForm()
    branches = [(branch.name, branch.name) for branch in SchoolBranch.query.all()]
    branches.insert(0, ("", "Select Branch"))  
    form.branch.choices = branches 

    if form.validate_on_submit():
        selected_branch = SchoolBranch.query.filter_by(name=form.branch.data).first()
        try: 
            new_teacher = Teacher(
                teacher_name = form.teacher_name.data.strip(),
                tsc_no = form.tsc_no.data,
                id_no = form.id_no.data,
                phone_no = form.phone_no.data,
                branch = selected_branch,
                salary = form.salary.data,
                email = form.email.data.strip() if form.email.data else None,
                gender = form.gender.data
            )
            db.session.add(new_teacher)
            db.session.flush()  
             
            username = generate_username(new_teacher.teacher_name)  
            default_password = str(new_teacher.id_no)  
            
            new_user = User(
                teacher_id = new_teacher.id,
                username = username,
                is_password_updated = False  
            )
 
            new_user.set_password(default_password) # Hash pwd.
            db.session.add(new_user)
            db.session.commit()
             
            flash(
                f"""Teacher '{new_teacher.teacher_name}' 
                was added successfully! Username: {username}""", 
                'success'
            )
            return redirect(
                url_for('admin_bp.add_teacher')
            )
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            flash(
               'An error occurred while adding the teacher. Please try again.', 
               'danger'
            )
            # raise InternalServerError(f"Error: {str(e)}")   

    return render_template(
        'manage_teachers/add_teacher.html',
        t_active=ACTIVE,
        form=form,
        title='Add Teacher'
    )


@admin_bp.route('/assign_teacher_roles', methods=['GET', 'POST'])
@login_required
def assign_teacher_roles():
    form = TeacherForm() 
    form.branch.choices = [(branch.name, branch.name) for branch in SchoolBranch.query.all()]

    page = request.args.get('page', 1, type=int)
    per_page = 7  
    teachers_paginated = Teacher.query.order_by(Teacher.id.desc()).paginate(page=page, per_page=per_page)

    try:
        subjects = Subject.query.all()
    except:
        subjects = []

    return render_template(
        'manage_teachers/teachers_roles.html',
        t_active=ACTIVE,
        subjects=subjects,
        form=form,
        teachers_paginated=teachers_paginated
    )


@admin_bp.route('/update_profile', methods = ['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateForm()
    if form.validate_on_submit(): 
        if form.current_password.data.strip():
            if not current_user.check_password(form.current_password.data):
                flash('Incorrect current password!', 'danger')
                # Re-render the update template.
                return render_template(
                    'manage_teachers/update_profile.html', 
                    t_active = ACTIVE, 
                    form = form, 
                    title = 'Update Profile'
                )
            
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
                flash('Password updated successfully!', 'info')
                db.session.commit()

        # update phone number.
        if form.phone_no.data:
            try:
                current_user.teacher.phone_no = form.phone_no.data
                db.session.commit()
                flash('Phone number updated successfully!', 'info')
            except IntegrityError as e:
                db.session.rollback()
                flash(
                    f'The phone number "{form.phone_no.data}" is already in use.', 
                    'danger'
                )
                current_app.logger.error(f'EXISTING PHONE NUMBER: {str(e)}')
                return render_template(
                    'manage_teachers/update_profile.html', 
                    t_active = ACTIVE, 
                    form = form, 
                    title = 'Update Profile'
                )    
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(
                    'Something went wrong! You phone number was not updated. Try again.',
                    'danger'
                )
                current_app.logger.error( InternalServerError(f"Error: {str(e)}"))

        # upload profile picture
        uploaded_img = form.profile_picture.data
        if uploaded_img:
            try:
                current_user.teacher.passport_filename = img_editor(uploaded_img)
                db.session.commit()
                flash('Profile picture uploaded successfully!', 'info')
            except ValueError:
                flash('Please upload a file of type JPG, JPEG, PNG, or GIF.', 'danger')
                return render_template(
                    'manage_teachers/update_profile.html', 
                    t_active = ACTIVE, 
                    form = form, 
                    title = 'Update Profile'
                )
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"CANNOT UPLOAD IMAGE: Unexpected error: {str(e)}")
                flash(
                    'Sorry, we cannot upload your picture right now. Please try again later.', 'danger'
                )
                return render_template(
                    'manage_teachers/update_profile.html', 
                    t_active = ACTIVE, 
                    form = form, 
                    title = 'Update Profile'
                )

    return render_template(
        'manage_teachers/update_profile.html',
        t_active = ACTIVE,
        form = form, 
        title = 'Update Profile'
    )


@admin_bp.route('/update_teacher_role/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def update_teacher_role(teacher_id):
    """
     Update the roles assigned to the teacher. A teacher can have
     more than one role in addition of being a teacher as the basic role.
    """
    branch_name = ''

    try:
        teacher = Teacher.query.filter_by(id=teacher_id).first()
        if not teacher:
            flash('Teacher not found.', 'danger')
            return redirect(url_for('admin_bp.assign_teacher_roles'))
        branch = SchoolBranch.query.filter_by(id=teacher.branch_id).first()
        if branch:
            branch_name = branch.name
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Error {e}, \nTraceback: {traceback.format_exc()}')
        flash('Oops! Something went wrong in our side. Please try again.', 'warning')
    except Exception as e:
        current_app.logger.error(f'{e} \n TRACEBACK: {traceback.format_exc()}')
        flash('Unexpected error occurred.', 'danger')

    form = AssignTeacherRoleForm()
    if form.validate_on_submit(): 
        try:
            role = form.role.data
            center_branch = form.center_branch.data 
            is_center_manager = form.is_center_manager.data
            stream = request.form.get('stream')
            
            grade = Grade.query.filter_by(grade_name=form.grade.data).first()
            # Validate stream entered.
            if branch_name and grade and stream:
                valid_streams = GradeStreamBranch.query.filter_by(
                    grade_id=grade.id,
                    branch_id=branch.id
                ).all()

                if stream not in [s.stream_name for s in valid_streams]:
                    flash('Invalid stream name!', 'danger')
                    return redirect(url_for('admin_bp.assign_teacher_roles'))

            previous_assigned_roles = Role.query.filter_by(
                teacher_id=teacher.id
            ).first()

            if previous_assigned_roles: 
                # Update teacher roles
                if center_branch:
                    previous_assigned_roles.center_branch = center_branch.name
                if form.grade.data:
                    previous_assigned_roles.grade = grade.grade_name
                if stream:
                    previous_assigned_roles.stream = stream
                if role:
                    previous_assigned_roles.role = role
                
            else:
                teacher_roles = Role(
                    teacher_id=teacher.id,
                    role= role if role else 'teacher'
                )
                
                if is_center_manager and center_branch:
                    teacher_roles.center_branch = center_branch.name
                if grade:
                    teacher_roles.grade = grade.grade_name
                if stream:
                    teacher_roles.stream = stream
                db.session.add(teacher_roles)
            
            try:
                db.session.commit()
                # Update database data.
                flash(f'Teacher roles upadted successfully for teacher {teacher.teacher_name}.',
                'info'
                ) 
                return redirect(url_for('admin_bp.assign_teacher_roles'))
            except SQLAlchemyError as e:
                db.session.rollback()
                current_app.logger.error(f'Error: {e} \nTRACEBACK: {traceback.format_exc()}')
                flash('Unexpected error occured! System support has been notified.', 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Error: {e} \nTRACEBACK: {traceback.format_exc()}')
            flash('Unexpected error occured! System support has been notified.', 'danger')
        

    form.grade.data = ''
    previous_assigned_roles = Role.query.filter_by(
        teacher_id=teacher.id).first()
    
    return render_template(
        'manage_teachers/update_teacher_role.html',
        t_active = ACTIVE,
        form = form, 
        teacher = teacher,
        branch_name = branch_name,
        previous_assigned_roles = previous_assigned_roles,
        title = 'Update Teacher Roles'
    ) 



@admin_bp.route('/admin-view', methods=['GET', 'POST'])
@login_required
def teachers_classic_view(): 
    is_all_selected = False
    branch = request.form.get('branch')
    if branch == 'all':
        teachers = Teacher.query.all()
        is_all_selected = True
    else:
        branch_id = SchoolBranch.query.filter_by(name=branch).first().id
        teachers = Teacher.query.filter_by(branch_id=branch_id).all()
    return render_template(
        'manage_teachers/classic_teachers_view.html', 
        t_active = ACTIVE,
        teachers = teachers,
        all = is_all_selected,
        title = 'Classic Teachers View'
    )


@admin_bp.route('/fetch_teacher_data', methods=['POST'])
@login_required
def fetch_teacher_data():
    data = request.get_json()   
    teacher_id = data.get('id')  

    if not teacher_id:
        return jsonify({'error': 'Missing teacher ID'}), 400

    teacher = Teacher.query.get_or_404(teacher_id)
    branch = SchoolBranch.query.filter_by(id=teacher.branch_id).first()

    return jsonify({
        'id': teacher.id,
        'fullname': teacher.teacher_name,
        'email': teacher.email,
        'salary': teacher.salary,
        'gender': teacher.gender,
        'phone_no': teacher.phone_no,
        'branch': branch.name,
        'id_no': teacher.id_no,
        'tsc_no': teacher.tsc_no 
    })


@admin_bp.route('/edit_teacher_data', methods=['POST'])
@login_required
def edit_teacher_data():
    form = TeacherForm()
    branch = form.branch.data 
    fullname = form.teacher_name.data
    tsc_no = form.tsc_no.data
    id_no = form.id_no.data
    phone_no = form.phone_no.data
    salary = form.salary.data

    mandatory_fields = [branch, fullname, id_no, phone_no]
    if not all(field is not None and str(field).strip() for field in mandatory_fields):
        flash('Failed to update teacher data. Some required fields are empty.', 'danger')
        return redirect(url_for('admin_bp.assign_teacher_roles'))

    teacher_id = request.form.get('tr-id')
    teacher = Teacher.query.filter_by(id=teacher_id).first()
    if not teacher:
        flash('Teacher not found.', 'danger')
        return redirect(url_for('admin_bp.assign_teacher_roles'))

    # Check if id_no is used by another teacher
    if Teacher.query.filter(Teacher.id_no == id_no, Teacher.id != teacher.id).first():
        flash('ID Number already exists for another teacher.', 'danger')
        return redirect(url_for('admin_bp.assign_teacher_roles'))

    # Check if phone_no is used by another teacher
    if Teacher.query.filter(Teacher.phone_no == phone_no, Teacher.id != teacher.id).first():
        flash('Phone Number already exists for another teacher.', 'danger')
        return redirect(url_for('admin_bp.assign_teacher_roles'))
    

    new_branch = SchoolBranch.query.filter_by(name=branch).first()

    if teacher.branch.id != new_branch.id:
        # Delete subjects assigned to the teacher in old branch.
        TeacherSubjectAssignment.query.filter_by(teacher_id=teacher.id).delete()

    teacher.branch = new_branch
    teacher.teacher_name = fullname
    teacher.tsc_no = tsc_no
    teacher.id_no = id_no  # ← you can safely update now
    teacher.phone_no = phone_no
    teacher.salary = salary

    
    db.session.commit()

    flash('Teacher\'s details updated successfully.', 'success')
    return redirect(url_for('admin_bp.assign_teacher_roles'))

 

@admin_bp.route('/generate_teachers_list_pdf', methods=['POST'])
@login_required
def generate_teachers_list_pdf():
    target_branch = request.form.get('target-branch', '').strip()
    teachers = []
    branch_name = 'All'
    address = 'P.O. Box 289, Nairobi' 

    try:
        if target_branch.lower() == 'all':
            teachers = Teacher.query.all()
            branch_name = "BUSHRA SCHOOLS TEACHERS [ALL]"
        else:
            branch = SchoolBranch.query.filter_by(name=target_branch).first()
            if not branch:
                flash(f"No branch found with name '{target_branch}'.", 'warning')
                return redirect(url_for('admin_bp.view_teachers')) 
            teachers = Teacher.query.filter_by(branch_id=branch.id).all()
            branch_name = branch.name

        if not teachers:
            flash(f"No teachers found for branch '{branch_name}'.", 'warning')
            return redirect(url_for('admin_bp.view_teachers'))

        addr = SchoolInfo.query.first().address
        address = addr if addr else 'No Address Found'
        
        return generate_teacher_list_pdf(teachers, branch_name, address)

    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Something went wrong. Please try again later.', 'danger')
        current_app.logger.error(f'Error: {e}, Traceback: {traceback.format_exc()}')
        return redirect(url_for('admin_bp.view_teachers'))



@admin_bp.route('delete_teacher', methods=['POST'])
@login_required
def delete_teacher(): 
    target_teacher = request.form.get('delete-teacher-name')
    try:
        tr = Teacher.query.filter_by(teacher_name=target_teacher).first()
        if not tr:
            flash('Teacher not found.', 'warning')
            return redirect(url_for('admin_bp.assign_teacher_roles'))

        # Delete associated roles
        tr_role = Role.query.filter_by(teacher_id=tr.id).first()
        if tr_role:
            db.session.delete(tr_role)

        # Delete assigned subjects
        TeacherSubjectAssignment.query.filter_by(teacher_id=tr.id).delete()

        # Delete user login account
        User.query.filter_by(teacher_id=tr.id).delete()

        # Delete teacher record
        db.session.delete(tr)
        db.session.commit()

        flash(f'Teacher {tr.teacher_name} was successfully deleted!', 'info')
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Error: {e} \nTRACEBACK\n {traceback.format_exc()}')
        flash('Sorry, something went wrong on our side!', 'danger')

    return redirect(url_for('admin_bp.assign_teacher_roles'))



@admin_bp.route('/manage_staff', methods=['GET', 'POST'])
@login_required
def manage_staff(): 
    form = StaffForm()
    # Use branch names as both value and label
    form.branch.choices = [('', 'Select Branch')] + [
        (branch.name, branch.name) for branch in SchoolBranch.query.all()
    ]

    if form.validate_on_submit():
        try:
            # Fetch the branch by name
            selected_branch = SchoolBranch.query.filter_by(name=form.branch.data).first()
            if not selected_branch:
                flash('Invalid branch selected.', 'danger')
                return redirect(url_for('admin_bp.manage_staff'))

            # Create new staff instance
            new_staff = Staff(
                fullname=form.fullname.data.strip(),
                branch_id=selected_branch.id,
                designation=form.designation.data.strip(),
                phone_number=form.phone_number.data.strip()
            )

            db.session.add(new_staff)
            db.session.commit()
            flash('Staff member added successfully.', 'success')
            return redirect(url_for('admin_bp.manage_staff'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding staff: {e}")
            flash('An error occurred while adding the staff member.', 'danger')

    return render_template(
        'manage_staff.html',
        st_active=ACTIVE,
        form=form,
        all_staff = Staff.query.all()[::-1],
        branches = SchoolBranch.query.all(),
        title='Manage Staff'
    )


@admin_bp.route('/update_staff_info', methods=['POST'])
@login_required
def update_staff_info():
    """Update staff member information"""
    
    original_name = request.form.get('hidden-staff-name').strip()
    updated_name = request.form.get('staffname').strip()
    updated_phone = request.form.get('phone-number').strip()
    updated_designation = request.form.get('staff-design')
    updated_branch_name = request.form.get('staff-branch')

    current_staff = Staff.query.filter_by(fullname=original_name).first()

    # Check if another staff member already has the new name
    existing_name_match = Staff.query.filter_by(fullname=updated_name).first()
    if existing_name_match and existing_name_match.id != current_staff.id:
        flash(f'A staff member with the name "{updated_name}" already exists.', 'danger')
        return redirect(url_for('admin_bp.manage_staff'))

    # Check if another staff member already has the new phone number
    existing_phone_match = Staff.query.filter_by(phone_number=updated_phone).first()
    if existing_phone_match and existing_phone_match.id != current_staff.id:
        flash(f'Phone number "{updated_phone}" belong to another staff.', 'danger')
        return redirect(url_for('admin_bp.manage_staff'))
    
    # Check if phone number is made up of exactly 10 digits
    if len(str(updated_phone)) != 10:
        flash(f'The phone number "{updated_phone}" you entered is invalid!', 'danger')
        return redirect(url_for('admin_bp.manage_staff'))


    # Update the staff details
    current_staff.fullname = updated_name
    current_staff.phone_number = updated_phone
    current_staff.designation = updated_designation
    current_staff.branch = SchoolBranch.query.filter_by(name=updated_branch_name).first()

    try:
        db.session.commit()
        current_app.logger.info(
            f'{current_staff} info updated by {current_user.teacher.teacher_name}'
        )
        flash('Staff information updated successfully.', 'info')
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        flash('Oops! Failed to update staff info. Please try again later.', 'danger')

    return redirect(url_for('admin_bp.manage_staff'))


@admin_bp.route('/delete_staff', methods=['POST'])
@login_required
def delete_staff():
    staff_name = request.form.get('staff-name')
    if staff_name:
        try:
            staff = Staff.query.filter_by(fullname=staff_name).first()
            db.session.delete(staff)
            db.session.commit()
            flash('Staff member deleted successfully.', 'info')
            current_app.logger.info(f"Staff '{staff_name}' deleted by user '{current_user.username}' (ID: {current_user.id})")
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            flash('An error occured when deleting staff! Please try again later.', 'danger')
    return redirect(url_for('admin_bp.manage_staff'))


@admin_bp.route('/grade_streams_setup', methods=['GET', 'POST'])
@login_required
def grade_streams_setup():
    form = GradeForm()
    form.branch.choices = [('', 'Select Branch')] + [
        (branch.name, branch.name) for branch in SchoolBranch.query.all()
    ]

    if form.validate_on_submit():
        entered_streams = list(filter(None, 
            [form.stream1.data, form.stream2.data, form.stream3.data])
        )

        if len(set(entered_streams)) != len(entered_streams):
            flash('You cannot have same name for two streams!', 'danger')
            return redirect(url_for('admin_bp.grade_streams_setup'))

        selected_branch = SchoolBranch.query.filter_by(name=form.branch.data).first()
        selected_grade = Grade.query.filter_by(grade_name=form.grade_name.data).first()

        existing_streams = GradeStreamBranch.query.filter_by(
            branch_id=selected_branch.id,
            grade_id=selected_grade.id
        ).all()

        existing_names = [s.stream_name for s in existing_streams]

        # Update or insert streams
        for stream in entered_streams:
            if stream not in existing_names:
                new_entry = GradeStreamBranch(
                    branch_id=selected_branch.id,
                    grade_id=selected_grade.id,
                    stream_name=stream
                )
                db.session.add(new_entry)
            # else: stream already exists, skip or update logic can go here

        db.session.commit()

        flash('Streams added/updated successfully.', 'success')
        return redirect(url_for('admin_bp.grade_streams_setup'))

    return render_template(
        'grade_streams_setup.html',
        form=form,
        d_active=ACTIVE,
        title='Grades/Streams setup'
    )


@admin_bp.route('/fetch_streams', methods=['POST'])
def fetch_streams():
    data = request.get_json() 
    stream_names = []
    try:
        branch = SchoolBranch.query.filter_by(name=data.get('branch')).first()
        grade = Grade.query.filter_by(grade_name=data.get('grade')).first()
        print(branch, grade)
        if branch and grade:
            streams = GradeStreamBranch.query.filter_by(
                branch_id=branch.id, grade_id=grade.id
            ).all()
            stream_names = [stream.stream_name for stream in streams]
            return jsonify({'success': True, 'streams': stream_names})

    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Sorry an error occured while fetching streams. Please try again.', 'danger')
        current_app.logger.error(f'Error: {e} \nTraceback: {traceback.format_exc()}')

    return jsonify({'success': False, 'streams': []}), 500


# # Endpoint to fetch streams of the selected grade.
@admin_bp.route('/get_streams', methods = ['GET', 'POST'])
@login_required
def get_streams():
    targeted_grade = request.json 
    grade = Grade.query.filter_by(grade_name = targeted_grade.get(
            'selectedValue')).first()
    streams = Stream.query.filter_by(grade_id = grade.id).all()
    streams_list = [str(s) for s in streams]
    return jsonify(streams_list)


@admin_bp.route('/studentdash')
@login_required
def student_dash():
    form = SearchStudent()
    student_info = {}

    try:
        # Query student counts by grade and gender 
        results = db.session.query(
            Student.grade,
            Student.gender,
            func.count(Student.id)
        ).group_by(Student.grade, Student.gender).all()

        # Process results into a dictionary
        for grade, gender, count in results:
            if grade not in student_info:
                student_info[grade] = {"boys": 0, "girls": 0}
            if gender == "Male":
                student_info[grade]["boys"] = count
            elif gender == "Female":
                student_info[grade]["girls"] = count
            student_info[grade]['total'] = student_info[grade]["girls"] + student_info[grade]["boys"]
 
    except SQLAlchemyError as e:
        current_app.logger.error(e)

    return render_template(
        'manage_students/student_dash.html',
        s_active=ACTIVE,
        form=form, 
        student_info=student_info  
    )


@admin_bp.route('/add_student', methods = ['GET', 'POST'])
@login_required
def add_student(): 
    form = StudentRegistrationForm()
    branches = [(branch.name, branch.name) for branch in SchoolBranch.query.all()]
    branches.insert(0, ("", "Select Branch"))  
    form.branch.choices = branches
    if form.validate_on_submit(): 
        selected_branch = SchoolBranch.query.filter_by(name=form.branch.data).first()
        student = Student(
            fullname = form.fullname.data,
            grade = form.grade.data, 
            adm_no = form.adm_no.data, 
            gender = form.gender.data,
            stream = form.stream.data,
            branch = selected_branch,
            parent_name = form.parent_name.data, 
            contact_phone = form.contact_phone.data, 
            health_info = form.health_info.data
        )
        strm = request.form.get('streams')
        if strm:
            student.stream = strm
        try:
            photo_file = form.photo.data
            if photo_file:
                student.photo = img_editor(photo_file)
            db.session.add(student)
            db.session.commit()
            flash('Student was added successfully!', 'info')
            return redirect(url_for('admin_bp.add_student'))
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(e)
            flash('Something went wrong!', 'danger')
            return redirect(url_for('admin_bp.add_student'))
        
    form.branch.data = ""

    return render_template(
        'manage_students/add_student.html',
        s_active = ACTIVE,
        form = form
    )


@admin_bp.route('/delete_student', methods=['POST'])
@login_required
def delete_student():
    adm_no = request.form.get('adm_no')
    try:
        student = Student.query.filter_by(adm_no=adm_no).first()         
        # Delete all exam marks related to the student
        ExamMarks.query.filter_by(student_id=student.id).delete()
        db.session.delete(student)

        db.session.commit()
        flash('Student was deleted successfully', 'info')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        flash('Sorry, can\'t delete student. Please try again later.', 'warning')

    return redirect(url_for('admin_bp.add_student'))


@admin_bp.route('/update_student_biodata', methods=['POST'])
@login_required
def update_student_biodata():
    adm_no = request.form.get('adm_no')
    stream = request.form.get('stream')
    branch_name = request.form.get('branch')

    # Fetch the student
    target_student = Student.query.filter_by(adm_no=adm_no).first()

    if not target_student:
        flash('Student not found!', 'danger')
        return redirect(url_for('admin_bp.dashboard'))

    # Query branch from name
    branch = SchoolBranch.query.filter_by(name=branch_name).first()
    if not branch:
        flash('Invalid branch provided.', 'danger')
        return redirect(url_for('admin_bp.dashboard'))

    # Update student data
    target_student.fullname = request.form.get('fullname')
    target_student.gender = request.form.get('gender')
    target_student.grade = request.form.get('grade')
    target_student.parent_name = request.form.get('parent_name')
    target_student.contact_phone = request.form.get('contact_phone')
    target_student.branch_id = branch.id

    target_student.health_info = request.form.get('health_info')

    if stream and stream != 'None':
        target_student.stream = stream

    # Commit to DB
    try:
        db.session.commit()
        flash('Student information updated successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating student biodata: {e}")
        flash('An error occurred while updating the student.', 'danger')

    # Re-render the searched student page
    form = SearchStudent()
    return render_template(
        'manage_students/searched_student.html',
        form=form,
        student_info=target_student,
        branches = SchoolBranch.query.all(),
        grades = Grade.query.all(),
        s_active=ACTIVE
    ) 


# Update the student passport
@admin_bp.route('/update_student_passport', methods=['POST'])
@login_required
def update_student_passport(): 
    student_adm_no = request.form.get('adm_no')
    target_student = Student.query.filter_by(adm_no=student_adm_no).first()
    
    if not target_student:
        flash('Student not found!', 'danger')
        return redirect(url_for('admin_bp.dashboard'))

    photo_file = request.files.get('passport')
    if photo_file:
        target_student.photo = img_editor(photo_file)
        try:
            db.session.commit()
            flash('Passport updated successfully.', 'info')
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            flash('Oops! Something went wrong! Couldn\'t update passport!', 'danger')

    # After updating, render the searched_student.html with updated data
    form = SearchStudent()
    return render_template(
        'manage_students/searched_student.html', 
        form=form,
        student_info=target_student,
        branches = SchoolBranch.query.all(),
        grades = Grade.query.all(),
        s_active=ACTIVE
    )


@admin_bp.route('/search_student', methods = ['GET', 'POST'])
@login_required
def search_student():
    form = SearchStudent()
    branches = SchoolBranch.query.all()
    search_data = request.form.get('search_input').strip()
    if search_data:
        try:
            student = Student.query.filter(
                or_(
                    Student.adm_no.ilike(search_data),    
                    Student.fullname.ilike(search_data)  
                )
            ).first() 

            if student is None:
                flash('Oops! There is no student with the credentials you entered!', 
                    'danger') 
                return redirect(url_for('admin_bp.dashboard'))
            
            return render_template(
                'manage_students/searched_student.html', 
                form = form,
                student_info = student,
                branches = branches,
                grades = Grade.query.all(),
                s_active = ACTIVE,
            )
        
        except SQLAlchemyError as e:
            flash(
                'Oops! Something went wrong from our side! Please try again!', 
                'danger'
            )
            current_app.logger.error(f"Error searching for student: {e}")
            return render_template(
                'manage_students/student_dash.html', 
                form = form, 
                s_active = ACTIVE,
            )


@admin_bp.route('/get_students', methods=['POST', 'GET'])
@login_required
def get_students():
    data = request.json
    grade = data.get('grade')
    stream = data.get('stream')

    if stream:
        students = Student.query.filter_by(grade=grade, stream=stream).all()
    else:
        students = Student.query.filter_by(grade=grade).all()

    student_list = [{
        "adm_no": s.adm_no,
        "fullname": s.fullname,
        "grade": s.grade,
        "stream": s.stream,
        "gender": s.gender,
        "parent_name": s.parent_name,
        "contact_phone": s.contact_phone
    } for s in students]

    return jsonify(student_list)


from collections import defaultdict

@admin_bp.route('/view_subjects', methods=['GET', 'POST'])
@login_required
def view_subjects():
    grades = Grade.query.all()
    all_subjects_info = []

    try:
        all_assignments = TeacherSubjectAssignment.query.all()

        for assignment in all_assignments:
            subs_holder = {}

            stream = GradeStreamBranch.query.filter_by(id=assignment.grade_stream_branch_id).first()
            subject = Subject.query.get(assignment.subject_id)
            teacher = Teacher.query.get(assignment.teacher_id)

            if not subject or not teacher:
                continue  # Skip incomplete data

            if stream:
                branch = SchoolBranch.query.get(stream.branch_id)
                grd = Grade.query.get(stream.grade_id)


                subs_holder = {
                    'teacher': teacher.teacher_name,
                    'branch': branch.name if branch else None,
                    'subject': subject.subject,
                    'stream': stream.stream_name,
                    'grade': grd.grade_name if grd else None
                }
            elif assignment.grade:
                grade = Grade.query.get(assignment.grade)
                subs_holder = {
                    'teacher': teacher.teacher_name,
                    'branch': teacher.branch.name if teacher.branch else None,
                    'subject': subject.subject,
                    'grade': grade.grade_name if grade else None,
                    'stream': None
                }

            all_subjects_info.append(subs_holder)

    except SQLAlchemyError as e:
        current_app.logger.error(f'{e} TRACEBACK\n{traceback.format_exc()}')
        db.session.rollback()
        flash('Failed to load subjects! There may be no subjects or an internal error occurred.', 'danger')

    # Group by subject
    grouped_subjects = defaultdict(list)
    for info in all_subjects_info:
        grouped_subjects[info['subject']].append(info)

    return render_template(
        'view_subjects.html',
        grouped_subjects=grouped_subjects,
        grades=grades,
        view_active=HORIZONTAL_ACTIVE,
        sub_active=ACTIVE
    )




@admin_bp.route('/add_subject', methods = ['GET', 'POST'])
@login_required
def add_subject():
    error_sms = 'Oops, something went wrong on our side please try again later!'
    all_subjects = Subject.query.all()[::-1]
    form = SubjectForm()
    if form.validate_on_submit():
        selected_grades = [
            field.label.text for name, field in form._fields.items()
            if field.type == 'BooleanField' and field.data and name != 'all_classes'
        ] 
        sub = Subject(
            subject = form.subject.data.strip(),
            grades = selected_grades,
            short_form = form.sub_short_form.data
        )

        if sub.subject.isdigit():
            flash(f'Oops! Subject name cannot be numbers!', 'danger')
            return redirect(url_for('admin_bp.add_subject')) 

        if sub.subject.lower() in [s.subject.lower() for s in all_subjects]:
            flash(f'{sub.subject} already exists in the system!', 'danger')
            return redirect(url_for('admin_bp.add_subject'))

        try:
            db.session.add(sub)
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('admin_bp.add_subject'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(error_sms, 'danger')
            current_app.logger.error(f'Subject Insertion Error {e} occurred!')
        except:
            db.session.rollback()
            flash(error_sms, 'danger')
            current_app.logger.error('Unknown error occurred!')

    return render_template(
        'add_subject.html', 
        form = form,
        all_subjects = all_subjects,
        sub_active = ACTIVE,
        add_active = HORIZONTAL_ACTIVE
    )


@admin_bp.route('/delete_subject', methods=['POST'])
@login_required
def delete_subject():
    subject_name = request.form.get('delete-subject-name')

    try:
        # Find the subject
        subject = Subject.query.filter_by(subject=subject_name).first()
        if not subject:
            flash(f'Subject "{subject_name}" not found!', 'warning')
            return redirect(url_for('admin_bp.add_subject'))

        # Delete all assignments related to this subject
        TeacherSubjectAssignment.query.filter_by(subject_id=subject.id).delete()

        # Now delete the subject
        db.session.delete(subject)
        db.session.commit()

        flash(f'{subject_name} was deleted successfully!', 'info')

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Something went wrong {e}')
        flash(f'Error deleting {subject_name}', 'danger')

    return redirect(url_for('admin_bp.add_subject'))

 
@admin_bp.route('/assign_teacher_subjects/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def assign_teacher_subjects(teacher_id):
    try:
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            flash("Teacher not found!", "warning")
            return redirect(url_for('admin_bp.assign_teacher_roles')) 
        branch = teacher.branch
        if not branch:
            flash("Branch for the teacher not found!", "warning")
            return redirect(url_for('admin_bp.assign_teacher_roles'))

        grade_names = [g.grade_name for g in Grade.query.all()]
 
        # Handle subject submission.
        if request.method == 'POST':
            grade = request.form.get('grade')
            stream = request.form.get('stream')
            subject_ids = request.form.getlist('subjects')  # list of subject IDs

            if not subject_ids:
                flash("You must select atleast one subjct to assign.", "warning")
                return redirect(request.url)

            selected_grade = Grade.query.filter_by(grade_name=grade).first()
            if not selected_grade:
                flash("Invalid grade selected.", "danger")
                return redirect(request.url)

            grade_id = selected_grade.id

            # Determine applicable streams
            if stream == "All Streams":
                all_streams = GradeStreamBranch.query.filter_by(branch_id=branch.id, grade_id=grade_id).all()
                stream_names = [s.stream_name for s in all_streams]
            else:
                stream_names = [stream] if stream else []

            if stream:
                for stream_name in stream_names:
                    gsb =  GradeStreamBranch.query.filter_by(
                            branch_id=branch.id,
                            grade_id=grade_id,
                            stream_name=stream_name
                    ).first()
                    if not gsb:
                        continue # skip non-exisiting class

                    # Add new subject assignments
                    for subject_id in subject_ids:
                        # Remove existing assignments for this teacher in this class
                        TeacherSubjectAssignment.query.filter_by(
                            teacher_id=teacher.id,
                            grade_stream_branch_id=gsb.id,
                            subject_id=subject_id
                        ).delete()

                        # Remove assignment if another teacher has it.
                        # exist_branch = SchoolBranch.query.filter_by(
                        #     id = gsb.id
                        # ).first()

                        # if exist_branch.id == teacher.id:
                        existing_assignment = TeacherSubjectAssignment.query.filter_by(
                            grade_stream_branch_id=gsb.id,
                            subject_id=subject_id,
                                            
                        ).first()

                        if existing_assignment:
                            db.session.delete(existing_assignment)

                        new_assignment = TeacherSubjectAssignment(
                            teacher_id=teacher.id,
                            subject_id=int(subject_id),
                            grade_stream_branch_id=gsb.id
                        )
                        db.session.add(new_assignment)

            # Assign Subjects to a teacher in a grade with no streams
            if not stream and grade_id:
                for subject_id in subject_ids:
                    # Remove other teacher with this subject in the same grade.
                    existing_assignment = TeacherSubjectAssignment.query.filter_by(
                        grade=grade_id,
                        subject_id=subject_id,                   
                    ).first()
                      
                    if existing_assignment:
                        # Delete subject if it belong to another teacher in the same branch.
                        prev_sub_assign = Teacher.query.filter_by(
                            id=existing_assignment.teacher_id).first()
                        
                        if prev_sub_assign.branch.id == teacher.branch.id:
                            db.session.delete(existing_assignment)

                    # Remove existing assignments for this teacher in this class
                    TeacherSubjectAssignment.query.filter_by(
                        teacher_id=teacher.id,
                        grade=grade_id,
                        subject_id=subject_id
                    ).delete()

                    new_assignment = TeacherSubjectAssignment(
                        teacher_id=teacher.id,
                        subject_id=int(subject_id),
                        grade=grade_id
                    )
                    db.session.add(new_assignment) 
            
            db.session.commit()
            flash("Teacher subject assignments updated successfully.", "success")
            return redirect(url_for('admin_bp.assign_teacher_subjects', teacher_id=teacher_id))
                    

        # ========== GET REQUEST: Fetch assigned subjects ==========
        assigned_subjects = []
        assignments = TeacherSubjectAssignment.query.filter_by(teacher_id=teacher_id).all()
        
        for assign in assignments:
            gsb = assign.grade_stream_branch
            if not gsb:
                grd = Grade.query.filter_by(id=assign.grade).first()
                assigned_subjects.append({
                    'subject_name': assign.subject.subject,
                    'grade_name': grd.grade_name
                }) 
            else:           
                assigned_subjects.append({
                    'subject_name': assign.subject.subject,
                    'grade_name': gsb.grade.grade_name,
                    'stream_name': gsb.stream_name
                })

        return render_template(
            'manage_teachers/assign_teacher_subjects.html',
            t_active=ACTIVE,
            teacher=teacher,
            grades=grade_names, 
            branch_info=branch,
            assigned_subjects=assigned_subjects[::-1]
        )

    except Exception as e:
        current_app.logger.error(f"Error assigning subjects to teacher {teacher_id}: {e}")
        current_app.logger.error(f'\n TRACEBACK: {traceback.format_exc()}')
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('admin_bp.assign_teacher_roles'))



@admin_bp.route('/fetch_subjects_by_grade', methods=['POST'])
def fetch_subjects_by_grade():
    data = request.get_json()
    grade = data.get('grade')

    if not grade:
        return jsonify({'success': False, 'message': 'Grade not provided'}), 400

    try:
        subjects = Subject.query.all()
        filtered_subjects = [
            {'id': subj.id, 'subject': subj.subject, 'short_form': subj.short_form}
            for subj in subjects
            if subj.grades and grade in subj.grades
        ]

        return jsonify({'success': True, 'subjects': filtered_subjects})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error fetching subjects'}), 500






























































@admin_bp.route('/get_teacher_subjects/<teacher_id>', methods=['GET'])
def get_teacher_subjects(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"message": "Teacher not found"}), 404

    assignments = TeacherSubjectAssignment.query.filter_by(teacher_id=teacher_id).all()
    
    result = []
    for assignment in assignments:
        result.append({
            "subject": assignment.subject.subject,
            "grade": assignment.grade,
            "stream": assignment.stream
        })

    return jsonify({"teacher": teacher.teacher_name, "subjects": result})


@admin_bp.route('/display_students_list', methods=['GET', 'POST'])
@login_required
def display_students_list():
    "Display students lists."
    form = StudentListForm() 

    students = subjects = []
    branch = stream = grade = None

    try:
        branches =[('', 'Select Branch')] + [
            (branch.name, branch.name) for branch in SchoolBranch.query.all()
        ]
        form.branch.choices = branches
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        pass
    
    # Remove stream validation if grade has no streams.
    if request.method == 'POST':
        branch = SchoolBranch.query.filter_by(name=form.branch.data).first()
        grade = Grade.query.filter_by(grade_name=form.grade.data).first()
        
        if branch and grade:
            streams = GradeStreamBranch.query.filter_by(
                grade_id=grade.id, branch_id=branch.id
            ).all()

            if len(streams) == 0:
                form.stream.validators = ()  # Remove all validators for stream

    if form.validate_on_submit():
        stream = form.stream.data
        list_type = form.list_type.data
    
        if stream:
            students = Student.query.filter_by(
                branch_id=branch.id, 
                grade=grade.grade_name,
                stream = stream 
            ).all()
        else:
            students = Student.query.filter_by(
                branch_id=branch.id, 
                grade=grade.grade_name
            ).all()
        
        if list_type == 'Mark list':
            subjects = [
                sub.short_form for sub in Subject.query.all() \
                    if grade.grade_name in sub.grades
            ]
            
    # Reset branch select for new selection.
    form.branch.data = "Select Branch"
    
    query_data = {
        'branch': branch, 
        'grade': grade, 
        'stream': stream,
        'school_addr': SchoolInfo.query.first().address,
        'list_type': form.list_type.data or None,
        'sub_info': {
            'subjects': subjects,
            'sub_len': len(subjects)
        }
    }
    
    sorted_students = sorted(students, key=lambda s: int(s.adm_no))
    return render_template(
        'printouts.html',
        form = form,
        query_data = query_data,
        students = sorted_students,
        p_active = ACTIVE
    )



@admin_bp.route('/generate_student_pdf_list', methods=['POST'])
@login_required
def generate_student_pdf_list():
    """
    This works to generate two types of lists depending on the input of the
    user. => Class list or Mark list.
    """
    import ast
    stream = request.form.get('strm')
    branch = SchoolBranch.query.filter_by(
        name=request.form.get('branch')
    ).first()
    grade = Grade.query.filter_by(
        grade_name=request.form.get('grade')
    ).first()

    
    list_type = request.form.get('list-type')

    subjects = ast.literal_eval(request.form.get('subjects'))
    
    if branch and grade:
        students = Student.query.filter_by(
            branch_id=branch.id, 
            grade=grade.grade_name
        ).all()

        streams_obj = GradeStreamBranch.query.filter_by(
            branch_id=branch.id, grade_id=grade.id
        ).all()
        if streams_obj:
            streams = [s.stream_name for s in streams_obj]
            students = [student for student in students \
                        if student.stream == stream]          
        
        config = {
            'branch_name': branch.name, 
            'grade': grade.grade_name,
            'stream': stream or '',
            'addr': SchoolInfo.query.first().address
        }

        sorted_students = sorted(students, key=lambda s: int(s.adm_no))
        # Instead of saving the PDF to disk, generate it into memory
        pdf_buffer = io.BytesIO()
        generate_marklist(
            sorted_students, 
            subjects, 
            list_type, 
            config=config, 
            output=pdf_buffer
        )
        pdf_buffer.seek(0)

        # Send the PDF back to browser, inline (to view)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=False,  # <--- This makes it open instead of download
            download_name=f'{branch.name}_{grade.grade_name}_{list_type}.pdf'
        )

    return 'Error generating PDF'



@admin_bp.route('/add_new_exam', methods=['GET', 'POST'])
@login_required
def add_new_exam():
    form = ExamForm()
    
    if form.validate_on_submit():
        new_exam = Exam(
            name=form.exam_name.data,
            term=form.term.data,
            year=form.year.data,  
            created_at=form.exam_date.data
        )
        
        if Exam.query.filter_by(name=form.exam_name.data).first():
            flash('Examination with that name already exist in the System!', 'danger')
            return redirect(url_for('admin_bp.add_new_exam'))
        try:
            # Check first if there is an open exam.
            exams = Exam.query.all()
            if exams:
                for ex in exams:
                    if ex.status == 'open':
                        flash('Sorry you have unpublished exam!.', 'danger')
                        return redirect(url_for('admin_bp.add_new_exam')) # Work on a better redirect later.
            db.session.add(new_exam)
            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            flash('Sorry we can\'t add new exam now! Try later.', 'danger')
            return redirect(url_for('admin_bp.add_new_exam'))
        
        flash("Exam added successfully!", "success")
        print('EXAM ADDED SUCCESSFULLY!')
        return redirect(url_for('admin_bp.add_new_exam'))
    
    return render_template(
        'manage_exams/add_new_exam.html',
        form=form,
        ex_active=ACTIVE
    ) 



@admin_bp.route('/admin_marks_entry')
@login_required
def admin_marks_entry():
    # Get the latest open exam
    open_exam = Exam.query.filter_by(status='open').first()
    if not open_exam:
        flash('All exams have been published! Create new exam or unpublish exam to enter marks.', 'warning')
        return redirect(url_for('admin_bp.add_new_exam'))

    # Fetch all grades
    all_grades = Grade.query.all()
    
    # Prepare dict for grades missing marks
    grades_without_marks = {}

    for grade in all_grades:
        # Get only subjects that include this grade in their assigned list
        subjects = [
            subject for subject in Subject.query.all()
            if subject.grades and grade.grade_name in subject.grades
        ]

        missing_subjects = [] 
        for subject in subjects:
            # Get all students in this grade
            students_in_grade = Student.query.filter_by(grade=grade.grade_name).all()

            # Check if all students in the grade have marks for this subject
            marks_exist = all(
                ExamMarks.query.filter_by(
                    exam_id=open_exam.id,
                    subject_id=subject.id,
                    student_id=student.id
                ).first() is not None
                for student in students_in_grade
            )

            if not marks_exist:
                missing_subjects.append(subject.subject)

        if missing_subjects:
            grades_without_marks[grade.grade_name] = missing_subjects

    return render_template(
        'manage_exams/admin_marks_entry.html', 
        open_exam=open_exam,
        ex_active=ACTIVE,
        grades_without_marks=grades_without_marks
    )


@admin_bp.route('/get_students_for_grade')
@login_required
def get_students_for_grade():
    grade = request.args.get('grade')
    students = Student.query.filter_by(grade=grade).all()
    student_list = [{"id": student.id, "name": student.fullname} for student in students]
    return jsonify({"students": student_list})


"""
 Handles the uploading and saving of students marks for a 
 particular examination.
"""
@admin_bp.route('/save_marks', methods=['POST'])
@login_required
def save_marks():
    grade = request.form.get('grade') 
    subject_name = request.form.get('subject')
 
    marks_data = {key: value for key, value in request.form.items() 
                  if key.startswith("marks[")
    }

    exam = Exam.query.filter_by(status='open').first()
    subject = Subject.query.filter_by(subject=subject_name).first()
    
    for adm_no_key, mark in marks_data.items():
        # Extract admission number manually
        if adm_no_key.startswith("marks[") and adm_no_key.endswith("]"):
            adm_no = adm_no_key[6:-1]  # Remove "marks[" at start and "]" at end

            student = Student.query.filter_by(adm_no=adm_no, grade=grade).first()
            if student:
                existing_record = ExamMarks.query.filter_by(
                    exam_id=exam.id, student_id=student.id, subject_id=subject.id
                ).first()

                if existing_record:
                    existing_record.marks = mark # update marks.
                else:
                    new_mark = ExamMarks(
                        exam_id=exam.id,
                        student_id=student.id,
                        subject_id=subject.id,
                        marks=mark
                    )
                    db.session.add(new_mark)

    db.session.commit() 
    flash("Marks saved successfully!", "success")
    return redirect(url_for('admin_bp.admin_marks_entry'))


@admin_bp.route('/manage_exams', methods=['GET', 'POST'])
@login_required
def manage_exams():
    all_exams = Exam.query.all()
    return render_template(
        'manage_exams/manage_exams.html',
        all_exams = all_exams,
        ex_active = ACTIVE
    ) 


@admin_bp.route('/toggle_exam_status', methods=['POST'])
@login_required
def toggle_exam_status():
    target_exam = request.form.get('exam-name')
    target_exam_status = request.form.get('exam-status')
    try:
        exams = Exam.query.all()
        EXAM = Exam.query.filter_by(name=target_exam).first()
        if target_exam_status == 'open':
            EXAM.status = 'closed'
        if target_exam_status == 'closed':
            for ex in exams:
                ex.status = 'closed'
            EXAM.status = 'open'
        db.session.commit()
        return redirect(url_for('admin_bp.manage_exams'))

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        flash('Something went wrong! Try later', 'warning')
        db.session.rollback()


@admin_bp.route('/delete_exam', methods=['GET', 'POST'])
@login_required
def delete_exam():
    exam_name = request.form.get('delete-exam-name')
    exam = Exam.query.filter_by(name=exam_name).first()
    try:
        # Delete related exam marks in the database.
        marks = ExamMarks.query.filter_by(exam_id=exam.id).all()
        for mark in marks: db.session.delete(mark)
        # Delete actual exam
        db.session.delete(exam)
        db.session.commit()
        flash(f'{exam_name} was deleted successfully.', 'info') 

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback
        flash('Oops! Can\'t delete exam. Please try again later', 'danger')
    return redirect(url_for('admin_bp.manage_exams'))


@admin_bp.route('/edit_exam_data', methods=['GET', 'POST'])
@login_required
def edit_exam_data():
    submited_data = {
        'original_exam_name' : request.form.get('hidden-exam-name'),
        'new_exam_name' : request.form.get('exam-name').strip(),
        'new_exam_term_info' : request.form.get('term-info').strip()
    }
    try:
        target_exam = Exam.query.filter_by(name=
            submited_data['original_exam_name']
        ).first()

        if target_exam:
            # Check if there is an exam with the new name
            if Exam.query.filter_by(name=submited_data['new_exam_name']).first():
                flash(f'There is already an exam with the name {submited_data["new_exam_name"]}', 'danger')
            else:
                target_exam.name = submited_data['new_exam_name']
                if target_exam.term != submited_data['new_exam_term_info']:
                    target_exam.term = submited_data['new_exam_term_info']
                db.session.commit()
                flash('Examinatin Info updated successfully!', 'info')

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        flash('Oops something went wrong! We can\'t update exam information right now!', 'warning')
    return redirect(url_for('admin_bp.manage_exams'))



@admin_bp.route('/generate_report_forms', methods=['GET', 'POST'])
@login_required
def generate_report_forms(): 
    exams = Exam.query.all()
    is_any_exam_published = False

    for exam in exams:
        if exam.status == 'closed':
            is_any_exam_published = True
            break 
    
    if not is_any_exam_published:
        # No published exam
        flash('No published exam! Please publish an exam first before generating report cards',
              'danger'
        )
        return redirect(url_for('admin_bp.manage_exams'))
        
    return render_template(
        'manage_exams/report_forms/report_forms_base.html',
        exams = exams,
        ex_active = ACTIVE,
        is_any_exam_published = is_any_exam_published
    )


@admin_bp.route('/process_report_forms', methods=['GET', 'POST'])
@login_required
def process_report_forms():
    exams = Exam.query.all()  # Get all exams
    report_cards = []
    is_rank_enabled = False

    if request.method == 'POST':
        grade = request.form.get('grade')
        exam_name = request.form.get('exam')
        stream = request.form.get('streams') 
        rank = request.form.get('rank')
        download_report = request.form.get('download')
        dates = {
            'closing_date' : request.form.get('closing-date'),
            'opening_date' : request.form.get('opening-date')
        }
        

        if rank == 'yes': 
            is_rank_enabled = True

        
        # Get the selected exam
        exam = Exam.query.filter_by(name=exam_name).first()

        if not exam:
            flash("Exam not found!", "danger")
            return redirect(url_for('admin_bp.process_report_forms'))

        # Get all students in the selected grade
        students = Student.query.filter_by(grade=grade).all()
        tot_subs = TeacherSubjectAssignment.query.filter_by(grade=grade).count()
    
        if stream:
            # Get teacher-subject assignments for this grade
            teacher_assignments = TeacherSubjectAssignment.query.join(Teacher).join(Subject).filter(
                (TeacherSubjectAssignment.grade == grade) &
                (TeacherSubjectAssignment.stream == stream)
            ).all()
        else:
            teacher_assignments = TeacherSubjectAssignment.query.join(Teacher).join(Subject).filter(
                TeacherSubjectAssignment.grade == grade
            ).all()

        # Store teacher assignments in a dictionary {subject_name: teacher_name}
        teacher_dict = {assignment.subject.subject: assignment.teacher.teacher_name for assignment in teacher_assignments}

        # Fetch marks for each student
        for student in students:
            marks = ExamMarks.query.join(Subject).filter(
                ExamMarks.exam_id == exam.id,
                ExamMarks.student_id == student.id
            ).all()

            def get_initials(name):
                return ".".join([part[0].upper() for part in name.split()])
            
            student_report = {
                "student": student,
                "marks": {
                    mark.subject.subject: {
                        "score": mark.marks,
                        "teacher": get_initials( teacher_dict.get(mark.subject.subject, "--"))  # Get teacher or default to "N/A"
                    }
                    for mark in marks
                    
                },
                "total": sum([mark.marks for mark in marks]),
                "attempted_any_exam": any([mark.marks for mark in marks])
            }
            

            report_cards.append(student_report)
            
            if is_rank_enabled:
                report_cards = sorted(report_cards, key=lambda report: report["total"], reverse=True) 
                for index, s in enumerate(report_cards):
                    s['position'] = index + 1
   
    if download_report:
        # Generate report cards if download btn is clicked
        report_cards = [card for card in report_cards if card['attempted_any_exam']]
        generate_report_cards_pdf(
            exam, 
            report_cards, 
            is_rank_enabled,
            dates=dates,
            grade=grade
        )
        flash(f'{grade} report forms generated successfully. Go to download folder to print them.', 'info')
        return redirect(url_for('admin_bp.generate_report_forms'))

    return render_template(
        "manage_exams/report_forms/report_forms_base.html",
        exams=exams,
        target_exam=exam,
        ex_active=ACTIVE,
        dates = dates,
        tot_subs = tot_subs,
        is_rank_enabled = is_rank_enabled,
        report_cards=report_cards
    )


@admin_bp.route('/manage_branch', methods=['GET', 'POST'])
def manage_branch():
    form = BranchForm()
    branches = SchoolBranch.query.all()[::-1]
    branch_id = request.form.get("branch_id")
    if branch_id:
        form.branch_id.data = branch_id 
    if form.validate_on_submit():
        if branch_id:
            # UPDATE flow
            branch_info = SchoolBranch.query.get(branch_id)
            if branch_info:
                branch_info.name = form.name.data
                branch_info.branch_manager = form.manager.data
                branch_info.branch_head = form.branch_head.data
                branch_info.branch_level = form.branch_level.data
                try:
                    db.session.commit()
                    flash('Branch info updated successfully.', 'info')
                    return redirect(url_for('admin_bp.manage_branch'))
                except SQLAlchemyError as e:
                    current_app.logger.error(e)
                    db.session.rollback()
                    flash('Error updating branch. Please try again.', 'danger')
        else:
            # ADD flow
            new_branch = SchoolBranch(
                name = form.name.data,
                branch_manager = form.manager.data,
                branch_head = form.branch_head.data,
                branch_level = form.branch_level.data
            )
            try:
                db.session.add(new_branch)
                db.session.commit()
                flash('Branch was added successfully.', 'info')
                return redirect(url_for('admin_bp.manage_branch'))
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                db.session.rollback()
                flash('Oops! Something went wrong. Please try again.', 'danger')
                
    return render_template(
        'add_branch.html', 
        b_active = ACTIVE,
        branches = branches,
        form = form
    )


# Logout user
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
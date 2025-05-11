from flask import render_template, url_for, flash, redirect
from . import auth_bp
from ..admin import admin_bp
from .forms import LoginForm
from ..models import Teacher, User, db 
from flask_login import login_user, login_required


# Mock Data
user = {
    'usermail': 'oyarojared278@gmail.com',
    'password': 'code',
    'role': 'admin'
}


# The login route serves as a single entry point for teachers, parents, and admins.
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.email.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_bp.dashboard'))
        
        flash('Invalid usermail or password!', 'danger')
    return render_template(
        'login.html', 
        form=form, 
        title='Login'
      )


@auth_bp.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    return render_template('recover_password.html')

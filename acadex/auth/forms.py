from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField(
        'User Email',
        validators=[
            DataRequired(message='You must provide a valid email to login!'), 
            Length(max=50)
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='You must provide a password to continue!'),
            Length(
                min=4,
                message='Password must be more than 4 characters long.'
            )
        ]
    )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

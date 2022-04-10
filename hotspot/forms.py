from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.fields import DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed
from hotspot.models import User
from flask_login import current_user

from string import ascii_letters, digits

from datetime import datetime

def get_location():
    if current_user != None:
        return current_user.location
    return 'Location'

class Sign_up_form(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    username = StringField('User Name', validators=[DataRequired(), Length(min=3, max=20)])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    mobile = StringField('Phone', validators=[DataRequired(), Length(min=10, max=10)])
    location = StringField('Location', validators=[DataRequired(), Length(max=20)])

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Password doesn't match")])

    submit = SubmitField('Sign Up!')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The Username is Already taken')
        else:
            for i in username.data:
                print(i)
                if i not in ascii_letters+digits:
                    raise ValidationError('Username should contain only Alphanumeric characters')    

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Account already exists')

    def validate_mobile(self, mobile):
        try:
            n = int(mobile.data)
        except:
            raise ValidationError('Invalid Mobile Number')
    
    def validate_dob(self, dob):
        d = datetime.now().strftime('%Y-%m-%d')
        #yr = int(datetime.now().strftime('%Y')) 
        # threshold for account creation can be added
        if str(dob.data) >= d:
            raise ValidationError('Invalid DOB')
        
class Login_form(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class Reset_request_form(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    submit = SubmitField('Get Reset Link')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('No such account exists')

class Reset_password_form(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Password doesn't match")])

    submit = SubmitField('Reset')

class Create_resouce(FlaskForm):
    name = StringField('Resource Name', validators=[DataRequired(), Length(min=5, max=20)])
    tag = StringField('Tag', validators=[DataRequired(), Length(min=2, max=15)])
    description = name = StringField('Resource Description', validators=[DataRequired(), Length(min=10, max=50)])
    picture = FileField('Resource Image', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'JPG, JPEG and PNG are only allowed')])
    cost = StringField('Cost', default='0')
    #owner = StringField('', validators=[DataRequired(), Length(min=3, max=20)])
    location = StringField('Location', default=get_location, validators=[DataRequired(), Length(min=5, max=20)])
    expiry = DateField('Expiry Date', validators=[DataRequired()])

    submit = SubmitField('Create')

    def validate_expiry(self, expiry):
        d = datetime.now().strftime('%Y-%m-%d')
        if str(expiry.data) < d:
            raise ValidationError('Invalid Expiry Date!')


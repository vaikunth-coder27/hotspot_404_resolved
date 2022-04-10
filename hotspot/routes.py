from flask import render_template, url_for, flash, redirect, request
from hotspot import app, db, bcrypt

from hotspot.models import User, Resource
from hotspot.forms import Sign_up_form, Login_form, Reset_request_form, Reset_password_form, Create_resouce

from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename

import random
import string

@app.route('/')
def front():
    return redirect(url_for('login'))

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        flash('Already Logged In. Please Log Out to Register', 'info')
        return redirect(url_for('dashboard'))

    form = Sign_up_form()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, 
                    password=hashed_password, dob=form.dob.data, 
                    mobile=form.mobile.data, location=form.location.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created for { form.username.data } ! You can now log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', title='Join Us Today', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash('Already Logged In.', 'info')
        return redirect(url_for('dashboard'))

    form = Login_form()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


def send_reset_email(user):
    m = 5
    token = user.get_reset_token(m*60) #120 sec valid token
    subject = 'Password Reset Request'
    to = user.email
    body = f'''
    To reset Password, Click on the following link (expires in {m} mins)
    {url_for('reset_password', token=token, _external=True)}
    '''
    send_mail(to, subject, body)


@app.route('/forget_password', methods=["GET", "POST"])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = Reset_request_form()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Please check your mail for reset !', 'info')
        return redirect(url_for('login'))

    return render_template('password_reset.html', title='Forgot Password', form=form)

@app.route('/forget_password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid request or Expired token !!!', 'warning')
        return redirect(url_for('forget_password'))
    
    form = Reset_password_form()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been reset! ', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', title='Reset Password',form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    posts = Resource.query.all()
    cart_items = current_user.cart
    if not cart_items:
        cart_items = ''
    return render_template('home.html', items=posts, cart_items=cart_items)

def searchfeed(tag):
    return Resource.query.filter_by(tag=tag).all()

def all_resources():
    return Resource.query.all()

@app.route('/resources')
@login_required
def rsrcs():
    cart_items = current_user.cart
    if not cart_items:
        cart_items = ''
    return render_template('resources.html', rsrcs=all_resources(), cart_items=cart_items)

@app.route('/searchfeed')
@login_required
def search():
    tag = request.args.get('tag')
    cart_items = current_user.cart
    if not cart_items:
        cart_items = ''
    return render_template('searchfeed.html', items=searchfeed(tag), cart_items=cart_items)

@app.route('/newpost', methods=['GET', 'POST'])
@login_required
def newpost():
    form = Create_resouce()
    r_id=''
    for i in range(3):
        r_id+=''.join(random.choice(string.ascii_letters) for x in range(3))
        r_id+='-'
    r_id = r_id[:-2]
    #print(f'\n\n\n{form.validate_on_submit()}')
    if form.validate_on_submit():
        filename = r_id + '_' + secure_filename(form.picture.data.filename)

        form.picture.data.save( os.path.join('hotspot/static/uploads', filename))
    
        rsrc = Resource(id=r_id, tag=form.tag.data,
                        title=form.name.data, description=form.description.data, cost=form.cost.data,
                        owner=current_user.username, owner_number=current_user.mobile,
                        location=form.location.data, expiry=str(form.expiry.data),
                        picture=filename)

        db.session.add(rsrc)
        db.session.commit()
        #print("\n\ndone done done\n\n\n")

        flash(f'Resouce {form.name.data} Created', 'success')
        return redirect(url_for('dashboard'))


    return render_template('newpost.html', form=form)

def cart_items():
    resources = []
    c = current_user.cart
    
    if c == None:
        return -1

    for i in c.split(',')[:-1]:
        r = Resource.query.filter_by(id=i).first()
        if r:
            resources.append(r)

    return resources    

@app.route('/cart_items')
@login_required
def cart():
    return render_template('cart.html', items=cart_items())

@app.route('/add-cart/<id_>')
@login_required
def add_to_cart(id_):
    r = Resource.query.filter_by(id=id_).first()
    if r:
        c = current_user.cart
        if c == None:
            current_user.cart = r.id + ','
        elif r not in c.split(','):
            current_user.cart += r.id + ','
            flash('Item successfully added to cart !', 'success')
        else:
            flash('Already in Cart !', 'info')
        db.session.commit()
    return redirect(request.referrer)


@app.route('/delete_resource/<id>')
def delete_resource(id):
    r = Resource.query.filter_by(id=id).first()
    if r.owner != current_user.username:
        flash('Operation not possible !', 'danger')
    else:
        os.remove(os.path.join('hotspot/static/uploads', r.picture))

        Resource.query.filter_by(id=id).delete()
        db.session.commit()

        flash('Resource Deleted !', 'success')

    return redirect(request.referrer)
@app.route('/profile')
@login_required
def profile():
    items = Resource.query.filter_by(owner=current_user.username)
    return render_template('profile.html', items=items)


@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Successfully Logged Out!', 'success')
    
    return redirect(url_for('login'))

@app.errorhandler(404)	
def page_not_found(e):	
    return 'Error 404: No Such Endpoint'
    #return render_template('page_not_found.html')	

@app.errorhandler(405)	
def method_not_allowed(e):	
    return 'Error 405: Method Not Allowed'
    #return render_template('method_not_allowed.html')	


#***************************************
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import mimetypes

import os

def send_mail(to, subject, body, format='plain', attachments=[]):
    creds = None
    SCOPES = ['https://mail.google.com/']
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    file_attachments = attachments

    #html = ''
    #with open('message.html') as msg:
    #    html += msg.read()

    #create email
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = to
    mimeMessage['subject'] = subject
    #mimeMessage.attach(MIMEText(html,'html'))
    mimeMessage.attach(MIMEText(body, format))

    for attachment in file_attachments:
        content_type, encoding = mimetypes.guess_type(attachment)
        main_type, sub_type = content_type.split('/', 1)
        file_name = os.path.basename(attachment)

        with open(attachment, 'rb') as f:
            myFile = MIMEBase(main_type, sub_type)
            myFile.set_payload(f.read())
            myFile.add_header('Content-Disposition', attachment, filename=file_name)
            encoders.encode_base64(myFile)

        mimeMessage.attach(myFile)


    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()


    message = service.users().messages().send(
        userId='me',
        body={'raw': raw_string}).execute()

    return message

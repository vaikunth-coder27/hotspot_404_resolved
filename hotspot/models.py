from email.policy import default
from hotspot import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    mobile = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(20), nullable=False)
    tags = db.Column(db.String(120))
    cart = db.Column(db.String(120), default='')

    def get_reset_token(self, expiry_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expiry_sec)
        return s.dumps( {'user_id': self.id} ).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.dob}', '{self.profile_pic}')"


'''class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    
    content = db.Column(db.String(100), nullable=False)
    cnt_by = db.Column(db.String(20), nullable=False)
'''
class Resource(db.Model):
    sno = db.Column(db.Integer, primary_key=True)

    id = db.Column(db.String(10), unique=True, nullable=False)
    tag = db.Column(db.String(15), nullable=False)
    title = db.Column(db.String(20), nullable=False)
    #status = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(50), nullable=False)
    picture = db.Column(db.String(40), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.String(20), nullable=False)
    owner_number = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(20), nullable=False)
    expiry = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'{self.id} : {self.tag} : {self.title} : {self.description} : {self.cost} : {self.owner} : {self.location} : {self.expiry}'

if "database.db" not in os.listdir():
    db.create_all()
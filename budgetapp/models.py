from budgetapp import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(12), nullable=False)
    dep_num= db.Column(db.String(12), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.department}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    department = db.Column(db.Text, nullable=False)
    dep_num= db.Column(db.String(12), nullable=False) #Sub-department
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Text, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', {self.department})"

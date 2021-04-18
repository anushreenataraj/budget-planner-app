from flask import render_template, url_for, flash, redirect, request
from budgetapp.forms import RegistrationForm, LoginForm, UpdateAccountForm
from budgetapp.models import User, Post
from budgetapp import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

posts =[
    {
        "author": "admin",
        "title": "Budget Update",
        "content": "FY21 quarterly earnings are likely to be 30 percent higher than the target.",
        "date_posted": "24 January, 2021"
    },
    {
        "author": "admin",
        "title": "December 2020 quarter",
        "content": "Company's deal pipeline continues to be healthy and strong as the profits jumped by 65.7 percent.",
        "date_posted": "12 January, 2021"
    }
]
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/operations")
@login_required
def revenue():
    return render_template('operations.html', title='Operations')

@app.route("/marketing")
@login_required
def expense():
    return render_template('marketing.html', title='Marketing')

@app.route("/sales")
@login_required
def expense():
    return render_template('sales.html', title='Sales')

@app.route("/register", methods = ["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'register', form =  form)

@app.route("/login", methods = ["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsucessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods = ["POST", "GET"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)
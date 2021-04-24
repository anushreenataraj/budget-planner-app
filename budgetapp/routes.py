from flask import render_template, url_for, flash, redirect, request
from budgetapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, DeleteAccountForm, CheckAccountForm
from budgetapp.models import User, Post
from budgetapp import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
import numpy as np

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


page_access = 0
@app.route("/home")
@login_required
def home():
    return render_template('home.html', posts=posts)

@app.route("/operations")
@login_required
def operations():
    global page_access
    if page_access == 1:
        return render_template('operations.html', title='Operations')
    elif page_access == 2:
        return render_template('operations.html', title='Operations')
    else:
        return render_template('no_access_page.html')

@app.route("/marketing")
@login_required
def marketing():
    global page_access
    if page_access == 1:
        return render_template('marketing.html', title='Marketing')
    elif page_access == 3:
        return render_template('marketing.html', title='Marketing')
    else:
        return render_template('no_access_page.html')

@app.route("/sales")
@login_required
def sales():
    global page_access
    if page_access == 1:
        return render_template('sales.html', title='Sales')
    elif page_access == 4:
        return render_template('sales.html', title='Sales')
    else:
        return render_template('no_access_page.html')

@app.route("/register", methods = ["POST", "GET"])
@login_required
def register():
    form = RegistrationForm()
    if page_access == 1:
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data,department=form.department.data,password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash(f'Account Has Been Created Successfully', 'success')
            return render_template('home.html', page_access=page_access)
        return render_template('register.html', title = 'register', form = form)
    else:
        return render_template('no_access_page.html')


@app.route("/delete_account",methods = ["POST", "GET"])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if page_access == 1:
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('Account Has Been Deleted Successfully', 'success')
                return redirect(url_for('home'))
        return render_template('delete_user.html', form=form)

@app.route("/", methods = ["POST", "GET"])
def login():
    global user
    global page_access
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if user.department == 'Admin':
                page_access = 1
            elif user.department == 'Operations':
                page_access = 2
            elif user.department == 'Marketing':
                page_access = 3
            elif user.department == 'Sales':
                page_access = 4
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else render_template('home.html',page_access=page_access)
        else:
            flash('Login Unsucessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')

@app.route("/account", methods = ["POST", "GET"])
@login_required
def account():
    departments = ['', 'Admin', 'Operations', 'Marketing', 'Sales'][page_access]
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
    return render_template('account.html', title='Account', form=form, user_access=page_access, user_department=departments)

@app.route('/checkuser', methods=['GET', 'POST'])
@login_required
def check_user():
    form = CheckAccountForm()
    if page_access == 1:
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                return render_template('check_user.html', user=user, form=form)
            else:
                flash('account not exists', 'warning')
        return render_template('check_user.html', form=form)
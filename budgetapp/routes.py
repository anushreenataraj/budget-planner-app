from flask import render_template, url_for, flash, redirect, request
from budgetapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, DeleteAccountForm, CheckAccountForm, PostForm, DeletePostForm
from budgetapp.models import User, Post
from budgetapp import app, db, bcrypt, dropzone
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
import io,os,csv
import requests
from werkzeug.utils import secure_filename
from flask_dropzone import Dropzone

page_access = 0
def find(l,k):
    count=0
    for i in l:
        if i == k:
            count=count+1
        if i.isalpha():
            count=count+1
    if count>1:
        return 1
    return 0

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route("/home")
@login_required
def home():
    posts = Post.query.filter_by(department='Admin')
<<<<<<< HEAD
    return render_template('home.html', posts=posts,active_h='active')
file_o=file_m=file_s=''
@app.route("/operations", methods=['POST','GET'])
=======
    return render_template('home.html', posts=posts, active_h='active')

@app.route("/operations")
>>>>>>> 50bbbdac634b2434b25a7bd9a85b6c8d662d6d34
@login_required
def operations():
    global page_access,file_o
    posts = Post.query.filter_by(department='Operations')
<<<<<<< HEAD
    data=[]
    expense=[]
    revenue=[]
    label=[]
    if request.method=="POST":
        f = request.files['csvfile']
        if f.filename == '':
            file_o=''
            return redirect(url_for('operations'))
        elif f:
            filename = secure_filename(f.filename)
            file_o= filename
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as file:
            csvfile=csv.reader(file)
            k=''
            for row in csvfile:
                if find(row,k)==0:
                    data.append(row)
        for i in data:
            label.append(i[1])
            expense.append(int(i[2]))
            revenue.append(int(i[3]))
        labels=','.join(label)
        return render_template("operations.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_o='active')
    if file_o:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], file_o)) as file:
            csvfile=csv.reader(file)
            k=''
            for row in csvfile:
                if find(row,k)==0:
                    data.append(row)
        for i in data:
            label.append(i[1])
            expense.append(int(i[2]))
            revenue.append(int(i[3]))
        labels=','.join(label)
        return render_template("operations.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_o='active')
    if page_access == 1 or page_access == 2:
        return render_template('operations.html', title='Operations', posts=posts,active_o='active')
    else:
        return render_template('no_access_page.html',active_o='active')
=======
    if page_access == 1:
        return render_template('operations.html', title='Operations', posts=posts, active_o='active')
    elif page_access == 2:
        return render_template('operations.html', title='Operations', posts=posts, active_o='active')
    else:
        return render_template('no_access_page.html', active_o='active')
>>>>>>> 50bbbdac634b2434b25a7bd9a85b6c8d662d6d34

@app.route("/marketing",methods = ["POST", "GET"])
@login_required
def marketing():
    global page_access,file_m
    data=[]
    expense=[]
    revenue=[]
    label=[]
    posts = Post.query.filter_by(department='Marketing')
<<<<<<< HEAD
    if request.method=="POST":
        f = request.files['csvfile']
        if f.filename == '':
            file_m=''
            return redirect(url_for('marketing'))
        elif f:
            filename = secure_filename(f.filename)
            file_m= filename
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as file:
            csvfile=csv.reader(file)
            k=''
            for row in csvfile:
                if find(row,k)==0:
                    data.append(row)
        for i in data:
            label.append(i[1])
            expense.append(int(i[2]))
            revenue.append(int(i[3]))
        labels=','.join(label)
        return render_template("marketing.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_m='active')
    if file_m:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], file_m)) as file:
            csvfile=csv.reader(file)
            k=''
            for row in csvfile:
                if find(row,k)==0:
                    data.append(row)
        for i in data:
            label.append(i[1])
            expense.append(int(i[2]))
            revenue.append(int(i[3]))
        labels=','.join(label)
        return render_template("marketing.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_m='active')
    if page_access == 1 or page_access == 3:
        return render_template('marketing.html', title='Marketing', posts=posts,active_m='active')
    else:
        return render_template('no_access_page.html',active_m='active')
=======
    if page_access == 1:
        return render_template('marketing.html', title='Marketing', posts=posts, active_m='active')
    elif page_access == 3:
        return render_template('marketing.html', title='Marketing', posts=posts, active_m='active')
    else:
        return render_template('no_access_page.html', active_m='active')
>>>>>>> 50bbbdac634b2434b25a7bd9a85b6c8d662d6d34

@app.route("/sales",methods = ["POST", "GET"])
@login_required
def sales():
    global page_access,file_s
    posts = Post.query.filter_by(department='Sales')
<<<<<<< HEAD
    data=[]
    expense=[]
    revenue=[]
    label=[]
    if request.method=="POST":
        f = request.files['csvfile']
        if f.filename == '':
            file_s=''
            return redirect(url_for('sales'))
        elif f:
            filename = secure_filename(f.filename)
            file_s= filename
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as file:
            csvfile=csv.reader(file)
            k=''
            for row in csvfile:
                if find(row,k)==0:
                    data.append(row)
        for i in data:
            label.append(i[1])
            expense.append(int(i[2]))
            revenue.append(int(i[3]))
        labels=','.join(label)
        return render_template("sales.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_s='active')
    if file_s:
        with open(os.path.join(app.config['UPLOAD_FOLDER'], file_s)) as file:
            csvfile=csv.reader(file)
            k=''
            for row in csvfile:
                if find(row,k)==0:
                    data.append(row)
        for i in data:
            label.append(i[1])
            expense.append(int(i[2]))
            revenue.append(int(i[3]))
        labels=','.join(label)
        return render_template("sales.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_s='active')
    if page_access == 1 or page_access == 4:
        return render_template('sales.html', title='Sales', posts=posts,active_s='active')
=======
    if page_access == 1:
        return render_template('sales.html', title='Sales', posts=posts, active_s='active')
    elif page_access == 4:
        return render_template('sales.html', title='Sales', posts=posts, active_s='active')
>>>>>>> 50bbbdac634b2434b25a7bd9a85b6c8d662d6d34
    else:
        return render_template('no_access_page.html',active_s='active')

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
    else:
        return render_template('no_access_page.html')

@app.route("/", methods = ["POST", "GET"])
def login():
    global user
    global page_access
    global file_m,file_s,file_o
    file_m=file_s=file_o=''
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
    return render_template('account.html', title='Account', form=form, user_access=page_access, user_department=departments, active_a='active')

@app.route('/checkuser', methods=['GET', 'POST'])
@login_required
def check_user():
    form = CheckAccountForm()
    if page_access == 1:
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                print(User.query.all())
                return render_template('check_user.html', user=user, form=form, users=User.query.all())
            else:
                print(User.query.all())
                flash('No Account found', 'warning')
        return render_template('check_user.html', form=form, users=User.query.all())
    else:
        return render_template('no_access_page.html')

@app.route('/Dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    posts = Post.query.all()
    departments = ['', 'Admin', 'Operations', 'Marketing', 'Sales'][page_access]
<<<<<<< HEAD
    return render_template('dashboard.html', department=departments, user=current_user, page_access=page_access, posts=posts,active_d='active')
=======
    return render_template('dashboard.html', department=departments, user=current_user, page_access=page_access, posts=posts, active_d='active')
>>>>>>> 50bbbdac634b2434b25a7bd9a85b6c8d662d6d34

@app.route('/new_post', methods=['POST', 'GET'])
@login_required
def create_new_post():
    form = PostForm()
    if form.validate_on_submit():
        departments = ['', 'Admin', 'Operations', 'Marketing', 'Sales'][page_access]
        post = Post.query.filter_by(title=form.title.data).first()
        if post:
            flash('Post with Same Title Already exists', 'warning')
        else:
            post = Post(title=form.title.data, content=form.content.data, author=current_user, department=departments)
            flash('Post Created Successfully', 'success')
            db.session.add(post)
            db.session.commit()
    return render_template('new_post.html', form=form)

@app.route('/delete_post', methods=['POST', 'GET'])
@login_required
def delete_post():
    form = DeletePostForm()
    departments = ['', 'Admin', 'Operations', 'Marketing', 'Sales'][page_access]
    if form.validate_on_submit():
        post = Post.query.filter_by(title=form.title.data).first()
        if post:
            if post.author.username == current_user:
                flash('Post deleted successfully', 'success')
                db.session.delete(post)
                db.session.commit()
            elif post.department == departments:
                flash('Post deleted successfully', 'success')
                db.session.delete(post)
                db.session.commit()
            else:
                flash('You Cannot Delete This Post', 'warning')
        else:
            flash('Post not found', 'warning')
    return render_template('delete_post.html', form=form)


<<<<<<< HEAD
        
=======
def find(l,k):
    count=0
    for i in l:
        if i == k:
            count=count+1
    if count>2:
        return 1
    return 0



@app.route('/data', methods=['POST'])
@login_required
def data():
    posts = Post.query.filter_by(department='Operations')
    if request.method=="POST":
        f = request.files['csvfile']
        if f.filename == '':
            return redirect(url_for('operations'))
        elif f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data=[]
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as file:
            csvfile=csv.reader(file)
            k=''
            for row in csvfile:
                if find(row,k)==0:
                    data.append(row)
        return render_template("sales.html",data=data)

>>>>>>> 50bbbdac634b2434b25a7bd9a85b6c8d662d6d34

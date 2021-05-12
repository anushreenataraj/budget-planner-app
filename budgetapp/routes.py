from flask import render_template, url_for, flash, redirect, request
from budgetapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, DeleteAccountForm, CheckAccountForm, PostForm, DeletePostForm
from budgetapp.models import User, Post
from budgetapp import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
import io,os,csv
import requests
from werkzeug.utils import secure_filename
from datetime import datetime

page_access = 0
def avg(list):
    total=0
    for i in list:
        total=total+i
    return (total/len(list))
def total(list):
    tot=0
    for i in list:
        tot=tot+i
    return (tot)
def clean(filename):
    data=[]
    u=[]
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'r') as file:
        csvfile=csv.reader(file)
        for row in csvfile:
            data.append(row)
        for i in data:
            for j in i:
                count=i.count('')
                for k in range(count):
                    i.remove('')
        for i in data:
            if len(i)>1:
                u.append(i)
                k=u.index(i)
                u[k][0]=str(k+1)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'w',newline='') as file:
        writer = csv.writer(file, escapechar='/', quoting=csv.QUOTE_NONE)
        writer.writerows(u)
@login_required
def post_add(filename,dep):
    global today
    p= filename+"\n"
    now=datetime.now()
    dt=now.strftime(" %d-%b-%Y (%H:%M)")
    t='Monthly '+dep+' Details'+dt
    d=dict()
    u=[]
    count=0;
    clean(filename)
    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    for i in df.columns:
        u.append(i)
    if "Category" not in u:
        if "category" not in u:
            return -1
    for i in df.columns:
        if i.isnumeric() or i.upper() == "CATEGORY":
            continue
        else:
            d['Total'+" "+i]= df[i].sum()
            d['Avgerage'+" "+i]=round(df[i].mean(),2)
            d['Maximum'+" "+i]= df[i].max()
            d['Minimum'+" "+i]= df[i].min() 
    for k in d:
        p = p+str(k)+" : Rs"+str(d[k])+"\n" 
    post = Post.query.filter_by(title=t).first()
    if post:
        print("Post already exist")
        return 0
    else:
        post = Post(title=t, content=p, author=current_user, department=dep)
        db.session.add(post)
        db.session.commit() 
        return 1        

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route("/home")
@login_required
def home():
    Dep=['Admin', 'Operations', 'Marketing', 'Sales']
    file=dict()
    for i in Dep:
        file[i]=Post.query.filter_by(department=i)
    return render_template('home.html',dep=file,active_h='active')
file_o=file_m=file_s=''
@app.route("/operations", methods=['POST','GET'])
@login_required
def operations():
    posts= Post.query.filter_by(department='Operations')
    global page_access,file_o
    data=[]
    expense=[]
    revenue=[]
    label=[]
    if page_access == 1 or page_access == 2:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename == '':
                return redirect(url_for('operations'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('operations'))
            clean(filename)
            k=post_add(filename,'Operations')
            if k==0:
                flash('Post Already exist', 'warning')
                return redirect(url_for('operations'))
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('operations'))
            else :
                flash('Post added Sucessfully', 'success')
                file_o = filename
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as file:
                csvfile=csv.reader(file)
                for row in csvfile:
                    if row[1].isalpha():
                        continue
                    else:
                        data.append(row)
            for i in data:
                label.append(i[1])
                expense.append(int(i[2]))
                revenue.append(int(i[3]))
            labels=','.join(label)
            posts= Post.query.filter_by(department='Operations')
            return render_template("operations.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_o='active')
        elif file_o :
            with open(os.path.join(app.config['UPLOAD_FOLDER'], file_o)) as file:
                csvfile=csv.reader(file)
                for row in csvfile:
                    if row[1].isalpha():
                        continue
                    else:
                        data.append(row)
            for i in data:
                label.append(i[1])
                expense.append(int(i[2]))
                revenue.append(int(i[3]))
            labels=','.join(label)
            return render_template("operations.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_o='active')
        else:
            return render_template('operations.html', title='Operations', posts=posts,active_o='active')
    else:
        return render_template('no_access_page.html',active_o='active')

@app.route("/marketing",methods = ["POST", "GET"])
@login_required
def marketing():
    global page_access,file_m
    data=[]
    expense=[]
    revenue=[]
    label=[]
    posts = Post.query.filter_by(department='Marketing')
    if page_access == 1 or page_access == 3:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename == '':
                return redirect(url_for('marketing'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('marketing'))
            clean(filename)
            k=post_add(filename,'Marketing')
            if k==0:
                flash('Post Already exist', 'warning')
                return redirect(url_for('marketing'))
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('marketing'))
            else:
                flash('Post added Sucessfully', 'success')
                file_m = filename
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as file:
                csvfile=csv.reader(file)
                for row in csvfile:
                    if row[1].isalpha():
                        continue
                    else:
                        data.append(row)
            for i in data:
                label.append(i[1])
                expense.append(int(i[2]))
                revenue.append(int(i[3]))
            labels=','.join(label)
            posts= Post.query.filter_by(department='Marketing')
            return render_template("marketing.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_m='active')
        elif file_m:
            with open(os.path.join(app.config['UPLOAD_FOLDER'], file_m)) as file:
                csvfile=csv.reader(file)
                for row in csvfile:
                    if row[1].isalpha():
                        continue
                    else:
                        data.append(row)
            for i in data:
                label.append(i[1])
                expense.append(int(i[2]))
                revenue.append(int(i[3]))
            labels=','.join(label)
            return render_template("marketing.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_m='active')
        else:
            return render_template('marketing.html', title='Marketing', posts=posts,active_m='active')
    else:
        return render_template('no_access_page.html',active_m='active')

@app.route("/sales",methods = ["POST", "GET"])
@login_required
def sales():
    global page_access,file_s
    posts = Post.query.filter_by(department='Sales')
    data=[]
    expense=[]
    revenue=[]
    label=[]
    if page_access == 1 or page_access == 4:
        if request.method=="POST":
            print("in post")
            f = request.files['csvfile']
            if f.filename == '':
                return redirect(url_for('sales'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('sales'))
            clean(filename)
            k=post_add(filename,'Sales')
            if k==0:
                flash('Post Already exist', 'warning')
                return redirect(url_for('sales'))
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('sales'))
            else:
                flash('Post added Sucessfully', 'success')
                file_s = filename
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as file:
                csvfile=csv.reader(file)
                for row in csvfile:
                    if row[1].isalpha():
                        continue
                    else:
                        data.append(row)
            for i in data:
                label.append(i[1])
                expense.append(int(i[2]))
                revenue.append(int(i[3]))
            labels=','.join(label)
            posts= Post.query.filter_by(department='Sales')
            return render_template("sales.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_s='active')
        elif file_s:
            with open(os.path.join(app.config['UPLOAD_FOLDER'],file_s)) as file:
                csvfile=csv.reader(file)
                for row in csvfile:
                    if row[1].isalpha():
                        continue
                    else:
                        data.append(row)
            for i in data:
                label.append(i[1])
                expense.append(int(i[2]))
                revenue.append(int(i[3]))
            labels=','.join(label)
            return render_template("sales.html",posts=posts,labels=labels,rev=revenue,exp=expense,active_s='active')
        else:
            return render_template('sales.html', title='Sales', posts=posts,active_s='active')
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
                print(page_access)
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
    return render_template('dashboard.html', department=departments, user=current_user, page_access=page_access, posts=posts,active_d='active')

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
            if post.author.username == current_user.username:
                flash('Post deleted successfully', 'success')
                db.session.delete(post)
                db.session.commit()
            elif departments == 'Admin':
                flash('Post deleted successfully', 'success')
                db.session.delete(post)
                db.session.commit()
            else:
                flash('You Cannot Delete This Post', 'warning')
        else:
            flash('Post not found', 'warning')
        
    return render_template('delete_post.html', form=form)

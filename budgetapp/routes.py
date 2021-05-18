from flask import render_template, url_for, flash, redirect, request
from budgetapp.forms import RegistrationForm,RegistrationForm_Ope,RegistrationForm_Mar,RegistrationForm_Sal, LoginForm, UpdateAccountForm, DeleteAccountForm, CheckAccountForm, PostForm, DeletePostForm
from budgetapp.models import User, Post
from budgetapp import app, db, bcrypt,mail
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
import io,os,csv
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail, Message

page_access = 0;h=0
o=ope=0
m=mar=0
s=sal=0
file_o_1=file_o_2=file_o_3=''
file_m_1=file_m_2=file_m_3=''
file_s_1=file_s_2=file_s_3=''
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
def post_add(filename,dep,dep_num):
    global today
    p= filename+"\n"
    now=datetime.now()
    dt=now.strftime(" %d-%b-%Y (%H:%M)")
    t='Monthly '+dep_num+' Details'+dt
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
        post = Post(title=t, content=p, author=current_user, department=dep,dep_num=dep_num)
        db.session.add(post)
        db.session.commit() 
        return 1   
@login_required
def func_2(file):
    val=[]
    data=[]
    expense=[]
    revenue=[]
    label=[]
    cat=[]
    with open(os.path.join(app.config['UPLOAD_FOLDER'], file)) as file:
        csvfile=csv.reader(file)
        for row in csvfile:
            data.append(row)
    for i in range(len(data)):
        if i==0:
            cat.append(data[i][1])
            cat.append(data[i][2])
            cat.append(data[i][3])
        else:
            label.append(data[i][1])
            expense.append(int(data[i][2]))
            revenue.append(int(data[i][3]))
    val.append(cat)
    val.append(label)
    val.append(expense)
    val.append(revenue)
    return(val)
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404
def if_post(post):
    c=0;
    for i in post:
        c=c+1
    if c==0:
        return 0
    return 1

@app.route("/home")
@login_required
def home():
    global h,o,s,m
    Dep=['Admin', 'Operations', 'Marketing', 'Sales']
    file=dict()
    for i in Dep:
        post=Post.query.filter_by(department=i)
        if if_post(post):
            file[i]=post
    return render_template('home.html',dep=file,active_h='active',h=h,o=o,s=s,m=m)
@app.route("/return", methods=['POST','GET'])
@login_required
def go_back():
    global h,o,s,m
    h=1;o=0;m=0;s=0
    Dep=['Admin', 'Operations', 'Marketing', 'Sales']
    file=dict()
    for i in Dep:
        post=Post.query.filter_by(department=i)
        if if_post(post):
            file[i]=post
    return render_template('home.html',dep=file,active_h='active',h=h,o=o,s=s,m=m)
@app.route("/operations")
@login_required
def operations():
    global page_access,o,m,s,h
    if page_access==1 or page_access==2:
        Dep_num=['Dep-Admin', 'Operations-Dep:1', 'Operations-Dep:2', 'Operations-Dep:3']
        file=dict() 
        for i in Dep_num:
            post=Post.query.filter_by(department="Operations",dep_num=i)
            if if_post(post):
                file[i]=post
        o=1;m=0;s=0;h=0
    else:
        o=0
        return render_template('no_access_page.html',active_o='active',h=h,o=o,s=s,m=m)
    return render_template('home.html',active_h='active',h=h,o=o,s=s,m=m,dep=file)
@app.route("/marketing")
@login_required
def marketing():
    global page_access,m,o,s,h
    if page_access==1 or page_access==3:
        Dep_num=['Dep-Admin', 'Marketing-Dep:1', 'Marketing-Dep:2', 'Marketing-Dep:3']
        file=dict()
        for i in Dep_num:
            post=Post.query.filter_by(department="Marketing",dep_num=i)
            if if_post(post):
                file[i]=post
        m=1;s=0;o=0;h=0
    else:
        m=0
        return render_template('no_access_page.html',active_m='active',h=h,o=o,s=s,m=m)
    return render_template('home.html',active_h='active',h=h,o=o,s=s,m=m,dep=file)
@app.route("/sales")
@login_required
def sales():
    global page_access,s,m,o,h
    if page_access==1 or page_access==4:
        Dep_num=['Dep-Admin', 'Sales-Dep:1', 'Sales-Dep:2', 'Sales-Dep:3']
        file=dict()
        for i in Dep_num:
            post=Post.query.filter_by(department="Sales",dep_num=i)
            if if_post(post):
                file[i]=post
        s=1;m=0;o=0;h=0
    else:
        s=0
        return render_template('no_access_page.html',active_s='active',h=h,o=o,s=s,m=m)
    return render_template('home.html',active_h='active',h=h,o=o,s=s,m=m,dep=file)

@app.route("/operations/department-1", methods=['POST','GET'])
@login_required
def operations_1():
    posts= Post.query.filter_by(department='Operations',dep_num='Operations-Dep:1')
    global ope,file_o_1,h,o
    data=[]
    if ope == 1 or ope == 2:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename=='':
                return redirect(url_for('operations_1'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('operations_1'))
            clean(filename)
            k=post_add(filename,'Operations','Operations-Dep:1')
            if k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('operations_1'))
            else :
                flash('Post added Sucessfully', 'success')
                file_o_1 = filename
            data=func_2(filename)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            posts= Post.query.filter_by(department='Operations',dep_num='Operations-Dep:1')
            return render_template("operations_1.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_o_1='active',h=h,o=o)
        elif file_o_1 :
            data=func_2(file_o_1)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            return render_template("operations_1.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_o_1='active',h=h,o=o)
        else:
            return render_template('operations_1.html', posts=posts,active_o_1='active',h=h,o=o)
    else:
        return render_template('no_access_page.html',active_o_1='active',h=h,o=o)
@app.route("/operations/department-2", methods=['POST','GET'])
@login_required
def operations_2():
    posts= Post.query.filter_by(department='Operations',dep_num='Operations-Dep:2')
    global ope,file_o_2,h,o
    data=[]
    if ope == 1 or ope == 3:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename=='':
                return redirect(url_for('operations_2'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('operations_2'))
            clean(filename)
            k=post_add(filename,'Operations','Operations-Dep:2')
            if k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('operations_2'))
            else :
                flash('Post added Sucessfully', 'success')
                file_o_2 = filename
            data=func_2(filename)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            posts= Post.query.filter_by(department='Operations',dep_num='Operations-Dep:2')
            return render_template("operations_2.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_o_2='active',h=h,o=o)
        elif file_o_2 :
            data=func_2(file_o_2)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            return render_template("operations_2.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_o_2='active',h=h,o=o)
        else:
            return render_template('operations_2.html', posts=posts,active_o_2='active',h=h,o=o)
    else:
        return render_template('no_access_page.html',active_o_2='active',h=h,o=o)
 
@app.route("/operations/department-3", methods=['POST','GET'])
@login_required
def operations_3():
    posts= Post.query.filter_by(department='Operations',dep_num='Operations-Dep:3')
    global ope,file_o_3,h,o
    data=[]
    if ope == 1 or ope == 4:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename=='':
                return redirect(url_for('operations_3'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('operations_3'))
            clean(filename)
            k=post_add(filename,'Operations','Operations-Dep:3')
            if k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('operations_3'))
            else :
                flash('Post added Sucessfully', 'success')
                file_o_3 = filename
            data=func_2(filename)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            posts= Post.query.filter_by(department='Operations',dep_num='Operations-Dep:3')
            return render_template("operations_3.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_o_3='active',h=h,o=o)
        elif file_o_3 :
            data=func_2(file_o_3)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            return render_template("operations_3.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_o_3='active',h=h,o=o)
        else:
            return render_template('operations_3.html', posts=posts,active_o_3='active',h=h,o=o)
    else:
        return render_template('no_access_page.html',active_o_3='active',h=h,o=o)

@app.route("/marketing/department-1",methods = ["POST", "GET"])
@login_required
def marketing_1():
    global mar,file_m_1,h,m
    data=[]
    posts = Post.query.filter_by(department='Marketing',dep_num='Marketing-Dep:1')
    if mar == 1 or mar == 2:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename=='':
                return redirect(url_for('marketing_1'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('marketing_1'))
            clean(filename)
            k=post_add(filename,'Marketing','Marketing-Dep:1')
            if k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('marketing_1'))
            else :
                flash('Post added Sucessfully', 'success')
                file_m_1 = filename
            data=func_2(filename)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            posts= Post.query.filter_by(department='Marketing',dep_num='Marketing-Dep:1')
            return render_template("marketing_1.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_m_1='active',h=h,m=m)
        elif file_m_1:
            data=func_2(file_m_1)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            return render_template("marketing_1.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_m_1='active',h=h,m=m)
        else:
            return render_template('marketing_1.html', title='Marketing', posts=posts,active_m_1='active',h=h,m=m)
    else:
        return render_template('no_access_page.html',active_m_1='active',h=h,m=m)
@app.route("/marketing/department-2",methods = ["POST", "GET"])
@login_required
def marketing_2():
    global mar,file_m_2,h,m
    data=[]
    posts = Post.query.filter_by(department='Marketing',dep_num='Marketing-Dep:2')
    if mar == 1 or mar == 3:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename=='':
                return redirect(url_for('marketing_2'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('marketing_2'))
            clean(filename)
            k=post_add(filename,'Marketing','Marketing-Dep:2')
            if k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('marketing_2'))
            else :
                flash('Post added Sucessfully', 'success')
                file_m_2 = filename
            data=func_2(filename)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            posts= Post.query.filter_by(department='Marketing',dep_num='Marketing-Dep:2')
            return render_template("marketing_2.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_m_2='active',h=h,m=m)
        elif file_m_2:
            data=func_2(file_m_2)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            return render_template("marketing_2.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_m_2='active',h=h,m=m)
        else:
            return render_template('marketing_2.html', title='Marketing', posts=posts,active_m_2='active',h=h,m=m)
    else:
        return render_template('no_access_page.html',active_m_2='active',h=h,m=m)
@app.route("/marketing/department-3",methods = ["POST", "GET"])
@login_required
def marketing_3():
    global mar,file_m_3,m,h
    data=[]
    posts = Post.query.filter_by(department='Marketing',dep_num='Marketing-Dep:3')
    if mar == 1 or mar == 4:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename=='':
                return redirect(url_for('marketing_3'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('marketing_3'))
            clean(filename)
            k=post_add(filename,'Marketing','Marketing-Dep:3')
            if k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('marketing_3'))
            else :
                flash('Post added Sucessfully', 'success')
                file_m_3 = filename
            data=func_2(filename)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            posts= Post.query.filter_by(department='Marketing',dep_num='Marketing-Dep:3')
            return render_template("marketing_3.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_m_3='active',h=h,m=m)
        elif file_m_3:
            data=func_2(file_m_3)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            return render_template("marketing_3.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_m_3='active',h=h,m=m)
        else:
            return render_template('marketing_3.html', title='Marketing', posts=posts,active_m_3='active',h=h,m=m)
    else:
        return render_template('no_access_page.html',active_m_3='active',h=h,m=m)

@app.route("/sales/department-1",methods = ["POST", "GET"])
@login_required
def sales_1():
    global sal,file_s_1,s,h
    posts = Post.query.filter_by(department='Sales',dep_num='Sales-Dep:1')
    data=[]
    if sal == 1 or sal == 2:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename=='':
                return redirect(url_for('sales_1'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('sales_1'))
            clean(filename)
            k=post_add(filename,'Sales','Sales-Dep:1')
            if k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('sales_1'))
            else :
                flash('Post added Sucessfully', 'success')
                file_s_1 = filename
            data=func_2(filename)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            posts= Post.query.filter_by(department='Sales',dep_num='Sales-Dep:1')
            return render_template("sales_1.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_s_1='active',h=h,s=s)
        elif file_s_1:
            data=func_2(file_s_1)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            return render_template("sales_1.html",posts=posts,labels=labels,rev=revenue,u=cat,exp=expense,active_s_1='active',h=h,s=s)
        else:
            return render_template('sales_1.html', title='Sales', posts=posts,active_s_1='active',h=h,s=s)
    else:
        return render_template('no_access_page.html',active_s_1='active',h=h,s=s)
@app.route("/sales/department-2",methods = ["POST", "GET"])
@login_required
def sales_2():
    global sal,file_s_2,h,s
    posts = Post.query.filter_by(department='Sales',dep_num='Sales-Dep:2')
    data=[]
    if sal == 1 or sal == 3:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename=='':
                return redirect(url_for('sales_2'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('sales_2'))
            clean(filename)
            k=post_add(filename,'Sales','Sales-Dep:2')
            if k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('sales_2'))
            else :
                flash('Post added Sucessfully', 'success')
                file_s_2 = filename
            data=func_2(filename)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            posts= Post.query.filter_by(department='Sales',dep_num='Sales-Dep:2')
            return render_template("sales_2.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_s_2='active',h=h,s=s)
        elif file_s_2:
            data=func_2(file_s_2)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            return render_template("sales_2.html",posts=posts,labels=labels,rev=revenue,u=cat,exp=expense,active_s_2='active',h=h,s=s)
        else:
            return render_template('sales_2.html', title='Sales', posts=posts,active_s_2='active',h=h,s=s)
    else:
        return render_template('no_access_page.html',active_s_2='active')
@app.route("/sales/department-3",methods = ["POST", "GET"])
@login_required
def sales_3():
    global sal,file_s_3,s,h
    posts = Post.query.filter_by(department='Sales',dep_num='Sales-Dep:3')
    data=[]
    if sal == 1 or sal == 4:
        if request.method=="POST":
            f = request.files['csvfile']
            if f.filename=='':
                return redirect(url_for('sales_3'))
            elif f:
                p=f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('sales_3'))
            clean(filename)
            k=post_add(filename,'Sales','Sales-Dep:3')
            if k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('sales_3'))
            else :
                flash('Post added Sucessfully', 'success')
                file_s_3 = filename
            data=func_2(filename)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            posts= Post.query.filter_by(department='Sales',dep_num='Sales-Dep:3')
            return render_template("sales_3.html",posts=posts,labels=labels,rev=revenue,exp=expense,u=cat,active_s_3='active',h=h,s=s)
        elif file_s_3:
            data=func_2(file_s_3)
            cat=data[0]
            label=data[1]
            expense=data[2]
            revenue=data[3]
            labels=','.join(label)
            return render_template("sales_3.html",posts=posts,labels=labels,rev=revenue,u=cat,exp=expense,active_s_3='active',h=h,s=s)
        else:
            return render_template('sales_3.html', title='Sales', posts=posts,active_s_3='active',h=h,s=s)
    else:
        return render_template('no_access_page.html',active_s_3='active',h=h,s=s)

def mail_sender(email,username,passw):
    msg = Message('Login Credentials for Budget-Management App', sender='ksdrao7@gmail.com', recipients = [email])
    msg.body = "Hello "+username+" ,Login Credentials for Budget-Management App:\n mail id: "+email+"\nPassword:"+passw
    mail.send(msg)
@app.route("/register", methods = ["POST", "GET"])
@login_required
def register():
    global h,o,m,s
    if page_access == 1:
        form = RegistrationForm();
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user1 = User(username=form.username.data, email=form.email.data,department=form.department.data,dep_num=form.dep_num.data,password=hashed_password)
            db.session.add(user1)
            db.session.commit()
            flash(f'Account Has Been Created Successfully', 'success')
            mail_sender(form.email.data,form.username.data,form.password.data)
            return render_template('home.html', page_access=page_access,h=h,o=o,m=m,s=s)
        return render_template('register.html', title = 'register',page_access=page_access, form=form,h=h,o=o,m=m,s=s)
    elif current_user.dep_num=='Dep-Admin':
        if current_user.department=="Operations":
            form = RegistrationForm_Ope();
        elif current_user.department=="Marketing":
            form = RegistrationForm_Mar();
        elif current_user.department=="Sales":
            form = RegistrationForm_Sal();
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user1 = User(username=form.username.data, email=form.email.data,department=current_user.department,dep_num=form.dep_num.data,password=hashed_password)
            db.session.add(user1)
            db.session.commit()
            flash(f'Account Has Been Created Successfully', 'success')
            mail_sender(form.email.data,form.username.data,form.password.data)
            return render_template('home.html', page_access=page_access,h=h,o=o,m=m,s=s)
        return render_template('register.html', title = 'register',form = form,h=h,o=o,m=m,s=s)
    else:
        return render_template('no_access_page.html')


@app.route("/delete_account",methods = ["POST", "GET"])
@login_required
def delete_account():
    global h,s,m,o
    form = DeleteAccountForm()
    if page_access == 1:
        if form.validate_on_submit():
            user1 = User.query.filter_by(email=form.email.data).first()
            post=Post.query.filter_by(user_id=user1.id)
            if user1:
                if post:
                    for post in post:
                        db.session.delete(post)
                db.session.delete(user1)
                db.session.commit()
                flash('Account Has Been Deleted Successfully', 'success')
                return redirect(url_for('home'))
        return render_template('delete_user.html', form=form,h=h,o=o,m=m,s=s)
    elif current_user.dep_num=='Dep-Admin':
        if form.validate_on_submit():
            user1 = User.query.filter_by(email=form.email.data).first()
            post=Post.query.filter_by(user_id=user1.id)
            if user1:
                if page_access==2:
                    if user1.department == 'Operations' and current_user.department =='Operations' :
                        if post:
                            for post in post:
                                db.session.delete(post)
                        db.session.delete(user1)
                        db.session.commit()
                elif page_access==3:
                    if user1.department  == 'Marketing' and current_user.department =='Marketing': 
                        if post:
                            for post in post:
                                db.session.delete(post)
                        db.session.delete(user1)
                        db.session.commit()
                elif page_access==4:
                    if user1.department  == 'Sales' and current_user.department =='Sales':
                        if post:
                            for post in post:
                                db.session.delete(post)
                        db.session.delete(user1)
                        db.session.commit()
                flash('Account Has Been Deleted Successfully', 'success')
                return redirect(url_for('home'))
            return render_template('delete_user.html', form=form, h=h,o=o,m=m,s=s)
    else:
        return render_template('no_access_page.html')

@app.route("/", methods = ["POST", "GET"])
def login():
    global user,o,m,s,h
    global page_access,ope,sal,mar,h
    global file_o_1,file_o_2,file_o_3,file_m_1,file_m_2,file_m_3,file_s_1,file_s_2,file_s_3
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash((user.password).encode(encoding='UTF-8') , form.password.data):
            h=1
            login_user(user, remember=form.remember.data)
            if user.department == 'admin' or user.department == 'Admin':
                page_access = 1
                ope=1;mar=1;sal=1
            elif user.department == 'Operations':
                page_access = 2
                if user.dep_num == 'Dep-Admin':
                    ope=1
                elif user.dep_num == 'Operations-Dep:1':
                    ope=2
                elif user.dep_num == 'Operations-Dep:2':
                    ope=3
                elif user.dep_num == 'Operations-Dep:3':
                    ope=4
            elif user.department == 'Marketing':
                page_access = 3
                if user.dep_num == 'Dep-Admin':
                    mar=1
                elif user.dep_num == 'Marketing-Dep:1':
                    mar=2
                elif user.dep_num == 'Marketing-Dep:2':
                    mar=3
                elif user.dep_num == 'Marketing-Dep:3':
                    mar=4
            elif user.department == 'Sales':
                page_access = 4
                if user.dep_num == 'Dep-Admin':
                    sal=1
                elif user.dep_num == 'Sales-Dep:1':
                    sal=2
                elif user.dep_num == 'Sales-Dep:2':
                    sal=3
                elif user.dep_num == 'Sales-Dep:3':
                    sal=4
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else render_template('home.html',page_access=page_access,h=h,m=m,o=o,s=s)
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
    global page_access,m,s,h,o
    form = CheckAccountForm()
    if page_access == 1:
        if form.validate_on_submit():
            user1 = User.query.filter_by(email=form.email.data).first()
            if user1:
                return render_template('check_user.html', user=user1, form=form, users=User.query.all(),h=h,o=o,m=m,s=s)
            else:
                flash('No Account found', 'warning')
        return render_template('check_user.html', form=form, users=User.query.all(),h=h,o=o,m=m,s=s)
    elif current_user.dep_num=='Dep-Admin':
        if form.validate_on_submit():
            user1 = User.query.filter_by(email=form.email.data).first()
            if user1:
                if page_access==2:
                    if user1.department == 'Operations':
                        return render_template('check_user.html', user=user1, form=form, users=User.query.all())
                elif page_access==3:
                    if user1.department  == 'Marketing': 
                        return render_template('check_user.html', user=user1, form=form, users=User.query.all())
                elif page_access==4:
                    if user1.department  == 'Sales':
                        return render_template('check_user.html', user=user1, form=form, users=User.query.all())
                else:
                    flash('No Account found', 'warning')
        return render_template('check_user.html', form=form, users=User.query.all(),h=h,o=o,m=m,s=s)
    else:
        return render_template('no_access_page.html',h=h,o=o,m=m,s=s)

@app.route('/Dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    global page_access,m,s,h,o
    posts = Post.query.all()
    departments = ['', 'Admin', 'Operations', 'Marketing', 'Sales'][page_access]
    return render_template('dashboard.html', department=departments, user=current_user,o=o,m=m,h=h,s=s, page_access=page_access,active_d='active')

@app.route('/new_post', methods=['POST', 'GET'])
@login_required
def create_new_post():
    global o,m,s,h
    form = PostForm()
    if form.validate_on_submit():
        departments = ['', 'Admin', 'Operations', 'Marketing', 'Sales'][page_access]
        post = Post.query.filter_by(title=form.title.data).first()
        if post:
            flash('Post with Same Title Already exists', 'warning')
        else:
            post = Post(title=form.title.data, content=form.content.data, author=current_user, department=departments,dep_num=current_user.dep_num)
            db.session.add(post)
            db.session.commit()
            flash('Post Created Successfully', 'success')
    return render_template('new_post.html', form=form,h=h,o=o,m=m,s=s)

@app.route('/delete_post', methods=['POST', 'GET'])
@login_required
def delete_post():
    global h,o,m,s
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
            elif post.dep_num == 'Dep-Admin':
                if post.department == departments:
                    flash('Post deleted successfully', 'success')
                    db.session.delete(post)
                    db.session.commit()
            else:
                flash('You Cannot Delete This Post', 'warning')
        else:
            flash('Post not found', 'warning')
        
    return render_template('delete_post.html', form=form,h=h,o=o,m=m,s=s)

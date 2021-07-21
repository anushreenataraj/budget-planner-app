from flask import render_template, url_for, flash, redirect, request
from budgetapp.forms import RegistrationForm,RegistrationForm_Ope,RegistrationForm_Mar,RegistrationForm_Sal,SalaryForm,MonthDataForm, UploadForm, LoginForm, UpdateAccountForm, DeleteAccountForm, CheckAccountForm,DeleteDataForm,DeleteDataForm_Sal,DeleteDataForm_Mar,DeleteDataForm_Ope
from budgetapp.models import User, Post,Data_month,Data_year
from budgetapp import app, db, bcrypt,mail
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
import os,csv
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail, Message

page_access = 0;h=0;salary=0
o=ope=0
m=mar=0
s=sal=0
filename_salary=''
file_o_1=file_o_2=file_o_3=''
file_m_1=file_m_2=file_m_3=''
file_s_1=file_s_2=file_s_3=''
@login_required
def function(k):
    count=0
    for i in k:
        i=(count,i)
    return k

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
                if i[0].isnumeric():
                    i.pop(0)
                u.append(i)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'w',newline='') as file:
        writer = csv.writer(file, escapechar='/', quoting=csv.QUOTE_NONE)
        writer.writerows(u)
@login_required
def maxi(p,q):
    t=[]
    k=max(q)
    for i in range(len(q)):
        if q[i] == k:
            t.append(p[i])
    return t
def mini(p,q):
    t=[]
    k=min(q)
    for i in range(len(q)):
        if q[i] == k:
            t.append(p[i])
    return t

@login_required
def maximum(u):
    d=dict()
    cat=u[0]
    for i in range(1,len(cat)):
        d[cat[i]]=maxi(u[1],u[i+1])
    return d
@login_required
def minimum(u):
    d=dict()
    cat=u[0]
    for i in range(1,len(cat)):
        d[cat[i]]=mini(u[1],u[i+1])
    return d

@login_required
def year_db(dep,dep_num,data,year):
    y=Data_year.query.filter_by(department=dep,dep_num=dep_num,year=year).first()
    if y:
        count=y.count
        d = eval(y.content)
        for i in d:
            d[i]=d[i]+data[i]
        y.count=count+1
        y.content=str(d)
        db.session.commit()
    else:
        y=Data_year(department=dep,dep_num=dep_num,year=year,count=1,content=str(data))
        db.session.add(y)
        db.session.commit()
@login_required
def post_add(filename,dep,dep_num,type_of_file,month,year):
    global today
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month]
    d=dict()
    
    data=dict()
    u=[]
    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    for i in df.columns:
        u.append(i)
    if len(u)!=3:
        return ()
    if "Category" not in u:
        if "category" not in u:
            return -1
    for i in df.columns:
        d_sub=dict()
        if i.isnumeric() or i.upper() == "CATEGORY":
            continue
        else:
            data[i]= df[i].sum()
            d_sub['Average']=round(df[i].mean(),2)
            d_sub['Total Ammount'] = df[i].sum()  
            d[i]=d_sub  
    post = Post.query.filter_by(month=month,year=year,dep_num=dep_num,department=dep,mode=type_of_file).first()
    if post:
        return 0
    else:
        u=func_2(filename)
        d_1=maximum(u)
        d_2=minimum(u)
        for i in d:
            if i in d_1 and i in d_2:
                new=d[i]
                new.update({'Maximum':d_1[i]})
                new.update({'Minimum':d_2[i]})
        check=Data_month.query.filter_by(department=dep,dep_num=dep_num,month=month,year=year,mode=type_of_file).first()
        if check:
            i=1
        else:   
            if type_of_file=='Actual':
                year_db(dep,dep_num,data,year)
            data1=Data_month(department=dep,dep_num=dep_num,month=month,year=year,content=str(data),mode=type_of_file)
            db.session.add(data1)
        post = Post(author=current_user, department=dep,dep_num=dep_num,month=month,year=year,content=str(u),data=str(d),mode=type_of_file)
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
            cat.append(data[i][0])
            cat.append(data[i][1])
            cat.append(data[i][2])
        else:
            label.append(data[i][0])
            expense.append(int(data[i][1]))
            revenue.append(int(data[i][2]))
    val.append(cat)
    val.append(label)
    val.append(expense)
    val.append(revenue)
    return(val)
@login_required
def year_visualization(inter_dep,from_mon,from_year,to_mon,to_year,type_of_file):
    months=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    mon=from_mon
    year=from_year
    data=[];exp=[];rev=[];val=[];labels=[]
    act=Data_month.query.filter_by(dep_num=inter_dep,mode=type_of_file,month=from_mon,year=from_year).first()
    while act:
        d = eval(act.content)
        for k in d:
            data.append(d[k])
        labels.append(months[mon]+" "+str(year))
        if year==to_year and mon==to_mon:
            break
        if mon == 12:
            mon=1
            year=year+1
        else:
            mon=mon+1
        act=Data_month.query.filter_by(dep_num=inter_dep,mode=type_of_file,month=mon,year=year).first()
    if year==to_year and mon==to_mon:
        for i in range(len(data)):
            if i%2==0:
                exp.append(data[i])
            else:
                rev.append(data[i])
        val.append(labels)
        val.append(exp)
        val.append(rev)
        return val
    else :
        return -1
@login_required
def store_salary(filename):
    data=[]
    u=[]
    p=[]
    dep=['Operations-Department:1','Operations-Department:2','Operations-Department:3', 'Marketing-Department:1','Marketing-Department:2','Marketing-Department:3','Sales-Department:1','Sales-Department:2','Sales-Department:3']
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
                if i[0].isnumeric():
                    i.pop(0)
                u.append(i)
        if len(u[0])!=4:
            return ()
        p.append(u[0])
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'w',newline='') as file:
        writer = csv.writer(file, escapechar='/', quoting=csv.QUOTE_NONE)
        writer.writerows(u)   
        while len(u):
            for i in dep:
                for j in range(1,len(u)):
                    if u[j][2] == i :
                        p.append(u[j])
                    if u[j][2] not in dep:
                        return j
                    if len(p) == len(u)-1:
                        break    
            if len(p) == len(u)-1 :
                break
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'w',newline='') as file:
        writer = csv.writer(file, escapechar='/', quoting=csv.QUOTE_NONE)
        writer.writerows(p)   
    return p 
def get_salary(filename):
    data=[]
    count=1
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'r') as file:
        csvfile=csv.reader(file)
        for row in csvfile:
            data.append(row)
        for i in data[0]:
            if type(i)!=str:
                return -1
        for i in range(1,len(data)):
            data[i].insert(0,count)
            count=count+1
    return data
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
    return c
def percent(val,num):
    p=val/num
    p=p*100
    p=round(p,2)
    return p
@login_required
def generate_data(dept,inter_dep,month,year):
    new=dict()
    d=dict()
    d1=dict()
    exp=Data_month.query.filter_by(department=dept,dep_num=inter_dep,mode='Expected',month=month,year=year).first()
    act=Data_month.query.filter_by(department=dept,dep_num=inter_dep,mode='Actual',month=month,year=year).first()
    current_year_data=Data_year.query.filter_by(department=dept,dep_num=inter_dep,year=year).first()
    last_year_data=Data_year.query.filter_by(department=dept,dep_num=inter_dep,year=year-1).first()
    last_year_current_month=Data_month.query.filter_by(department=dept,dep_num=inter_dep,mode='Actual',month=month,year=year-1).first()
    if act.month == '1':
        last_month=Data_month.query.filter_by(department=dept,dep_num=inter_dep,mode='Actual',month=12,year=year-1).first()
    else:
        last_month=Data_month.query.filter_by(department=dept,dep_num=inter_dep,mode='Actual',month=month-1,year=year).first()
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    if act:
        mon_current=mon[int(month)]
        d1=eval(act.content)
        for k in d1:
            u=[]
            if exp:
                d=eval(exp.content)
                p=[]
                val = d1[k]-d[k]
                p.append(abs(val))
                p.append("Expected vs Actual (Total "+k+" )")
                p.append(str(percent(abs(val),d1[k]))+'%')
                if val < 0:
                    p.append('danger')
                else:
                    p.append('success')
                p.append("For "+mon_current+"'s month")
                u.append(p)
            if last_month:
                mon_prev=mon[int(last_month.month)]
                l_m_data=eval(last_month.content)
                p=[]
                val = d1[k]-l_m_data[k]
                p.append(abs(val))
                p.append("Total "+k)
                p.append(str(percent(abs(val),d1[k]))+'%')
                if val < 0:
                    p.append('danger')
                else:
                    p.append('success')
                p.append(mon_prev+" - "+mon_current+"  Analysis"+" ( "+act.year+" )")
                u.append(p)
            '''if current_year_data and last_year_data:
                if current_year_data.count==12 and last_year_data.count==12:
                    c_y_data=eval(current_year_data.content)
                    l_y_data=eval(last_year_data.content)
                    p=[]
                    val = c_y_data[k]-l_y_data[k]
                    p.append(abs(val))
                    p.append("Total "+k)
                    p.append(str(percent(abs(val),d1[k]))+'%')
                    if val < 0:
                        p.append('danger')
                    else:
                        p.append('success')
                    p.append(last_year_data.year+" - "+current_year_data.year+" Analysis")
                    u.append(p)'''
            if last_year_current_month:
                l_m_data=eval(last_year_current_month.content)
                p=[]
                val = d1[k]-l_m_data[k]
                p.append(abs(val))
                p.append("Total "+k)
                p.append(str(percent(abs(val),d1[k]))+'%')
                if val < 0:
                    p.append('danger')
                else:
                    p.append('success')
                p.append(str(year-1)+" - "+str(year)+" "+mon_current+"'s Analysis")
                u.append(p)
            new[k]=u
    count=0
    for i in new:
        if len(new[i]) != 0:
            count=count+1
    if count>0:
        return new
    else:
        return -1
@login_required
def generate_tendencies(data):
    val=dict()
    for i in data:
        new=[]
        p=data[i]
        for j in p:
            k=[]
            if j == 'Average':
                k.append(j)
                k.append(p[j])
                k.append('graph')
                new.append(k)
            if j == 'Total Ammount':
                k.append(j)
                k.append(p[j])
                k.append('plus')
                new.append(k)
            if j=='Maximum':
                for u in p[j]:
                    n=[]
                    n.append(j)
                    n.append(u)
                    n.append('arrow-up')
                    new.append(n)
            if j=='Minimum':
                for u in p[j]:
                    n=[]
                    n.append(j)
                    n.append(u)
                    n.append('arrow-down')
                    new.append(n)
        val[i]=new
    return val 
@app.route("/home")
@login_required
def home():
    global h,o,s,m,page_access
    now=datetime.now()
    month = int(now.strftime("%m"))
    year = int(now.strftime("%Y"))
    file=dict()
    if month==1:
        month=12;year=year-1
    else:
        month=month-1
    Dep=['Operations-Dep:1','Operations-Dep:2','Operations-Dep:3', 'Marketing-Dep:1','Marketing-Dep:2','Marketing-Dep:3','Sales-Dep:1','Sales-Dep:2','Sales-Dep:3']
    for i in Dep:
        post = Post.query.filter_by(month=month,year=year,dep_num =i,mode='Actual').first()
        if post:
            data=eval(post.data)
            k = generate_tendencies(data)
            file[i]=k
    return render_template('home.html',dep=file,active_h='active',h=h,o=o,s=s,m=m,page_access=page_access)

@app.route("/return", methods=['POST','GET'])
@login_required
def go_back():
    global h,o,s,m,page_access
    h=1;o=0;m=0;s=0
    now=datetime.now()
    month = int(now.strftime("%m"))
    year = int(now.strftime("%Y"))
    file=dict()
    if month==1:
        month=12;year=year-1
    else:
        month=month-1
    Dep=['Operations-Dep:1','Operations-Dep:2','Operations-Dep:3', 'Marketing-Dep:1','Marketing-Dep:2','Marketing-Dep:3','Sales-Dep:1','Sales-Dep:2','Sales-Dep:3']
    for i in Dep:
        post = Post.query.filter_by(month=month,year=year,dep_num =i,mode='Actual').first()
        if post:
            data=eval(post.data)
            k = generate_tendencies(data)
            file[i]=k
    return render_template('home.html',dep=file,active_h='active',h=h,o=o,s=s,m=m,page_access=page_access)
@app.route("/operations")
@login_required
def operations():
    global page_access,o,m,s,h
    if page_access==1 or page_access==2:
        Dep_num=['Dep-Admin', 'Operations-Dep:1', 'Operations-Dep:2', 'Operations-Dep:3']
        file=dict() 
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
        s=1;m=0;o=0;h=0
    else:
        s=0
        return render_template('no_access_page.html',active_s='active',h=h,o=o,s=s,m=m)
    return render_template('home.html',active_h='active',h=h,o=o,s=s,m=m,dep=file)
@app.route("/salary", methods=['POST','GET'])
@login_required
def salary():
    global page_access,o,m,s,h,filename_salary
    data=[]
    p=[];label=''
    if page_access==1:
        form=SalaryForm()
        if form.validate_on_submit():
            f=form.file.data
            if f.filename=='':
                return redirect(url_for('salary'))
            elif f:
                p= f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('salary'))
            data=store_salary(filename)
            if type(data)== tuple:
                flash('Required columns are not mentioned', 'danger')
                return redirect(url_for('salary'))
            elif type(data)== int:
                flash('Please check the inter-department name in the line '+str(data+1), 'danger')
                return redirect(url_for('salary'))
            elif type(data)== list:
                p=get_salary(filename)
                if p==-1:
                    flash('Enter all the Categories', 'danger')
                    return redirect(url_for('salary'))
                filename_salary=filename
                return render_template('salary.html',form=form,sal=p,active_sal='active',h=h,o=o,s=s,m=m,page_access=page_access)
        elif filename_salary:
            p=get_salary(filename_salary)
            if p==-1:
                flash('Enter all the Categories', 'danger')
                return redirect(url_for('salary'))
            return render_template('salary.html',form=form,sal=p,active_sal='active',h=h,o=o,s=s,m=m,page_access=page_access)
        return render_template('salary.html',form=form,active_sal='active',h=h,o=o,s=s,m=m,page_access=page_access)
    else:
        return render_template('no_access_page.html',active_o='active',h=h,o=o,s=s,m=m,page_access=page_access)
def to_month(month,year,num):
    for i in range(1,num+1):
        if month==12:
            month=1
            year=year+1
        else:
            month=month+1
    return (month,year)
@app.route("/operations/department-1", methods=['POST','GET'])
@login_required
def operations_1():
    global ope,file_o_1,h,o
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data=[];time_period=0
    d=dict()
    if ope == 1 or ope == 2:
        form=UploadForm()
        form_1=MonthDataForm()
        if form.submit.data and form.validate():
            f=form.file.data
            month=form.month.data
            month=mon.index(month)
            year=int(form.year.data.year)
            type_of_file= form.type_of_file.data
            if f.filename=='':
                return redirect(url_for('operations_1'))
            elif f:
                p= f.filename.split(".")
                if "csv" in p:
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Uploaded file is not in csv format', 'danger')
                    return redirect(url_for('operations_1'))
            clean(filename)
            k=post_add(filename,'Operations','Operations-Dep:1',type_of_file,month,year)
            if type(data)== tuple:
                flash('Required columns are not mentioned', 'danger')
                return redirect(url_for('operations_1'))
            elif k==0:
                flash('Data already added', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
            else :
                flash('Data added Sucessfully', 'success')
            return render_template("operations_1.html",form=form,form_1=form_1,active_o_1='active',h=h,o=o) 
        if form_1.submit1.data and form_1.validate():
            type_of_file= form_1.type_of_file.data
            mode=form_1.mode.data
            month= form_1.month.data
            month=mon.index(month)
            year=int(form_1.year.data.year)
            post = Post.query.filter_by(month=month,year=year,dep_num='Operations-Dep:1',department='Operations',mode=type_of_file).first()
            if post:  
                if mode=='Monthly':
                    u=eval(post.content)
                    data=eval(post.data)
                    cat=u[0]
                    label=u[1]  
                    expense=u[2]
                    revenue=u[3]
                    labels=','.join(label)
                    k = generate_tendencies(data)
                    d = generate_data('Operations','Operations-Dep:1',month,year)
                    if type(d) == dict:
                        return render_template("operations_1.html",form=form,form_1=form_1,labels=labels,k=k,rev=revenue,d=d,exp=expense,u=cat,active_o_1='active',h=h,o=o)
                    return render_template("operations_1.html",form=form,form_1=form_1,labels=labels,k=k,rev=revenue,exp=expense,u=cat,active_o_1='active',h=h,o=o)
                elif type_of_file:
                    if mode=='Quarterly':
                        time_period=4
                    elif mode=='Half-yearly':
                        time_period=6
                    elif mode == 'Annually':
                        time_period=12
                    to=to_month(month,year,time_period)
                    new=year_visualization('Operations-Dep:1',month,year,to[0],to[1],type_of_file)
                    if new==-1:
                        flash("Insufficient information","warning")
                        return redirect(url_for('operations_1'))
                    label=new[0]
                    labels=','.join(label)
                    exp=new[1]
                    rev=new[2]
                    return render_template('operations_1.html',form=form,form_1=form_1,labels=labels,revenue=rev,expense=exp,active_o_1='active',h=h,o=o)
                else:
                    flash("Check the inputs and try again",'warning')
                return render_template("operations_1.html",form=form,form_1=form_1,active_o_1='active',h=h,o=o)
            else:
                flash("Data not added",'warning')
                return render_template("operations_1.html",form=form,form_1=form_1,active_o_1='active',h=h,o=o)
        return render_template("operations_1.html",form=form,form_1=form_1,active_o_1='active',h=h,o=o) 
    else:
        return render_template('no_access_page.html',active_o_1='active',h=h,o=o)
@app.route("/operations/department-2", methods=['POST','GET'])
@login_required
def operations_2():
    global ope,file_o_2,h,o
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data=[];time_period=0
    d=dict()
    if ope == 1 or ope == 3:
        form=UploadForm()
        form_1=MonthDataForm()
        if form.submit.data and form.validate():
            f=form.file.data
            month=form.month.data
            month=mon.index(month)
            year=int(form.year.data.year)
            type_of_file= form.type_of_file.data
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
            k=post_add(filename,'Operations','Operations-Dep:2',type_of_file,month,year)
            if type(data)== tuple:
                flash('Required columns are not mentioned', 'danger')
                return redirect(url_for('operations_2'))
            elif k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
            else :
                flash('Post added Sucessfully', 'success')
            return render_template("operations_2.html",form=form,form_1=form_1,active_o_2='active',h=h,o=o) 
        if form_1.submit1.data and form_1.validate():
            type_of_file= form_1.type_of_file.data
            mode=form_1.mode.data
            month= form_1.month.data
            month=mon.index(month)
            year=int(form_1.year.data.year)
            post = Post.query.filter_by(month=month,year=year,dep_num='Operations-Dep:2',department='Operations',mode=type_of_file).first()
            if post:  
                if mode=='Monthly':
                    u=eval(post.content)
                    data=eval(post.data)
                    cat=u[0]
                    label=u[1]  
                    expense=u[2]
                    revenue=u[3]
                    labels=','.join(label)
                    k = generate_tendencies(data)
                    d = generate_data('Operations','Operations-Dep:2',month,year)
                    if type(d)== dict:
                        return render_template("operations_2.html",form_1=form_1,form=form,d=d,k=k,labels=labels,rev=revenue,exp=expense,u=cat,active_o_2='active',h=h,o=o)
                    return render_template("operations_2.html",form=form,form_1=form_1,labels=labels,k=k,rev=revenue,exp=expense,u=cat,active_o_2='active',h=h,o=o)
                elif type_of_file:
                    if mode=='Quarterly':
                        time_period=4
                    elif mode=='Half-yearly':
                        time_period=6
                    elif mode == 'Annually':
                        time_period=12
                    to=to_month(month,year,time_period)
                    new=year_visualization('Operations-Dep:2',month,year,to[0],to[1],type_of_file)
                    if new==-1:
                        flash("Insufficient information","warning")
                        return redirect(url_for('operations_2'))
                    label=new[0]
                    labels=','.join(label)
                    exp=new[1]
                    rev=new[2]
                    return render_template('operations_2.html',form=form,form_1=form_1,labels=labels,revenue=rev,expense=exp,active_o_2='active',h=h,o=o)
                else:
                    flash("Check the inputs and try again",'warning')
                return render_template("operations_2.html",form=form,form_1=form_1,active_o_2='active',h=h,o=o)
            else:
                flash("Data not added",'warning')
                return render_template("operations_2.html",form=form,form_1=form_1,active_o_2='active',h=h,o=o)
        return render_template("operations_2.html",form=form,form_1=form_1,active_o_2='active',h=h,o=o)
    else:
        return render_template('no_access_page.html',active_o_2='active',h=h,o=o)
 
@app.route("/operations/department-3", methods=['POST','GET'])
@login_required
def operations_3():
    posts= Post.query.filter_by(department='Operations',dep_num='Operations-Dep:3')
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data=[];time_period=0
    d=dict()
    if ope == 1 or ope == 4:
        form=UploadForm()
        form_1=MonthDataForm()
        if form.submit.data and form.validate():
            f=form.file.data
            month=form.month.data
            month=mon.index(month)
            year=int(form.year.data.year)
            type_of_file= form.type_of_file.data
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
            k=post_add(filename,'Operations','Operations-Dep:3',type_of_file,month,year)
            if type(data)== tuple:
                flash('Required columns are not mentioned', 'danger')
                return redirect(url_for('operations_3'))
            elif k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
            else :
                flash('Post added Sucessfully', 'success')
            return render_template("operations_3.html",form=form,form_1=form_1,active_o_3='active',h=h,o=o) 
        if form_1.submit1.data and form_1.validate():
            type_of_file= form_1.type_of_file.data
            mode=form_1.mode.data
            month= form_1.month.data
            month=mon.index(month)
            year=int(form_1.year.data.year)
            post = Post.query.filter_by(month=month,year=year,dep_num='Operations-Dep:3',department='Operations',mode=type_of_file).first()
            if post:  
                if mode=='Monthly':
                    u=eval(post.content)
                    data=eval(post.data)
                    cat=u[0]
                    label=u[1]  
                    expense=u[2]
                    revenue=u[3]
                    labels=','.join(label)
                    k = generate_tendencies(data)
                    d = generate_data('Operations','Operations-Dep:3',month,year)
                    if type(d)== dict:
                        return render_template("operations_3.html",form=form,form_1=form_1,labels=labels,k=k,d=d,rev=revenue,exp=expense,u=cat,active_o_3='active',h=h,o=o)
                    return render_template("operations_3.html",form=form,form_1=form_1,k=k,labels=labels,rev=revenue,exp=expense,u=cat,active_o_3='active',h=h,o=o)
                elif type_of_file:
                    if mode=='Quarterly':
                        time_period=4
                    elif mode=='Half-yearly':
                        time_period=6
                    elif mode == 'Annually':
                        time_period=12
                    to=to_month(month,year,time_period)
                    new=year_visualization('Operations-Dep:3',month,year,to[0],to[1],type_of_file)
                    if new==-1:
                        flash("Insufficient information","warning")
                        return redirect(url_for('operations_3'))
                    label=new[0]
                    labels=','.join(label)
                    exp=new[1]
                    rev=new[2]
                    return render_template('operations_3.html',form=form,form_1=form_1,labels=labels,revenue=rev,expense=exp,active_o_3='active',h=h,o=o)
                else:
                    flash("Check the inputs and try again",'warning')
                return render_template("operations_3.html",form=form,form_1=form_1,active_o_3='active',h=h,o=o)
            else:
                flash("Data not added",'warning')
                return render_template("operations_3.html",form=form,form_1=form_1,active_o_3='active',h=h,o=o)
        return render_template("operations_3.html",form=form,form_1=form_1,active_o_3='active',h=h,o=o) 
    else:
        return render_template('no_access_page.html',active_o_3='active',h=h,o=o)

@app.route("/marketing/department-1",methods = ["POST", "GET"])
@login_required
def marketing_1():
    global mar,file_m_1,h,m
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data=[];time_period=0
    d=dict()
    if mar == 1 or mar == 2:
        form=UploadForm()
        form_1=MonthDataForm()
        if form.submit.data and form.validate():
            f=form.file.data
            month=form.month.data
            month=mon.index(month)
            year=int(form.year.data.year)
            type_of_file= form.type_of_file.data
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
            k=post_add(filename,'Marketing','Marketing-Dep:1',type_of_file,month,year)
            if type(data)== tuple:
                flash('Required columns are not mentioned', 'danger')
                return redirect(url_for('marketing_1'))
            elif k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
            else :
                flash('Post added Sucessfully', 'success')
            return render_template("marketing_1.html",form=form,form_1=form_1,active_m_1='active',h=h,m=m) 
        if form_1.submit1.data and form_1.validate():
            type_of_file= form_1.type_of_file.data
            mode=form_1.mode.data
            month= form_1.month.data
            month=mon.index(month)
            year=int(form_1.year.data.year)
            post = Post.query.filter_by(month=month,year=year,dep_num='Marketing-Dep:1',department='Marketing',mode=type_of_file).first()
            if post:  
                if mode=='Monthly':
                    u=eval(post.content)
                    data=eval(post.data)
                    cat=u[0]
                    label=u[1]  
                    expense=u[2]
                    revenue=u[3]
                    labels=','.join(label)
                    k = generate_tendencies(data)
                    d = generate_data('Marketing','Marketing-Dep:1',month,year)
                    if type(d)== dict:
                        return render_template("marketing_1.html",form_1=form_1,form=form,k=k,d=d,labels=labels,rev=revenue,exp=expense,u=cat,active_m_1='active',h=h,m=m)
                    return render_template("marketing_1.html",form_1=form_1,form=form,k=k,labels=labels,rev=revenue,exp=expense,u=cat,active_m_1='active',h=h,m=m)
                elif type_of_file:
                    if mode=='Quarterly':
                        time_period=4
                    elif mode=='Half-yearly':
                        time_period=6
                    elif mode == 'Annually':
                        time_period=12
                    to=to_month(month,year,time_period)
                    new=year_visualization('Marketing-Dep:1',month,year,to[0],to[1],type_of_file)
                    if new==-1:
                        flash("Insufficient information","warning")
                        return redirect(url_for('marketing_1'))
                    label=new[0]
                    labels=','.join(label)
                    exp=new[1]
                    rev=new[2]
                    return render_template('marketing_1.html',form=form,form_1=form_1,labels=labels,revenue=rev,expense=exp,active_m_1='active',h=h,m=m)
                else:
                    flash("Check the inputs and try again",'warning')
                return render_template('marketing_1.html',form=form,form_1=form_1,active_m_1='active',h=h,m=m)
            else:
                flash("Data not added",'warning')
                return render_template('marketing_1.html',form=form,form_1=form_1,active_m_1='active',h=h,m=m)
        return render_template('marketing_1.html',form=form,form_1=form_1,active_m_1='active',h=h,m=m)
    else:
        return render_template('no_access_page.html',active_m_1='active',h=h,m=m)
@app.route("/marketing/department-2",methods = ["POST", "GET"])
@login_required
def marketing_2():
    global mar,file_m_2,h,m
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data=[];time_period=0
    d=dict()
    if mar == 1 or mar == 3:
        form=UploadForm()
        form_1=MonthDataForm()
        if form.submit.data and form.validate():
            f=form.file.data
            month=form.month.data
            month=mon.index(month)
            year=int(form.year.data.year)
            type_of_file= form.type_of_file.data
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
            k=post_add(filename,'Marketing','Marketing-Dep:2',type_of_file,month,year)
            if type(data)== tuple:
                flash('Required columns are not mentioned', 'danger')
                return redirect(url_for('marketing_2'))
            elif k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
            else :
                flash('Post added Sucessfully', 'success')
            return render_template("marketing_2.html",form=form,form_1=form_1,active_m_2='active',h=h,m=m) 
        if form_1.submit1.data and form_1.validate():
            type_of_file= form_1.type_of_file.data
            mode=form_1.mode.data
            month= form_1.month.data
            month=mon.index(month)
            year=int(form_1.year.data.year)
            post = Post.query.filter_by(month=month,year=year,dep_num='Marketing-Dep:2',department='Marketing',mode=type_of_file).first()
            if post:  
                if mode=='Monthly':
                    u=eval(post.content)
                    data=eval(post.data)
                    cat=u[0]
                    label=u[1]  
                    expense=u[2]
                    revenue=u[3]
                    labels=','.join(label)
                    k = generate_tendencies(data)
                    d = generate_data('Marketing','Marketing-Dep:2',month,year)
                    if type(d)== dict:
                        return render_template("marketing_2.html",form_1=form_1,form=form,k=k,d=d,labels=labels,rev=revenue,exp=expense,u=cat,active_m_2='active',h=h,m=m)
                    return render_template("marketing_2.html",form_1=form_1,form=form,k=k,labels=labels,rev=revenue,exp=expense,u=cat,active_m_2='active',h=h,m=m)
                elif type_of_file:
                    if mode=='Quarterly':
                        time_period=4
                    elif mode=='Half-yearly':
                        time_period=6
                    elif mode == 'Annually':
                        time_period=12
                    to=to_month(month,year,time_period)
                    new=year_visualization('Marketing-Dep:2',month,year,to[0],to[1],type_of_file)
                    if new==-1:
                        flash("Insufficient information","warning")
                        return redirect(url_for('marketing_2'))
                    label=new[0]
                    labels=','.join(label)
                    exp=new[1]
                    rev=new[2]
                    return render_template('marketing_2.html',form=form,form_1=form_1,labels=labels,revenue=rev,expense=exp,active_m_2='active',h=h,m=m)
                else:
                    flash("Check the inputs and try again",'warning')
                return render_template('marketing_2.html',form=form,form_1=form_1,active_m_2='active',h=h,m=m)
            else:
                flash("Data not added",'warning')
                return render_template('marketing_2.html',form=form,form_1=form_1,active_m_2='active',h=h,m=m)
        return render_template('marketing_2.html',form=form,form_1=form_1,active_m_2='active',h=h,m=m)
    else:
        return render_template('no_access_page.html',active_m_2='active',h=h,m=m)
@app.route("/marketing/department-3",methods = ["POST", "GET"])
@login_required
def marketing_3():
    global mar,file_m_3,m,h
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data=[];time_period=0
    d=dict()
    if mar == 1 or mar == 4:
        form=UploadForm()
        form_1=MonthDataForm()
        if form.submit.data and form.validate():
            f=form.file.data
            month=form.month.data
            month=mon.index(month)
            year=int(form.year.data.year)
            type_of_file= form.type_of_file.data
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
            k=post_add(filename,'Marketing','Marketing-Dep:3',type_of_file,month,year)
            if type(data)== tuple:
                flash('Required columns are not mentioned', 'danger')
                return redirect(url_for('marketing_3'))
            elif k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
            else :
                flash('Post added Sucessfully', 'success')
            return render_template("marketing_3.html",form=form,form_1=form_1,active_m_3='active',h=h,m=m) 
        if form_1.submit1.data and form_1.validate():
            type_of_file= form_1.type_of_file.data
            mode=form_1.mode.data
            month= form_1.month.data
            month=mon.index(month)
            year=int(form_1.year.data.year)
            post = Post.query.filter_by(month=month,year=year,dep_num='Marketing-Dep:3',department='Marketing',mode=type_of_file).first()
            if post:  
                if mode=='Monthly':
                    u=eval(post.content)
                    data=eval(post.data)
                    cat=u[0]
                    label=u[1]  
                    expense=u[2]
                    revenue=u[3]
                    labels=','.join(label)
                    k = generate_tendencies(data)
                    d = generate_data('Marketing','Marketing-Dep:3',month,year)
                    if type(d)== dict:
                        return render_template("marketing_3.html",form_1=form_1,k=k,form=form,d=d,labels=labels,rev=revenue,exp=expense,u=cat,active_m_3='active',h=h,m=m)
                    return render_template("marketing_3.html",form_1=form_1,k=k,form=form,labels=labels,rev=revenue,exp=expense,u=cat,active_m_3='active',h=h,m=m)
                elif type_of_file:
                    if mode=='Quarterly':
                        time_period=4
                    elif mode=='Half-yearly':
                        time_period=6
                    elif mode == 'Annually':
                        time_period=12
                    to=to_month(month,year,time_period)
                    new=year_visualization('Marketing-Dep:3',month,year,to[0],to[1],type_of_file)
                    if new==-1:
                        flash("Insufficient information","warning")
                        return redirect(url_for('marketing_3'))
                    label=new[0]
                    labels=','.join(label)
                    exp=new[1]
                    rev=new[2]
                    return render_template('marketing_3.html',form=form,form_1=form_1,labels=labels,revenue=rev,expense=exp,active_m_3='active',h=h,m=m)
                else:
                    flash("Check the inputs and try again",'warning')
                return render_template('marketing_3.html',form=form,form_1=form_1,active_m_3='active',h=h,m=m)
            else:
                flash("Data not added",'warning')
                return render_template('marketing_3.html',form=form,form_1=form_1,active_m_3='active',h=h,m=m)
        return render_template('marketing_3.html',form=form,form_1=form_1,title='Marketing',active_m_3='active',h=h,m=m)
    else:
        return render_template('no_access_page.html',active_m_3='active',h=h,m=m)

@app.route("/sales/department-1",methods = ["POST", "GET"])
@login_required
def sales_1():
    global sal,file_s_1,s,h
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data=[];time_period=0
    d=dict()
    if sal == 1 or sal == 2:
        form=UploadForm()
        form_1=MonthDataForm()
        if form.submit.data and form.validate():
            f=form.file.data
            month=form.month.data
            month=mon.index(month)
            year=int(form.year.data.year)
            type_of_file= form.type_of_file.data
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
            k=post_add(filename,'Sales','Sales-Dep:1',type_of_file,month,year)
            if type(data)== tuple:
                flash('Required columns are not mentioned', 'danger')
                return redirect(url_for('sales_1'))
            elif k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
            else :
                flash('Post added Sucessfully', 'success')
            return render_template("sales_1.html",form=form,form_1=form_1,active_s_1='active',h=h,s=s) 
        if form_1.submit1.data and form_1.validate():
            type_of_file= form_1.type_of_file.data
            mode=form_1.mode.data
            month= form_1.month.data
            month=mon.index(month)
            year=int(form_1.year.data.year)
            post = Post.query.filter_by(month=month,year=year,dep_num='Sales-Dep:1',department='Sales',mode=type_of_file).first()
            if post:  
                if mode=='Monthly':
                    u=eval(post.content)
                    data=eval(post.data)
                    cat=u[0]
                    label=u[1]  
                    expense=u[2]
                    revenue=u[3]
                    labels=','.join(label)
                    k = generate_tendencies(data)
                    d = generate_data('Sales','Sales-Dep:1',month,year)
                    if type(d)== dict:
                        return render_template("sales_1.html",form_1=form_1,k=k,form=form,d=d,labels=labels,rev=revenue,exp=expense,u=cat,active_s_1='active',h=h,s=s)
                    return render_template("sales_1.html",form_1=form_1,k=k,form=form,labels=labels,rev=revenue,exp=expense,u=cat,active_s_1='active',h=h,s=s)
                elif type_of_file:
                    if mode=='Quarterly':
                        time_period=4
                    elif mode=='Half-yearly':
                        time_period=6
                    elif mode == 'Annually':
                        time_period=12
                    to=to_month(month,year,time_period)
                    new=year_visualization('Sales-Dep:1',month,year,to[0],to[1],type_of_file)
                    if new==-1:
                        flash("Insufficient information","warning")
                        return redirect(url_for('sales_1'))
                    label=new[0]
                    labels=','.join(label)
                    exp=new[1]
                    rev=new[2]
                    return render_template('sales_1.html',form=form,form_1=form_1,labels=labels,revenue=rev,expense=exp,active_s_1='active',h=h,s=s)
                else:
                    flash("Check the inputs and try again",'warning')
                return render_template('sales_1.html',form=form,form_1=form_1,active_s_1='active',h=h,s=s)
            else:
                flash("Data not added",'warning')
                return render_template('sales_1.html',form=form,form_1=form_1,active_s_1='active',h=h,s=s)
        return render_template('sales_1.html', form=form,title='Sales',form_1=form_1,active_s_1='active',h=h,s=s)
    else:
        return render_template('no_access_page.html',active_s_1='active',h=h,s=s)
@app.route("/sales/department-2",methods = ["POST", "GET"])
@login_required
def sales_2():
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data=[];time_period=0
    d=dict()
    if sal == 1 or sal == 3:
        form=UploadForm()
        form_1=MonthDataForm()
        if form.submit.data and form.validate():
            f=form.file.data
            month=form.month.data
            month=mon.index(month)
            year=int(form.year.data.year)
            type_of_file= form.type_of_file.data
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
            k=post_add(filename,'Sales','Sales-Dep:2',type_of_file,month,year)
            if type(data)== tuple:
                flash('Required columns are not mentioned', 'danger')
                return redirect(url_for('sales_2'))
            elif k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('sales_2'))
            else :
                flash('Post added Sucessfully', 'success')
                file_s_2 = filename
            return render_template("sales_2.html",form=form,form_1=form_1,active_s_2='active',h=h,s=s) 
        if form_1.submit1.data and form_1.validate():
            type_of_file= form_1.type_of_file.data
            mode=form_1.mode.data
            month= form_1.month.data
            month=mon.index(month)
            year=int(form_1.year.data.year)
            post = Post.query.filter_by(month=month,year=year,dep_num='Sales-Dep:2',department='Sales',mode=type_of_file).first()
            if post:  
                if mode=='Monthly':
                    u=eval(post.content)
                    data=eval(post.data)
                    cat=u[0]
                    label=u[1]  
                    expense=u[2]
                    revenue=u[3]
                    labels=','.join(label)
                    k = generate_tendencies(data)
                    d = generate_data('Sales','Sales-Dep:2',month,year)
                    if type(d)== dict:
                        return render_template("sales_2.html",form_1=form_1,k=k,form=form,d=d,labels=labels,rev=revenue,exp=expense,u=cat,active_s_2='active',h=h,s=s)
                    return render_template("sales_2.html",form_1=form_1,k=k,form=form,labels=labels,rev=revenue,exp=expense,u=cat,active_s_2='active',h=h,s=s)
                elif type_of_file:
                    if mode=='Quarterly':
                        time_period=4
                    elif mode=='Half-yearly':
                        time_period=6
                    elif mode == 'Annually':
                        time_period=12
                    to=to_month(month,year,time_period)
                    new=year_visualization('Sales-Dep:2',month,year,to[0],to[1],type_of_file)
                    if new==-1:
                        flash("Insufficient information","warning")
                        return redirect(url_for('sales_2'))
                    label=new[0]
                    labels=','.join(label)
                    exp=new[1]
                    rev=new[2]
                    return render_template('sales_2.html',form=form,form_1=form_1,labels=labels,revenue=rev,expense=exp,active_s_2='active',h=h,s=s)
                else:
                    flash("Check the inputs and try again",'warning')
                return render_template('sales_2.html',form=form,form_1=form_1,active_s_2='active',h=h,s=s)
            else:
                flash("Data not added",'warning')
                return render_template('sales_2.html',form=form,form_1=form_1,active_s_2='active',h=h,s=s)
        return render_template('sales_2.html', form=form,title='Sales',form_1=form_1,active_s_2='active',h=h,s=s)
    else:
        return render_template('no_access_page.html',active_s_2='active')
@app.route("/sales/department-3",methods = ["POST", "GET"])
@login_required
def sales_3():
    global sal,file_s_3,s,h
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data=[];time_period=0
    d=dict()
    if sal == 1 or sal == 4:
        form=UploadForm()
        form_1=MonthDataForm()
        if form.submit.data and form.validate():
            f=form.file.data
            month=form.month.data
            month=mon.index(month)
            year=int(form.year.data.year)
            type_of_file= form.type_of_file.data
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
            k=post_add(filename,'Sales','Sales-Dep:3',type_of_file,month,year)
            if type(data)== tuple:
                flash('Required columns are not mentioned', 'danger')
                return redirect(url_for('sales_3'))
            elif k==0:
                flash('Post Already exist', 'warning')
            elif k==-1:
                flash('Add "Category" to Column names in the CSV file and Try again', 'danger')
                return redirect(url_for('sales_3'))
            else :
                flash('Post added Sucessfully', 'success')
                file_s_3 = filename
            return render_template("sales_3.html",form=form,form_1=form_1,active_s_3='active',h=h,s=s) 
        if form_1.submit1.data and form_1.validate():
            type_of_file= form_1.type_of_file.data
            mode=form_1.mode.data
            month= form_1.month.data
            month=mon.index(month)
            year=int(form_1.year.data.year)
            post = Post.query.filter_by(month=month,year=year,dep_num='Sales-Dep:3',department='Sales',mode=type_of_file).first()
            if post:  
                if mode=='Monthly':
                    u=eval(post.content)
                    data=eval(post.data)
                    cat=u[0]
                    label=u[1]  
                    expense=u[2]
                    revenue=u[3]
                    labels=','.join(label)
                    k = generate_tendencies(data)
                    d = generate_data('Sales','Sales-Dep:3',month,year)
                    if type(d)== dict:
                        return render_template("sales_3.html",form_1=form_1,k=k,form=form,d=d,labels=labels,rev=revenue,exp=expense,u=cat,active_s_3='active',h=h,s=s)
                    return render_template("sales_3.html",form_1=form_1,k=k,form=form,labels=labels,rev=revenue,exp=expense,u=cat,active_s_3='active',h=h,s=s)
                elif type_of_file:
                    if mode=='Quarterly':
                        time_period=4
                    elif mode=='Half-yearly':
                        time_period=6
                    elif mode == 'Annually':
                        time_period=12
                    to=to_month(month,year,time_period)
                    new=year_visualization('Sales-Dep:3',month,year,to[0],to[1],type_of_file)
                    if new==-1:
                        flash("Insufficient information","warning")
                        return redirect(url_for('sales_3'))
                    label=new[0]
                    labels=','.join(label)
                    exp=new[1]
                    rev=new[2]
                    return render_template('sales_3.html',form=form,form_1=form_1,labels=labels,revenue=rev,expense=exp,active_s_3='active',h=h,s=s)
                else:
                    flash("Check the inputs and try again",'warning')
                return render_template('sales_3.html',form=form,form_1=form_1,active_s_3='active',h=h,s=s)
            else:
                flash("Data not added",'warning')
                return render_template('sales_3.html',form=form,form_1=form_1,active_s_3='active',h=h,s=s)
        return render_template('sales_3.html',form=form,form_1=form_1,active_s_3='active',h=h,s=s)
    else:
        return render_template('no_access_page.html',active_s_3='active',h=h,s=s)

def mail_sender(email,username,passw):
    msg = Message('Login Credentials for Budget-Management App', sender='ksdrao7@gmail.com', recipients = [email]) #add your email id at the sender
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

@login_required
def year_db_delete(dep_num,data,year):
    y=Data_year.query.filter_by(dep_num=dep_num,year=year).first()
    data=eval(data)
    if y:
        count=y.count
        d = eval(y.content)
        for i in d:
            d[i]=d[i]-data[i]
        y.count=count-1
        y.content=str(d)
        db.session.commit()
        for i in d:
            if d[i]==0:
                db.session.delete(y)
                db.session.commit()
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
                        data=Data_month.query.filter_by(department=post.department,dep_num=post.dep_num,month=post.month,year=post.year,mode=post.mode)
                        if post.mode=='Actual':
                            year_db_delete(post.dep_num,data.content,post.year)
                        db.session.delete(data)
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
                                data=Data_month.query.filter_by(department=post.department,dep_num=post.dep_num,month=post.month,year=post.year,mode=post.mode)
                                if post.mode=='Actual':
                                    year_db_delete(post.dep_num,data.content,post.year)
                                db.session.delete(data)
                        db.session.delete(user1)
                        db.session.commit()
                elif page_access==3:
                    if user1.department  == 'Marketing' and current_user.department =='Marketing': 
                        if post:
                            for post in post:
                                db.session.delete(post)
                                data=Data_month.query.filter_by(department=post.department,dep_num=post.dep_num,month=post.month,year=post.year,mode=post.mode)
                                if post.mode=='Actual':
                                    year_db_delete(post.dep_num,data.content,post.year)
                                db.session.delete(data)
                        db.session.delete(user1)
                        db.session.commit()
                elif page_access==4:
                    if user1.department  == 'Sales' and current_user.department =='Sales':
                        if post:
                            for post in post:
                                db.session.delete(post)
                                data=Data_month.query.filter_by(department=post.department,dep_num=post.dep_num,month=post.month,year=post.year,mode=post.mode)
                                if post.mode=='Actual':
                                    year_db_delete(post.dep_num,data.content,post.year)
                                db.session.delete(data)
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


@app.route('/delete_post', methods=['POST', 'GET'])
@login_required
def delete_post():
    mon=['-','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    global h,o,m,s,page_access
    department=''
    form=DeleteDataForm()
    if page_access==1:
        form=DeleteDataForm()
    elif current_user.department=="Operation":
        form=DeleteDataForm_Ope()
    elif current_user.department=="Marketing":
        form=DeleteDataForm_Mar()
    elif current_user.department=="Sales":
        form=DeleteDataForm_Sal()
    if form.validate_on_submit():
        dep_num=form.dep_num.data
        type_of_file= form.type_of_file.data
        month= mon.index(form.month.data)
        year=int(form.year.data.year)
        if page_access==1:
            department = form.department.data
        else:
            department = current_user.department
        post= Post.query.filter_by(department=department,dep_num=dep_num,month=month,year=year,mode=type_of_file).first()
        if post:
            data= Data_month.query.filter_by(department=department,dep_num=dep_num,month=month,year=year,mode=type_of_file).first()
            if current_user.department == 'Admin':
                db.session.delete(post)
                if type_of_file=='Actual':
                    year_db_delete(dep_num,data.content,year)
                db.session.delete(data)
                db.session.commit()
                flash('Data deleted successfully', 'success')
            elif current_user.department == 'Dep-Admin':
                if data.department == current_user.departmet:
                    db.session.delete(post)
                    if type_of_file=='Actual':
                        year_db_delete(dep_num,data.content,year)
                    db.session.delete(data)
                    db.session.commit()
                    flash('Data deleted successfully', 'success')
            elif post.author.username == current_user.username:
                if data.department == current_user.department:
                    db.session.delete(post)
                    if type_of_file=='Actual':
                        year_db_delete(dep_num,data.content,year)
                    db.session.delete(data)
                    db.session.commit()
                    flash('Data deleted successfully', 'success')
            else:
                flash('You Cannot Delete the Data', 'warning')
        else:
            flash('Data not found','warning') 
    return render_template('delete_post.html',form=form,h=h,o=o,m=m,s=s,page_access=page_access)

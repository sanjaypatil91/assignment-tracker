from flask import Flask,send_from_directory,render_template,redirect,url_for,request,session
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import re
import random


app=Flask(__name__)
Uploder="C:\\Users\\HP\\student-assignment-tracker"

app.secret_key="defaultkey"
app.config['UPLOAD_FOLDER']='Uploder'
app.config['MAX_CONTENT_PATH']='5,00,000'

mysql = MySQL(app)
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Yashraj@1984'
app.config['MYSQL_DB'] = 'login_details'
  
@app.route("/basic")
def show_homepage():
    page=render_template("basic.html")
    return page
    
@app.route('/userlogin',methods=["GET","POST"])
def userlogin():
    if request.method == "GET":
        page=render_template("userlogin.html")
        return page
    elif request.method == "POST":
        msg=' '
        user_type=request.form['user_type']
        name = request.form['username']
        password = request.form['password']
        USERS = get_USER(name)
        if len(USERS)==0:
            if user_type=='Student':
                return render_template("studentprofile.html")
            elif user_type=='Faculty':
                return render_template("facultyprofile.html")
        elif len(USERS)>1:
            raise Exception (f"Multiple USERS with same name present")
        USER = USERS[0]
        if USER[3]==password:
            session['username']=request.form['username']
            if user_type=='Student':
                return redirect(url_for("studentprofile"))
            elif user_type=='Faculty':
                return redirect(url_for("facultyprofile"))
        else:
            page=render_template('userlogin.html')
            return page
    
            
                    
def get_USER(name):
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select * from USER where name = '{name}';""")
    result= cursor.fetchall()
    return result
    
@app.route("/userregister",methods=["GET","POST"])
def userregister():
    userid=str(random.randint(0,10000))
    msg=" "
    if request.method=="GET":
        return render_template("userregister.html")
    else:
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        user_type=request.form['user_type']
        USERS = get_USER(name)
        if len(USERS)>0:
            return render_template("userregister.html",already_exists=True)
        elif len(USERS)==0:
            cursor=mysql.connection.cursor()
            cursor.execute(f"""insert into user(userid,name,email,password,user_type)
                       values('{userid}','{name}','{email}','{password}','{user_type}');
                       """)
            mysql.connection.commit()
            cursor.close()
            session['name']=request.form['name']
            session['email']=request.form['email']
            session['password']=request.form['password']
            session['user_type']=request.form['user_type']
            msg="You Have Successfully Registered!!!"
            return redirect(url_for('userlogin'))
            
@app.route("/studentprofile",methods=["GET","POST"])
def studentprofile():
    username=None
    if 'username' in session:
        username=session['username']
    page=render_template("studentprofile.html",username=username)
    return page
    
@app.route("/uploadfile",methods=["GET","POST"])
def uploadfile():
    if request.method=='GET':
        username=session['username']
        return render_template("uploadfile.html",username=username)
    elif request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return 'file uploaded successfully'
        

@app.route("/facultyprofile",methods=["GET","POST"])
def facultyprofile():
    page=render_template("facultyprofile.html")
    return page
    
@app.route("/newassignment",methods=["GET","POST"])
def newassignment():
    if request.method=='GET':
        return render_template('newassignment.html')
    elif request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return 'file uploaded successfully'

    
@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('show_homepage'))

@app.route("/")
def home_page():
    return redirect(url_for('show_homepage'))
    
@app.route('/static_pages/<path:file_name>')
def static_pages(file_name):
    return send_from_directory('static_pages',file_name)    
    
if __name__=="__main__":
    app.run(host="0.0.0.0",port=50000)
    
            

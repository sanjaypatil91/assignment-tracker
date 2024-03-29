

from flask import Flask, render_template, request, redirect, url_for, session, send_file,flash
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import re
import os.path
import random
from datetime import datetime
  
UPLOAD_FOLDER="C:/Users/DELL/Documents/assignment_submission/uploaded_files"  

app = Flask(__name__)
app.secret_key = 'some_random_key'
  
mysql = MySQL(app)
app.config['UPLOAD_FOLDER']='uploader'  
app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_CURSORCLASS"]="DictCursor"
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password_123'
app.config['MYSQL_DB'] = 'admin'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER 


@app.route('/Home', methods=['POST','GET'])
def Home():
    return render_template('Home.html')
  
@app.route('/')
@app.route('/login/', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        type_of_user = request.form['type_of_user']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE name = % s AND password = % s', (name, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            session['password'] = user['password']
            session['type_of_user'] = user['type_of_user']

        if type_of_user=='Student':   
            return redirect(url_for("student_dashboard"))
        elif type_of_user=='Teacher':
            return redirect(url_for("teacher_dashboard"))
        else:
            mesage = 'Please enter correct username / password !'
    return render_template('login.html', mesage = mesage) 


@app.route('/forgot_password',methods=['GET','POST'])
def forgot_password():
    mesage=''
    if request.method == 'POST' and 'password' in request.form:
        password = request.form['password']
        #cursor.execute('update user set password= (password) where name=session['name']')
        query = f""" update user set password = '{password}' where name = '{session['name']}' """
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query)
        connection.commit()
        mesage='Password is changed successfully..!!'
    return render_template('forgot_password.html',mesage1=mesage)
    

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/')  
@app.route('/register/',methods=['POST','GET'])
def register():
    user_id=str(random.randint(0,10000))
    mesage=''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form and 'type_of_user' in request.form:
        # user_id=request.form['user_id']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        type_of_user = request.form['type_of_user']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor=mysql.connection.cursor()
        cursor.execute("insert into user(user_id,name,email,password,type_of_user) values(%s,%s,%s,%s,%s)",(user_id,name,email,password,type_of_user))
        mysql.connection.commit()
        cursor.close()
        mesage='Registration Successfully. Login Here...','success'
        return redirect(url_for('login'))
    return render_template("register.html",mesage=mesage)



@app.route("/display")
def display():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE user_id = % s', (session['user_id'], ))
        user = cursor.fetchone()    
        return render_template("display.html", user = user)
    return redirect(url_for('login'))    

@app.route('/')
@app.route("/update", methods =['GET', 'POST'])
def update():
    mesage = ''
    if 'loggedin' in session:
        if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE name = %s', (name))
            user = cursor.fetchone()
            if user:
                mesage = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                mesage = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', name):
                mesage = 'name must contain only characters and numbers !'
            else:
                cursor.execute('UPDATE user SET  name =%s, email =%s, password =%s WHERE user_id =%s', (name,email,password, (session['user_id'],),))
                mysql.connection.commit()
                mesage = 'You have successfully updated !'
        elif request.method == 'POST':
            mesage = 'Please fill out the form !'
        return render_template("update.html", mesage = mesage)
    return redirect(url_for('login'))   


@app.route("/delete/")
def delete():
    if request.method=='POST':
        connection=mysql.connection.cursor()
        cursor.execute("delete from user")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mysql.connection.commit()
        connection.close()
        mesage=('User details deleted')
    return redirect(url_for("Home"))


@app.route("/student_dashboard",methods=["GET","POST"])
def student_dashboard():
    if 'name' in session:
        name=session['name']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        result = cursor.fetchall()
    return render_template("student_dashboard.html", user=result, name=name)

    
@app.route("/teacher_dashboard",methods=["GET","POST"])
def teacher_dashboard():
    if 'name' in session:
        name=session['name']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        result=cursor.fetchone()
    return render_template("teacher_dashboard.html", user=result, name=name)
      

@app.route('/post_assignment',methods=['GET','POST'])
def post_assignment():
    assignment_id=str(random.randint(0,10000))
    mesage=''
    if request.method=='POST':
        assignment_title = request.form['assignment_title']
        description = request.form['description']
        submission_due_date = request.form['submission_due_date']
        cursor=mysql.connection.cursor()
        cursor.execute("insert into assignment(assignment_id,assignment_title,description,submission_due_date )values(%s,%s,%s,%s)",(assignment_id,assignment_title,description,submission_due_date))
        mysql.connection.commit()
        cursor.close()
        mesage = 'You have successfully added new assignment!'
        return redirect(url_for('teacher_dashboard'))
    return render_template("post_assignment.html",mesage=mesage)


@app.route("/view_assignment")
def view_assignment():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM assignment')
        user = cursor.fetchall()
        return render_template("view_assignment.html", user=user)    
    return redirect(url_for('login'))  


@app.route("/view_solution")
def view_solution():
    if 'loggedin' in session:
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from submission')
        user = cursor.fetchall()
        return render_template("view_solution.html", user=user)    
  
#Below code(status_of_assignment) for teacher can see solution of assignment submiited by student and teacher can approve and reject assignment.

@app.route('/status_of_assignment',methods=['POST'])
def status_of_assignment():
    if request.method == 'POST':
        status_of_assignment = request.form['status_of_assignment']
        submission_id = request.form['submission_id']
        query = f"""update submission set status_of_assignment = '{status_of_assignment}' where submission_id ='{submission_id}';"""
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query)
        cursor = mysql.connection.cursor()
        mysql.connection.commit()
        return render_template('view_solution.html')

#Below code (check_status)for students can view their assignments status-approved/reject.

@app.route('/check_status') 
def check_status():
    if 'name' in session:
        name=session['name']
        u1 = f"""select user_id from user where name='{session['name']}' ;"""
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(u1)
        user_id_record=cursor.fetchall()
        user_id=user_id_record[0]
        # print(user_id)
        # print(u1)
        query2 = f"""select submission_id, assignment_id,user_id,status_of_assignment from submission where user_id ='{user_id['user_id']}';"""
        cursor.execute(query2)
        result = cursor.fetchall()
        # print(result)
        return render_template('check_status.html', records=result)

#Below code (track_of_assignment)for teacher can track the assignments of students.

@app.route("/track_of_assignment")
def track_of_assignment():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM submission')
        result = cursor.fetchall()    
        return render_template("track_of_assignment.html", records=result)
   
@app.route('/approved_list') 
def approved_list():
    cursor=mysql.connection.cursor()
    query=f"""select name,email from user where user_id in (select user_id from submission where status_of_assignment="approved") ;"""
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template("approved_list.html", records=result)
   

@app.route('/rejected_list') 
def rejected_list():
    cursor=mysql.connection.cursor()
    query=f"""select name,email from user where user_id in (select user_id from submission where status_of_assignment="rejected") ;"""
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template("rejected_list.html", records=result)
   

@app.route('/download/<string:filename>', methods=['GET'])
def download(filename):
   print(filename)
   uploads=UPLOAD_FOLDER
   return send_file(uploads+'/'+filename, as_attachment=True)


@app.route('/upload')
def upload():
   return render_template('upload.html')
    
       
@app.route('/uploader',methods=['GET','POST'])
def upload_file():
    submission_id=str(random.randint(0,10000))
    mesage=''
    if request.method=='POST':
        submission_date = datetime.now()
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        

        u1 =f"""select user_id from user where name ='{session['name']}';"""
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(u1)
        user_id_user=cursor.fetchall()
        user_id=user_id_user[0]
        l1=user_id.get('user_id')
        print(l1)

        assignment_title=request.form['assignment_title']
        a1 =f"""select assignment_id from assignment where assignment_title={'assignment_title'};"""
        cursor.execute(a1)
        assignment_id_rec=cursor.fetchone()
        l2=assignment_id_rec.get('assignment_id')
        print(l2)
        query=f"""insert into submission(submission_id,assignment_id,user_id,submission_date,solution )values('{submission_id}','{l2}','{l1}','{submission_date}','{f.filename}');"""
        print(query)
        q=cursor.execute(query)
        print(q)
        mysql.connection.commit()
        cursor.close()
        mesage = 'You have successfully uploaded new assignment!'
        return render_template('student_dashboard.html')


@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']  
        f.save(f.filename)  
        return render_template("success.html", name = f.filename)  


    # @app.route('/static/<path:filename>',)
    # def static(filename):
    #    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run()



# @app.route('/login',methods=["GET","POST"])
# def login():
#     if request.method == "GET":
#         return render_template("login.html")
#         return page
#     elif request.method == "POST":
#         mesage="Invalid Login"
#         name = request.form['name']
#         password = request.form['password']
#         USERS = get_USER(name)
#         User_type=get_type_of_user(name)

#         if len(USERS)==0:
#             return render_template("login.html")
#         if len(USERS)>1:
#             raise Exception (f"Multiple USERS with same name present")

#         USER = USERS[0]
#         User_type=User_type[0]
        
#         if USER[2]==password and User_type[0]=="Student":
#             session['name']=request.form['name']
#             return redirect(url_for("student_dashboard"))

#         elif USER[2]==password and User_type[0]=="Faculty":
#             return redirect(url_for("teacher_dashboard"))
#         else:
#             return render_template('login.html',mesage=mesage)
    
        
# def get_USER(name):
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute(f"""select * from user where name = '{name}';""")
#     result=cursor.fetchall()
#     return result
    
# def get_type_of_user(name):
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute(f"""select type_of_user from user where name = '{name}';""")
#     result=cursor.fetchall()
#     return result



# @app.route('/register/', methods =['GET', 'POST'])
# def register():
#     user_id=str(random.randint(0,10000))
#     mesage=''
#     if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form and 'type_of_user' in request.form:
#         name = request.form['name']
#         email_ = request.form['email']
#         password = request.form['password']
#         type_of_user = request.form['type_of_user']
#         cursor=mysql.connection.cursor()
#         cursor.execute("insert into user(user_id,name,email,password, type_of_user) values(%s,%s,%s,%s,%s),(user_id,name,email,password, type_of_user)")
#         #cursor.execut("insert into user(user_id,name,email,password, type_of_user)values('{user_id}','{name}','{email}','{password}','{type_of_user}');")
#         connection.commit()
#         cursor.close()
#         mesage = 'You have successfully registered !'
#         return redirect(url_for('login'))
#     return render_template('register.html', mesage = mesage)



# @app.route('/delete')
# def delete():
#     mesage=''
#     if request.method=='POST':
#         if 'name' in session:
#             name = session['name']
#             print(name)
#             cursor.execute('delet FROM user WHERE name = %s', (name))
#             #query=f"""delete from user where name='{name}';"""
#             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#             mysql.connection.commit()
#             mesage="Your account is deleted successfully"   
#         return render_template("Home.html",mesage=mesage)
    

# @app.route("/index")s
# def index():
#     if 'loggedin' in session: 
#         return render_template("index.html")
#     return redirect(url_for('login'))


# @app.route("/solution")
# def solution():
#     return render_template ('solution.html')


# @app.route('/view_solution',methods=['GET','POST'])
# def view_solution():
#     submission_id=str(random.randint(0,10000))
#     mesage=''
#     if request.method=='POST':
#         assignment_id = request.form['assignment_id']
#         user_id = request.form['user_id']
#         submission_date = request.form['submission_date']
#         solution= request.form['solution']
#         cursor=mysql.connection.cursor()
#         cursor.execute("select * from submission")
#         mysql.connection.commit()
#         mesage = 'You have successfully added new assignment!'
#         return redirect(url_for('teacher_dashboard'))
#     return render_template("view_solution.html",user=user)


# @app.route("/view_assignment")
# def view_assignment(): 
#     cursor=mysql.connection.cursor()
#     cursor.execute("select * from assignment") 
#     result = cursor.fetchall() 
#     return render_template("view_assignment.html", records=result)

# @app.route("/view_solution")
# def view_solution():
#     if 'loggedin' in session:
#         cursor = mysql.connection.cursor()
#         cursor.execute('SELECT * FROM submission')
#         user = cursor.fetchall()
#         return render_template("view_solution.html", user=user)    
#     return redirect(url_for('login')) 



# @app.route('/result',methods = ['POST', 'GET'])
# def result():
#       return render_template("result.html")


# @app.route("/uploader",methods=["GET","POST"])
# def upload_file():
#     submission_id=str(random.randint(0,1000000))
#     mesage=''
#     if request.method=='POST':

#         submission_date=datetime.now()
#         f = request.files['file']
#         f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
#         u1 =f"""select user_id from user where name ='{session['name']}';"""
#         cursor = mysql.connection.cursor()
#         cursor.execute(u1)

#         assignment_id=cursor.fetchone()
#         assignment_title=request.form('assignment_title')
#         cursor.execute(f"""insert into submission(submission_id,assignment_id,user_id,submission_date,solution)
#                     values('{submission_id}','{assignment_id}','{user_id}','{submission_date}','{f.filename}');""")
#         mysql.connection.commit()
#         cursor.close()
#         mesage = 'You have successfully uploaded new assignment !'
#         return render_template("student_dashboard.html",mesage=mesage)



# @app.route('/upload', methods = ['GET', 'POST'])
# def upload():
#    if request.method == 'POST':
#       f = request.files['file']
#       f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
#       return 'file uploaded successfully' 


# @app.route("/index",methods=['GET','POST'])
# def index():
#     if request.method=='POST':
#         connection=mysql.connection.cursor()
#         cursor.execute("SELECT * FROM user")
#         mysql.connection.commit()
#         res=connection.fetchall()  
#         return render_template("index.html",datas=res)


#display data from database
# @app.route("/test", methods=['post', 'get']) 
# def test():   
#     cursor.execute("select * from user") 
#     result = cursor.fetchall() 
#     return render_template("test.html", data=result)


#Download the file
# @app.route('/download',methods=['POST','GET'])
# def download():
#     if request.method=='POST':
#         return send_file('login.docx', as_attachment=True)
#         return render_template('download.html')

# @app.route('/profile')
# def profile():
#     if 'loggedin' in session:
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM user WHERE user_id = %s', (session['user_id'],))
#         user = cursor.fetchone()
#         return render_template('profile.html', user=user)
#     return redirect(url_for('login'))    


# @app.route("/profile",methods=['GET','POST'])
# def profile():
#     if request.method=='POST':
#         name=request.form['name']
#         email=request.form['email']
#         password=request.form['password']
        
#         cursor.execute("update user set(name,email,password) values(%s,%s,%s)",(name,email,password))
#         connection.execute(sql,[name,email,password])
#         mysql.connection.commit()
#         connection.close()
#         flash('User details added')        
#         return redirect(url_for("profile"))
#     return render_template("profile.html")




# @app.route('/post_assignment',methods=['GET','POST'])
# def post_assignment():
#     assignment_id=str(random.randint(0,10000))
#     mesage = 'You have successfully added new assignment!'
#     cursor=mysql.connection.cursor()
#     if request.method=='GET':
#         return render_template("post_assignment.html",mesage=mesage)
#     elif request.method=='POST':

#         assignment_title = request.form['assignment_title']
#         description = request.form['description']
#         submission_due_date = request.form['submission_due_date']
#         cursor.execute(f"""insert into assignment(assignment_id,assignment_title, description, submission_due_date)values('{assignment_id}','{assignment_title}', '{description}', '{submission_due_date}');""")
#         result=mysql.connection.commit()
#         print(result)
#         return redirect(url_for('teacher_dashboard'))

# @app.route('/view_assignment') 
# def view_assignment():
#     try:
#         with mysql.connector.connect(host="localhost",user="root",password="password_123",database="admin") as connection:
#             with connection.cursor() as cursor:
#                 query=f"""select * from assignment;"""
#                 print(query)
#                 cursor.execute(query)
#                 result = cursor.fetchall()
               
#     except Exception as e:
#         print(e)
#     return render_template('view_assignment.html', records=result)
    
           

# @app.route("/view_assignment")
# def view_assignment():  
#         cursor = mysql.connection.cursor()
#         cursor.execute('SELECT * FROM assignment')
#         result = cursor.fetchone()


from flask import Flask, render_template, request, redirect, url_for, session, send_file,flash
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import re
import os.path
import random
from datetime import datetime
  
app = Flask(__name__)
app.secret_key = 'some_random_key'
app.config['UPLOAD_FOLDER']='UPLOAD_FOLDER'

  
mysql = MySQL(app)
app.config['UPLOAD_FOLDER']='uploader'  
app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_CURSORCLASS"]="DictCursor"
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password_123'
app.config['MYSQL_DB'] = 'admin'

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
            session['password'] = user['password'],
            session['type_of_user'] = user['type_of_user']

        if type_of_user=='Student':   
            return render_template('student_dashboard.html', mesage = mesage) 
        elif type_of_user=='Teacher':
            return render_template('teacher_dashboard.html',mesage=mesage)
        else:
            mesage = 'Please enter correct username / password !'
    return render_template('login.html', mesage = mesage) 


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('login'))
  
@app.route('/register/',methods=['POST','GET'])
def register():
    mesage=''
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute("insert into user(name,email,password) values(%s,%s,%s)",(name,email,password))
        mysql.connection.commit()
        cursor.close()
        mesage='Registration Successfully. Login Here...','success'
        return redirect(url_for('login'))
    return render_template("register.html",mesage=mesage)

@app.route("/index")
def index():
    if 'loggedin' in session: 
        return render_template("index.html")
    return redirect(url_for('login'))


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
            cursor.execute('SELECT * FROM user WHERE name = %s', (name, ))
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


@app.route('/delete')
def delete():
    msg="Your account is deleted successfully"
    if 'name' in session:
        name = session['name']
    print(name)
    query=f"""delete from user where name='{name}';"""
    try:
        with mysql.connector.connect(host="localhost",user="root",password="password_123",database="admin") as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Exception as e:
        print(e)    
    
    page = render_template("Home.html",msg=msg)
    return page



# @app.route("/delete",methods=['GET','POST'])
# def delete():
#     if request.method=='POST':
#         connection=mysql.connection.cursor()
#         sql="delete from user where user_id=%s"
#         connection.execute(sql,user_id)
#         mysql.connection.commit()
#         connection.close()
#         mesage=('User details deleted')
#         return redirect(url_for("Home"))


@app.route("/student_dashboard",methods=["GET","POST"])
def student_dashboard():
    if 'name' in session:
        name=session['name']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        result = cursor.fetchall()
    return render_template("student_dashboard.html", records=result, name=name)

    
@app.route("/teacher_dashboard",methods=["GET","POST"])
def teacher_dashboard():
    if 'name' in session:
        name=session['name']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        result=cursor.fetchone()
    return render_template("teacher_dashboard.html", records=result, name=name)
      

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

@app.route("/view_solution")
def view_solution():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM submission')
        user = cursor.fetchall()
        return render_template("view_solution.html", user=user)    
    return redirect(url_for('login')) 


@app.route('/download/<string:filename>',methods=['GET'])
def download(filename):
    print(filename)
    uploads=UPLOAD_FOLDER
    return send_file(uploads+'/'+filename, as_attachment=True)

# @app.route("/solution")
# def solution():
#     return render_template ('solution.html')



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
        u1 =('select user_id from user where name = % s', (session['name'], ))
        cursor.execute(u1)
        user_id_user=cursor.fetchall()
        user_id=user_id_user[0]
        assignment_title=request.form['title']
        assignment_id = request.form['assignment_title']
        a1 =('select assignment_id from assignment where assignment_title = %s',('assignment_title'))
        cursor.execute(a1)
        assignment_id_rec=cursor.fetchone()
        print(user_id_user)
        print(assignment_id_rec)
        query=cursor.execute("insert into submission(submission_id,assignment_id,user_id,submission_date,solution )values(%s,%s,%s,%s,%s)",('submission_id','assignment_id_rec[0]','user_id[0]','submission_date','UPLOAD_FOLDER'))
        cursor.execute(query)
        mysql.connection.commit()
        cursor.close()
        mesage = 'You have successfully uploaded new assignment!'
        return render_template('student_dashboard.html')


# @app.route('/upload', methods = ['GET', 'POST'])
# def upload():
#    if request.method == 'POST':
#       f = request.files['file']
#       f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
#       return 'file uploaded successfully' 

@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']  
        f.save(f.filename)  
        return render_template("success.html", name = f.filename)  

@app.route('/result',methods = ['POST', 'GET'])
def result():
      return render_template("result.html")

# @app.route('/static/<path:file_name>',)
# def static(file_name):
#    return send_from_directory('static', file_name)

if __name__ == "__main__":
    app.run()









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


# @app.route("/")
# def home():
#     connection=mysql.connection.cursor()
#     sql="SELECT * FROM user"
#     connection.execute(sql)
#     res=connection.fetchall()
#     return render_template("home.html",datas=res)



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
#         return render_template("view_assignment.html",records=result)

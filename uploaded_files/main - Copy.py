from flask import Flask,request,session,request,redirect,url_for,send_from_directory,render_template
import mysql.connector
import random
 

app = Flask(__name__)
app.secret_key = "some_random_key"


@app.route('/')
def home():
    return render_template("Home.html")


@app.route('/register',methods=["GET","POST"])
def register():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form :
        page = render_template("register.html")
        return page
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        record = cursor.fetchall()
        if record:
            query = ("insert into users(username,email,password)values(%s,%s,%s)",(username,email,password))
            cursor.execute(query,(username,useremail,userpassword))
            connection.commit()
        return redirect(url_for('login'))
    else:
        msg="password does-not match"
        return render_template("register.html")
    return render_template("register.html")
       
    try:
        with mysql.connector.connect(host="localhost",user="root",password="password_123",database="accounts") as connection:
            with connection.cursor() as cursor:
                cursor = connection.cursor()
                result = cursor.fetchall()
    except Exception as e:
        print(e)    

@app.route('/login',methods=['GET', 'POST'])
def login():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'useremail' in request.form and 'userpassword' in request.form :
        username.request.get("username")
        password.request.get("userpassword")
        usernamedata = cursor.execute("select username from user where username=%s",(username))
        passworddata = cursor.execute("select username from user where userpassword=%s",(userpassword))
        data=cursor.fetchone()

        if usernamedata is None:
            msg='Login Successfully!'
            return render_template("login.html")
    else:
        msg='Invalid Login. Try Again'
        return render_template('login.html')
    return render_template('login.html')

    try:
        with mysql.connector.connect(host="localhost",user="root",password="password_123",database="accounts") as connection:
            with connection.cursor() as cursor:
                cursor = connection.cursor()
                result = cursor.fetchall()         
    except Exception as e:
        print(e)

        
if __name__=="__main__":

    app.secret_key = "some_random_key"
    app.run(host="0.0.0.0", port=50000) 


















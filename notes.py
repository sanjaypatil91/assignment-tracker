Download a file

from flask import Flask, request,render_template ,send_file 

app = Flask(__name__) 

Download a file
@app.route('/')
def upload_form():
    return render_template('download.html')          


@app.route('/download_file',methods=['POST', 'GET'])
def download_file():
    if request.method=='GET':
        path = "login.docx"

    return send_file(path, as_attachment=True)



Read a file.....
from flask import Flask, render_template 
 
app = Flask(__name__) 
 
@app.route('/') 
def content(): 
    with open('textfile.txt', 'r') as f: 
        return render_template('content.html', text=f.read())


Upload assignment....

from flask import Flask, render_template, url_for, request

app = Flask(__name__)

 

@app.route('/')
@app.route('/Home')
def home():
    return render_template("index.html")

@app.route('/result',methods=['POST', 'GET'])
def result():
    output = request.form.to_dict()
    print(output)
    name = output["name"]
    return render_template('index.html', name = name)


if __name__ == "__main__":
    app.run(debug=True)

Main program

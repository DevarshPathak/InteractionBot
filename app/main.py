from flask import Flask,render_template,request,jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_mail import Mail, Message
from random import randint
from flask import Flask, redirect, url_for, session, request
import os
import jwt
import datetime
import json
from flask_cors import CORS
from werkzeug.utils import secure_filename
import assemblyai as aai

api_key = None
with open('<PATH_TO_ASSEMBLY_KEY>', 'r') as f:
    api_key1 = f.read().strip()
aai.settings.api_key = api_key1
app = Flask(__name__)
path = os.getcwd()
app.static_folder = 'static'
CORS(app)
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')
CORS(app, resources={r"/*": {"origins": "http://0.0.0.0:5000"}})

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = '<HOST_NAME>'
app.config['MYSQL_USER'] = '<USERNAME>'
app.config['MYSQL_PASSWORD'] = '<PASSWORD>'
app.config['MYSQL_DB'] = 'drugInteraction'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = '<EMAIL>'
app.config['MAIL_PASSWORD'] = '<PASSWORD>'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
mail = Mail(app)
secret_key = os.urandom(24)
secret_key_string = secret_key.hex()
app.secret_key = secret_key_string


# @app.before_request
# def check_authentication():
#     # Define a list of routes that do not require authentication
#     excluded_routes = ['/', '/signin', '/forgot', '/signup','/logout','/check_email','/forgotOTP','/passcpass']  # Add more routes as needed
    
#     # Check if the requested route requires authentication
#     if request.path not in excluded_routes and 'user' not in session:
#         # User is not authenticated, redirect them to the signin page
#         return redirect(url_for('signin'))



@app.route('/')
def hello_world():
    return render_template('signin.html')



@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' in request.files:
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return 'No selected audio file', 400
        if audio_file:
            filename = secure_filename(audio_file.filename)
            print('filename--->',filename)
            audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            FILE_URL="uploads/"+filename
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(FILE_URL)
            print(transcript.text)
            t = transcript.text
            return jsonify({'transcriptText':t,'status':200,'success':'true'})
    return 'No audio file provided', 400


@app.route('/generate_response', methods=['POST'])
def generate_response():
    question = request.json.get('message')  # Retrieve JSON data correctly
    from agent import generate_response
    data = generate_response(question)
    print('data----->',data)
    return jsonify({'data':data,'status':200,'success':'true'})


CORS(app, origins=['http://127.0.0.1:5000/upload-audio'])

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM credentials WHERE email = % s', (email, ))
        account = cursor.fetchone()
        print(account)
        if account:
            if account['password'] == pwd:
                if account['isverify'] == "1" or account['isverify'] == True:
                    payload = {
                            'id': account['id'],
                            'email': account['email'],
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
                        }
                    token = jwt.encode(
                        payload, app.secret_key, algorithm='HS256')
                    cursor.execute(
                        'update credentials set token= %s where email = %s', (token, email,))
                    mysql.connection.commit()
                    cursor.close()
                    msg = 'Logged in successfully !'
                    print(msg)   
                    return render_template('index.html')
                
                msg = 'Please verify your email !'
                print(msg)  
                generate_otp = randint(1111, 9999)
                msg = Message('Verify Your Registration',
                            sender='edupmetest@gmail.com', recipients=[email])
                msg.body = "Your verification code is: " + str(generate_otp)
                mail.send(msg)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    'SELECT * FROM credentials WHERE email = % s', (email,))
                account = cursor.fetchone()
                if account:
                    cursor.execute(
                        'update credentials set otp = %s where email = %s', (generate_otp, email,))
                    mysql.connection.commit()

                    msg = "Successfully email submit!"
                    cursor.close()


                return render_template('verifyOTP.html', email=email)
                    
            cursor.close()
            msg = 'Incorrect password !'
            print(msg)   
            return render_template('signin.html',msg=msg)
        cursor.close()
        msg = "Your Email Doesn't Exits!"
        return render_template('signin.html',msg=msg)
    
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        pwd = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM credentials WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            msg = 'Email Already Exits!'
            cursor.close()
            print(msg)
            return render_template('signup.html',msg=msg)
        else:
            sql = "INSERT INTO credentials (username, email,password,isverify) VALUES (%s, %s, %s,%s)"
            val = (username, email, pwd, False)
            cursor.execute(sql, val)
            mysql.connection.commit()
            cursor.close()
            msg = 'You have successfully registered!'
            print(msg)

            generate_otp = randint(1111, 9999)
            msg = Message('Verify Your Registration',
                          sender='edupmetest@gmail.com', recipients=[email])
            msg.body = "Your verification code is: " + str(generate_otp)
            mail.send(msg)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM credentials WHERE email = % s', (email,))
            account = cursor.fetchone()
            print('account---->',account)
            if account:
                print('--------')
                payload = {
                            'id': account['id'],
                            'email': account['email'],
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
                        }
                token = jwt.encode(
                    payload, app.secret_key, algorithm='HS256')
                print('generate_otp---->',generate_otp,email,token)
                cursor.execute(
                     'UPDATE credentials SET otp = %s, token = %s WHERE email = %s', (generate_otp, token, email))
                mysql.connection.commit()

                msg = "Email submitted successfully!"
                print(msg)
                cursor.close()

            return render_template('verifyOTP.html', email=email)

    return render_template('signup.html')


@app.route('/verifyOTP', methods=['GET', 'POST'])
def verifyOTP():
    if request.method == 'POST':
        email = request.form['email']
        otp = request.form['otp']
        print(email)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM credentials WHERE email = % s', (email,))
        account = cursor.fetchone()
        print
       
        if account:
            generate_otp = account['otp']
            print(otp,generate_otp)
            if str(generate_otp) == str(otp):
                cursor.execute(
                    'update credentials set isverify = %s where email = %s', ('1', email,))
                mysql.connection.commit()

                msg = 'your OTP matched successfully'
                print(msg)
                cursor.close()
                return render_template('index.html',msg=msg, email=email)
            msg = "Your OTP does not match"
            print(msg)
            cursor.close()
            return render_template('verifyOTP.html',msg=msg, email=email)
        msg = "Email Doesn't Exists"
        print(msg)
        cursor.close()
    email=request.args.get('email','')
    return render_template('verifyOTP.html',email=email)

@app.route('/passcpass',methods=['GET','POST'])
def passcpass():
    if request.method=='POST':
        email = request.form['email']
        npass = request.form['New password']
        print(npass)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT otp FROM credentials WHERE email = % s', (email,))
        account = cursor.fetchone()
        if account:
            cursor.execute(
                    'update credentials set password = %s where email = %s', (npass, email,))
            mysql.connection.commit()
            return render_template('signin.html')
        msg = "Email Doesn't Exists"
        return render_template('passcpass.html',msg=msg)
    email=request.args.get('email','')
    return render_template('passcpass.html',email=email)
    
@app.route('/forgotOTP', methods=['GET', 'POST'])
def forgotOTP():
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT otp FROM credentials WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            if account['otp']:
                if str(account['otp']) == request.form['otp']:
                    cursor.execute('UPDATE credentials SET isverify = %s WHERE email = %s', (True, email,))
                    mysql.connection.commit()
                    return render_template('passcpass.html', email=email)
                else:
                    msg = "Your OTP does not match"
                    return render_template('forgotOTP.html', msg=msg, email=email)
            else:
                msg = "No OTP found for this email"
                return render_template('forgotOTP.html', msg=msg, email=email)
        else:
            msg = "Email doesn't exist"
            return render_template('forgotOTP.html', msg=msg, email=email)

    email = request.args.get('email', '')
    return render_template('forgotOTP.html', email=email)

@app.route('/check_email', methods=['GET','POST'])
def check_email():
    email = request.json.get('email')
    print(email)

    # Query the database to check if the email exists
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM credentials WHERE email = %s', (email,))
    account = cursor.fetchone()
    cursor.close()

    # Return a JSON response indicating whether the email exists or not
    if account:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM credentials WHERE email = % s', (email,))
        account = cursor.fetchone()
        print(email)
        if account:
            generate_otp = randint(111111, 999999)
            msg = Message('Verify Your Registration',
                            sender='edupmetest@gmail.com', recipients=[email])
            msg.body = "Your verification code is: " + str(generate_otp)
            mail.send(msg)
            print(generate_otp)
            cursor.execute(
                    'update credentials set otp = %s where email = %s', (generate_otp, email,))
            mysql.connection.commit()
            return render_template("forgotOTP.html",email=email)
        msg="Email doesn't exists!"
        return render_template("forgot.html",msg=msg)     
    return render_template('forgot.html')


@app.route('/logout')
def logout():
    # Clear user session data upon logout
    session.pop('user', None)
    return redirect(url_for('signin'))



# main driver function
if __name__ == '__main__':
    app.run(host="0.0.0.0")

from flask import Flask, redirect, url_for, render_template
from flask import session, request, send_from_directory
from flask_wtf import FlaskForm
import pyrebase
import firebase_admin
from firebase_admin import db, credentials, firestore
from datetime import datetime
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from grayscale import grayscale
import firebaseStorage

app = Flask(__name__)

config = {
    "apiKey": "AIzaSyDCe_5uQYZrSH87RQ9kp9pfJgG8PA8IHsk",
    "authDomain": "relatives-test.firebaseapp.com",
    "projectId": "relatives-test",
    "storageBucket": "relatives-test.appspot.com",
    "messagingSenderId": "1063389234635",
    "appId": "1:1063389234635:web:981285ab821cd1702f624e",
    "databaseURL": "https://relatives-test-default-rtdb.firebaseio.com"
    # "databaseURL":"gs://relatives-test.appspot.com"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
storage = firebase.storage()

app.secret_key = 'e6rduyitfvdasjkb'

# Upload folder
app.config['UPLOAD_FOLDER'] = 'static/files'

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

filepath = relativefilepath = ''

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    relativeFile = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload Files")


@app.route('/')
def home():
    if 'user' in session:
        app.logger.info(session)
        email = session['user']
        password = session['password']
        auth.sign_in_with_email_and_password(email, password)
    return render_template("404.html")


# @app.route('/addToPastTests', methods=["POST", "GET"])
# def addToPastTests():
#     if 'user' in session:
#         userInfo = db.collection('users').document(session['user'])
#         userInfo.update({'pasttests': firestore.ArrayUnion([str(datetime.now())])})
#         storage.child('hello.png').put('static/files/mountains.png')
#         #firebaseStorage.pushFile('static/files/mountains.png')
#         return 'Hello'



@app.route('/takethetest', methods=["POST", "GET"])
def test():
    global filepath, relativefilepath
    form = UploadFileForm()


    if form.validate_on_submit():
        if 'user' in session:
            # First grab the file
            file = form.file.data
            relativeFile = form.relativeFile.data

            filePath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                   secure_filename(file.filename))
            relativeFilePath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                   secure_filename(relativeFile.filename))

            file.save(filePath)  # Then save the file
            relativeFile.save(relativeFilePath)

            app.logger.info("files saved")

            testName = str(datetime.now()).replace(" ","")
            # link in pasttests
            userInfo = db.collection('users').document(session['user'])
            userInfo.update({'pasttests': firestore.ArrayUnion([testName])})

            #store in Storage
            storage.child(str(session['user'])+"-"+testName+'/main.png').put(filePath)
            storage.child(str(session['user']) + "-" + testName + '/relative.png').put(filePath)

            #store links
            link = storage.child(str(session['user']) + "-" + testName + '/main.png').get_url(None)
            relativeLink = storage.child(str(session['user']) + "-" + testName + '/relative.png').get_url(None)

            userInfo = db.collection('links').document(str(session['user'])+"-"+testName)
            userInfo.set({
                "mainLink": link,
                "relativeLink": relativeLink
            })




            # os.remove(filePath)
            # os.remove(relativeFilePath)
            #app.logger.info()
            # render_template('displayImage.html', link=link)
            return redirect('/getanalysis')
        else:
            return 'Login First'
        # try:
        #     firebaseStorage.pushFile(file.filename)
        # except:
        #     app.logger.info('problem')



        # os.remove('/static/files/'+file.filename)




    return render_template('upload.html', form=form)
    # return render_template("test.html")

@app.route('/imageChangeing')
def imageChanging():
    storage.child('djjagga@gmail.com-2023-03-0211:22:05.254523.png').download('static/files/downloadedimage.png')

    initial = 'static/files/downloadedimage.png'
    destination = 'static/files/grayscale.png'

    grayscale(initial, destination)

    return render_template('chooseFile.html', link=url_for('static', filename='files/grayscale.png'))
# The Team
@app.route('/davidjagga')
def davidjagga():
    # data = ['account']
    return render_template("404.html")


@app.route('/siddrangavajulla')
def siddrangavajulla():
    return render_template("404.html")


@app.route('/dhruvaddanki')
def dhruvaddanki():
    return render_template("404.html")


# How does it work?
@app.route('/goldenratio')
def goldenratio():
    return render_template("404.html")


@app.route('/symmetry')
def symmetry():
    return render_template("404.html")


@app.route('/featuredetection')
def featuredetection():
    return render_template("404.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'user' in session:
        return redirect('/')
    if request.method == "POST":
        app.logger.info('smth happening')
        email = request.form.get('email')
        password = request.form.get('password')
        app.logger.info(f'Email :{email}, Password: {password}')
        try:
            app.logger.info('1')
            user = auth.sign_in_with_email_and_password(email, password)
            app.logger.info('2')
            session['user'] = email
            session['password'] = password
            app.logger.info('Logged In')
            return redirect('/')

        except:
            print("hello")
            app.logger.info('Failed to Log In 2')
    app.logger.info(f'Failed to Log In, {request.method}')
    return render_template("bootstrap/login.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'user' in session:
        return redirect('/')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        fname = request.form.get('firstname')
        lname = request.form.get('lastname')
        pass2 = request.form.get('password2')
        try:
            app.logger.info(email)
            app.logger.info(password)
            user = auth.create_user_with_email_and_password(email, password)
            app.logger.info("Made account")
            session['user'] = email
            session['password'] = password
            app.logger.info("Put account in session")

            userInfo = db.collection('users').document(email)
            userInfo.set({
                "fname": fname,
                "lname": lname,
                "email": email,
                "pasttests": []

            })
            app.logger.info("Made user info collection")

            # app.logger.info('Logged In')
            return redirect('/')

        except:
            print('hello')
            app.logger.info('Failed to Register')
    # app.logger.info('Failed to Log In')
    return render_template("bootstrap/register.html")


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        session.pop('password')
    return redirect('/login')
    # return render_template("bootstrap/blank.html")


@app.route('/resetpassword')
def resetpassword():
    if request.method == "POST":
        email = request.form.get('email')
        try:
            auth.send_password_reset_email(email)
        except:
            print('hello')
    return render_template("bootstrap/forgot-password.html")


@app.route('/pasttests')
def pasttests():
    return render_template("404.html")




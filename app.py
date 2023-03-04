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
from imageanalysistest import grayscale2
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

filePath = relativeFilePath = ''

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    relativeFile = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload Files")



@app.route('/', methods=["POST", "GET"])
def test():
    global filePath, relativeFilePath
    form = UploadFileForm()


    if 'user' in session:
        email = session['user']
        password = session['password']
        auth.sign_in_with_email_and_password(email, password)
        if form.validate_on_submit():

            # First grab the file
            file = form.file.data
            relativeFile = form.relativeFile.data

            filePath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                   secure_filename("main"+file.filename))
            relativeFilePath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                   secure_filename("relative"+relativeFile.filename))

            file.save(filePath)  # Then save the file
            relativeFile.save(relativeFilePath)

            app.logger.info("files saved")

            testName = str(datetime.now()).replace(" ","")
            # link in pasttests
            userInfo = db.collection('users').document(session['user'])
            userInfo.update({'pasttests': firestore.ArrayUnion([testName])})

            #store in Storage
            storage.child("img/"+str(session['user'])+"-"+testName+'/main.png').put(filePath)
            storage.child("img/"+str(session['user']) + "-" + testName + '/relative.png').put(filePath)

            #store links
            link = storage.child("img/"+str(session['user']) + "-" + testName + '/main.png').get_url(None)
            relativeLink = storage.child("img/"+str(session['user']) + "-" + testName + '/relative.png').get_url(None)

            userInfo = db.collection('links').document(str(session['user'])+"-"+testName)
            userInfo.set({
                "mainLink": link,
                "relativeLink": relativeLink
            })


            # os.remove(filePath)
            # os.remove(relativeFilePath)
            return redirect('/getanalysis')
        else:
            return render_template('upload.html', form=form)
    else:
        return render_template('404.html', error="Login first!", active='test')
    # return render_template("test.html")
@app.route('/getanalysis')
def analysis():
    if not (filePath or relativeFilePath): return redirect('/')
    analysis = grayscale2(filePath, relativeFilePath)
    analysis['filepath'] = analysis['filepath'][analysis['filepath'].index('/static'):]
    analysis['relativefilepath'] = analysis['relativefilepath'][analysis['relativefilepath'].index('/static'):]

    return render_template('displayImage.html', analysis=analysis)

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
    return render_template("bootstrap/login.html", active='account')

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
    return render_template("bootstrap/register.html", active='account')


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        session.pop('password')
    return render_template('bootstrap/logout.html')

@app.route('/resetpassword')
def resetpassword():
    if request.method == "POST":
        email = request.form.get('email')
        try:
            auth.send_password_reset_email(email)
        except:
            print('hello')
    return render_template("bootstrap/forgot-password.html", active='account')


@app.route('/pasttests')
def pasttests():
    if 'user' not in session: return render_template("404.html", error="You haven't logged in just yet", active='account')
    email = str(session['user'])

    userInfo = db.collection('users').document(email).get().to_dict()

    testList = userInfo['pasttests']
    if not testList: return render_template('404.html', error="You don't have any past tests yet!", active='account')

    testList = testList[:10]

    links = db.collection('links')

    linkList = []


    for test in testList:
        testlinks = links.document(email + "-" + test).get().to_dict()
        mainLink = testlinks['mainLink']
        relativeLink = testlinks['relativeLink']
        linkList.append({
            'main': mainLink,
            'relative': relativeLink,
            'test': test
        })
    app.logger.info(linkList)


    return render_template('pastTests.html', links=linkList, email=email, active='account')

@app.route('/oldtest/<testid>')
def oldtest(testid):
    global filePath, relativeFilePath
    if 'user' not in session: return render_template('404.html', error="Login first!", active='test')

    filePath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                            secure_filename("main.png"))
    relativeFilePath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                    secure_filename("relative.png"))

    try:
        storage.child("img/"+testid+"/main.png").download(filePath)
        storage.child("img/" + testid + "/relative.png").download(relativeFilePath)
    except:
        return render_template('404.html', error='File Not Found', active="")


    return redirect('/getanalysis')


#Information Pages

@app.route('/davidjagga')
def davidjagga():
    # data = ['account']
    return render_template("404.html", error="We're still making this page.", active='team')


@app.route('/siddrangavajulla')
def siddrangavajulla():
    return render_template("404.html", error="We're still making this page.", active='team')


@app.route('/dhruvaddanki')
def dhruvaddanki():
    return render_template("404.html", error="We're still making this page.", active='team')


# How does it work?
@app.route('/goldenratio')
def goldenratio():
    return render_template("404.html", error="We're still making this page.", active='info')


@app.route('/symmetry')
def symmetry():
    return render_template("404.html", error="We're still making this page.", active='info')


@app.route('/featuredetection')
def featuredetection():
    return render_template("404.html", error="We're still making this page.", active='info')





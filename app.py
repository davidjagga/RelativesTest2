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


class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route('/')
def home():
    if session:
        app.logger.info(session)

    return render_template("test.html")


@app.route('/addToPastTests')
def addToPastTests():
    if session:
        userInfo = db.collection('users').document(session['user'])
        userInfo.update({'pasttests': firestore.ArrayUnion([str(datetime.now())])})


@app.route('/takethetest', methods=["POST", "GET"])
def test():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data  # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))  # Then save the file
        return "File has been uploaded to static/files folder"
    return render_template('index.html', form=form)
    # return render_template("test.html")


# The Team
@app.route('/davidjagga')
def davidjagga():
    # data = ['account']
    return render_template("bootstrap/blank.html")


@app.route('/siddrangavajulla')
def siddrangavajulla():
    return render_template("bootstrap/blank.html")


@app.route('/dhruvaddanki')
def dhruvaddanki():
    return render_template("bootstrap/blank.html")


# How does it work?
@app.route('/goldenratio')
def goldenratio():
    return render_template("bootstrap/blank.html")


@app.route('/symmetry')
def symmetry():
    return render_template("bootstrap/blank.html")


@app.route('/featuredetection')
def featuredetection():
    return render_template("bootstrap/blank.html")


from account import accountspage

app.register_blueprint(accountspage)
# Account





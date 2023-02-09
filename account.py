from flask import Blueprint
from flask import Flask, redirect, url_for, render_template, session, request
from app import app, auth, db

accountspage = Blueprint('accountspage', __name__, template_folder='templates')


@accountspage.route('/login', methods=['POST', 'GET'])
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


@accountspage.route('/register', methods=['POST', 'GET'])
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


@accountspage.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect('/login')
    # return render_template("bootstrap/blank.html")


@accountspage.route('/resetpassword')
def resetpassword():
    if request.method == "POST":
        email = request.form.get('email')
        try:
            auth.send_password_reset_email(email)
        except:
            print('hello')
    return render_template("bootstrap/forgot-password.html")


@accountspage.route('/pasttests')
def pasttests():
    return render_template("bootstrap/blank.html")


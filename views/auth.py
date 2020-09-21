# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import Blueprint, json, request, render_template, redirect, url_for, make_response
from datetime import datetime, timedelta, time
auth = Blueprint('auth', __name__)

import classes.classes as classes



@auth.route("/login", methods=['GET','POST'])
def login ():
    return render_template("login.html")

@auth.route("/submitlogin", methods=['GET','POST'])
def submitlogin ():
    sysvars=classes.globalvars()
    username=request.form['username']
    password=request.form['password']
    result=classes.submitLogin(username,password)
    if result==0:
        return render_template("login.html", message="Login failure")
    elif result==2:
        return render_template("changepassword.html",username=username)
    else:
        expire_date = datetime.now()
        expire_date = expire_date + timedelta(days=1)
        response = make_response(redirect(sysvars['landingpage']))  
        response.set_cookie('username',result['username'], expires=expire_date, max_age=int(sysvars['idle_timeout']))
        response.set_cookie('token',result['token'], expires=expire_date, max_age=int(sysvars['idle_timeout']))
        return response


@auth.route("/submitchangepassword",methods=['GET','POST'])
def submitchangepassword():
    # First check if the passwords are the same
    if request.form['password']==request.form['repeatpassword']:
        print("Passwords are the same")
        classes.changePassword(request.form['username'],request.form['password'])
    else:
        print("Passwords are not the same")
        return render_template("changepassword.html", username=request.form['username'],message="Passwords are not the same")
    return render_template("login.html", message="Password changed")

@auth.route("/logout", methods=['GET','POST'])
def logout ():
    return redirect(url_for('auth.login'))

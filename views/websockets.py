# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, json, request, render_template, jsonify
websockets = Blueprint('websockets', __name__)
from datetime import datetime
import requests
import urllib
import json
import classes.classes as classes
sessionid = requests.Session()

@websockets.route("/subscribe", methods=['GET','POST'])
def subscribe ():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        try:
            formresult=request.form
        except:
            formresult=[]
        queryStr="select id, description, ipaddress, ostype, platform, osversion from devices where ostype='arubaos-cx'"
        devicelist=classes.sqlQuery(queryStr,"select")
        return render_template("websockets.html", formresult=formresult, devicelist=devicelist, authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@websockets.route("/getcxcookie", methods=['GET','POST'])
def getcxCookie ():
    authOK=classes.checkAuth()
    global sessionid
    if authOK!=0:
        sysvars=classes.globalvars()
        my_cookie=list()
        formresult=request.form
        queryStr="select * from devices where (id='{}')".format(formresult['deviceid'])
        deviceresult=classes.sqlQuery(queryStr,"selectone")
        url = "https://" + deviceresult['ipaddress']
        baseurl="https://{}/rest/v1/".format(deviceresult['ipaddress'])
        credentials={'username': deviceresult['username'],'password': classes.decryptPassword(sysvars['secret_key'], deviceresult['password']) }
        # Login to the switch. The cookie value is stored in the session cookie jar
        response = sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=5)
        for cookie in response.cookies:
            cEntry= {"name":cookie.name,"value":cookie.value,"domain":deviceresult['ipaddress'],"path":'/'}
            my_cookie.append(dict(cEntry))
        return json.dumps({'deviceip':deviceresult['ipaddress'],'cookies':my_cookie})
    else:
        return render_template("login.html")


@websockets.route("/getSubs", methods=['GET','POST'])
def getSubs():
    authOK=classes.checkAuth()
    if authOK!=0:
        try:
            subscriptions=classes.getSubscriptions(request.form['deviceid'],request.form['subscriber_name'])
        except:
            subscriptions=[]
        return json.dumps(subscriptions)
    else:
        return render_template("login.html")

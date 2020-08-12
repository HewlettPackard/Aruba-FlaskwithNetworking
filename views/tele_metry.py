# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, request,json, render_template
import socket
from datetime import datetime
import psutil, sys, os, platform, subprocess
from subprocess import Popen, PIPE

tele_metry = Blueprint('tele_metry', __name__)

import classes.classes as classes

@tele_metry.route("/telemetry", methods=['GET', 'POST'])
def telemetry ():
    authOK=classes.checkAuth("telemetry","menu")
    if authOK!=0:
        # Check on which IP address the server is listening
        # Obtain the active IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        hostip=s.getsockname()[0]
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant device information from the database
        result=classes.telemetrydbAction(formresult)
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("telemetry.html",result=result['result'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars, hostip=hostip)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")


@tele_metry.route("/subscriptions", methods=['GET','POST'])
def subscriptions ():
    formresult=request.form
    sysvars=classes.globalvars()
    # Perform actions based on the form input

    if "resource" in formresult:
        resource=formresult['resource']
    else:
        resource=""
    if "subscriber" in formresult:
        subscriber=formresult['subscriber']
    else:
        subscriber=""
    if "addSubscription" in formresult:
        addSubscription=formresult['addSubscription']
    else:
        addSubscription = ""
    if "confirmDelete" in formresult:
        confirmDelete=formresult['confirmDelete']
    else:
        confirmDelete = 0
    deviceinfo=classes.subscriptionAction(formresult['action'],formresult['id'], subscriber, resource, addSubscription, confirmDelete)
    return json.dumps({'deviceinfo':deviceinfo,'subscriptions':deviceinfo['subscriptions']})


@tele_metry.route("/telemetrystatus", methods=['GET','POST'])
def telemetrystatus ():
    formresult=request.form
    sysvars=classes.globalvars()
    # Perform actions based on the form input
    isRunning=classes.checkRunningws(formresult['deviceid'])
    subscriptions=classes.checkSubscriptions(formresult['deviceid'])
    return json.dumps({"deviceid":formresult['deviceid'],"isRunning": isRunning,"subscriptions":subscriptions})

@tele_metry.route("/startwsClient", methods=['GET','POST'])
def startwsClient ():
    formresult=request.form
    scriptName="/var/www/html/bash/wsclient.py"
    args=["python3",scriptName,str(formresult['id'])]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return json.dumps({"status":"ok"})




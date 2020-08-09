# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, json, request
from werkzeug.datastructures import ImmutableMultiDict
import time
sysadmin = Blueprint('sysadmin', __name__)

from datetime import datetime, time
from flask import render_template

import classes.classes as classes

@sysadmin.route("/useradmin",methods=['GET','POST'])
def useradmin():
    authOK=classes.checkAuth("sysuseraccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant information from the database
        result=classes.userdbAction(formresult)
        if authOK['hasaccess']==True:
            return render_template("useradmin.html",result=result['userresult'],roleresult=result['roleresult'],formresult=formresult, authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@sysadmin.route("/userroles",methods=['GET','POST'])
def userroles():
    authOK=classes.checkAuth("sysroleaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        dictform=formresult.to_dict(flat=True)
        # Obtain the relevant information from the database
        result=classes.roledbAction(dictform)
        if authOK['hasaccess']==True:
            return render_template("roleadmin.html",result=result,formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")


@sysadmin.route("/editrole",methods=['GET','POST'])
def editrole():
    formresult=request.form
    sysvars=classes.globalvars()
    queryStr="select * from sysrole where id='{}'".format(formresult['id'])
    # Obtain the relevant user role information from the database
    result=classes.sqlQuery(queryStr,"selectone")
    return json.dumps(result)


@sysadmin.route("/sysconf",methods=['GET','POST'])
def sysconf():
    authOK=classes.checkAuth("sysadminaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        try:
            if formresult['action']=="Submit changes":
                classes.submitsysConf(formresult)
                sysvars=classes.globalvars()
        except:
            pass
        return render_template("sysconf.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@sysadmin.route("/sysmon",methods=['GET','POST'])
def sysmon():
    authOK=classes.checkAuth("servicesstatusaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        if formresult:
            classes.processAction(formresult['name'],formresult['action'])
        if authOK['hasaccess']==True:
            return render_template("sysmon.html",authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@sysadmin.route("/factory",methods=['GET','POST'])
def factory():
    formresult=request.form
    if formresult:
        classes.factoryDefault(formresult)    
        return render_template("login.html")
    else:
        return render_template("factorydefault.html")

@sysadmin.route("/monitorProcess",methods=['GET','POST'])
def monitorProcess():
    # Check whether the process is running and return this information in the rendered page
    sysvars=classes.globalvars()
    processInfo=classes.checkProcess(request.args.get('name'))
    return render_template("monitorprocess.html", sysvars=sysvars, name=request.args.get('name'), status=processInfo['status'], cpu=processInfo['cpu'], memory=processInfo['memory'])

@sysadmin.route("/getsysTime",methods=['GET','POST'])
def getsysTime():
    # Return system time to calling station
    sysTime=classes.sysTime()
    return json.dumps(sysTime)

@sysadmin.route("/ipamStatus",methods=['GET','POST'])
def ipamStatus():
    # Check whether IPAM is online
    formresult=request.form
    if formresult['ipamsystem']=="PHPIPAM":
        result=classes.checkPhpipam(formresult)
    elif formresult['ipamsystem']=="Infoblox":
        result=classes.checkInfoblox(formresult)
    return result

@sysadmin.route("/clearprocessLog",methods=['GET','POST'])
def clearprocessLog():
    formresult=request.form
    with open("/var/www/html/log/{}.log".format(formresult['processName']), 'w') as logFile:
        # Write the timestamp
        timestamp=str(int(datetime.now().timestamp()))
        logFile.write("---"+timestamp+"---\n")
    logFile.close()
    return "{} Log is cleared".format(formresult['processName'])

@sysadmin.route("/downloadLog",methods=['GET','POST'])
def downloadLog():
    formresult=request.form
    logFile=open("/var/www/html/log/{}.log".format(formresult['processName'],"r"))
    logContent=logFile.read()
    logFile.close()
    return json.dumps([formresult['processName'],logContent])
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, request, json, redirect, render_template
import os
from urllib.parse import quote
from jinja2 import Template, Environment, meta
deviceupgrades = Blueprint('deviceupgrades', __name__)

from datetime import datetime


ALLOWED_EXTENSIONS = set(['swi','SWI'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import classes.classes as classes


@deviceupgrades.route("/deviceimages", methods=['GET','POST'])
def deviceimages ():
    authOK=classes.checkAuth("imageaccess","submenu")
    message=""
    filename=""
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        if formresult:
            if formresult['action']=="Submit image" or formresult['action']=="Submit changes":
                # check if the post request has the file part
                if request.files['softwareimage']:
                    file = request.files['softwareimage']
                    if file.filename == '':
                        message='No file selected for uploading'
                    if file and allowed_file(file.filename):
                        file.save(os.path.join('/var/www/html/images/', file.filename))
                        message=''
                        filename=file.filename
                    else:
                        message='Allowed file type is swi'
            # Obtain the relevant device information from the database
            result=classes.imagedbAction(formresult,filename,message)
        else:
            # Obtain the relevant device information from the database
            result=classes.imagedbAction(formresult,'','')
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("deviceimages.html",result=result['result'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")


@deviceupgrades.route("/upgradescheduler", methods=['GET','POST'])
def upgradescheduler ():
    authOK=classes.checkAuth("upgradescheduleraccess","submenu")
    message=""
    filename=""
    upgradeStatus={0:'Not started', 1: 'Upgrade initiated', 5: 'Copy software onto the switch', 10: 'Software copied successfully', 20: 'Software copied successfully: switch is rebooted', 50: 'There is another software upgrade in progress', 100: 'Software upgrade completed successfully', 110: 'Software upgrade completed successfully: reboot is required' }
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        result=classes.upgradescheduledbAction(formresult)
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("upgradescheduler.html",upgraderesult=result['upgraderesult'], upgradestatus=upgradeStatus, switchresult=result['switchresult'],formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")


@deviceupgrades.route("/imageInfo", methods=['GET','POST'])
def imageInfo ():
    formresult=request.form
    sysvars=classes.globalvars()
    queryStr="select * from deviceimages where id='{}'".format(formresult['id'])
    # Obtain the relevant image information from the database
    result=classes.sqlQuery(queryStr,"selectone")
    return json.dumps(result)


@deviceupgrades.route("/upgradeStatus", methods=['GET','POST'])
def upgradeStatus ():
    formresult=request.form
    sysvars=classes.globalvars()
    queryStr="select * from softwareupdate where id='{}'".format(formresult['id'])
    # Obtain the relevant software update information from the database
    upgraderesult=classes.sqlQuery(queryStr,"selectone")
    queryStr="select ipaddress, description,ostype,osversion from devices where id='{}'".format(upgraderesult['switchid'])
    # Obtain the relevant device information from the database
    switchresult=classes.sqlQuery(queryStr,"selectone")
    upgraderesult['switchresult']=switchresult
    return json.dumps(upgraderesult)


@deviceupgrades.route("/switchReboot", methods=['GET','POST'])
def switchReboot ():
    formresult=request.form
    sysvars=classes.globalvars()
    queryStr="select * from softwareupdate where id='{}'".format(formresult['id'])
    # Obtain the relevant software update information
    upgraderesult=classes.sqlQuery(queryStr,"selectone")
    queryStr="select ostype from devices where id='{}'".format(formresult['deviceid'])
    # Obtain the relevant software update information
    deviceresult=classes.sqlQuery(queryStr,"selectone")
    if deviceresult['ostype']=="arubaos-switch":
        if upgraderesult['activepartition']=="primary":
            activepartition="BI_PRIMARY_IMAGE"
        else:
            activepartition="BI_SECONDARY_IMAGE"
    else:
        activepartition=upgraderesult['activepartition']
    response=classes.bootSwitch(deviceresult['ostype'],formresult['id'], formresult['deviceid'], activepartition)
    return json.dumps(response)


@deviceupgrades.route("/deleteUpgrade", methods=['GET','POST'])
def deleteupgrade ():
    formresult=request.form
    sysvars=classes.globalvars()
    print(formresult)
    queryStr="delete from softwareupdate where id='{}'".format(formresult['id'])
    print(queryStr)
    try:
        response=classes.sqlQuery(queryStr,"selectone")
    except:
        response={"message":"Scheduled upgrade removal failed"}
    return json.dumps(response)
    


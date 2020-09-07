# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, json, request
anycli = Blueprint('anycli', __name__)

from datetime import datetime
from flask import render_template

import classes.classes as classes

@anycli.route("/anycli", methods=['GET','POST'])
def index ():
    authOK=classes.checkAuth("anycliaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        try:
            formresult=request.form
        except:
            formresult=[]
        queryStr="select id, description, ipaddress, ostype, platform, osversion from devices where ostype='arubaos-switch'"
        devicelist=classes.sqlQuery(queryStr,"select")
        if formresult:
            if classes.checkifOnline(formresult['deviceid'],"arubaos-switch")=="Online":
                if formresult['cmd']:
                    cmdResult=classes.anycli(formresult['cmd'],formresult['deviceid'])
                    if cmdResult:
                        cmdContent=classes.b64decode(cmdResult['result_base64_encoded']).decode('utf_8')
                    else:
                        cmdContent="Could not obtain information"
                else:
                    cmdResult=[]
                    cmdContent="No command entered..."
            else:
                cmdResult=[]
                cmdContent="Switch is offline"
        else:
            cmdResult=[]
            cmdContent=[]
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("anycli.html", formresult=formresult, devicelist=devicelist, cmdResult=cmdResult, cmdContent=cmdContent, authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

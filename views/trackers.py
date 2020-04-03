# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, json, request
import time
trackers = Blueprint('trackers', __name__)

from datetime import datetime
from flask import render_template

import classes.classes as classes

@trackers.route("/snmptracker",methods=['GET','POST'])
def snmptracker():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        try:
            if formresult['action']=="Delete":
                classes.deleteEntry("snmptracker",formresult['id'])
        except:
            pass
        # Obtain the relevant device information from the database
        result=classes.snmpdbAction(formresult)
        return render_template("snmptracker.html",result=result['dbresult'],formresult=formresult, versionInfo=result['versionInfo'],communityInfo=result['communityInfo'],totalentries=result['totalentries'],pageoffset=result['pageoffset'],entryperpage=result['entryperpage'], authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@trackers.route("/dhcptracker",methods=['GET','POST'])
def dhcptracker():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        try:
            if formresult['action']=="Delete":
                classes.deleteEntry("dhcptracker",formresult['id'])
        except:
            pass
        # Obtain the relevant device information from the database
        result=classes.dhcpdbAction(formresult)
        return render_template("dhcptracker.html",result=result['dbresult'],formresult=formresult,dhcptypeInfo=result['dhcptypeInfo'],totalentries=result['totalentries'],pageoffset=result['pageoffset'],entryperpage=result['entryperpage'], authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@trackers.route("/syslog",methods=['GET','POST'])
def syslog():
    authOK=classes.checkAuth()
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        try:
            if formresult['action']=="Delete":
                classes.deleteEntry("syslog",formresult['id'])
        except:
            pass
        # Obtain the relevant device information from the database
        result=classes.syslogdbAction(formresult)
        return render_template("syslog.html",result=result['dbresult'],formresult=formresult,facilityInfo=result['facilityInfo'],severityInfo=result['severityInfo'],totalentries=result['totalentries'],pageoffset=result['pageoffset'],entryperpage=result['entryperpage'], authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")
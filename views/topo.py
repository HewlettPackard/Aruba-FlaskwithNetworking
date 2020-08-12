# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, request, json
topo = Blueprint('topo', __name__)

from datetime import datetime
from flask import render_template

import classes.classes as classes

@topo.route("/topology", methods=['GET', 'POST'])
def topology ():
    authOK=classes.checkAuth("topology","menu")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant device information from the database
        result=classes.topodbAction(formresult)
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("topology.html",result=result['result'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")


@topo.route("/endpointInfo", methods=['GET', 'POST'])
def endpointInfo ():
    sysvars=classes.globalvars()
    formresult=request.form
    # Obtain the relevant endpoint information from the database
    result=classes.endpointInfo(formresult['id'])
    return json.dumps(result)

@topo.route("/topodeviceStatus", methods=['GET', 'POST'])
def topodeviceStatus ():
    sysvars=classes.globalvars()
    formresult=request.form
    # Obtain the device status from the database
    result=classes.checktopoDevice(formresult['deviceid'])
    return result

@topo.route("/topoInfo", methods=['GET', 'POST'])
def topoInfo ():
    sysvars=classes.globalvars()
    formresult=request.form
    # Obtain the device status from the database
    result=classes.topoInfo(formresult['id'])
    topoInfo={'nodes':result[0],'links': result[1]}
    return json.dumps(topoInfo)
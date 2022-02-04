# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, request,json
arubacentral = Blueprint('arubacentral', __name__)

from datetime import datetime
from flask import render_template

import classes.classes as classes


@arubacentral.route("/checkauthentication", methods=['GET', 'POST'])
def checkauthentication ():
    sysvars=classes.globalvars()
    arubacentralvars=classes.obtainVars('sysarubacentral')
    if isinstance(arubacentralvars, str):
        arubacentralvars=json.loads(arubacentralvars)
    formresult=request.form
    # Only verify if centralcustomerid, centralclientid, centralclientsecret and centralurl variables exist
    # If arubacentraltokeninfo exists in the variables, we only have to check whether the token is still valid
    if "arubacentraltokeninfo" in arubacentralvars:
        response=classes.checkcentralToken("authentication")
    else:
        arubacentralvars.update({'arubacentralurl':formresult['arubacentralurl']})
        arubacentralvars.update({'arubacentralusername':formresult['arubacentralusername']})
        arubacentralvars.update({'arubacentraluserpassword':formresult['arubacentraluserpassword']})
        arubacentralvars.update({'arubacentralclientid':formresult['arubacentralclientid']})
        arubacentralvars.update({'arubacentralcustomerid':formresult['arubacentralcustomerid']})
        arubacentralvars.update({'arubacentralclientsecret':formresult['arubacentralclientsecret']})
        if formresult['arubacentralurl']!="" and formresult['arubacentralusername']!="" and formresult['arubacentraluserpassword']!="" and formresult['arubacentralclientid']!="" and formresult['arubacentralcustomerid']!="" and formresult['arubacentralclientsecret']!="":
            print("All parameters are there, perform centralAuthentication")
            response=classes.centralAuthentication(arubacentralvars)
        else:
            response={"message":"Authentication pending."}
    return json.dumps(response)


@arubacentral.route("/checkauthorization", methods=['GET', 'POST'])
def checkauthorization ():
    arubacentralvars=classes.obtainVars('sysarubacentral')
    if isinstance(arubacentralvars, str):
        arubacentralvars=json.loads(arubacentralvars)
    # Only verify if centralcustomerid, centralclienttoken and centralrefreshtoken variables exist
    # If arubacentraltokeninfo exists in the variables, we only have to check whether the token is still valid
    if "arubacentraltokeninfo" in arubacentralvars:
        response=classes.checkcentralToken("authorization")
    else:
        if "arubacentralclientid" in arubacentralvars and "arubacentralcustomerid" in arubacentralvars and "arubacentralcsrftoken" in arubacentralvars  and "arubacentralsession" in arubacentralvars:
            if arubacentralvars['arubacentralcustomerid'] and arubacentralvars['arubacentralclientid'] and arubacentralvars['arubacentralcsrftoken']  and arubacentralvars['arubacentralsession']:
                response=classes.centralAuthorization(arubacentralvars)
            else:
                response={"message":"Authorization unsuccessful"}
        else:
            response={"message":"Authorization pending"}
    return json.dumps(response)
# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, request,json
arubacentral = Blueprint('arubacentral', __name__)

from datetime import datetime
from flask import render_template

import classes.classes as classes


@arubacentral.route("/checkauthentication", methods=['GET', 'POST'])
def checkauthentication ():
    sysvars=classes.globalvars()
    # Only verify if centralcustomerid, centralclientid, centralclientsecret and centralurl variables exist
    # If arubacentraltokeninfo exists in the variables, we only have to check whether the token is still valid
    if "arubacentraltokeninfo" in sysvars:
        response=classes.checkcentralToken("authentication")
    else:
        if "centralurl" in sysvars and "centralusername" in sysvars and "centralusername" in sysvars and "centralclientid" in sysvars:
            if sysvars['centralcustomerid'] and sysvars['centralclientid'] and sysvars['centralclientsecret'] and sysvars['centralurl']:
                response=classes.centralAuthentication()
            else:
                response={"message":"Authentication pending"}
    return json.dumps(response)


@arubacentral.route("/checkauthorization", methods=['GET', 'POST'])
def checkauthorization ():
    sysvars=classes.globalvars()
    # Only verify if centralcustomerid, centralclienttoken and centralrefreshtoken variables exist
    # If arubacentraltokeninfo exists in the variables, we only have to check whether the token is still valid
    if "arubacentraltokeninfo" in sysvars:
        response=classes.checkcentralToken("authorization")
    else:
        if "centralclientid" in sysvars and "centralcustomerid" in sysvars and "arubacentralcsrftoken" in sysvars  and "arubacentralsession" in sysvars:
            if sysvars['centralcustomerid'] and sysvars['centralclientid'] and sysvars['arubacentralcsrftoken']  and sysvars['arubacentralsession']:
                response=classes.centralAuthorization()
            else:
                response={"message":"Authorization unsuccessful"}
        else:
            response={"message":"Authorization pending"}
    return json.dumps(response)
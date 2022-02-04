# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, json, request
psm = Blueprint('psm', __name__)

from datetime import datetime
from flask import render_template
import uuid

import classes.classes as classes


@psm.route("/psmdss", methods=['GET','POST'])
def psmdss ():
    authOK=classes.checkAuth("psmdssaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        url="configs/cluster/v1/distributedservicecards"
        psminfo=classes.getRestpsm(url)
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
        return render_template("psmdss.html", authOK=authOK, psminfo=psminfo, sysvars=sysvars)
    else:
        return render_template("login.html")


@psm.route("/psmnetworks", methods=['GET','POST'])
def psmnetworks ():
    authOK=classes.checkAuth("psmnetworksaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        url="configs/network/v1/networks"
        psminfo=classes.getRestpsm(url)
        if psminfo['items']==None:
            psminfo['items']=[]
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
        return render_template("psmnetworks.html", authOK=authOK, psminfo=psminfo, sysvars=sysvars)
    else:
        return render_template("login.html")

@psm.route("/psmsecuritypolicies", methods=['GET','POST'])
def psmsecuritypolicies ():
    authOK=classes.checkAuth("psmsecuritypoliciesccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        url="configs/security/v1/networksecuritypolicies"
        psminfo=classes.getRestpsm(url)
        if psminfo['items']==None:
            psminfo['items']=[]
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
        return render_template("psmsecuritypolicies.html", authOK=authOK, psminfo=psminfo, sysvars=sysvars)
    else:
        return render_template("login.html")

@psm.route("/psmalertpolicies", methods=['GET','POST'])
def psmalertpolicies ():
    authOK=classes.checkAuth("psmalertpoliciesaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        url="configs/monitoring/v1/alertPolicies"
        psmalertpolicies=classes.getRestpsm(url)
        if psmalertpolicies['items']==None:
            psmalertpolicies['items']=[]
        url="configs/monitoring/v1/alertDestinations"
        psmalertdestinations=classes.getRestpsm(url)
        if psmalertdestinations['items']==None:
            psmalertdestinations['items']=[]
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
        return render_template("psmalertpolicies.html", authOK=authOK, psmalertpolicies=psmalertpolicies, psmalertdestinations=psmalertdestinations, sysvars=sysvars)
    else:
        return render_template("login.html")


@psm.route("/psmalertDestinations", methods=['GET','POST'])
def psmalertDestinations ():
    url="configs/monitoring/v1/alertDestinations"
    psmalertdestinations=classes.getRestpsm(url)
    if psmalertdestinations['items']==None:
        psmalertdestinations['items']=[]
    return psmalertdestinations


@psm.route("/psmalertPolicies", methods=['GET','POST'])
def psmalertPolicies ():
    url="configs/monitoring/v1/alertPolicies"
    psmalertpolicies=classes.getRestpsm(url)
    if psmalertpolicies['items']==None:
        psmalertpolicies['items']=[]
    return psmalertpolicies
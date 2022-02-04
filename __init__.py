# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

from flask import Flask, render_template
import json
import ssl
from urllib.parse import unquote, quote
from datetime import datetime, time, timedelta
import urllib.request,http.cookiejar
import classes.classes as classes
import classes.sysadmin as sysadmin
import psutil, sys, os, platform, subprocess
from subprocess import Popen,PIPE
from waitress import serve
import socket


# Obtain the active IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
hostip=s.getsockname()[0]

sys.path.append('../')
systemlog = open('/var/www/html/log/system.log', 'a')
systemlog.write('{}: Starting the app. \n'.format(datetime.now()))
# Start the processes

globalsconf=classes.globalvars()

# Start the processes. The scripts are found in the /bash folder
if sys.version_info<(3,6,0):
    sys.stderr.write("You need python 3.6 or later to run this script\n")
else:


    scriptName=["/var/www/html/bash/cleanup.sh","/var/www/html/bash/topology.sh","/var/www/html/bash/ztp.sh","/var/www/html/bash/listener.sh","/var/www/html/bash/telemetry.sh","/var/www/html/bash/device-upgrade.sh","/var/www/html/bash/data-collector.sh"]
    for items in scriptName:
        try:
            proc = subprocess.Popen(items, shell=True, stdout=subprocess.PIPE)
            systemlog.write('{}: Started  {}. \n'.format(datetime.now(),items))
        except Exception as err:
            systemlog.write('{}: Error starting  {}. \n {} \n'.format(datetime.now(),items,err))


# Check whether something has changed in the hardware and update the globalvars config if that's the case
sysadmin.checksysConf()

__name__="CommPass"
app=Flask(__name__)

     
#Make Python definitions calleable in the Jinja template
app.jinja_env.globals.update(decryptPass=classes.decryptPassword)
app.jinja_env.globals.update(ctime=classes.convertTime)
app.jinja_env.globals.update(dsprofileInfo=classes.dsprofileInfo)
app.jinja_env.globals.update(loopCounter=classes.loopCounter)
app.jinja_env.globals.update(listofIntegers=classes.listofIntegers)
app.jinja_env.globals.update(converttoJSON=classes.converttoJSON)
app.jinja_env.globals.update(converttoInteger=classes.converttoInteger)
app.jinja_env.globals.update(showdataType=classes.showdataType)
app.jinja_env.globals.update(getService=classes.getService)
app.jinja_env.globals.update(provisionSwitch=classes.provisionSwitch)
app.jinja_env.globals.update(sysTime=classes.sysTime)
app.jinja_env.globals.update(timeDelta=classes.timeDelta)
app.jinja_env.globals.update(timeDuration=classes.timeDuration)
app.jinja_env.globals.update(upgradeprofileName=classes.getupgradeprofileName)
app.jinja_env.globals.update(va=classes.verifyAccess)
app.jinja_env.globals.update(sqlQuery=classes.jinjasqlQuery)
app.jinja_env.globals.update(afcswitchInfo=classes.afcswitchInfo)

from views.afc import afc
app.register_blueprint(afc)
from views.psm import psm
app.register_blueprint(psm)
from views.anycli import anycli
app.register_blueprint(anycli)
from views.devices import devices
app.register_blueprint(devices)
from views.deviceview import deviceview
app.register_blueprint(deviceview)
from views.dynseg import dynseg
app.register_blueprint(dynseg)
from views.trackers import trackers
app.register_blueprint(trackers)
from views.sysadmin import sysadmin
app.register_blueprint(sysadmin)
from views.auth import auth
app.register_blueprint(auth)
from views.ztp import ztp
app.register_blueprint(ztp)
from views.deviceupgrades import deviceupgrades
app.register_blueprint(deviceupgrades)
from views.topo import topo
app.register_blueprint(topo)
from views.tele_metry import tele_metry
app.register_blueprint(tele_metry)
from views.arubacentral import arubacentral
app.register_blueprint(arubacentral)

systemlog.close()

if (__name__) == "CommPass": 
    serve(app,listen="*:8080 [::]:8080", ident="Compass", threads=32)
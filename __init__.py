# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

from flask import Flask, render_template
import json
import ssl
from urllib.parse import unquote, quote
import datetime
from time import gmtime, strftime, time
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

# Start the processes

globalsconf=classes.globalvars()

# Start the processes. The scripts are found in the /bash folder
if sys.version_info<(3,6,0):
    sys.stderr.write("You need python 3.6 or later to run this script\n")
else:
    scriptName=globalsconf['appPath'] +"bash/cleanup.sh"
    proc = subprocess.Popen(scriptName, shell=True, stdout=subprocess.PIPE)
    scriptName=globalsconf['appPath'] +"bash/topology.sh"
    proc = subprocess.Popen(scriptName, shell=True, stdout=subprocess.PIPE)
    scriptName=globalsconf['appPath'] +"bash/ztp.sh"
    proc = subprocess.Popen(scriptName, shell=True, stdout=subprocess.PIPE)
    scriptName=globalsconf['appPath'] +"bash/listener.sh"
    proc = subprocess.Popen(scriptName, shell=True, stdout=subprocess.PIPE)

# Check whether something has changed in the hardware and update the globalvars config if that's the case
sysadmin.checksysConf()

__name__="carius"
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
from views.websockets import websockets
app.register_blueprint(websockets)
from views.sysadmin import sysadmin
app.register_blueprint(sysadmin)
from views.auth import auth
app.register_blueprint(auth)
from views.ztp import ztp
app.register_blueprint(ztp)
from views.topo import topo
app.register_blueprint(topo)

if (__name__) == "carius": 
    #serve(app,host='0.0.0.0',port=8080,ident="Carius")
    serve(app,listen="*:8080 [::]:8080", ident="Carius", threads=8)
    #app.run(host=hostip, port=8080, debug=True)
    

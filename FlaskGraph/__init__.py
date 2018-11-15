# (C) Copyright 2018 Hewlett Packard Enterprise Development LP.

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import json
from urllib.parse import unquote, quote
import datetime
from time import gmtime, strftime, time

import classes as classes

app=Flask(__name__)
Bootstrap(app)

app.config['BOOTSTRAP_SERVE_LOCAL']=True

#Make Python definitions calleable in the Jinja template
app.jinja_env.globals.update(decryptPass=classes.decryptPassword)
app.jinja_env.globals.update(getREST=classes.getRESTcx)
app.jinja_env.globals.update(ctime=classes.convertTime)

@app.route("/", methods=['GET', 'POST'])
def index ():
    formresult=request.form
    # Obtain the relevant device information from the database
    result=classes.devicedbAction(formresult)
    return render_template("index.html",result=result, formresult=formresult)

@app.route("/deviceinfo", methods=['GET','POST'])
def deviceinfo ():
    # Definition for the main device monitoring page. If no switch has been selected, only the select form is rendered (deviceinfo.html). 
    # Based on the information that is returned from the deviceInformation definition, a cx or switch page is rendered
    devInfo={}
    interface=""
    interfaces={}
    isOnline=""
    try:
        formresult=request.form
    except:
        formresult=[]
    if formresult:
        queryStr="select ipaddress, username, password, ostype, sysinfo, interfaces from devices where id='{}'".format(formresult['deviceid'])
        devInfo=classes.sqlQuery(queryStr,"selectone")
        if devInfo is not None:
            interfaces=json.loads(devInfo['interfaces'])
            sysinfo=json.loads(devInfo['sysinfo'])
            ostype=devInfo['ostype']
        else:
            ostype="none"
            sysinfo="none"
            interfaces="none"
        if 'interface' in formresult:
            interface=formresult['interface']
        isOnline=classes.checkifOnline(formresult['deviceid'],ostype)
    else:
        ostype="none"
    devicelist=classes.devicedbAction(formresult)
    if ostype=="arubaos-cx":
        return render_template("deviceinfocx.html", formresult=formresult, interfaces=interfaces, interface=interface, ostype=ostype, devicelist=devicelist, isOnline=isOnline)
    elif ostype=="arubaos-switch":
        return render_template("deviceinfoswitch.html",devicelist=devicelist, sysinfo=sysinfo, formresult=formresult, interfaces=interfaces, interface=interface, ostype=ostype, isOnline=isOnline)
    else:
        return render_template("deviceinfo.html", formresult=formresult, devInfo=devInfo, devicelist=devicelist)

@app.route ("/showInterface", methods=['GET','POST'])
def showInterface():
    # Definition that shows the interface statistics of a selected interface
    interfaceinfo=classes.interfacedbAction(request.args.get('deviceid'),request.args.get('interface'),request.args.get('ostype'))
    if request.args.get('ostype')=="arubaos-cx":
        return render_template("showcxinterface.html", interfaceinfo=interfaceinfo[0], lldpinfo=interfaceinfo[1], interface=request.args.get('interface'))
    elif request.args.get('ostype')=="arubaos-switch":
        return render_template("showinterface.html", interfaceinfo=interfaceinfo[0], lldpinfo=interfaceinfo[1], interface=request.args.get('interface'))
    else:
        return('',204)

@app.route ("/showDevice", methods=['GET','POST'])
def showDevice():
    # Show the device information from the selected device
    if request.args.get('ostype')=="arubaos-cx":
        queryStr="select sysinfo,bridge,vsx,vrf from devices where id='{}'".format(request.args.get('deviceid'))
        deviceinfo=classes.sqlQuery(queryStr,"selectone")
        return render_template("showcxdevice.html", sysinfo=json.loads(deviceinfo['sysinfo']),bridgeinfo=json.loads(deviceinfo['bridge']), vsxinfo=json.loads(deviceinfo['vsx']),vrfinfo=json.loads(deviceinfo['vrf']))
    elif request.args.get('ostype')=="arubaos-switch":
        # Check whether the device is a stackable or standalone device. The json structure is different so rendering different scripts
        queryStr="select sysinfo, vsf, bps from devices where id='{}'".format(request.args.get('deviceid'))
        deviceinfo=classes.sqlQuery(queryStr,"selectone")
        sysinfo=json.loads(deviceinfo['sysinfo'])
        vsfinfo=json.loads(deviceinfo['vsf'])
        bpsinfo=json.loads(deviceinfo['bps'])
        if request.args.get('stacktype')=="standalone":
              return render_template("showdevicesa.html", sysinfo=sysinfo)
        elif request.args.get('stacktype')=="vsf":
            return render_template("showdevicevsf.html", sysinfo=sysinfo, vsfinfo=vsfinfo)
        elif request.args.get('stacktype')=="bps":
            return render_template("showdevicebps.html", sysinfo=sysinfo, bpsinfo=bpsinfo)
        else:
            return('',204)
    else:
        return('',204)
    
@app.route("/showGraph", methods=['GET', 'POST'])
def showGraph ():
    line_chart=classes.showLinechart(request.args.get('deviceid'),request.args.get('entity'),request.args.get('ostype'),request.args.get('stacktype'),request.args.get('commander'),request.args.get('title'))
    return line_chart.render_response()

@app.route("/updatedeviceinfo", methods=['GET', 'POST'])
def updatedeviceinfo ():
    #Obtain all relevant information from a selected device
    if request.args.get('ostype')=="arubaos-cx":
        classes.getcxInfo(request.args.get('deviceid'))
    elif request.args.get('ostype')=="arubaos-switch":
        classes.getswitchInfo(request.args.get('deviceid'), request.args.get('stacktype'))
    return('',204)

if (__name__) == "__main__":
    app.run(host='172.16.1.10', port=8080, debug=True)


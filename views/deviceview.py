# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, json, request
deviceview = Blueprint('deviceview', __name__)

from datetime import datetime
from flask import render_template

import classes.classes as classes

@deviceview.route ("/selectInterface", methods=['GET','POST'])
def selectInterface():
    # Definition for selecting the interface
    interfaces=[]
    queryStr="select ostype,interfaces from devices where id='{}'".format(request.args.get('deviceid'))
    interfaceinfo=classes.sqlQuery(queryStr,"selectone")
    # We only have to return the interface number
    ifInfo=json.loads(interfaceinfo['interfaces'])
    if interfaceinfo['ostype']=="arubaos-cx":
        for items in ifInfo:
            interfaces.append(items)
    else:
        interfaces=ifInfo
    return render_template("selectinterface.html", interfaces=interfaces, ostype=interfaceinfo['ostype'])

@deviceview.route ("/showInterface", methods=['GET','POST'])
def showInterface():
    # Definition that shows the interface statistics of a selected interface
    lldpinfo=[]
    queryStr="select ostype from devices where id='{}'".format(request.args.get('deviceid'))
    deviceinfo=classes.sqlQuery(queryStr,"selectone")
    try:
        interfaceinfo=classes.interfacedbAction(request.args.get('deviceid'),request.args.get('interface'),deviceinfo['ostype'])
        if deviceinfo['ostype']=="arubaos-cx":
            # Get the LLDP information for the given interface 
            try:
                url="system/interfaces/" + request.args.get('interface').replace('/', '%2f') + "/lldp_neighbors?depth=2"
                lldpinfo=classes.getcxREST(request.args.get('deviceid'),url)
            except:
                lldpinfo={}
            return render_template("showcxinterface.html", interfaceinfo=interfaceinfo[0], lldpinfo=lldpinfo, interface=request.args.get('interface'))
        elif deviceinfo['ostype']=="arubaos-switch":
            return render_template("showinterface.html", interfaceinfo=interfaceinfo[0], lldpinfo=interfaceinfo[1], interface=request.args.get('interface'))
        else:
            return('',204)
    except:
        return('',204)

@deviceview.route ("/showDevice", methods=['GET','POST'])
def showDevice():
    # Show the device information from the selected device
    globalvars=classes.globalvars()
    # Obtain the device information from the database
    queryStr="select id, description, ipaddress, platform, sysinfo, ostype, ports, vsx, vsxlags, vrf, vsf, bps, routeinfo from devices where id='{}'".format(request.args.get('deviceid'))
    deviceinfo=classes.sqlQuery(queryStr,"selectone")
    if deviceinfo['ostype']=="arubaos-cx":
        vsfinfo=[]
        if isinstance(deviceinfo['vsf'],str):
            vsfitems=json.loads(deviceinfo['vsf'])
        else:
            vsfitems=deviceinfo['vsf']
        try:
            for items in vsfitems[1]:
                vsfinfo.append(vsfitems[1][items])
            vsfstatus=vsfitems[0]
        except:
            vsfstatus={}
        return render_template("showcxdevice.html", deviceid=request.args.get('deviceid'), ipaddress=deviceinfo['ipaddress'],description=deviceinfo['description'], platform=deviceinfo['platform'],sysinfo=json.loads(deviceinfo['sysinfo']),portinfo=json.loads(deviceinfo['ports']), vsxinfo=json.loads(deviceinfo['vsx']), vsxlags=json.loads(deviceinfo['vsxlags']),vrfinfo=json.loads(deviceinfo['vrf']),vsfinfo=vsfinfo, vsfstatus=vsfstatus, routeinfo=json.loads(deviceinfo['routeinfo']),globalvars=globalvars)
    elif deviceinfo['ostype']=="arubaos-switch":
        # Check whether the device is a stackable or standalone device. The json structure is different so rendering different scripts
        sysinfo=json.loads(deviceinfo['sysinfo'])
        vsfinfo=json.loads(deviceinfo['vsf'])       
        bpsinfo=json.loads(deviceinfo['bps'])
        if 'vsf_member_element' in sysinfo:
            return render_template("showdevicevsf.html", deviceid=request.args.get('deviceid'), ipaddress=deviceinfo['ipaddress'], description=deviceinfo['description'], sysinfo=sysinfo, vsfinfo=vsfinfo)
        elif 'bps_member_element' in sysinfo:
            return render_template("showdevicebps.html", deviceid=request.args.get('deviceid'), ipaddress=deviceinfo['ipaddress'], description=deviceinfo['description'], sysinfo=sysinfo, bpsinfo=bpsinfo)
        else:
            return render_template("showdevicesa.html", deviceid=request.args.get('deviceid'), ipaddress=deviceinfo['ipaddress'], description=deviceinfo['description'], sysinfo=sysinfo)
    else:
        return('',204)
    
@deviceview.route("/showGraph", methods=['GET', 'POST'])
def showGraph ():
    queryStr="select id,sysinfo,ostype,ports,vsx,vsxlags,vrf,vsf,bps from devices where id='{}'".format(request.args.get('deviceid'))
    deviceinfo=classes.sqlQuery(queryStr,"selectone")
    sysinfo=json.loads(deviceinfo['sysinfo'])
    if sysinfo:
        if 'vsf_member_element' in sysinfo:
            stacktype="vsf"
            title="CPU Utilization"
        elif 'bps_member_element' in sysinfo:
            stacktype="bps"
        else:
            stacktype="standalone"
    else:
        stacktype="standalone"


    if request.args.get('entity')=="cpu":
        title="CPU Utilization"
    elif request.args.get('entity')=="memory":
        if deviceinfo['ostype']=="arubaos-cx":
            title="Memory Utilization"
        elif deviceinfo['ostype']=="arubaos-switch":
            if stacktype=="standalone":
                title="Memory Utilization"
            else:
                title="Available Memory"
   
    line_chart=classes.showLinechart(request.args.get('deviceid'),request.args.get('entity'),deviceinfo['ostype'],stacktype,title)
    return line_chart.render_response()

@deviceview.route("/updatedeviceinfo", methods=['GET', 'POST'])
def updatedeviceinfo ():
    #Obtain all relevant information from a device
    deviceid=int(request.args.get('deviceid'))
    queryStr="select sysinfo,ostype from devices where id='{}'".format(request.args.get('deviceid'))
    deviceinfo=classes.sqlQuery(queryStr,"selectone")
    sysinfo=json.loads(deviceinfo['sysinfo'])
    if sysinfo:
        if 'vsf_member_element' in sysinfo:
            stacktype="vsf"
        elif 'bps_member_element' in sysinfo:
            stacktype="bps"
        else:
            stacktype="standalone"
    else:
        stacktype="standalone"
    if deviceinfo['ostype']=="arubaos-cx":
        classes.getcxInfo(request.args.get('deviceid'))
    elif deviceinfo['ostype']=="arubaos-switch":
        classes.getswitchInfo(deviceid, stacktype)
    return('',204)
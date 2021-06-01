# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
# Generic Aruba Switch classes

import classes.classes
import requests, json
import psutil, sys, os, platform, subprocess
sessionid = requests.Session()

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import pygal  
from pygal.style import BlueStyle
from pygal.style import Style

custom_style = Style(
  background='transparent',
  plot_background='transparent',
  foreground='#004d4d',
  foreground_strong='#004d4d',
  foreground_subtle='#004d4d',
  opacity='.6',
  opacity_hover='.9',
  transition='400ms ease-in',
  label_font_size=15,
  title_font_size=20,
  colors=('#E853A0', '#E8537A', '#E95355', '#E87653', '#E89B53'))

def checkifOnline(deviceid,ostype):
    # Login and logout of the device to see if the device is online
    if ostype=="arubaos-cx":
        try:
            response=classes.classes.checkcxCookie(deviceid)
        except:
            return "Unstable"
    if ostype=="arubaos-switch":
        try:
            response=classes.classes.checkswitchCookie(deviceid)
        except:
            return "Unstable"
    queryStr="select ipaddress,switchstatus from devices where id='{}'".format(deviceid)
    response=classes.classes.sqlQuery(queryStr,'selectone')
    if response['switchstatus']==200:
        return "Online"
    elif response['switchstatus']==101 or response['switchstatus']==102:
        return "Unstable"
    else:
        return "Offline"

def discoverModel(deviceid):
    # Performing REST calls to discover what switch model we are dealing with
    discoverSuccess=0
    # Check whether the device is ArubaOS-Switch by obtaining the local lldp and system information 
    try:
        url="lldp/local_device/info"
        response =classes.classes.getswitchREST(url,deviceid)
        if 'system_description' in response:
            # This is an ArubaOS-Switch switch. System description is a comma separated string that contains product and version information
            # Splitting the string into a list and then assign the values  
            deviceInfo=response['system_description'].split(",")
            hostname=response['system_name']
            # Obtaining system information. This information also contains port information
            url="system/status/switch"
            sysinfo =classes.classes.getswitchREST(url,deviceid)
            # Check whether the device is configured for VSF or BPS, or whether it's a stand alone switch. If the latter is the case, the vsf and bps fields remain empty
            try:
                if sysinfo['switch_type']=="ST_STACKED":
                    url="stacking/vsf/members"
                    vsfinfo =classes.classes.getswitchREST(url,deviceid)
                    # Getting the member information, this information contains which device is the master/commander. This is for running VSF
                    if 'message' in vsfinfo:
                        vsfinfo={}
                    else:
                        sysinfo= {**sysinfo,**vsfinfo}
                    # If there is no response, this means that the switches are running BPS
                    url="stacking/bps/members"
                    bpsinfo =classes.classes.getswitchREST(url,deviceid)
                    if 'message' in bpsinfo:
                        bpsinfo={}
                    else:
                        sysinfo= {**sysinfo,**bpsinfo}
                    # Updating the database with all the gathered information
            except:
                pass
            queryStr="update devices set description='{}', ostype='arubaos-switch', platform='{}', osversion='{}', sysinfo='{}' where id='{}'".format(hostname,deviceInfo[0],deviceInfo[1],json.dumps(sysinfo),deviceid)
            try:
                classes.classes.sqlQuery(queryStr,"update")
            except:
                pass
            discoverSuccess=1
    except:
        pass
    # Now check whether this might be an AOS-CX switch
    if discoverSuccess==0:
        try:
            url="system?attributes=boot_time%2Chostname%2Cmgmt_intf%2Cmgmt_intf_status%2Cplatform_name%2Csoftware_images%2Csoftware_info%2Csoftware_version%2Cstatus%2Csubsystems&depth=1"
            response =classes.classes.getcxREST(deviceid,url)
            if 'platform_name' in response:
                sysinfo=json.dumps(response)
                # It is an ArubaOS-CX device. Check whether it's running in VSF, obtain the interface information and then update the database
                try:
                    url="system/vsf_members?attributes=id%2Clinks%2Crole%2Cstatus&depth=2"
                    vsfInfo=classes.classes.getcxREST(deviceid,url)
                    if vsfInfo is None:
                        vsfInfo=json.dumps({})
                    else:
                        vsfInfo=json.dumps(vsfInfo)
                except:
                    vsfInfo=json.dumps({})
                try:
                    if "hostname" in response:
                        hostname=response['hostname']
                    elif "hostname" in response['mgmt_intf_status']:
                        #The hostname is not in the response. For some strange reason CX has hidden the hostname in another place
                        hostname=response['mgmt_intf_status']['hostname']
                    else:
                        hostname=response['platform_name']
                    queryStr="update devices set description='{}',ostype='arubaos-cx', platform='{}', osversion='{}', sysinfo='{}', vsf='{}' where id='{}'".format(hostname,response['platform_name'], response['software_version'], sysinfo,vsfInfo,deviceid)
                    classes.classes.sqlQuery(queryStr,"update")
                    discoverSuccess=1
                except:
                    pass
        except:
            pass
    # Device has not been discovered. We have to set the ostype, platform and osversion to unknown
    if discoverSuccess==0:
        queryStr="update devices set ostype='Unknown', platform='Unknown', osversion='Unknown' where id='{}'".format(deviceid)
        classes.classes.sqlQuery(queryStr,"update")
    
def devicedbAction(formresult):
    # This definition is for all the database actions for switches, based on the user click on the pages
    queryStr="select distinct ostype from devices where ostype='arubaos-cx' or ostype='arubaos-switch' or ostype='Unknown'"
    switchos=classes.classes.sqlQuery(queryStr,"select")
    globalsconf=classes.classes.globalvars()
    queryStr="select distinct platform from devices where ostype='arubaos-cx' or ostype='arubaos-switch' or ostype='Unknown'"
    platforms=classes.classes.sqlQuery(queryStr,"select")
    searchAction="None"
    entryExists=0
    if "subscriber" in formresult:
        subscriber=formresult['subscriber']
    else:
        subscriber=""
    if(bool(formresult)==True): 
        if 'topology' in formresult:
            topology=1
        else:
            topology=0
        if 'telemetryenable' in formresult:
            telemetryenable=1
        else:
            telemetryenable=0
            subscriber=""
            switchstatus=""
        try:
            formresult['pageoffset']
            pageoffset=formresult['pageoffset']
        except:
            pageoffset=0
        if(formresult['action']=="Submit device"):
            # First check if the IP address already exists. If there is already a device with the same IP address, don't insert
            queryStr="select id from devices where ipaddress='{}'".format(formresult['ipaddress'])
            checkDuplicate=classes.classes.sqlQuery(queryStr,"selectone")
            if checkDuplicate:
                entryExists=1
            else:
                queryStr="insert into devices (description,ipaddress,username,password,telemetryenable,subscriptions,subscriber,cpu,memory,sysinfo,ports,interfaces,vrf,vsx,vsxlags,vsf,bps,lldp,routeinfo,topology, deviceattributes) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','[]')" \
                .format(formresult['description'],formresult['ipaddress'],formresult['username'],classes.classes.encryptPassword(globalsconf['secret_key'],formresult['password']),telemetryenable,'[[],0]',subscriber,'[]','[]','[]','[]','[]','{}','{}','{}','{}','{}','{}','{}',topology)
                deviceid=classes.classes.sqlQuery(queryStr,"insert")
                # Discover what type of device this is and update the database with the obtained information
                discoverModel(deviceid)
        elif  (formresult['action']=="Submit changes"):
            # First check if the IP address already exists. If there is already a device with the same IP address, don't insert
            queryStr="select id from devices where ipaddress='{}'".format(formresult['ipaddress'])
            checkDuplicate=classes.classes.sqlQuery(queryStr,"selectone")
            # If the id result is different than the deviceid formresult, then there is already another entry with the same IP address
            if checkDuplicate:
                if str(checkDuplicate['id'])!=formresult['deviceid']:
                    entryExists=1
                else:
                    # If telemetry is disabled, we have to check whether there is a websocket client alive and kill the subprocess it it exists
                    if telemetryenable==0:
                        clearWS(formresult['deviceid'])
                    queryStr="update devices set description='{}',ipaddress='{}',username='{}',password='{}', topology='{}', telemetryenable='{}', subscriber='{}' where id='{}' "\
                    .format(formresult['description'],formresult['ipaddress'],formresult['username'],classes.classes.encryptPassword(globalsconf['secret_key'], formresult['password']),topology, telemetryenable, subscriber, formresult['deviceid'])
                    classes.classes.sqlQuery(queryStr,"update")
                    # Discover what type of device this is and update the database with the obtained information
                    discoverModel(formresult['deviceid'])
                    # If there is an entry in the topology table, we also have to update the IP address, if the IP address has changed
                    if formresult['orgIPaddress']!=formresult['ipaddress']:
                        #IP address has changed, update the topology
                        queryStr="update topology set switchip='{}' where switchip='{}'".format(formresult['ipaddress'],formresult['orgIPaddress'])
                        classes.classes.sqlQuery(queryStr,"update")
            else:
                queryStr="update devices set description='{}',ipaddress='{}',username='{}',password='{}', topology='{}', telemetryenable='{}' where id='{}' "\
                .format(formresult['description'],formresult['ipaddress'],formresult['username'],classes.classes.encryptPassword(globalsconf['secret_key'], formresult['password']),topology, telemetryenable, formresult['deviceid'])
                classes.classes.sqlQuery(queryStr,"update")
                # Discover what type of device this is and update the database with the obtained information
                discoverModel(formresult['deviceid'])
                # If there is an entry in the topology table, we also have to update the IP address, if the IP address has changed
                if formresult['orgIPaddress']!=formresult['ipaddress']:
                    #IP address has changed, update the topology
                    queryStr="update topology set switchip='{}' where switchip='{}'".format(formresult['ipaddress'],formresult['orgIPaddress'])
                    classes.classes.sqlQuery(queryStr,"update")

        elif (formresult['action']=="Delete"):
            # Delete from the topology table, if entries exist
            queryStr="select ipaddress from devices where id='{}'".format(formresult['deviceid'])
            result=classes.classes.sqlQuery(queryStr,"selectone")
            queryStr="delete from topology where switchip='{}'".format(result['ipaddress'])
            classes.classes.sqlQuery(queryStr,"delete")
            # Delete from the software upgrades table
            queryStr="delete from softwareupdate where switchid='{}'".format(formresult['deviceid'])
            classes.classes.sqlQuery(queryStr,"delete")
            # Delete from the devices table
            queryStr="delete from devices where id='{}'".format(formresult['deviceid'])
            classes.classes.sqlQuery(queryStr,"delete")
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""    
        if formresult['searchIPaddress'] or formresult['searchDescription'] or formresult['searchVersion'] or formresult['searchPlatform'] or formresult['searchOS'] or formresult['searchTopology']  or formresult['searchTelemetry']:
            constructQuery= " where (ostype='arubaos-cx' or ostype='arubaos-switch' or ostype='Unknown') AND "
        else:
            constructQuery="where (ostype='arubaos-cx' or ostype='arubaos-switch' or ostype='Unknown')      "
        if formresult['searchDescription']:
            constructQuery += " description like'%" + formresult['searchDescription'] + "%' AND "
        if formresult['searchVersion']:
            constructQuery += " osversion like '%" + formresult['searchVersion'] + "%' AND "
        if formresult['searchIPaddress']:
            constructQuery += " ipaddress like'%" + formresult['searchIPaddress'] + "%' AND "
        if formresult['searchPlatform']:
            constructQuery += " platform like'%" + formresult['searchPlatform'] + "%' AND "
        if formresult['searchTopology']:
            constructQuery += " topology='" + formresult['searchTopology'] + "' AND "
        if formresult['searchTelemetry']:
            constructQuery += " telemetryenable='" + formresult['searchTelemetry'] + "' AND "
        if formresult['searchOS']:
            constructQuery += " ostype like'%" + formresult['searchOS'] + "%' AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from devices " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=navResult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from devices " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from devices where (ostype='arubaos-cx' or ostype='arubaos-switch' or ostype='Unknown')"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=10
        pageoffset=0
        queryStr="select id, description, ipaddress, username, password, ostype, platform, osversion, topology, telemetryenable from devices where ostype='arubaos-cx' or ostype='arubaos-switch' or ostype='Unknown' LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'switchos': switchos, 'platforms': platforms, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage,'entryExists': entryExists}


def interfacedbAction(deviceid, interface,ostype):
    # Definition that obtains all the relevant information from the database for showing on the html pages
    queryStr="select sysinfo,interfaces, lldp from devices where id='{}'".format(deviceid)
    result=classes.classes.sqlQuery(queryStr,"selectone")
    interfaceinfo=json.loads(result['interfaces'])
    if ostype=="arubaos-switch" and interfaceinfo:
        lldpinfo=json.loads(result['lldp'])
    else:
        lldpinfo={}
    sysinfo=json.loads(result['sysinfo'])
    if ostype=="arubaos-cx":
        # extract the selected interface information
        for items in interfaceinfo:
            if items['name']==interface:
                # Assign the selected interface values
                interfaceinfo=items
    elif ostype=="arubaos-switch":
        # Obtain information of the selected interface
        if interfaceinfo:
            for items in interfaceinfo['port_statistics_element']:
                if items['id']==interface:
                    interfaceinfo=items
            for items in sysinfo['blades']:
                for hwitems in items['data_ports']:
                    if hwitems['port_name']==interface:
                        interfaceinfo= {**interfaceinfo,**hwitems}
        # Obtain lldp information from the selected interface
        if interface == "0":
            lldpinfo={}
        else:
            if lldpinfo:
                for items in lldpinfo['lldp_remote_device_element']:
                    if items['local_port']==interface:
                        lldpinfo=items
                    else:
                        pass
            else:
                lldpinfo={}
    return (interfaceinfo,lldpinfo)

def showLinechart(deviceid,entity,ostype,stacktype,title):
    # definition that obtains the information from the database and formats this to display a linechart
    dataset=[]
    # Obtaining the relevant data (CPU or Memory) from the database as dataset value.
    queryStr="select {} as dataset from devices where id={}".format(entity,deviceid)
    result=classes.classes.sqlQuery(queryStr,"selectone")
    if result['dataset']:
        dataset=json.loads(result['dataset'])
    # Based on the ostype value, the Y-title has to be different for the memory. In ArubaOS-CX the memory usage is displayed and in ArubaOS-Switch the available memory
    if ostype=="arubaos-cx":
        y_title="%"
    elif ostype=="arubaos-switch":
        # If the device is running VSF or BPS we have to provide some additional information to the getCPU and getMemory definitions
        if entity=='memory':
            y_title="Bytes"
        else:
            y_title="%"
    xlabel = []
    values = []
    # Creating the datasets for the linechart
    for items in dataset:
        xlabel.append(items[0])
        values.append(int(items[1]))
    line_chart = pygal.Line(style=custom_style, show_legend=False, y_title=y_title, x_label_rotation=80)
    line_chart.title = title
    line_chart.x_labels = map(str, xlabel)
    line_chart.add('', values)
    return line_chart

def portAccess(deviceid):
    # Show access port security for AOS-Switch
    try:
        url="monitoring/port-access/clients/detailed"
        response =classes.classes.getswitchREST(url,deviceid)
    except:
        response={}
    return response


def portAccesscx(deviceid):
    # Show access port security for AOS-CX switches
    # This is a combination of calls. We first have to check which switchports are configured for port access and which switch ports are operational
    portaccessInfo=[]
    try:
        url="system/interfaces?attributes=name&depth=1&filter=link_state%3Aup%2Ctype%3Asystem"
        response = sorted(classes.classes.getcxREST(deviceid,url), key=lambda k: k['name'])   
        # Response contains all the physical interfaces that are operational and up
        # Next is to iterate through the list and obtain the port-access information per interface. Append that information to a list of dicts
        for items in response:
            url="system/ports/" + items['name'].replace('/', '%2F') + "/port_access_clients?attributes=applied_role%2Cauth_attributes%2Cclient_state%2Cmac%2Cport%2Cubt_client_state&depth=2"
            response = classes.classes.getcxREST(deviceid,url)
            if response:
                portaccessInfo.append(response)
    except:
        return portaccessInfo
    return portaccessInfo

def getupgradeInfo(deviceInfo):
    # Obtain software version and partition information from the switch based on ostype. 
    bootInfo={}
    if deviceInfo['ostype']=="arubaos-switch":
        # There is no REST call available for AOS-Switch, therefore we have to use anycli
        cliResult=False
        while cliResult==False:
            try:
                header=classes.classes.checkswitchCookie(deviceInfo['id'])
                url="http://{}/rest/v7/cli".format(deviceInfo['ipaddress'])
                sendcmd={'cmd':'show flash'}
                response=requests.post(url, verify=False, headers=header, data=json.dumps(sendcmd), timeout=4)
                response=response.json()
                if "error_msg" in response:
                    if response['error_msg']=="":
                        cliResult=True
            except:
                pass
        # Now that the image and partition information has been obtained, we need to format this.
        flashInfo=classes.classes.b64decode(response['result_base64_encoded']).decode('utf_8').splitlines()
        res = [i for i in flashInfo if "Primary Image" in i]
        bootInfo['primaryImage'] = res[0].split()[-1]
        res = [i for i in flashInfo if "Secondary Image" in i]
        bootInfo['secondaryImage'] = res[0].split()[-1]
        res = [i for i in flashInfo if "Default Boot Image" in i]
        bootInfo['defaultImage'] = res[0].split()[-1]
        # Next, we need to obtain the software versions that are available for this switch. This means that we first have to identify which switch we have, and then obtain the images
        if "WC" in deviceInfo['osversion']:
            # It's a 2930 series. Obtain all the images that are available for the 2930 series
            queryStr="select * from deviceimages where devicefamily='2930'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        elif "KB" in deviceInfo['osversion']:
            # It's a 38x0/5400 series. Obtain all the images that are available for the 38x0/5400 series
            queryStr="select * from deviceimages where devicefamily='3810/5400'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        else:
            imageResult=[]
        bootInfo['images']=imageResult
        # Another thing to check is whether there is already an active upgrade scheduled. This is identified by the in the softwareupdate table with an existing switchid and a status that is set to 0
        # Status set to 0 means that the upgrade has not started yet and the upgrade can still be edited
        queryStr="select * from softwareupdate where switchid='{}' and NOT (status=100 OR status=110)".format(deviceInfo['id'])
        bootInfo['activeUpdate']=classes.classes.sqlQuery(queryStr,"selectone")
    elif deviceInfo['ostype']=="arubaos-cx":
        url="firmware"
        response = classes.classes.getcxREST(deviceInfo['id'],url)
        bootInfo['primaryImage']=response['primary_version']
        bootInfo['secondaryImage']=response['secondary_version']
        bootInfo['defaultImage']=response['default_image']
        if "FL" in deviceInfo['osversion']:
            # It's a 6300/6400 series. Obtain all the images that are available for the 6300/6400 series
            queryStr="select * from deviceimages where devicefamily='6300/6400'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        elif "TL" in deviceInfo['osversion']:
            # It's a 8320 series. Obtain all the images that are available for the 8320 series
            queryStr="select * from deviceimages where devicefamily='8320'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        elif "GL" in deviceInfo['osversion']:
            # It's a 8325 series. Obtain all the images that are available for the 8325 series
            queryStr="select * from deviceimages where devicefamily='8325'"
            imageResult=classes.classes.sqlQuery(queryStr,"select")
        else:
            imageResult=[]
        bootInfo['images']=imageResult
        queryStr="select * from softwareupdate where switchid='{}' and NOT (status=100 OR status=110)".format(deviceInfo['id'])
        bootInfo['activeUpdate']=classes.classes.sqlQuery(queryStr,"selectone")
    return bootInfo


def clearClient(deviceid,macaddress,port,authmethod):
    # based on the authentication method, push reset client
    result=""
    if authmethod=="macauth":
        cmd="aaa port-access mac-based " + port + " reauthenticate mac-addr " + macaddress
        result=classes.classes.anycli(cmd,deviceid)
    elif authmethod=="dot1x":
        # cmd="aaa port-access authenticator " + port + " reauthenticate"
        cmd="interface " + port + " disable"
        result=classes.classes.anycli(cmd,deviceid)
        cmd="interface " + port + " enable"
        result=classes.classes.anycli(cmd,deviceid)
    return result

def clearWS(id):
    for proc in psutil.process_iter():
        processname="/var/www/html/bash/wsclient"
        cmdline=proc.cmdline()
        if len(cmdline)>1:
            if processname in cmdline[1]:
                if id==cmdline[2]:
                    proc.kill()
                    # Update the database and clear the subscriber information
                    queryStr="update devices set subscriber='' where id='{}'".format(id)
                    classes.classes.sqlQuery(queryStr,"update")
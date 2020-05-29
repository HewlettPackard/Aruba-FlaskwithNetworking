# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Generic ArubaOS-Switch classes

import classes.classes
import requests
import base64

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import datetime
from time import gmtime, strftime, time

def loginswitch (deviceid):
    globalsconf=classes.classes.globalvars()
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    url="http://{}/rest/v7/login-sessions".format(deviceCreds['ipaddress'])
    credentials = {"userName": deviceCreds['username'], "password": classes.classes.decryptPassword(globalsconf['secret_key'], deviceCreds['password']) }
    try:
        # Login to the switch. The cookie value is returned to the calling definition. It is not stored in the cookie jar.
        response = requests.post(url, verify=False, data=json.dumps(credentials), timeout=2)
        sessioninfo = response.json()
        header={'cookie': sessioninfo['cookie']}
        #print("Logged into Arubaos-Switch")
        return header
    except:
        #print("Error logging into Arubaos-Switch")
        return 401

def logoutswitch(header,deviceid):
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    url="http://{}/rest/v7/login-sessions".format(deviceCreds['ipaddress'])
    try:
        response = requests.delete(url,headers=header,timeout=5)
        #print("Logged out from Arubaos-Switch")
    except:
        print("Error logging out of Arubaos-Switch")

def getRESTswitch(header,url,deviceid):
    # Obtain device information from the database
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    url="http://{}/rest/v7/".format(deviceCreds['ipaddress']) + url
    try:
        response=requests.get(url, verify=False, headers=header)
        # If the response contains information, the content is converted to json format
        response=json.loads(response.content.decode('utf-8'))
    except:
        response="No data"
    return response

def getswitchInfo(deviceid, stacktype):
    # This definition obtains all the relevant information from the arubaos-switch device and then stores this in the database
    # There are a couple steps, first gather sysinfo, interface and lldp information, then obtain vsf information or bps information
    # The last two only have to be obtained if the switch is actually a stack (vsf or bps)
    interfaces={}
    sysinfo={}
    bpsinfo={}
    vsfinfo={}
    lldpinfo={}
    header=loginswitch(deviceid)
    # First, get the system information
    urllist=["system/status/power/supply","system/status/switch","system/status","vlans","vlans-ports","dot1x","ipaddresses","lldp","radius_servers","system/time","lacp/port","snmp-server/communities","snmpv3/users","stp","telnet/server","monitoring/ntp/status"]
    for sysitems in urllist:
        try:
            result=getRESTswitch(header,sysitems,deviceid)
            # Join the dictionaries
            sysinfo= {**sysinfo,**result} 
            url="system/status/switch"
            # Check whether the device is configured for VSF or BPS, or whether it's a stand alone switch. If the latter is the case, the vsf and bps fields remain empty
            if sysitems=="system/status/switch":
                if sysinfo['switch_type']=="ST_STACKED":
                    url="stacking/vsf/members"
                    try:
                        vsfinfo=getRESTswitch(header,url,deviceid)
                        # If the result does not contain the message key, which means that there is an error, this means that there is actually information in the result
                        # And this implies that the switch is running VSF
                        if not 'message' in vsfinfo:
                            sysinfo= {**sysinfo,**vsfinfo}
                    except:
                        pass
                    url="stacking/bps/members"
                    try:
                        bpsinfo=getRESTswitch(header,url,deviceid)
                        # If the result does not contain the message key, which means that there is an error, this means that there is actually information in the result
                        # And this implies that the switch is running VSF
                        if not 'message' in bpsinfo:
                            sysinfo= {**sysinfo,**bpsinfo}
                    except:
                        pass
        except:
            pass

    # Obtain interface statistics
    urllist=["port-statistics","poe/ports/stats"]
    for interfaceitems in urllist:
        try:
            result=getRESTswitch(header,interfaceitems,deviceid)
            interfaces= {**interfaces,**result}
        except:
            pass
    # Obtain lldp information
    url="lldp/remote-device"
    try:
        lldpinfo=getRESTswitch(header,url,deviceid)
        lldpinfo=json.dumps(lldpinfo)
        # It is possible that the json contains double quotes with backslashes. Replace those.
        lldpinfo=lldpinfo.replace('\\"','')
    except:
        pass
    # If operating in a VSF stack, obtain all VSF information from the stack based on the urllist
    if stacktype=="vsf":
        bpsinfo={}
        urllist=["stacking/vsf/global_config","stacking/vsf/info","stacking/vsf/members","stacking/vsf/members/system_info","stacking/vsf/members_links_ports","system/status/members"]
        for vsfitems in urllist:
            try:
                result=getRESTswitch(header,vsfitems,deviceid)
                vsfinfo= {**vsfinfo,**result} 
            except:
                pass
        # Now for CPU and Memory. First obtain the commander device id
        for items in vsfinfo['vsf_member_element']:
            if items['status']=="VMS_COMMANDER":
                # Commander found. Need to get the CPU utilization and available memory
                for cpumemitems in vsfinfo['vsf_member_system_info_element']:
                    if cpumemitems['member_id']==items['member_id']:
                        cpuValappend=cpumemitems['cpu_util']
                        memValappend=cpumemitems['free_mem']
        # Now obtain the CPU and memory values from the database and append the latest CPU and memory value to the database
        queryStr="select cpu, memory from devices where id='{}'".format(deviceid)
        cpumemVal=classes.classes.sqlQuery(queryStr,"selectone")
        if cpumemVal['cpu']:
            cpuVallist = json.loads(cpumemVal['cpu'])        
        else:
            cpuVallist = list()
        if cpumemVal['memory']:
            memVallist = json.loads(cpumemVal['memory'])        
        else:
            memVallist = list()
        cpuVallist.append(tuple((strftime("%d-%m-%Y %H:%M:%S", gmtime()),cpuValappend))) 
        memVallist.append(tuple((strftime("%d-%m-%Y %H:%M:%S", gmtime()),memValappend)))
        #Store the last 30 values in the database, this value contains timestamp as key value and CPU or memory as value
        cpuVallist=json.dumps(cpuVallist[-30:])
        memVallist=json.dumps(memVallist[-30:])   
    # If operating in a BPS stack, obtain all BPS information from the stack based on the urllist
    elif stacktype=="bps":
        vsfinfo={}
        urllist=["stacking/bps/info","stacking/bps/members","stacking/bps/members/system_info","stacking/bps/stack_ports","system/status/members"]
        for bpsitems in urllist:
            try:
                result=getRESTswitch(header,bpsitems,deviceid)
                bpsinfo= {**bpsinfo,**result} 
            except:
                bpsinfo={}
        # Now for CPU and Memory. First obtain the commander device id
        for items in sysinfo['bps_member_element']:
            if items['status']=="SMS_COMMANDER":
                # Commander found. Need to get the CPU utilization and available memory
                for cpumemitems in bpsinfo['bps_member_system_info_element']:
                    if cpumemitems['member_id']==items['member_id']:
                        cpuValappend=cpumemitems['cpu_util']
                        memValappend=cpumemitems['free_memory']
        # Now obtain the CPU and memory values from the database and append the latest CPU and memory value to the database
        queryStr="select cpu, memory from devices where id='{}'".format(deviceid)
        cpumemVal=classes.classes.sqlQuery(queryStr,"selectone")
        if cpumemVal['cpu']:
            cpuVallist = json.loads(cpumemVal['cpu'])        
        else:
            cpuVallist = list()
        if cpumemVal['memory']:
            memVallist = json.loads(cpumemVal['memory'])        
        else:
            memVallist = list()
        cpuVallist.append(tuple((strftime("%d-%m-%Y %H:%M:%S", gmtime()),cpuValappend))) 
        memVallist.append(tuple((strftime("%d-%m-%Y %H:%M:%S", gmtime()),memValappend)))
        #Store the last 30 values in the database, this value contains timestamp as key value and CPU or memory as value
        cpuVallist=json.dumps(cpuVallist[-30:])
        memVallist=json.dumps(memVallist[-30:]) 
    else:
        queryStr="select cpu, memory from devices where id='{}'".format(deviceid)
        cpumemVal=classes.classes.sqlQuery(queryStr,"selectone")
        if cpumemVal['cpu']:
            cpuVallist = json.loads(cpumemVal['cpu'])        
        else:
            cpuVallist = list()
        if cpumemVal['memory']:
            memVallist = json.loads(cpumemVal['memory'])        
        else:
            memVallist = list()
        # Obtain the CPU value, there is no known REST call for this so we have to use anycli for this and obtain the unstructured data
        response=anycli("show cpu", deviceid)
        payload_str = base64.b64decode(response['result_base64_encoded']).decode('utf-8')
        # Need to get the CPU value for the 5 second interval
        cpuVal=payload_str[payload_str.find('5 sec ave')+11:]
        cpuVal=int(cpuVal[0:2])
        cpuVallist.append(tuple((strftime("%d-%m-%Y %H:%M:%S", gmtime()),cpuVal))) 
        memVallist.append(tuple((strftime("%d-%m-%Y %H:%M:%S", gmtime()),sysinfo['total_memory_in_bytes'])))
        #Store the last 30 values in the database, this value contains timestamp as key value and CPU or memory as value
        cpuVallist=json.dumps(cpuVallist[-30:])
        memVallist=json.dumps(memVallist[-30:]) 
    if bool(sysinfo)==True:
        queryStr="update devices set sysinfo='{}', cpu='{}', memory='{}', interfaces='{}', vsf='{}', bps='{}', lldp='{}' where id='{}'". format(json.dumps(sysinfo),cpuVallist,memVallist,json.dumps(interfaces), json.dumps(vsfinfo), json.dumps(bpsinfo), lldpinfo, deviceid)
        try:
            classes.classes.sqlQuery(queryStr,"update")
        except:
            print("error in query")
    logoutswitch(header,deviceid)

def anycli(cmd,deviceid):
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    try:
        header=loginswitch(deviceid)
        url="http://{}/rest/v7/cli".format(deviceCreds['ipaddress'])
        sendcmd={'cmd':cmd}
        try:
            response=requests.post(url, verify=False, headers=header, data=json.dumps(sendcmd))
            # If the response contains information, the content is converted to json format
            response=json.loads(response.content)
            #response=(b64decode(response['result_base64_encoded']).decode('utf_8'))
        except:
            response="No data"
        logoutswitch(header,deviceid)
    except:
        print("login failure")
        response="Login failure"
    return response

def anycliProvision(cmd,ipaddress,header):
    url="http://{}/rest/v7/cli".format(ipaddress)
    sendcmd={'cmd':cmd}
    try:
        response=requests.post(url, verify=False, headers=header, data=json.dumps(sendcmd))
        # If the response contains information, the content is converted to json format
        response=json.loads(response.content)
    except:
        response="No data"
    return response

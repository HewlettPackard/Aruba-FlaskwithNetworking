# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Generic ArubaOS-CX classes
import classes.classes
import requests
sessionid = requests.Session()

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import datetime
from time import gmtime, strftime, time

def logincx (deviceid):
    global sessionid
    globalsconf=classes.classes.globalvars()
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    baseurl="https://{}/rest/v1/".format(deviceCreds['ipaddress'])
    credentials={'username': deviceCreds['username'],'password': classes.classes.decryptPassword(globalsconf['secret_key'], deviceCreds['password']) }
    # First, check whether there is an existing sessionid. If there is, there is no need to login to the switch
    # This can easily be verified by issuing a get response
    try:
        # Login to the switch. The cookie value is stored in the session cookie jar
        response = sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=5)

        return sessionid
    except:
        return 401

def logoutcx(sessionid,deviceid):
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    baseurl="https://{}/rest/v1/".format(deviceCreds['ipaddress'])
    try:
        response = sessionid.post(baseurl + "logout", verify=False, timeout=5)
    except:
        return "Logout failure"

def getRESTcx(deviceid,url):
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    baseurl="https://{}/rest/v1/".format(deviceCreds['ipaddress'])
    try:
        sessionid=logincx(deviceid)
        response=sessionid.get(baseurl + url, verify=False, timeout=4)
        try:
            # If the response contains information, the content is converted to json format
            response=json.loads(response.content.decode('utf-8'))
        except:
            response={}
        logoutcx(sessionid,deviceid)
    except:
        return {}
    return response

def getcxInfo(deviceid):
    sysinfo={}
    interfaces={}
    portinfo={}
    vsxinfo={}
    vrfinfo={}
    vsxlags={}
    #This definition obtains all the relevant information from the cx device and then stores this in the database
    #urllist=["system/interfaces?attributes=admin_state%2Cduplex%2Chw_intf_info%2Clink_speed%2Clink_state%2Clink_state_hw%2Clldp_statistics%2Cmtu%2Cname%2Cstatistics&depth=2","system/ports?depth=1","system/subsystems?attributes=resource_utilization&depth=2","system?attributes=capabilities%2Ccapacities%2Ccapacities_status%2Chostname%2Cmgmt_intf%2Cmgmt_intf_status%2Cplatform_name%2Csoftware_images%2Csoftware_info%2Csoftware_version%2Csubsystems&depth=2","system/vsx?depth=3","system/vrfs?depth=2","system/vsx_remote_lags?depth=2"]
    urllist=["system/interfaces?attributes=admin_state%2Cduplex%2Chw_intf_info%2Clink_speed%2Clink_state%2Clink_state_hw%2Clldp_statistics%2Cmtu%2Cname%2Cstatistics&depth=2","system/ports?depth=1","system/subsystems?attributes=resource_utilization&depth=2","system?attributes=capabilities%2Ccapacities%2Ccapacities_status%2Chostname%2Cmgmt_intf%2Cmgmt_intf_status%2Cplatform_name%2Csoftware_images%2Csoftware_info%2Csoftware_version%2Csubsystems&depth=2","system/vsx?depth=3","system/vrfs?depth=2","system/vsx_remote_lags?depth=2", "system/vrfs/default/routes?depth=1"]
    for items in urllist:
        try:
            result=getRESTcx(deviceid,items)
        except:
            pass
        # Update the database with relevant information based on the url
        if items=="system/vsx?depth=3":         
            vsxinfo=json.dumps(result, separators=(',',':'))
        elif items=="system/vrfs?depth=2":
            vrfinfo=json.dumps(result, separators=(',',':'))
        elif items=="system/vsx_remote_lags?depth=2":
            vsxlags=json.dumps(result, separators=(',',':'))
        elif items=="system/ports?depth=1":
            portinfo=json.dumps(result, separators=(',',':'))
        elif items=="system/vrfs/default/routes?depth=1":
            routeinfo=json.dumps(result, separators=(',',':'))
        elif items=="system/interfaces?attributes=admin_state%2Cduplex%2Chw_intf_info%2Clink_speed%2Clink_state%2Clink_state_hw%2Clldp_statistics%2Cmtu%2Cname%2Cstatistics&depth=2":
            interfaces=json.dumps(result, separators=(',',':'))
        elif items=="system/subsystems?attributes=resource_utilization&depth=2":
            # Typically, we are receiving multiple entries for the utilization, based on the subsystem (chassis, base, management, etc)
            # We should obtain all the entries that actually contain the values and average them out
            cpuCounter=0
            memCounter=0
            cpuVal=0
            memVal=0
            # For next loop through the list. There is usually more than one entry
            for resourceList in result:
                # For next loop per resource_utilization dictionary. 
                for key in resourceList:
                    # For next loop through the items per resource_utilization dictionary
                    for value in resourceList[key]:
                        if value=="cpu":
                            if resourceList[key][value]:
                                # If the CPU key has a value we have to increase the counter and sum the cpu values
                                cpuVal=cpuVal+resourceList[key][value]
                                cpuCounter=cpuCounter+1
                        elif value=="memory":
                            if resourceList[key][value]:
                                # If the CPU key has a value we have to increase the counter and sum the cpu values
                                memVal=memVal+resourceList[key][value]
                                memCounter=memCounter+1
            # Now that all CPU utilizations and memories are summed up, average out
            if cpuVal>0:
                cpuValappend=str(int(cpuVal/cpuCounter))
            else:
                cpuValappend=0
            if memVal>0:
                memValappend=str(int(memVal/memCounter))
            else:
                memValappend=0
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
            sysinfo=json.dumps(result, separators=(',',':'))
    # Only update the database when we have system information, port and VRF information, otherwise don't update
    # When the switch has a clean configuration there is no interface and vsx information
    isOnline=classes.classes.checkifOnline(deviceid,"arubaos-cx")
    # if len(sysinfo)>2 and len(portinfo)>2 and len(vrfinfo)>2:
    if len(sysinfo)>2:
        queryStr="update devices set cpu='{}', memory='{}', sysInfo='{}', ports='{}', interfaces='{}', vsx='{}',vsxlags='{}', vrf='{}', routeinfo='{}' where id='{}'".format(cpuVallist, memVallist, sysinfo, portinfo, interfaces, vsxinfo, vsxlags, vrfinfo, routeinfo,str(deviceid))
        try:
            classes.classes.sqlQuery(queryStr,"update")
        except:
            print("Something went wrong with the query")
            pass


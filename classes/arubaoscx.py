# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# Generic ArubaOS-CX classes
import classes.classes
import requests
import paramiko

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import datetime
from time import gmtime, strftime, time, sleep

def checkcxCookie(deviceid):
    # Definition that checks whether the cookie that is stored in the database is still valid. If it is, then ok
    # If not ok, we need to login, and store the new cookie value
    # If login fails, this needs to be reflected in the database as well with the statuscode
    globalsconf=classes.classes.globalvars()
    queryStr="select ipaddress, username, password, secinfo, switchstatus from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    baseurl="https://{}/rest/v1/".format(deviceCreds['ipaddress'])
    # First, let's check if we can perform a REST call and get a response 200
    if deviceCreds['secinfo'] is None:
        # There is no cookie in the secinfo field, we HAVE to login
        credentials={'username': deviceCreds['username'],'password': classes.classes.decryptPassword(globalsconf['secret_key'], deviceCreds['password']) }
        try:
            # Login to the switch. The cookie value is stored in the session cookie jar
            response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
            if "set-cookie" in response.headers:
                # There is a cookie, so the login was successful. We don't have to logout because we will be using this cookie for subsequent calls
                cookie_header = {'Cookie': response.headers['set-cookie']}
            elif "session limit reached" in response.text:
                cs=clearSessions(deviceCreds['ipaddress'], deviceCreds['username'],classes.classes.decryptPassword(globalsconf['secret_key'], deviceCreds['password']))
                if cs=="ok":
                    response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                    if "set-cookie" in response.headers:
                        cookie_header = {'Cookie': response.headers['set-cookie']}
                    else:
                        cookie_header=""
            else:
                queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,deviceid)
                classes.classes.sqlQuery(queryStr,"update")
                return            
            queryStr="update devices set secinfo='{}', switchstatus='{}' where id='{}'".format(json.dumps(cookie_header),response.status_code,deviceid)
            classes.classes.sqlQuery(queryStr,"update")
            return cookie_header
        except:
            # Something went wrong with the login
            queryStr="update devices set switchstatus=100 where id='{}'".format(deviceid)
            classes.classes.sqlQuery(queryStr,"update")
            return
    else :
        try:
            if type(deviceCreds['secinfo']) is dict:
                header=deviceCreds['secinfo']
            else:
                header=json.loads(deviceCreds['secinfo'])
            try:
                response=requests.get(baseurl+"system?attributes=software_info&depth=2",headers=header,verify=False,timeout=5)
                if response.status_code==200:
                    # The cookie is still valid, return the cookie that is stored in the database
                    queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,deviceid)
                    classes.classes.sqlQuery(queryStr,"update")
                    return deviceCreds['secinfo']
                else:
                    # There is something wrong with the cookie, might be expired or the switch may be out of sessions
                    # If the latter is the case, we need to SSH into the switch and reset the sessions, then try to login again and get the cookie
                    # There could also be an authentication failure, if that is the case, we should return that result code
                    if "Authorization Required" in response.text:
                        # Need to login and store the cookie
                        credentials={'username': deviceCreds['username'],'password': classes.classes.decryptPassword(globalsconf['secret_key'], deviceCreds['password']) }
                        response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                        if "set-cookie" in response.headers:
                            cookie_header = {'Cookie': response.headers['set-cookie']}
                        else:
                            cookie_header=""                       
                        queryStr="update devices set secinfo='{}', switchstatus=200 where id='{}'".format(json.dumps(cookie_header),deviceid)
                        classes.classes.sqlQuery(queryStr,"update")
                        return cookie_header
                    elif "session limit reached" in response.text:
                        cs=clearSessions(deviceCreds['ipaddress'], deviceCreds['username'],classes.classes.decryptPassword(globalsconf['secret_key'], deviceCreds['password']))
                        if cs=="ok":
                            response = requests.post(baseurl + "login", params=credentials, verify=False, timeout=5)
                            if "set-cookie" in response.headers:
                                cookie_header = {'Cookie': response.headers['set-cookie']}
                            else:
                                cookie_header=""                       
                            queryStr="update devices set secinfo='{}', switchstatus=200 where id='{}'".format(json.dumps(cookie_header),deviceid)
                            classes.classes.sqlQuery(queryStr,"update")
                            return cookie_header
                        else:
                            queryStr="update devices set switchstatus=120 where id='{}'".format(deviceid)
                            classes.classes.sqlQuery(queryStr,"update")
                            return 120
                    else:
                        return deviceCreds['switchstatus']
            except:
                if deviceCreds['switchstatus']>100 and deviceCreds['switchstatus']<103:
                    switchstatus=deviceCreds['switchstatus']-1
                else:
                    switchstatus=100
                queryStr="update devices set switchstatus={} where id='{}'".format(switchstatus,deviceid)
                classes.classes.sqlQuery(queryStr,"update")
                return switchstatus
        except:
            if deviceCreds['switchstatus']>100 and deviceCreds['switchstatus']<103:
                switchstatus=deviceCreds['switchstatus']-1
            else:
                switchstatus=100
            queryStr="update devices set switchstatus={} where id='{}'".format(switchstatus,deviceid)
            classes.classes.sqlQuery(queryStr,"update")
            return switchstatus   
    # 100 means that the switch is not reachable at all
    return 100

def getcxREST(deviceid,url):
    response={}
    cookie_header=checkcxCookie(deviceid)
    if type(cookie_header) is dict:
        header=cookie_header
    else:
        header=json.loads(cookie_header)
    if cookie_header!="":
        queryStr="select ipaddress from devices where id='{}'".format(deviceid)
        deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
        baseurl="https://{}/rest/v1/".format(deviceCreds['ipaddress'])
        try:
            response=requests.get(baseurl + url,headers=header,verify=False, timeout=10)
            try:
                # If the response contains information, the content is converted to json format
                response=json.loads(response.content.decode('utf-8'))
                return response
            except:
                return
        except:
            return
    return

def getcxInfo(deviceid):
    sysinfo={}
    interfaces={}
    portinfo={}
    vsxinfo={}
    vrfinfo={}
    vsxlags={}
    vsfinfo={}
    cpuValappend=""
    memValappend=""
    try:
        #This definition obtains all the relevant information from the cx device and then stores this in the database
        urllist=["system/interfaces?attributes=admin_state%2Cduplex%2Chw_intf_info%2Clink_speed%2Clink_state%2Clink_state_hw%2Clldp_statistics%2Cmtu%2Cname%2Cstatistics&depth=2","system/ports?attributes=applied_vlan_trunks%2Cip4_address%2Cip4_address_secondary%2Cip6_addresses%2Cname%2Cvrf&depth=1","system/subsystems?attributes=resource_utilization&depth=2","system?attributes=capabilities%2Ccapacities%2Ccapacities_status%2Cboot_time%2Chostname%2Cmgmt_intf%2Cmgmt_intf_status%2Cplatform_name%2Csoftware_images%2Csoftware_info%2Csoftware_version%2Csubsystems&depth=2","system/vsx?depth=3","system/vrfs?depth=2","system/vsx_remote_lags?depth=2","system/vrfs/default/routes?depth=1"]
        for items in urllist:
            try:
                result=getcxREST(deviceid,items)
            except:
                result={}
            # Update the database with relevant information based on the url
            if items=="system/vsx?depth=3":         
                vsxinfo=json.dumps(result, separators=(',',':'))
            elif items=="system/vrfs?depth=2":
                vrfinfo=json.dumps(result, separators=(',',':'))
            elif items=="system/vsx_remote_lags?depth=2":
                vsxlags=json.dumps(result, separators=(',',':'))
            elif items=="system/ports?attributes=applied_vlan_trunks%2Cip4_address%2Cip4_address_secondary%2Cip6_addresses%2Cname%2Cvrf&depth=1":
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
                # sysinfo=json.dumps(result, separators=(',',':'))
                sysinfo=json.dumps(result)
        # Only update the database when we have system information, port and VRF information, otherwise don't update
        # When the switch has a clean configuration there is no interface and vsx information
        isOnline=classes.classes.checkifOnline(deviceid,"arubaos-cx")
        if len(sysinfo)>2 and len(portinfo)>2 and len(vrfinfo)>2:
            queryStr="update devices set cpu='{}', memory='{}', sysInfo='{}', ports='{}', interfaces='{}', vsx='{}',vsxlags='{}', vrf='{}', routeinfo='{}', vsf='{}' where id='{}'".format(cpuVallist, memVallist, sysinfo, portinfo, interfaces, vsxinfo, vsxlags, vrfinfo,routeinfo,vsfinfo,str(deviceid))
            try:
                classes.classes.sqlQuery(queryStr,"update")
            except:
                pass
        # If this switch is running VSF, we also need to obtain the VSF information, only update if there is VSF information
        try:
            url="system?attributes=vsf_config%2Cvsf_status&depth=3"
            vsfstatus=getcxREST(deviceid,url)
            try:
                # If the response contains information, the content is converted to json format
                vsfstatus=json.loads(vsfstatus.content.decode('utf-8'))
            except:
                vsfstatus=""
            url="system/vsf_members?depth=2"
            vsfmember=getcxREST(deviceid,url)
            try:
                # If the response contains information, the content is converted to json format
                vsfmember=json.loads(vsfmember.content.decode('utf-8'))
            except:
                vsfmember=""
            if isinstance(vsfstatus,list) and isinstance(vsfmember,dict):
                # Let's update the database because there is extensive VSF information
                vsfinfo="["+ vsfstatus + "," + vsfmember+ "]"
                queryStr="update devices set vsf='{}' where id='{}'".format(vsfinfo,str(deviceid))
                classes.sqlQuery(queryStr,"update")
        except:
            pass
    except:
        pass

def clearSessions(ipaddr, username,password):
    try:
        remoteclient=paramiko.SSHClient()
        remoteclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remoteclient.connect(ipaddr,username=username,password=password, timeout=5)
        # Logging in could take some time. Pause a bit
        sleep(5)
        connection=remoteclient.invoke_shell()
        connection.send("\n")
        sleep(3)
        connection.send("https session close all\n")
        sleep(3)
        connection.close()
        remoteclient.close()
        return "ok"
    except:
        return "nok"
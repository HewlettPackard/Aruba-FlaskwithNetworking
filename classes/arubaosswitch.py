# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Generic ArubaOS-Switch classes

import classes.classes
import requests
import base64
from netmiko import ConnectHandler


import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import datetime
from time import gmtime, strftime, time

def resetRest(deviceid):
    globalsconf=classes.classes.globalvars()
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    params={'device_type':'hp_procurve','ip':deviceCreds['ipaddress'],'username':deviceCreds['username'],'password':classes.classes.decryptPassword(globalsconf['secret_key'], deviceCreds['password'])}
    try:
        net_connect=ConnectHandler(**params)
        net_connect.config_mode()
        commands = ["no rest-interface","rest-interface","end"]
        net_connect.send_config_set(commands)
        net_connect.disconnect()
        return "ok"
    except:
        return "nok"

def checkswitchCookie(deviceid):
    # Definition to check whether the cookie for the switch is still valid
    # If not ok, we need to login, and store the new cookie value
    # If login fails, this needs to be reflected in the database as well with the statuscode
    globalsconf=classes.classes.globalvars()
    queryStr="select ipaddress, username, password, secinfo, switchstatus from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    baseurl="http://{}/rest/v7/".format(deviceCreds['ipaddress'])
    credentials = {"userName": deviceCreds['username'], "password": classes.classes.decryptPassword(globalsconf['secret_key'], deviceCreds['password']) }
    url="login-sessions"
    # First, let's check if we can perform a REST call and get a response 200
    if deviceCreds['secinfo'] is None:
        # There is no cookie in the secinfo field, we HAVE to login
        try:
            # Login to the switch. The cookie value is stored in the session cookie jar
            response = requests.post(baseurl+url, verify=False, data=json.dumps(credentials), timeout=5)
            sessioninfo = response.json()
            if "Set-Cookie" in response.headers:
                # There is a cookie, so the login was successful. We don't have to logout because we will be using this cookie for subsequent calls
                cookie_header={'Cookie': sessioninfo['cookie']}
                queryStr="update devices set secinfo='{}', switchstatus='{}' where id='{}'".format(json.dumps(cookie_header),response.status_code,deviceid)
                classes.classes.sqlQuery(queryStr,"update")
                return json.loads(cookie_header)
            else:
                return                 
        except:
            # Something went wrong with the login
            return
    else :
        try:
            response=requests.get(baseurl+"system",headers=json.loads(deviceCreds['secinfo']),verify=False,timeout=5)
            if response.status_code==200:
                # The cookie is still valid, return the cookie that is stored in the database
                queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,deviceid)
                classes.classes.sqlQuery(queryStr,"update")
                return json.loads(deviceCreds['secinfo'])
            else:
                # There is something wrong with the cookie, might be expired or the switch may be out of sessions
                # If the latter is the case, we need to SSH into the switch and reset the sessions, then try to login again and get the cookie
                # There could also be an authentication failure, if that is the case, we should return that result code
                if response.status_code==400:
                    # Need to login and store the cookie
                    response = requests.post(baseurl+url, verify=False, data=json.dumps(credentials), timeout=5)
                    sessioninfo = response.json()
                    if "Set-Cookie" in response.headers:
                        # There is a cookie, so the login was successful. We don't have to logout because we will be using this cookie for subsequent calls
                        cookie_header={'Cookie': sessioninfo['cookie']}
                        queryStr="update devices set secinfo='{}', switchstatus='{}' where id='{}'".format(json.dumps(cookie_header),response.status_code,deviceid)
                        classes.classes.sqlQuery(queryStr,"update")
                        return cookie_header
                    else:
                        queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,deviceid)
                        classes.classes.sqlQuery(queryStr,"update")
                        return                               
                elif "session limit reached" in response.text:
                    sr=resetRest(deviceid)
                    if sr=="ok":
                        response = requests.post(baseurl+url, verify=False, data=json.dumps(credentials), timeout=5)
                        sessioninfo = response.json()
                        if "Set-Cookie" in response.headers:
                            # There is a cookie, so the login was successful. We don't have to logout because we will be using this cookie for subsequent calls
                            cookie_header={'Cookie': sessioninfo['cookie']}
                            queryStr="update devices set secinfo='{}' where id='{}'".format(json.dumps(cookie_header),deviceid)
                            classes.classes.sqlQuery(queryStr,"update")
                            return cookie_header
                        else:
                            queryStr="update devices set switchstatus='{}' where id='{}'".format(response.status_code,deviceid)
                            classes.classes.sqlQuery(queryStr,"update")
                            return
                    else:
                        queryStr="update devices set switchstatus=120 where id='{}'".format(deviceid)
                        classes.classes.sqlQuery(queryStr,"update")
                        return 120
                else:
                    return deviceCreds['switchstatus']
        except:
            if deviceCreds['switchstatus']>100:
                switchstatus=deviceCreds['switchstatus']-1
            else:
                switchstatus=100
            queryStr="update devices set switchstatus={} where id='{}'".format(switchstatus,deviceid)
            classes.classes.sqlQuery(queryStr,"update")
            return switchstatus 
    # 100 means that the switch is not reachable at all
    return 100

def getswitchREST(url,deviceid):
    # Obtain device information from the database
    queryStr="select ipaddress, secinfo from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    url="http://{}/rest/v7/".format(deviceCreds['ipaddress']) + url
    header=checkswitchCookie(deviceid)
    try:
        response=requests.get(url, verify=False, headers=header)
        # If the response contains information, the content is converted to json format
        response=json.loads(response.content.decode('utf-8'))
        return response
    except:
        return



def postswitchREST(deviceid,url,parameters):
    # Obtain device information from the database
    queryStr="select ipaddress, secinfo from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    url="http://{}/rest/v7/".format(deviceCreds['ipaddress']) + url
    header=checkswitchCookie(deviceid)
    try:
        response = requests.post(url, verify=False, data=json.dumps(parameters), headers=header, timeout=20)
        # If the response contains information, the content is converted to json format
        response=json.loads(response.content.decode('utf-8'))
    except:
        response={} 
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
    cpuValappend=""
    memValappend=""
    # First, get the system information
    urllist=["system","system/status/power/supply","system/status/switch","system/status","vlans","vlans-ports","dot1x","ipaddresses","lldp","radius_servers","system/time","lacp/port","snmp-server/communities","snmpv3/users","stp","telnet/server","monitoring/ntp/status"]
    for sysitems in urllist:
        try:
            result=getswitchREST(sysitems,deviceid)
            if sysitems=="system":
                hostname=result['name']
            # Join the dictionaries
            sysinfo= {**sysinfo,**result} 
            url="system/status/switch"
            # Check whether the device is configured for VSF or BPS, or whether it's a stand alone switch. If the latter is the case, the vsf and bps fields remain empty
            if sysitems=="system/status/switch":
                if sysinfo['switch_type']=="ST_STACKED":
                    url="stacking/vsf/members"
                    try:
                        vsfinfo=getswitchREST(url,deviceid)
                        # If the result does not contain the message key, which means that there is an error, this means that there is actually information in the result
                        # And this implies that the switch is running VSF
                        if not 'message' in vsfinfo:
                            sysinfo= {**sysinfo,**vsfinfo}
                    except:
                        pass
                    url="stacking/bps/members"
                    try:
                        bpsinfo=getswitchREST(url,deviceid)
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
            result=getswitchREST(interfaceitems,deviceid)
            interfaces= {**interfaces,**result}
        except:
            pass
    # Obtain lldp information
    url="lldp/remote-device"
    try:
        lldpinfo=getswitchREST(url,deviceid)
        lldpinfo=json.dumps(lldpinfo)
        # It is possible that the json contains double quotes with backslashes. Replace those.
        lldpinfo=lldpinfo.replace('\\"','')
    except:
        pass
    # If operating in a VSF stack, obtain all VSF information from the stack based on the urllist
    if stacktype=="vsf":
        urllist=["stacking/vsf/global_config","stacking/vsf/info","stacking/vsf/members","stacking/vsf/members/system_info","stacking/vsf/members_links_ports","system/status/members"]
        for vsfitems in urllist:
            try:
                result=getswitchREST(vsfitems,deviceid)
                vsfinfo= {**vsfinfo,**result} 
            except:
                pass
        # Now for CPU and Memory. First obtain the commander device id
        if "vsf_member_element" in vsfinfo:
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
        urllist=["stacking/bps/info","stacking/bps/members","stacking/bps/members/system_info","stacking/bps/stack_ports","system/status/members"]
        for bpsitems in urllist:
            try:
                result=getswitchREST(bpsitems,deviceid)
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
        if response:
            payload_str = base64.b64decode(response['result_base64_encoded']).decode('utf-8')
            # Need to get the CPU value for the 5 second interval
            cpuVal=payload_str[payload_str.find('5 sec ave')+11:]
            cpuVal=int(cpuVal[0:2])
            cpuVallist.append(tuple((strftime("%d-%m-%Y %H:%M:%S", gmtime()),cpuVal)))
            if "total_memory_in_bytes" in sysinfo:
                memVallist.append(tuple((strftime("%d-%m-%Y %H:%M:%S", gmtime()),sysinfo['total_memory_in_bytes'])))
            #Store the last 30 values in the database, this value contains timestamp as key value and CPU or memory as value
        cpuVallist=json.dumps(cpuVallist[-30:])
        memVallist=json.dumps(memVallist[-30:]) 
    if bool(sysinfo)==True:
        queryStr="update devices set description='{}',sysinfo='{}', cpu='{}', memory='{}', interfaces='{}', vsf='{}', bps='{}', lldp='{}' where id='{}'". format(hostname,json.dumps(sysinfo),cpuVallist,memVallist,json.dumps(interfaces), json.dumps(vsfinfo), json.dumps(bpsinfo), lldpinfo, deviceid)
        try:
            classes.classes.sqlQuery(queryStr,"update")
        except:
            pass

def anycli(cmd,deviceid):
    # Obtain device information from the database
    header=checkswitchCookie(deviceid)
    queryStr="select ipaddress from devices where id='{}'".format(deviceid)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    url="http://{}/rest/v7/cli".format(deviceCreds['ipaddress'])
    sendcmd={'cmd':cmd}
    cliResult=False
    while cliResult==False:
        try:
            response=requests.post(url, verify=False, headers=header, data=json.dumps(sendcmd))
            # If the response contains information, the content is converted to json format
            jresponse=response.json()
            if "error_msg" in jresponse:
                if jresponse['error_msg']=="":
                    cliResult=True
        except:
            pass
    return json.loads(response.content)

def anycliProvision(cmd,ipaddress,header):
    queryStr="select id from devices where ipaddress='{}'".format(ipaddress)
    deviceCreds=classes.classes.sqlQuery(queryStr,"selectone")
    url="http://{}/rest/v7/cli".format(ipaddress)
    sendcmd={'cmd':cmd}
    header=checkswitchCookie(deviceCreds['id'])
    try:
        response=requests.post(url, verify=False, headers=header, data=json.dumps(sendcmd), timeout=20)
        # If the response contains information, the content is converted to json format
        response=json.loads(response.content)
    except:
        response="No data"
    return response

# (C) Copyright 2018 Hewlett Packard Enterprise Development LP.

import requests
sessionid = requests.Session()

import json

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import datetime
from time import gmtime, strftime, time

import pymysql.cursors

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


def convertTime(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S') 

def logincx (deviceid):
    global sessionid
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=sqlQuery(queryStr,"selectone")
    baseurl="https://{}/rest/v1/".format(deviceCreds['ipaddress'])
    credentials={'username': deviceCreds['username'],'password': decryptPassword("ArubaRocks!!!!!!", deviceCreds['password']) }
    try:
        # Login to the switch. The cookie value is stored in the session cookie jar
        response = sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=1)
        return sessionid
    except:
        return 401

def logoutcx(sessionid,deviceid):
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=sqlQuery(queryStr,"selectone")
    baseurl="https://{}/rest/v1/".format(deviceCreds['ipaddress'])
    try:
        response = sessionid.post(baseurl + "logout", verify=False, timeout=1)
    except:
        return "Logout failure"

def loginswitch (deviceid):
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=sqlQuery(queryStr,"selectone")
    url="http://{}/rest/v4/login-sessions".format(deviceCreds['ipaddress'])
    credentials = {"userName": deviceCreds['username'], "password": decryptPassword("ArubaRocks!!!!!!", deviceCreds['password']) }
    try:
        # Login to the switch. The cookie value is returned to the calling definition. It is not stored in the cookie jar.
        response = requests.post(url, verify=False, data=json.dumps(credentials), timeout=1)
        sessioninfo = response.json()
        header={'cookie': sessioninfo['cookie']}
        print("Logged into Arubaos-Switch")
        return header
    except:
        print("Error logging into Arubaos-Switch")
        return 401

def logoutswitch(header,deviceid):
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=sqlQuery(queryStr,"selectone")
    url="http://{}/rest/v4/login-sessions".format(deviceCreds['ipaddress'])
    try:
        response = requests.delete(url,headers=header,timeout=1)
        print("Logged out from Arubaos-Switch")
    except:
        print("Error logging out of Arubaos-Switch")
    

def sqlQuery(queryStr, command):
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    with dbconnection.cursor(pymysql.cursors.DictCursor) as cursor:
       if command=="select":
           cursor.execute(queryStr)
           result = cursor.fetchall()
           return result
       elif command=="selectone":
           cursor.execute(queryStr)
           result = cursor.fetchone()
           return result
       elif command=="insert":       
           try:
               cursor.execute(queryStr)
               return cursor.lastrowid
           except pymysql.InternalError as error:
               code, message = error.args
               return (code, message)
       elif command=="update" or command=="delete":       
           try:
               cursor.execute(queryStr)
               result="ok"
           except pymysql.InternalError as error:
               code, message = error.args
               return(code, message)
    dbconnection.close()
    return result

def encryptPassword(salt, password):
    cipher = AES.new(salt.encode(), AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(password.encode(), AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    return json.dumps({'iv':iv, 'ciphertext':ct})

def decryptPassword(salt, password):
    b64 = json.loads(password)
    iv = b64decode(b64['iv'])
    ct = b64decode(b64['ciphertext'])
    cipher = AES.new(salt.encode(), AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

def getRESTcx(deviceid,url,sessionid):
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=sqlQuery(queryStr,"selectone")
    baseurl="https://{}/rest/v1/".format(deviceCreds['ipaddress'])
    try:
        response=sessionid.get(baseurl + url, verify=False)
        try:
            # If the response contains information, the content is converted to json format
            response=json.loads(response.content)
        except:
            response={}
    except:
        return {}
    return response

def getRESTswitch(header,url,deviceid):
    # Obtain device information from the database
    queryStr="select ipaddress, username, password from devices where id='{}'".format(deviceid)
    deviceCreds=sqlQuery(queryStr,"selectone")
    url="http://{}/rest/v4/".format(deviceCreds['ipaddress']) + url
    try:
        response=requests.get(url, verify=False, headers=header)
        # If the response contains information, the content is converted to json format
        response=json.loads(response.content)
    except:
        response="No data"
    return response

def checkifOnline(deviceid,ostype):
    # Login and logout of the device to see if the device is online
    if ostype=="arubaos-cx":
        try:
            sessionid=logincx(deviceid)
            if sessionid==401:
                return "Offline"
        except:
            pass
        logoutcx(sessionid,deviceid)
        return "Online"
    if ostype=="arubaos-switch":
        try:
            header=loginswitch(deviceid)
            if header==401:
                return "Offline"
        except:
            pass
        logoutswitch(header,deviceid)
        return "Online"
    return

def getcxInfo(deviceid):
    sysinfo={}
    interfaces={}
    bridgeinfo={}
    vsxinfo={}
    vrfinfo={}
    #This definition obtains all the relevant information from the cx device and then stores this in the database
    sessionid=logincx(deviceid)
    urllist=["system/bridge?depth=2","system/interfaces?attributes=description%2Cduplex%2Cerror%2Cforwarding_state%2Chw_intf_info%2Chw_status%2Clink_speed%2Clink_state%2Clink_state_hw%2Cmtu%2Cname%2Coptions%2Cphysical_interface_state%2Cqueue_tx_bytes%2Cqueue_tx_errors%2Cqueue_tx_maxdepth%2Cqueue_tx_packets%2Cstatistics%2Cstatus%2Ctype&depth=1&filter=admin_state%3Aup%2Clink_state%3Aup","system/subsystems?attributes=resource_utilization&depth=2","system?attributes=capabilities%2Ccapacities%2Ccapacities_status%2Chostname%2Cmgmt_intf%2Cmgmt_intf_status%2Cplatform_name%2Csoftware_images%2Csoftware_info%2Csoftware_version%2Csubsystems&depth=2","system/vsx?depth=3","system/vrfs?depth=2"]
    for items in urllist:
        try:
            result=getRESTcx(deviceid,items,sessionid)
        except:
            pass
        # Update the database with relevant information based on the url
        if items=="system/vsx?depth=3":         
            vsxinfo=json.dumps(result, separators=(',',':'))
        elif items=="system/vrfs?depth=2":
            vrfinfo=json.dumps(result, separators=(',',':'))
        elif items=="system/bridge?depth=2":
            bridgeinfo=json.dumps(result, separators=(',',':'))
        elif items=="system/interfaces?attributes=description%2Cduplex%2Cerror%2Cforwarding_state%2Chw_intf_info%2Chw_status%2Clink_speed%2Clink_state%2Clink_state_hw%2Cmtu%2Cname%2Coptions%2Cphysical_interface_state%2Cqueue_tx_bytes%2Cqueue_tx_errors%2Cqueue_tx_maxdepth%2Cqueue_tx_packets%2Cstatistics%2Cstatus%2Ctype&depth=1&filter=admin_state%3Aup%2Clink_state%3Aup":
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
            cpumemVal=sqlQuery(queryStr,"selectone")
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
    # Only update the database when we have system information, bridge and VRF information, otherwise don't update
    # When the switch has a clean configuration there is no interface and vsx information
    isOnline=checkifOnline(deviceid,"arubaos-cx")
    if len(sysinfo)>2 and len(bridgeinfo)>2 and len(vrfinfo)>2:
        queryStr="update devices set cpu='{}', memory='{}', sysInfo='{}', bridge='{}', interfaces='{}', vsx='{}', vrf='{}' where id='{}'".format(cpuVallist, memVallist, sysinfo, bridgeinfo, interfaces, vsxinfo, vrfinfo,str(deviceid))
        try:
            sqlQuery(queryStr,"update")
        except:
            pass
    logoutcx(sessionid,deviceid)

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
    urllist=["system/status/power/supply","system/status/switch","system/status","vlans","vlans-ports","dot1x","ipaddresses","lldp","radius_servers","system/time","lacp/port","snmp-server/communities","snmpv3/users","stp","telnet/server","system/status/members"]
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
        cpumemVal=sqlQuery(queryStr,"selectone")
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
        cpumemVal=sqlQuery(queryStr,"selectone")
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
        # It's a stand alone switch, assigning empty values for cpu and memory
        cpuVallist=[]
        memVallist=[] 
    if bool(sysinfo)==True:
        queryStr="update devices set sysinfo='{}', cpu='{}', memory='{}', interfaces='{}', vsf='{}', bps='{}', lldp='{}' where id='{}'". format(json.dumps(sysinfo),cpuVallist,memVallist,json.dumps(interfaces), json.dumps(vsfinfo), json.dumps(bpsinfo), lldpinfo, deviceid)
        try:
            sqlQuery(queryStr,"update")
        except:
            print("error in query")
    logoutswitch(header,deviceid)

def discoverModel(deviceid,sessionid):
    # Performing REST calls to discover what switch model we are dealing with
    # Check whether device is ArubaOS-CX
    urllist=["system/interfaces?attributes=description%2Cduplex%2Cerror%2Cforwarding_state%2Chw_intf_info%2Chw_status%2Clink_speed%2Clink_state%2Clink_state_hw%2Cmtu%2Cname%2Coptions%2Cphysical_interface_state%2Cqueue_tx_bytes%2Cqueue_tx_errors%2Cqueue_tx_maxdepth%2Cqueue_tx_packets%2Cstatistics%2Cstatus%2Ctype&depth=1&filter=admin_state%3Aup%2Clink_state%3Aup","system?attributes=bridge%2Ccapabilities%2Ccapacities%2Ccapacities_status%2Cdb_version%2Chostname%2Cmgmt_intf%2Cmgmt_intf_status%2Cplatform_name%2Csoftware_images%2Csoftware_info%2Csoftware_version%2Csubsystems%2Cvrfs&depth=2"]
    try:
        sessionid=logincx(deviceid)
        for items in urllist:
            response =getRESTcx(deviceid,items,sessionid)
            if items=="system/interfaces?attributes=description%2Cduplex%2Cerror%2Cforwarding_state%2Chw_intf_info%2Chw_status%2Clink_speed%2Clink_state%2Clink_state_hw%2Cmtu%2Cname%2Coptions%2Cphysical_interface_state%2Cqueue_tx_bytes%2Cqueue_tx_errors%2Cqueue_tx_maxdepth%2Cqueue_tx_packets%2Cstatistics%2Cstatus%2Ctype&depth=1&filter=admin_state%3Aup%2Clink_state%3Aup":
                interfaces=json.dumps(response, separators=(',',':'))
            else:
                sysinfo=response
        logoutcx(sessionid,deviceid)
        if 'platform_name' in sysinfo:
            # It is an ArubaOS-CX device. Obtain the interface information and then update the database
            queryStr="update devices set ostype='arubaos-cx', platform='{}', osversion='{}', sysinfo='{}', interfaces='{}' where id='{}'".format(response['platform_name'], response['software_version'], json.dumps(response['subsystems']), interfaces, deviceid)
            try:
                result=sqlQuery(queryStr,"update")
            except:
                print("SQL error in discoverModel for ArubaOS-CX device")
    except:
        pass
    # Check whether the device is ArubaOS-Switch by obtaining the local lldp and system information 
    try:
        header=loginswitch(deviceid)
        url="lldp/local_device/info"
        response =getRESTswitch(header,url,deviceid)
        if 'system_description' in response:
            # This is an ArubaOS-Switch switch. System description is a comma separated string that contains product and version information
            # Splitting the string into a list and then assign the values  
            deviceInfo=response['system_description'].split(",")
            # Obtaining system information. This information also contains port information
            url="system/status/switch"
            sysinfo=getRESTswitch(header,url,deviceid)
            # Check whether the device is configured for VSF or BPS, or whether it's a stand alone switch. If the latter is the case, the vsf and bps fields remain empty
            if sysinfo['switch_type']=="ST_STACKED":
                url="stacking/vsf/members"
                # Getting the member information, this information contains which device is the master/commander. This is for running VSF
                try:
                    vsfinfo=getRESTswitch(header,url,deviceid)
                    if 'message' in vsfinfo:
                        vsfinfo={}
                    else:
                        sysinfo= {**sysinfo,**vsfinfo}
                except:
                    pass
                # If there is no response, this means that the switches are running BPS
                url="stacking/bps/members"
                try:
                    bpsinfo=getRESTswitch(header,url,deviceid)
                    if 'message' in bpsinfo:
                        bpsinfo={}
                    else:
                        sysinfo= {**sysinfo,**bpsinfo}
                except:
                    pass
            # Updating the database with all the gathered information
            queryStr="update devices set ostype='arubaos-switch', platform='{}', osversion='{}', sysinfo='{}' where id='{}'".format(deviceInfo[0],deviceInfo[1],json.dumps(sysinfo),deviceid)
            try:
                sqlQuery(queryStr,"update")
            except:
                print("SQL error in discoverModel for ArubaOS-Switch device")
        logoutswitch(header,deviceid)
    except:
        pass

def devicedbAction(formresult):
    # This definition is for all the database actions, based on the user click on the pages
    if(bool(formresult)==True):
        if(formresult['action']=="Submit device"):
            queryStr="insert into devices (description,ipaddress,username,password,cpu,memory,sysinfo,bridge,interfaces,vrf,vsx,vsf,bps,lldp) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')"\
            .format(formresult['description'],formresult['ipaddress'],formresult['username'],encryptPassword("ArubaRocks!!!!!!", formresult['password']),"[]","[]","{}","{}","{}","{}","{}","{}","{}",'{}')
            deviceid=sqlQuery(queryStr,"insert")
            # Discover what type of device this is and update the database with the obtained information
            discoverModel(deviceid,sessionid)
            # Build the list
            result=sqlQuery("select id, description, ipaddress, username, password, ostype, platform, osversion from devices","select")
        elif  (formresult['action']=="Submit changes"):
            queryStr="update devices set description='{}',ipaddress='{}',username='{}',password='{}' where id='{}' "\
            .format(formresult['description'],formresult['ipaddress'],formresult['username'],encryptPassword("ArubaRocks!!!!!!", formresult['password']),formresult['id'])
            sqlQuery(queryStr,"update")
            # Discover what type of device this is and update the database with the obtained information
            discoverModel(formresult['id'],sessionid)
            # Build the list
            result=sqlQuery("select id, description, ipaddress, username, password, ostype, platform, osversion from devices","select")
        elif (formresult['action']=="Delete"):
            queryStr="delete from devices where id='{}'".format(formresult['id'])
            sqlQuery(queryStr,"delete")
            result=sqlQuery("select id, description, ipaddress, username, password, ostype, platform, osversion from devices","select")
        elif (formresult['action']=="order by ipaddress"):
            result=sqlQuery("select id, description, ipaddress, username, password, ostype, platform, osversion from devices order by ipaddress ASC","select")
        elif (formresult['action']=="order by description"):
            result=sqlQuery("select id, description, ipaddress, username, password, ostype, platform, osversion from devices order by description ASC","select")
        else:
            result=sqlQuery("select id, description, ipaddress, username, password, ostype, platform, osversion from devices","select")
    else:
        result=sqlQuery("select id, description, ipaddress, username, password, ostype, platform, osversion from devices","select")
    return result

def interfacedbAction(deviceid, interface,ostype):
    # Definition that obtains all the relevant information from the database for showing on the html pages
    queryStr="select sysinfo,interfaces, lldp from devices where id='{}'".format(deviceid)
    result=sqlQuery(queryStr,"selectone")
    interfaceinfo=json.loads(result['interfaces'])
    if ostype=="arubaos-switch":
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
            for items in lldpinfo['lldp_remote_device_element']:
                if items['local_port']==interface:
                    lldpinfo=items
                else:
                    pass
    return (interfaceinfo,lldpinfo)

def showLinechart(deviceid,entity,ostype,stacktype,commander,title):
    # definition that obtains the information from the database and formats this to display a linechart
    dataset=[]
    # Obtaining the relevant data (CPU or Memory) from the database as dataset value.
    queryStr="select {} as dataset from devices where id={}".format(entity,deviceid)
    result=sqlQuery(queryStr,"selectone")
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

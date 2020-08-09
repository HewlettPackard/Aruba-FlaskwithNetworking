# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

from datetime import datetime, time, timedelta
import time
import json
import pymysql.cursors
import sys
import os
import requests
import urllib3
import ipaddress

from urllib.parse import quote, unquote
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sessionid = requests.Session()

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def discoverTopology():
    topolog = open('/var/www/html/log/topology.log', 'a')
    pathname = os.path.dirname(sys.argv[0])
    appPath = os.path.abspath(pathname) + "/globals.json"
    existingEntries=[]
    with open(appPath, 'r') as myfile:
        data=myfile.read()
    globalconf=json.loads(data)
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    # First step is to get all the devices from the database that have topology discovery enabled
    queryStr="select description,ipaddress,username,password,ostype, sysinfo from devices where topology='1'"
    cursor.execute(queryStr)
    result = cursor.fetchall()
    for items in result:
        password=decryptPassword(globalconf['secret_key'], items['password']) 
        # First check whether it is an ArubaOS-Switch or an AOS-CX switch
        if items['ostype']=="arubaos-switch":
            # Now determine whether the switch is running as standalone or in VSF
            sysinfo=json.loads(items['sysinfo'])
            if "switch_type" in sysinfo:
                if sysinfo['switch_type']=="ST_STACKED":
                    # It's a VSF switch
                    url="system/status/global_info"
                else:
                    # It's a stand alone switch
                    url="system/status"
            else:
                # There is no switch type information in sysinfo. Assume it is a standalone switch
                url="system/status"
                # Get the system name and system MAC address        
            try:
                header=loginswitch(items['ipaddress'],items['username'],password)
                switchresult=getRESTswitch(items['ipaddress'],header,url)
                # Format the system mac address. It's abcdef-ghijkl now. Has to be ab:cd:ef:gh:ij:kl
                sysmac=switchresult['base_ethernet_address']['octets']
                sysmac=sysmac.replace('-','')
                sysmac= ':'.join([sysmac[i:i+2] for i in range(0, len(sysmac), 2)])
                url="lldp/remote-device"
                lldpresult=getRESTswitch(items['ipaddress'],header,url)
                logoutswitch(items['ipaddress'], header)
                try:
                    for lldpitems in lldpresult['lldp_remote_device_element']:
                        queryStr="select id from topology where switchip='{}' and interface='{}'".format(items['ipaddress'],lldpitems['local_port'])
                        cursor.execute(queryStr)
                        result = cursor.fetchall()
                        if result:
                            # We should only store the remote IP address if the IP address of the remote system is the proper format
                            if "remote_management_address" in lldpitems:
                                if checkIpaddress(lldpitems['remote_management_address']['address'])==True: 
                                    queryStr="update topology set switchip='{}', systemmac='{}',hostname='{}',interface='{}',remoteswitchip='{}',remotesystemmac='{}',remotehostname='{}',remoteinterface='{}',lldpinfo='{}' where id='{}'" \
                                    .format(items['ipaddress'],sysmac,switchresult['name'],lldpitems['local_port'],lldpitems['remote_management_address']['address'],lldpitems['chassis_id'].replace(' ',':'),lldpitems['system_name'],lldpitems['port_description'],json.dumps(lldpresult),result[0]['id'])
                                else:
                                    queryStr="update topology set switchip='{}', systemmac='{}',hostname='{}',interface='{}',remoteswitchip='{}',remotesystemmac='{}',remotehostname='{}',remoteinterface='{}',lldpinfo='{}' where id='{}'" \
                                    .format(items['ipaddress'],sysmac,switchresult['name'],lldpitems['local_port'],'',lldpitems['chassis_id'].replace(' ',':'),lldpitems['system_name'],lldpitems['port_description'],json.dumps(lldpresult),result[0]['id'])
                                cursor.execute(queryStr)
                                #topolog.write('{}: Updated topology for {} ({}). \n'.format(datetime.now(),items['ipaddress'],switchresult['name']))
                                existingEntries.append(result[0]['id'])
                        else:
                            # We should only store the remote IP address if the IP address of the remote system is the proper format
                            if "remote_management_address" in lldpitems:
                                if checkIpaddress(lldpitems['remote_management_address']['address'])==True: 
                                    queryStr="insert into topology (switchip,systemmac,hostname,interface,remoteswitchip,remotesystemmac,remotehostname,remoteinterface,lldpinfo) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}')" \
                                    .format(items['ipaddress'],sysmac,switchresult['name'],lldpitems['local_port'],lldpitems['remote_management_address']['address'],lldpitems['chassis_id'].replace(' ',':'),lldpitems['system_name'],lldpitems['port_description'],json.dumps(lldpresult))
                                else:
                                    queryStr="insert into topology (switchip,systemmac,hostname,interface,remoteswitchip,remotesystemmac,remotehostname,remoteinterface,lldpinfo) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}')" \
                                    .format(items['ipaddress'],sysmac,switchresult['name'],lldpitems['local_port'],'',lldpitems['chassis_id'].replace(' ',':'),lldpitems['system_name'],lldpitems['port_description'],json.dumps(lldpresult))
                                cursor.execute(queryStr)
                                topolog.write('{}: Created new topology for {} ({}). \n'.format(datetime.now(),items['ipaddress'],switchresult['name']))
                except:
                    print("Could not create or update topology for switch {}".format(items['ipaddress']))
                    topolog.write('{}: Could not create or update topology for switch {} ({}). \n'.format(datetime.now(),items['ipaddress'],switchresult['name']))
                    pass
            except:
                #print ("could not obtain information from Arubaos-switch")
                logoutswitch(items['ipaddress'], header)
                pass
            
        elif items['ostype']=="arubaos-cx":
            # Obtain the interfaces from the switch
            url="system/interfaces?depth=1"         
            intresult=getRESTcx(items['ipaddress'],items['username'],password,url)
            # Obtain the system mac address and the hostname from the switch
            url="system?attributes=hostname%2Csystem_mac"
            switchresult=getRESTcx(items['ipaddress'],items['username'],password,url)
            for intitems in intresult:
                # Obtain the LLDP information from the interfaces
                url="system/interfaces/" + quote(intitems['name'], safe='') + "/lldp_neighbors?attributes=mac_addr%2Cneighbor_info%2Cport_id&depth=2"
                lldpresult=getRESTcx(items['ipaddress'],items['username'],password,url)
                if lldpresult:
                    # There is information from the interface. Now we need to check a couple of things
                    # if there is already an entry for the topology we have to update
                    queryStr="select id from topology where switchip='{}' and interface='{}'".format(items['ipaddress'],intitems['name'])
                    cursor.execute(queryStr)
                    result = cursor.fetchall()
                    if switchresult:
                        if switchresult['system_mac'] and "mgmt_ip_list" in lldpresult[0]['neighbor_info']:
                            if result:
                                queryStr="update topology set switchip='{}', systemmac='{}',hostname='{}',interface='{}',remoteswitchip='{}',remotesystemmac='{}',remotehostname='{}',remoteinterface='{}',lldpinfo='{}' where id='{}'" \
                                .format(items['ipaddress'],switchresult['system_mac'],switchresult['hostname'],intitems['name'],lldpresult[0]['neighbor_info']['mgmt_ip_list'],lldpresult[0]['mac_addr'],lldpresult[0]['neighbor_info']['chassis_name'],lldpresult[0]['port_id'] ,json.dumps(lldpresult[0]),result[0]['id'])
                                cursor.execute(queryStr)
                                #topolog.write('{}: Updated topology for {} ({}). \n'.format(datetime.now(),items['ipaddress'],switchresult['hostname']))
                                existingEntries.append(result[0]['id'])
                            else:
                                queryStr="insert into topology (switchip,systemmac,hostname,interface,remoteswitchip,remotesystemmac,remotehostname,remoteinterface,lldpinfo) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}')" \
                                .format(items['ipaddress'],switchresult['system_mac'],switchresult['hostname'],intitems['name'],lldpresult[0]['neighbor_info']['mgmt_ip_list'],lldpresult[0]['mac_addr'],lldpresult[0]['neighbor_info']['chassis_name'],lldpresult[0]['port_id'] ,json.dumps(lldpresult[0]))
                                cursor.execute(queryStr)
                                topolog.write('{}: Created new topology for {} ({}). \n'.format(datetime.now(),items['ipaddress'],switchresult['hostname']))
        else:
            pass
    if existingEntries:
        queryStr="update topology set remoteswitchip='',remotesystemmac='',remoteinterface='',lldpinfo='' where id NOT IN ({})".format(json.dumps(existingEntries)[1:-1])
        result=cursor.execute(queryStr)
    topolog.close()

def getRESTcx(ipaddress,username,password,url):
    global sessionid
    baseurl="https://{}/rest/v1/".format(ipaddress)
    credentials={'username': username,'password': password }
    try:
        sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=10)
        response = sessionid.get(baseurl + url, verify=False, timeout=10)
        try:
            # If the response contains information, the content is converted to json format
            response=json.loads(response.content)
        except:
            sessionid.post(baseurl + "logout", verify=False, timeout=5)
            # print("Error obtaining response from get call {}".format(ipaddress))
            response={}
        sessionid.post(baseurl + "logout", verify=False, timeout=5)
    except:
        response={}
    return response

def loginswitch(ipaddress,username,password):
    credentials = {"userName": username, "password": password }
    try:
        # Login to the switch. The cookie value is returned to the calling definition. It is not stored in the cookie jar.
        response = requests.post("http://{}/rest/v7/login-sessions".format(ipaddress), verify=False, data=json.dumps(credentials), timeout=5)
        sessioninfo = response.json()
        header={'cookie': sessioninfo['cookie']}
        #print("Logged into Arubaos-Switch")
        return header
    except:
        #print("Error logging into Arubaos-Switch")
        return 401

def logoutswitch(ipaddress, header):
    try:
        requests.delete("http://{}/rest/v7/login-sessions".format(ipaddress),headers=header,timeout=5)
        #print("Logged out of {}".format(ipaddress))
    except:
        #print("Error logging out of Arubaos-Switch")
        pass

def getRESTswitch(ipaddress,header,url):
    # Obtain device information from the database
    url="http://{}/rest/v7/".format(ipaddress) + url
    try:
        response=requests.get(url, verify=False, headers=header)
        # If the response contains information, the content is converted to json format
        response=json.loads(response.content.decode('utf-8'))
    except:
        response={} 
    return response

def decryptPassword(salt, password):
    b64 = json.loads(password)
    iv = b64decode(b64['iv'])
    ct = b64decode(b64['ciphertext'])
    cipher = AES.new(salt.encode(), AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

def checkIpaddress(ip):
    try:
        ipInfo=bool(ipaddress.ip_address(str(ip)))
        return True
    except:
        return False




# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
# Aruba Fabric Composer classes for the datacollector

import requests
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict

import urllib3
import json
from datetime import datetime, time, timedelta
import time
import pymysql.cursors

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def obtainafcToken(afcipaddress,afcusername,afcpassword, cursor):
    afcvars=obtainVars(cursor,'sysafc')
    if isinstance(afcvars,str):
        afcvars=json.loads(afcvars)
    try:
        url="https://" + afcipaddress + "/api/auth/token"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        headers['accept'] = "application/json; version=1.0"
        headers["X-Auth-Username"] = afcusername
        headers["X-Auth-Password"] = afcpassword
        headers["Content-Length"] = "0"
        response = requests.post(url, headers=headers, verify=False)
        response=response.json()
        afcvars.update({"afctoken":response['result']})
        queryStr="update systemconfig set datacontent='{}' where configtype='sysafc'".format(json.dumps(afcvars))
        cursor.execute(queryStr)
        return response.text
    except ConnectionError:
        response.update({"message":"Connection error, no response from AFC"})
        return response
    except Exception as err:
        response.update({"message":"Failed to establish a connection to AFC"})
        return response


def checkafcToken(afcipaddress, afctoken):
    response={}
    result={}
    try:
        url="https://" + afcipaddress + "/api/ping"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        headers['accept'] = "application/json; version=1.0"
        headers["Authorization"] = afctoken
        result = requests.get(url, headers=headers, verify=False, timeout=10)
        response.update({"status_code": result.status_code})
        return response
    except ConnectionError:
        response.update({"message":"Connection error, no response from AFC"})
        return response
    except Exception as err:
        response.update({"message":"Failed to establish a connection to AFC"})
        return response


def getRestafc(cursor,url, datacollectorlog):
    afcvars=obtainVars(cursor,'sysafc')
    if isinstance(afcvars,str):
        afcvars=json.loads(afcvars)
    result={}
    if not "afctoken" in afcvars or afcvars['afctoken']=="":
        response= obtainafcToken(afcvars['afcipaddress'],afcvars['afcusername'], afcvars['afcpassword'], cursor)
        if isinstance(response,str):
            response=json.loads(response)
        afcvars.update({"afctoken":response['result']})
        queryStr="update systemconfig set datacontent='{}' where configtype='sysafc'".format(json.dumps(afcvars))
        cursor.execute(queryStr)
    url="https://" + afcvars['afcipaddress'] + "/" + url
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers['accept'] = "application/json; version=1.0"
    headers["Authorization"] = afcvars['afctoken']
    try:
        response=checkafcToken(afcvars['afcipaddress'],afcvars['afctoken'])
        if "status_code" in response:
            if response['status_code']==204:
                # Token seems to be valid, we can issue the query
                response = requests.get(url, headers=headers, verify=False, timeout=10)
                response = response.json()
                if response['result']=="Authentication credential is not valid; please log in again":
                    # Authorization token is still not valid. We need to refresh
                    response= obtainafcToken(afcvars['afcipaddress'], afcvars['afcusername'], afcvars['afcpassword'], cursor)
                    if isinstance(response,str):
                        response = json.loads(response)
                    if "count" in response:
                        # Result is the afctoken. We need to update the afcvars
                        afcvars.update({"afctoken":response['result']})
                        queryStr="update systemconfig set datacontent='{}' where configtype='sysafc'".format(json.dumps(afcvars))
                        cursor.execute(queryStr)
                    # And issue the get request again
                    headers["Authorization"] = afcvars['afctoken']
                    response = requests.get(url, headers=headers, verify=False, timeout=10)
                    response = response.json()
            else:
                # Statuscode is not 204, try to refresh the token
                response= obtainafcToken(afcvars['afcipaddress'], afcvars['afcusername'], afcvars['afcpassword'], cursor)
                if isinstance(response,str):
                    response = json.loads(response)
                if "count" in response:
                    # Result is the afctoken. We need to update the afcvars
                    afcvars.update({"afctoken":response['result']})
                    queryStr="update systemconfig set datacontent='{}' where configtype='sysafc'".format(json.dumps(afcvars))
                    cursor.execute(queryStr)
                    # And issue the get request again
                    headers["Authorization"] = afcvars['afctoken']
                    response = requests.get(url, headers=headers, verify=False, timeout=10)
                    response = response.json()
                else:
                    # There is something wrong with the connectivity, return an error
                    response.update({"message":"Unable to obtain information, verify AFC credentials"})
        return response
    except Exception as errormessage:
        response.update({"message":errormessage})
        datacollectorlog.write('{}: Error: {}. \n'.format(datetime.now(),errormessage))
        return response


def afcfabrics():
    datacollectorlog = open('/var/www/html/log/collector.log', 'a')
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    try:
        url="api/fabrics?switches=true&tags=true&include_segments=true"
        fabricInfo=getRestafc(cursor,url, datacollectorlog)
        if "message" in fabricInfo:
            # There was an issue obtaining the information. Check the message from one of the rest calls and update the database
            queryStr="select jsondata from afc where infotype='fabrics'"
            dbInfo=cursor.execute(queryStr)
            if "message" in fabricInfo['message']:
                message=fabricInfo['message']['message']
            else:
                message=fabricInfo['message']
            if dbInfo > 0:           
                queryStr="update afc set message='{}' where infotype='fabrics'".format(message)
            else:
                # There is no AFC integration entry yet in the database, we need to insert
                queryStr="insert into afc (infotype,jsondata, message) values ('fabrics','','{}')".format(message)
            cursor.execute(queryStr)
        else:
            queryStr="select jsondata from afc where infotype='fabrics'"
            dbInfo=cursor.execute(queryStr)
            if dbInfo > 0:
                queryStr="update afc set jsondata='{}', message='' where infotype='fabrics'".format(json.dumps(fabricInfo['result']))
                cursor.execute(queryStr)
            else:
                queryStr="insert into afc (infotype,jsondata, message) values ('fabrics','{}','')".format(json.dumps(fabricInfo['result']))
                cursor.execute(queryStr)
                datacollectorlog.write('{}: Fabric created. \n'.format(datetime.now()))
    except Exception as e:
        datacollectorlog.write('{}: {}. \n'.format(datetime.now(),e))
    cursor.close()
    datacollectorlog.close()



def afcswitches():
    datacollectorlog = open('/var/www/html/log/collector.log', 'a')
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    try:
        url="api/switches?ports=true&software=true"
        # url="api/switches?software=true"
        switchInfo=getRestafc(cursor,url, datacollectorlog)
        if "message" in switchInfo:
            # There was an issue obtaining the information. Check the message from one of the rest calls and update the database
            queryStr="select jsondata from afc where infotype='switches'"
            dbInfo=cursor.execute(queryStr)
            if "message" in hostInfo['message']:
                message=switchInfo['message']['message']
            else:
                message=switchInfo['message']
            if dbInfo > 0:           
                queryStr="update afc set message='{}' where infotype='switches'".format(message)
            else:
                # There is no AFC integration entry yet in the database, we need to insert
                queryStr="insert into afc (infotype,jsondata, message) values ('switches','','{}')".format(message)
            cursor.execute(queryStr)
        else:
            queryStr="select jsondata from afc where infotype='switches'"
            dbInfo=cursor.execute(queryStr)
            switchInfo=json.dumps(switchInfo['result'], separators=(',',':'))
            switchInfo=switchInfo.replace("'","\\'")
            try:
                if dbInfo > 0:
                    # We should only update if there are switches in the result. If not leave the database alone

                    message="Update successful"
                    queryStr="update afc set jsondata='{}', message='{}' where infotype='switches'".format(switchInfo, message)   
                    cursor.execute(queryStr)
                else:
                    message="Create switches successfully"
                    queryStr="insert into afc (infotype,jsondata, message) values ('switches','{}','{}')".format(switchInfo, message)
                    cursor.execute(queryStr)
            except Exception as e:
                print(e)
    except Exception as e:
        datacollectorlog.write('{}: {}. \n'.format(datetime.now(),e))
    cursor.close()
    datacollectorlog.close()



def afcintegrations():
    datacollectorlog = open('/var/www/html/log/collector.log', 'a')
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    try:
        url="api/integrations?configurations=true"
        integrationInfo=getRestafc(cursor,url, datacollectorlog)
        if "message" in integrationInfo:
            # There was an issue obtaining the information. Check the message from one of the rest calls and update the database
            queryStr="select jsondata from afc where infotype='integrations'"
            dbInfo=cursor.execute(queryStr)
            if dbInfo > 0:
                if "message" in integrationInfo['message']:
                    message=integrationInfo['message']['message']
                else:
                    message=integrationInfo['message']
                queryStr="update afc set message='{}' where infotype='integrations'".format(message)
                cursor.execute(queryStr)
            else:
                # There is no AFC integration entry yet in the database, we need to insert
                if "message" in hostInfo['message']:
                    message=hostInfo['message']['message']
                else:
                    message=hostInfo['message']
                queryStr="insert into afc (infotype,jsondata, message) values ('integrations','','{}')".format(message)
                cursor.execute(queryStr)
        else:
            queryStr="select jsondata from afc where infotype='integrations'"
            dbInfo=cursor.execute(queryStr)
            if dbInfo > 0:
                queryStr="update afc set jsondata='{}', message='' where infotype='integrations'".format(json.dumps(integrationInfo['result']))
                cursor.execute(queryStr)
            else:
                message="Create integrations successfully"
                queryStr="insert into afc (infotype,jsondata, message) values ('integrations','{}','')".format(json.dumps(integrationInfo['result']))
                cursor.execute(queryStr)
    except Exception as e:
        datacollectorlog.write('{}: {}. \n'.format(datetime.now(),e))
    cursor.close()
    datacollectorlog.close()



def afcvmwareinventory():
    datacollectorlog = open('/var/www/html/log/collector.log', 'a')
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    # Obtain the host information, we should only obtain the information if the VMWare integration is enabled
    try:
        vmInfo=[]
        url="api/hosts?all_data=true"
        hostInfo=getRestafc(cursor,url,datacollectorlog)
        # Obtain the switch information
        url="api/switches"
        switchInfo=getRestafc(cursor,url, datacollectorlog)
        url="api/fabrics"                                   
        fabricInfo=getRestafc(cursor,url, datacollectorlog)
        # The idea is to create a hierarchy   vsphere-host-nic-portgroup-vswitch-arubaswitch
        # This makes it easier to navigate and create a topology per vm
        try:
            for items in hostInfo['result']:
                # There are different vSpheres. Go through each vSphere
                vsphereConstruct={}
                vsphereConstruct['vsphere'] = items['name']
                vsphereConstruct['vSphere_uuid'] = items ['associated_objects'][items['base_object_vendor']]['vsphere_uuid']
                vsphereConstruct['hosts']=[]
                vmConstruct = {}
                for items2 in items['vms']:
                    vmConstruct['name']= items2['name']
                    vmConstruct['power_state']= items2['power_state']
                    vmConstruct['uuid']= items2['associated_objects'][items['base_object_vendor']]['uuid']
                    vmConstruct['nics']=[]
                    nicConstruct = {}
                    for items3 in items2['nics']:
                        nicConstruct['uuid']=items3['associated_objects'][items['base_object_vendor']]['uuid']
                        nicConstruct['name']=items3['name']
                        nicConstruct['mac_address']=items3['associated_objects'][items['base_object_vendor']]['mac_address']
                        nicConstruct['ip_address']=items3['associated_objects'][items['base_object_vendor']]['ip_address']
                        nicConstruct['vni']=items3['associated_objects'][items['base_object_vendor']]['vni']
                        nicConstruct['vtep']=items3['associated_objects'][items['base_object_vendor']]['vtep']
                        nicConstruct['vlan']=items3['associated_objects'][items['base_object_vendor']]['vlan']
                        nicConstruct['portgroups']=[]
                        portgroupConstruct = {}
                        # Get the assigned port group(s) in the nicConstruct. The portgroup uuid is  items3['associated_objects'][items['base_object_vendor']]['portgroup_uuid']
                        # The port group information is found in the vswitches context
                        for items4 in items['vswitches']:
                            for items5 in items4['associated_objects'][items['base_object_vendor']]['portgroups']:
                                # Now check to which portgroup the vm belongs to
                                if items3['associated_objects'][items['base_object_vendor']]['portgroup_uuid']==items5['uuid']:
                                    # This portgroup is assigned to the VM
                                    portgroupConstruct['name']=items5['name']
                                    portgroupConstruct['uuid']=items5['uuid']
                                    portgroupConstruct['type']=items5['type']
                                    portgroupConstruct['vlans']=items5['vlans']
                                    vswitchConstruct={}
                                    vswitchConstruct['name']=items4['name']
                                    vswitchConstruct['uuid']=items4['associated_objects'][items['base_object_vendor']]['uuid']
                                    vswitchConstruct['type']=items4['associated_objects'][items['base_object_vendor']]['type']
                                    portgroupConstruct['vswitch']=vswitchConstruct
                                    # The vswitch is connected to a Network Interface Card. We need to go through the NIC information on the host to obtain the assigned NIC. The active_host_nic_uuids from the portgroup context
                                    # can be used to lookup the NIC information. It is also possible that there are multiple NICS (resilient link or LAG), therefore we need to iterate through the active_host_nic_uuids
                                    portgroupConstruct['vswitch']['nic']=[]
                                    pnicConstruct={}
                                    for items6 in items5['active_host_nic_uuids']:
                                        for items7 in items['nics']:
                                            if items7['associated_objects'][items['base_object_vendor']]['uuid']==items6:
                                                # Identified the NIC, add it to the NIC within the vswitch context
                                                pnicConstruct['switch_port_id']=items7['switch_port_id']
                                                pnicConstruct['connection_status']=items7['connection_status']
                                                pnicConstruct['switch_mac_address']=items7['switch_mac_address']
                                                pnicConstruct['link_speed']=items7['link_speed']
                                                pnicConstruct['name']=items7['name']
                                                pnicConstruct['mac_address']=items7['associated_objects'][items['base_object_vendor']]['mac_address']
                                                pnicConstruct['uuid']=items7['associated_objects'][items['base_object_vendor']]['uuid']
                                                pnicConstruct['switch']={}
                                                # Last step is to get the switch information that is connected to this NIC
                                                for items8 in switchInfo['result']:
                                                    if items7['switch_mac_address']==items8['mac_address']:
                                                        # Found the switch. Obtain the switch information
                                                        pnicConstruct['switch']['hostname']=items8['hostname']
                                                        pnicConstruct['switch']['mac_address']=items8['mac_address']
                                                        pnicConstruct['switch']['ip_address']=items8['ip_address']
                                                        pnicConstruct['switch']['uuid']=items8['uuid']
                                                        pnicConstruct['switch']['serial_number']=items8['serial_number']
                                                        pnicConstruct['switch']['description']=items8['description']
                                                        pnicConstruct['switch']['role']=items8['role']
                                                        # Obtain fabric membership of this switch.  items8['fabric_uuid'] is the fabric uuid
                                                        # Iterate through the fabric information
                                                        for items9 in fabricInfo['result']:
                                                            if items9['uuid']==items8['fabric_uuid']:
                                                                pnicConstruct['switch']['fabric']=items9['name']
                                                                pnicConstruct['switch']['fabric_description']=items9['description']
                                                                pnicConstruct['switch']['fabric_class']=items9['fabric_class']
                                                                pnicConstruct['switch']['fabric_uuid']=items9['uuid']
                                                            else:
                                                                pnicConstruct['switch']['fabric']=""
                                                                pnicConstruct['switch']['fabric_description']=""
                                                                pnicConstruct['switch']['fabric_class']=""
                                                                pnicConstruct['switch']['fabric_uuid']=""

                                                portgroupConstruct['vswitch']['nic'].append(pnicConstruct.copy()) 
                                                portgroupConstruct['vswitch']['nic'] = [i for n, i in enumerate(portgroupConstruct['vswitch']['nic']) if i not in portgroupConstruct['vswitch']['nic'][n + 1:]]
                                    nicConstruct['portgroups'].append(portgroupConstruct.copy())
                                    # And we can assign the vSwitch from this context
                    vmConstruct['nics'].append(nicConstruct.copy())
                    vsphereConstruct['hosts'].append(vmConstruct.copy())
                vmInfo.append(vsphereConstruct.copy())
        except:
            # There was an issue obtaining the information. Check the message from one of the rest calls and update the database
            if "message" in hostInfo:
                queryStr="select jsondata from afc where infotype='vmwareinventory'"
                dbInfo=cursor.execute(queryStr)
                if dbInfo > 0:
                    dbInfo = cursor.fetchall()
                    # Maintain the existing information and update the message
                    vmInfo=dbInfo[0]['jsondata']
                    if isinstance(vmInfo,str):
                        vmInfo=json.loads(vmInfo)
                    if "message" in hostInfo['message']:
                        message=hostInfo['message']['message']
                    else:
                        message=hostInfo['message']
                    message={'message': hostInfo['message']}   
                    queryStr="update afc set jsondata='{}', message='{}' where infotype='vmwareinventory'".format(json.dumps(vmInfo), message)
                    cursor.execute(queryStr)
                else:
                    # There is no AFC vmwareinventory entry yet in the database, we need to insert
                    vmInfo=[]
                    if "message" in hostInfo['message']:
                        message=hostInfo['message']['message']
                    else:
                        message=hostInfo['message']
                    queryStr="insert into afc (infotype,jsondata, message) values ('vmwareinventory','{}','{}')".format(json.dumps(vmInfo), message)
                    cursor.execute(queryStr)
        if not "message" in hostInfo:
            queryStr="select jsondata from afc where infotype='vmwareinventory'"
            dbInfo=cursor.execute(queryStr)
            if dbInfo > 0:
                queryStr="update afc set jsondata='{}', message='' where infotype='vmwareinventory'".format(json.dumps(vmInfo))
                cursor.execute(queryStr)
            else:
                queryStr="insert into afc (infotype,jsondata, message) values ('vmwareinventory','{}','')".format(json.dumps(vmInfo))
                cursor.execute(queryStr)
    except Exception as e:
        datacollectorlog.write('{}: {}. \n'.format(datetime.now(),e))
    cursor.close()
    datacollectorlog.close()


def afcauditinfo():
    datacollectorlog = open('/var/www/html/log/collector.log', 'a')
    dbconnection=pymysql.connect(host='localhost',user='aruba',password='ArubaRocks',db='aruba', autocommit=True)
    cursor=dbconnection.cursor(pymysql.cursors.DictCursor)
    # First thing to check is whether there are already entries in the database. If not, we need to obtain the audit information and store this in the database
    # If there are already entries in the database, we need to obtain the latest entry (the UUID) and we can then query AFC for all the events that happened after this UUID
    queryStr="select COUNT(*) as rowcount from afcaudit"
    cursor.execute(queryStr)
    result = cursor.fetchall()
    if result[0]['rowcount']==0:
        # There is no information in the database yet. Obtain the audit information from AFC and store the entries in the database
        url="api/audits"
        auditInfo=getRestafc(cursor,url, datacollectorlog)
        if "result" in auditInfo:
            sortedInfo=sorted(auditInfo['result'], key=lambda d: d['log_date'])
            for items in sortedInfo:
                try:
                    description= items['description'].replace("'", "\\'")
                    queryStr="insert into afcaudit (uuid,record_type,stream_id,description,severity,jsondata,log_date) values ('{}','{}','{}','{}','{}','{}',{})".format(items['uuid'],items['record_type'],items['stream_id'],description,items['severity'],json.dumps(items['data']),items['log_date'])
                    cursor.execute(queryStr)
                except Exception as e:
                    datacollectorlog.write('{}: {}. \n'.format(datetime.now()),e)
    else:
        # We need to obtain the UUID of the latest entry and perform the call using the UUID as last entry
        queryStr="SELECT id,uuid FROM afcaudit WHERE id=(SELECT MAX(id) FROM afcaudit)"
        cursor.execute(queryStr)
        result=cursor.fetchall()
        url="api/audits/{}".format(result[0]['uuid'])
        auditInfo=getRestafc(cursor,url, datacollectorlog)
        # If there is a result, this means that there is an audit entry with this uuid. We now need to check whether there are any new audits since this one.
        if "count" in auditInfo:
            if auditInfo['count']==1:
                url="api/audits?after={}".format(result[0]['uuid'])
                auditInfo=getRestafc(cursor,url, datacollectorlog)
                if "result" in auditInfo:
                    sortedInfo=sorted(auditInfo['result'], key=lambda d: d['log_date'])
                    for items in sortedInfo:
                        try:
                            description= items['description'].replace("'", "\\'")
                            queryStr="insert into afcaudit (uuid,record_type,stream_id,description,severity,jsondata,log_date) values ('{}','{}','{}','{}','{}','{}',{})".format(items['uuid'],items['record_type'],items['stream_id'],description,items['severity'],json.dumps(items['data']),items['log_date'])
                            cursor.execute(queryStr)
                        except TypeError:
                            datacollectorlog.write('{}: Type error issue obtaining information . \n'.format(datetime.now()))
                        except Exception as e:
                            datacollectorlog.write('{}: {}. \n'.format(datetime.now()),e)
        else:
            # For some strange reason the UUID was not found (could be that AFC has been initialized). If this is the case, obtain all (well max. 1000) entries in this query and store
            url="api/audits"
            auditInfo=getRestafc(cursor,url, datacollectorlog)
            if "result" in auditInfo:
                try:
                    sortedInfo=sorted(auditInfo['result'], key=lambda d: d['log_date'])
                    for items in sortedInfo:
                        try:
                            description= items['description'].replace("'", "\\'")
                            queryStr="insert into afcaudit (uuid,record_type,stream_id,description,severity,jsondata,log_date) values ('{}','{}','{}','{}','{}','{}',{})".format(items['uuid'],items['record_type'],items['stream_id'],description,items['severity'],json.dumps(items['data']),items['log_date'])
                            cursor.execute(queryStr)
                        except TypeError:
                            datacollectorlog.write('{}: Type error issue obtaining information . \n'.format(datetime.now()))
                        except Exception as e:
                            datacollectorlog.write('{}: {}. \n'.format(datetime.now()),e)
                except TypeError:
                    datacollectorlog.write('{}: Type error issue obtaining information . \n'.format(datetime.now()))
                except Exception as e:
                    datacollectorlog.write('{}: {}. \n'.format(datetime.now()),e)
    cursor.close()
    datacollectorlog.close()


def obtainVars(cursor, configtype):
    queryStr="select datacontent from systemconfig where configtype='{}'".format(configtype)
    cursor.execute(queryStr)
    result = cursor.fetchall()
    afcconf=result[0]
    if isinstance(afcconf,str):
        afcconf=json.loads(globalconf)
    afcconf=afcconf['datacontent']
    if isinstance(afcconf,str):
        afcconf=json.loads(afcconf)
    return afcconf


def integrationStatus(integrationInfo,integration):
    for items in integrationInfo:
        if items['name']==integration:
            # There is an integration, return True
            return True
    return False










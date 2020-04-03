# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# Generic Aruba Dynamic Segmentation Services classes

import classes.classes
import requests
sessionid = requests.Session()

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def dsservicedbAction(formresult):
    # This definition is for all the database actions for Dynamic Segmentation Services, based on the user click on the pages
    if(bool(formresult)==True):
        if(formresult['action']=="Submit service"): 
            queryStr="insert into dsservices (name,profile,policies) values ('{}','{}','{}')".format(formresult['name'],formresult['profile'],formresult['policies'])
            serviceid=classes.classes.sqlQuery(queryStr,"insert")
            # Build the list
            result=classes.classes.sqlQuery("select * from dsservices","select")
        elif  (formresult['action']=="Submit changes"):
            queryStr="update dsservices set name='{}',profile='{}', policies='{}' where id='{}'" \
                .format(formresult['name'],formresult['profile'],formresult['policies'],formresult['id'])
            classes.classes.sqlQuery(queryStr,"update")
            # Build the list
            result=classes.classes.sqlQuery("select * from dsservices","select")
        elif (formresult['action']=="Delete"):
            queryStr="delete from dsservices where id='{}'".format(formresult['id'])
            classes.classes.sqlQuery(queryStr,"delete")
            # Build the list
            result=classes.classes.sqlQuery("select * from dsservices","select")
        elif (formresult['action']=="order by name"):
            result=classes.classes.sqlQuery("select * from dsservices order by name ASC","select")
        else:
            result=classes.classes.sqlQuery("select * from dsservices","select")
    else:
        result=classes.classes.sqlQuery("select * from dsservices","select")
    return result


def getVLANinfo(mcid):
    # Obtain all VLAN ID and name information
    queryStr="select * from devices where id='{}'".format(mcid)
    mcInfo=classes.classes.sqlQuery(queryStr,"selectone")
    sysinfo=json.loads(mcInfo['sysinfo']) 
    cookie=classes.classes.loginmc(mcInfo['id'])
    # Obtain the VLAN name and ID
    if sysinfo['_global']['_switch_role']=="master":
        url="configuration/object/vlan_name_id?config_path=%2Fmd&UIDARUBA="
    else:
        url="configuration/object/vlan_name_id?UIDARUBA="
    vlanresult=classes.classes.getRESTmc(cookie,url,mcInfo['id'])
    vlanresult=vlanresult['_data']
    classes.classes.logoutmc(cookie,mcInfo['id']) 
    return vlanresult

def getVLANint(mcid, vlan):
    # Obtain VLAN interface information for the given VLAN ID
    queryStr="select * from devices where id='{}'".format(mcid)
    mcInfo=classes.classes.sqlQuery(queryStr,"selectone")
    sysinfo=json.loads(mcInfo['sysinfo'])
    cookie=classes.classes.loginmc(mcInfo['id'])
    # Obtain the roles
    if sysinfo['_global']['_switch_role']=="master":
        url="configuration/object/int_vlan?config_path=%2Fmd&filter=[{\"int_vlan.id\":{\"$eq\":[" + vlan + "]}}]&UIDARUBA="
    else:
        url="configuration/object/int_vlan?filter=[{\"int_vlan.id\":{\"$eq\":[" + vlan + "]}}]&UIDARUBA="
    vlanresult=classes.classes.getRESTmc(cookie,url,mcInfo['id'])
    vlanresult=vlanresult['_data']['int_vlan'][0]
    classes.classes.logoutmc(cookie,mcInfo['id']) 
    return vlanresult

def getVLANidname(mcid, vlan):
    # Obtain VLAN information for the given VLAN ID
    queryStr="select * from devices where id='{}'".format(mcid)
    mcInfo=classes.classes.sqlQuery(queryStr,"selectone")
    sysinfo=json.loads(mcInfo['sysinfo']) 
    cookie=classes.classes.loginmc(mcInfo['id'])
    # Obtain the VLAN name and ID
    if sysinfo['_global']['_switch_role']=="master":
        url="configuration/object/vlan_name_id?filter=[{\"vlan_name_id.vlan-ids\":{\"$eq\":[\""+ vlan + "\"]}}]&config_path=%2Fmd&UIDARUBA="
    else:
        url="configuration/object/vlan_name_id?filter=[{\"vlan_name_id.vlan-ids\":{\"$eq\":[\""+ vlan + "\"]}}]&UIDARUBA="
    vlanresult=classes.classes.getRESTmc(cookie,url,mcInfo['id'])
    vlanresult=vlanresult['_data']['vlan_name_id'][0]
    classes.classes.logoutmc(cookie,mcInfo['id']) 
    return vlanresult

def getRolesinfo(mcid):
    # Obtain all the roles from a given Mobility Controller
    queryStr="select id, description, ipaddress,sysinfo from devices where id='{}'".format(mcid)
    mcInfo=classes.classes.sqlQuery(queryStr,"selectone")
    sysinfo=json.loads(mcInfo['sysinfo'])
    cookie=classes.classes.loginmc(mcInfo['id'])
    # Obtain the roles
    if sysinfo['_global']['_switch_role']=="master":
        url="configuration/object/role?config_path=%2Fmd&UIDARUBA="
    else:
        url="configuration/object/role?UIDARUBA="
    roleresult=classes.classes.getRESTmc(cookie,url,mcInfo['id'])
    roleresult=roleresult['_data']
    classes.classes.logoutmc(cookie,mcInfo['id']) 
    return roleresult

def getRoleinfo(mcid,role):
    queryStr="select id, description, ipaddress,sysinfo from devices where id='{}'".format(mcid)
    mcInfo=classes.classes.sqlQuery(queryStr,"selectone")
    sysinfo=json.loads(mcInfo['sysinfo'])
    cookie=classes.classes.loginmc(mcInfo['id'])
    # Obtain the roles
    if sysinfo['_global']['_switch_role']=="master":
        url="configuration/object/role?config_path=%2Fmd&filter=[{\"role.rname\":{\"$eq\":[\"" + role +"\"]}}]&UIDARUBA="
    else:
        url="configuration/object/role?filter=[{\"role.rname\":{\"$eq\":[\"" + role +"\"]}}]&UIDARUBA="
    roleresult=classes.classes.getRESTmc(cookie,url,mcInfo['id'])
    roleresult=roleresult['_data']['role'][0]
    classes.classes.logoutmc(cookie,mcInfo['id']) 
    return roleresult

def getACLinfo(mcid,accname):
    aclresult={}
    queryStr="select id, description, ipaddress,sysinfo from devices where id='{}'".format(mcid)
    mcInfo=classes.classes.sqlQuery(queryStr,"selectone")
    sysinfo=json.loads(mcInfo['sysinfo'])
    cookie=classes.classes.loginmc(mcInfo['id'])
    # Obtain the roles
    if sysinfo['_global']['_switch_role']=="master":
        url="configuration/object/role?config_path=%2Fmd&filter=[{\"acl_sess.accname\":{\"$eq\":[\"" + accname + "\"]}}]&UIDARUBA="
    else:
        url="configuration/object/role?filter=[{\"acl_sess.accname\":{\"$eq\":[\"" + accname + "\"]}}]&UIDARUBA="
    aclresult=classes.classes.getRESTmc(cookie,url,mcInfo['id'])
    classes.classes.logoutmc(cookie,mcInfo['id']) 
    return aclresult

def getProfile():
    queryStr="select id, name, primarycontroller from dsprofiles"
    profileresult=classes.classes.sqlQuery(queryStr,"select")
    return profileresult

def getService(id):
    queryStr="select * from dsservices where id='{}'".format(id)
    #Get Service information
    serviceInfo=classes.classes.sqlQuery(queryStr,"selectone")
    # Get Profile information
    queryStr="select * from dsprofiles where id='{}'".format(serviceInfo['profile'])
    profileInfo=classes.classes.sqlQuery(queryStr,"selectone")
    # Get ClearPass information
    queryStr="select ipaddress,username,password,secinfo from devices where id='{}'".format(profileInfo['clearpass'])
    clearpassInfo=classes.classes.sqlQuery(queryStr,"selectone")
    # Get primary controller information
    queryStr="select ipaddress,username,password from devices where id='{}'".format(profileInfo['primarycontroller'])
    primarycontrollerInfo=classes.classes.sqlQuery(queryStr,"selectone")
    # Get backup controller information, if the backup controller entry exists
    if profileInfo['backupcontroller']:
        queryStr="select ipaddress,username,password from devices where id='{}'".format(profileInfo['backupcontroller'])
        backupcontrollerInfo=classes.classes.sqlQuery(queryStr,"selectone")
    else:
        backupcontrollerInfo={}
    #Now build the command structure for provisining the switches
    workflow=[]
    workflow.append("radius-server host {} dyn-authorization".format(clearpassInfo['ipaddress']))
    workflow.append("radius-server host {} time-window 0".format(clearpassInfo['ipaddress']))
    workflow.append("radius-server host {} clearpass key {}".format(clearpassInfo['ipaddress'],profileInfo['radiussecret']))
    workflow.append("radius-server cppm identity {} key {}".format(profileInfo['duradmin'],profileInfo['durpassword']))
    workflow.append("timesync ntp")
    workflow.append("ntp unicast")
    workflow.append("ntp server {} iburst".format(profileInfo['ntpserver']))
    workflow.append("ntp enable")
    workflow.append("tunneled-node-server controller-ip {}".format(primarycontrollerInfo['ipaddress']))
    # Is there a backup controller configured?
    if(backupcontrollerInfo):
        workflow.append("tunneled-node-server backup-controller-ip {}".format(backupcontrollerInfo['ipaddress']))
    workflow.append("tunneled-node-server mode role-based reserved-vlan 4091")
    workflow.append("aaa authorization user-role enable download")
    #Which aaa methods are configured (MAC Auth/Dot1x)
    if profileInfo['dot1x']==1:
        workflow.append("aaa authentication port-access eap-radius")
        workflow.append("aaa port-access authenticator {}".format(profileInfo['ports']))
        workflow.append("aaa port-access authenticator {} client-limit {}".format(profileInfo['ports'],profileInfo['dot1xlimit']))
        workflow.append("aaa port-access authenticator active")
    if profileInfo['macauth']==1:
        workflow.append("aaa port-access mac-based {}".format(profileInfo['ports']))
        workflow.append("aaa port-access mac-based {} addr-limit {}".format(profileInfo['ports'],profileInfo['maclimit']))
        workflow.append("aaa port-access mac-based {}".format(profileInfo['ports']))
    serviceInfo={"workflow":workflow,"memberInfo":json.loads(profileInfo['members']),"policies": serviceInfo['policies']}
    return json.dumps(serviceInfo)

def provisionSwitch(deviceid,workflow):
    #log into the switch and then issue the workflow commands
    queryStr="select ipaddress, description from devices where id='{}'".format(deviceid)
    deviceInfo=classes.classes.sqlQuery(queryStr,"selectone")
    response=[[deviceInfo['ipaddress'],deviceInfo['description']]]
    header=classes.classes.loginswitch(deviceid)
    # Now issue the REST commands
    for items in workflow:
        try:
            result=classes.classes.anycliProvision(items,deviceInfo['ipaddress'],header)
           # If there is an error, we should log this and show it
            if result['status']=="CCS_FAILURE":
                response.append([result['cmd'],result['error_msg']])
        except:
            pass
    classes.classes.logoutswitch(header,deviceid)
    return response

    
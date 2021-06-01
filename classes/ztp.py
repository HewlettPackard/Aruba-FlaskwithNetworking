# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# Generic ZTP classes

import classes.classes
import requests
import os
from jinja2 import Template, Environment
sessionid = requests.Session()

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ztpdevicedbAction(formresult):
    # This definition is for all the devices database actions for ZTP
    globalsconf=classes.classes.globalvars()
    searchAction="None"
    constructQuery=""
    ztpvlan={}
    if(bool(formresult)==True):
        # Check if IPAM is enabled, if it is and the gateway and netmask value exists (ipamgateway and ipamnetmask), we have to assign it to the appropriate vars
        if "ipamenabled" in globalsconf:
            if 'ipamgateway' in formresult:
                gateway=formresult['ipamgateway']
            if 'ipamnetmask' in formresult:
                netmask=formresult['ipamnetmask']
        else:
            if 'gateway' in formresult:
                gateway=formresult['gateway']
            else:
                gateway="0.0.0.0"
            if 'netmask' in formresult:
                netmask=formresult['netmask']
            else:
                netmask="0"
        if 'softwareimage' in formresult:
            softwareimage=formresult['softwareimage']
        else:
            softwareimage=0
        if "vrf" in formresult:
            if formresult['vrf']=="":
                vrf="0"
            else:
                vrf=formresult['vrf']
        else:
            vrf="0"
        if 'template' in formresult:
            template=formresult['template']
        else:
            template=0
        if 'enablevsf' in formresult:
            vsfenabled=1
        else:
            vsfenabled=0
        if 'vsfmember' in formresult:
            vsfmember=formresult['vsfmember']
        else:
            vsfmember=0
        if 'vsfmaster' in formresult:
            vsfmaster=formresult['vsfmaster']
        else:
            vsfmaster=0
        if 'vsfrole' in formresult:
            vsfrole=formresult['vsfrole']
        else:
            vsfrole=""
        if 'switchtype' in formresult:
            switchtype=formresult['switchtype']
        else:
            switchtype=0
        if 'link1' in formresult:
            link1=formresult['link1']
        else:
            link1=""
        if 'link2' in formresult:
            link2=formresult['link2']
        else:
            link2=""
        if 'ipamsubnet' in formresult:
            ipamsubnet=formresult['ipamsubnet']
        else:
            ipamsubnet=""
        if 'ztpdhcp' in formresult:
            gateway="0.0.0.0"
            netmask="0"
            ipaddress="0.0.0.0"
            vrf=""
            ztpdhcp=1
        else:
            ztpdhcp=0
            if "ipaddress" in formresult:
                ipaddress=formresult['ipaddress']
                if "vrf" in formresult:
                    vrf=formresult['vrf']
                else:
                    vrf="0"
        if 'uplinkVlan' in formresult:
            if formresult['uplinkVlan']!="" and (int(formresult['uplinkVlan'])>1 and int(formresult['uplinkVlan'])<4093):
                ztpvlan['uplinkVlan']=formresult['uplinkVlan']
            else:
               ztpvlan['uplinkVlan']="1"
        else:
            ztpvlan['uplinkVlan']="1"
        if 'taggedVlan' in formresult:
            ztpvlan['taggedVlan']=1
        else:
            ztpvlan['taggedVlan']=0
        try:
            formresult['pageoffset']
            pageoffset=formresult['pageoffset']
        except:
            pageoffset=0
        if(formresult['action']=="Submit device"):
            queryStr="insert into ztpdevices (name,macaddress,ipamsubnet,ipaddress,netmask,gateway,vrf,softwareimage,template,templateparameters,vsfenabled,vsfrole,vsfmember,vsfmaster,switchtype,link1,link2, \
            enableztp, ztpstatus,ztpdhcp,adminuser,adminpassword,ztpvlan) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','Disabled','{}','admin','{}','{}')".format(formresult['name'],formresult['macaddress'], \
            ipamsubnet,ipaddress,netmask,gateway,vrf,softwareimage,template,formresult['parameterValues'], vsfenabled,vsfrole,vsfmember,vsfmaster,switchtype,link1,link2,0,ztpdhcp,classes.classes.encryptPassword(globalsconf['secret_key'],globalsconf['ztppassword']),json.dumps(ztpvlan))
            deviceid=classes.classes.sqlQuery(queryStr,"insert")
        elif  (formresult['action']=="Submit changes"):
            queryStr="update ztpdevices set name='{}', macaddress='{}', ipamsubnet='{}',ipaddress='{}',netmask='{}', gateway='{}', vrf='{}', softwareimage='{}', template='{}', templateparameters='{}', \
            vsfenabled='{}', vsfrole='{}', vsfmember='{}',vsfmaster='{}',switchtype='{}', link1='{}', link2='{}', ztpdhcp='{}', ztpvlan='{}' where id='{}' ".format(formresult['name'],formresult['macaddress'], ipamsubnet, ipaddress, \
            netmask,gateway,vrf,softwareimage,template,formresult['parameterValues'],vsfenabled,vsfrole, \
            vsfmember,vsfmaster,int(switchtype),link1,link2,ztpdhcp,json.dumps(ztpvlan),formresult['deviceid'])
            classes.classes.sqlQuery(queryStr,"update")
        elif (formresult['action']=="Delete"):
            queryStr="delete from ztpdevices where id='{}'".format(formresult['deviceid'])
            classes.classes.sqlQuery(queryStr,"delete")
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""    
        if formresult['searchName'] or formresult['searchMacaddress'] or formresult['searchIpaddress'] or formresult['searchGateway']  or formresult['searchVrf']  or formresult['searchImage'] or formresult['searchTemplate'] or formresult['searchuplinkVlan']:
            constructQuery= " where "
        if formresult['searchName']:
            constructQuery += " name like'%" + formresult['searchName'] + "%' AND "
        if formresult['searchMacaddress']:
            constructQuery += " macaddress like'%" + formresult['searchMacaddress'] + "%' AND "
        if formresult['searchIpaddress']:
            constructQuery += " ipaddress like '%" + formresult['searchIpaddress'] + "%' AND "
        if formresult['searchGateway']:
            constructQuery += " gateway like'%" + formresult['searchGateway'] + "%' AND "
        if formresult['searchVrf']:
            constructQuery += " vrf='" + formresult['searchVrf'] + "' AND "
        if formresult['searchImage']:
            constructQuery += " softwareimage='" + formresult['searchImage'] + "' AND "
        if formresult['searchTemplate']:
            constructQuery += " template='" + formresult['searchTemplate'] + "' AND "
        if formresult['searchuplinkVlan']:
            constructQuery += " ztpvlan like '{\"uplinkVlan\": \"" + formresult['searchuplinkVlan'] + "%' AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from ztpdevices " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=formresult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from ztpdevices " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from ztpdevices"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=25
        pageoffset=0
        queryStr="select * from ztpdevices LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}


def ztptemplatedbAction(formresult):
    # This definition is for all the template database actions for ZTP
    globalsconf=classes.classes.globalvars()
    searchAction="None"
    constructQuery=""
    if(bool(formresult)==True): 
        try:
            formresult['pageoffset']
            pageoffset=formresult['pageoffset']
        except:
            pageoffset=0
        if(formresult['action']=="Submit template"):
            queryStr="insert into ztptemplates (name,description,template) values ('{}','{}','{}')".format(formresult['name'],formresult['description'], formresult['template'])
            templateid=classes.classes.sqlQuery(queryStr,"insert")
        elif (formresult['action']=="Submit changes"):
            queryStr="update ztptemplates set name='{}',description='{}',template='{}' where id='{}' "\
            .format(formresult['name'],formresult['description'],formresult['template'],formresult['templateid'])
            classes.classes.sqlQuery(queryStr,"update")
        elif (formresult['action']=="Delete"):
            queryStr="delete from ztptemplates where id='{}'".format(formresult['templateid'])
            classes.classes.sqlQuery(queryStr,"delete")
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""    
        if formresult['searchName'] or formresult['searchDescription']:
            constructQuery= " where "
        if formresult['searchName']:
            constructQuery += " name like'%" + formresult['searchName'] + "%' AND "
        if formresult['searchDescription']:
            constructQuery += " description like '%" + formresult['searchDescription'] + "%' AND "

        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from ztptemplates " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)

        totalentries=navResult['totalentries']
        entryperpage=formresult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from ztptemplates " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from ztptemplates"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=25
        pageoffset=0
        queryStr="select * from ztptemplates LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}


def ztpActivate(formresult):
    sysvars=classes.classes.globalvars()
    queryStr="select * from ztpdevices where id='{}'".format(formresult['id'])
    deviceResult=classes.classes.sqlQuery(queryStr,"selectone")
    # If ZTP DHCP is disabled, the init configuration file has to be generated. Else, the minimal initfile will be used.
    if deviceResult['ztpdhcp']==0:
        # Extract the VLAN ID from the uplinkVlan value
        if deviceResult['vrf']=="default":
            ztpvlan=json.loads(deviceResult['ztpvlan'])
            with open('bash/defaultztp.cfg', 'r') as myfile:
                data = myfile.read()
            template = Template(data)
            initConfig = template.render(switchtype=deviceResult['switchtype'],vlan=ztpvlan['uplinkVlan'],tagged=ztpvlan['taggedVlan'], ipaddress=deviceResult['ipaddress'], netmask=deviceResult['netmask'], gateway=deviceResult['gateway'])
        else:
            with open('bash/mgmtztp.cfg', 'r') as myfile:
                data = myfile.read()         
            template = Template(data)
            initConfig = template.render(ipaddress=deviceResult['ipaddress'], netmask=deviceResult['netmask'], gateway=deviceResult['gateway']) 
        outFileName="/home/tftpboot/" + deviceResult['macaddress'] + ".cfg"
        outFile=open(outFileName, "w")
        outFile.write(initConfig)
        outFile.close()
    # Also, initialize the adminpassword
    queryStr="update ztpdevices set adminpassword='{}',enableztp='1',ztpstatus='Enabled, start initialization' where id='{}'".format(classes.classes.encryptPassword(sysvars['secret_key'],sysvars['ztppassword']),formresult['id'])
    classes.classes.sqlQuery(queryStr,"update")
    response=["ZTP Provisioning enabled",formresult['id']]
    return response

def ztpDeactivate(formresult):
    queryStr="update ztpdevices set enableztp='0',ztpstatus='Disabled' where id='{}'".format(formresult['id'])
    classes.classes.sqlQuery(queryStr,"update")
    filename="/home/tftpboot/" + formresult['macaddress'] + ".cfg"
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except OSError as e:
            print (e.filename,e.strerror)
    response=["ZTP Provisioning disabled",formresult['id']]
    return response

def verifyCredentials(id,username,password, sysvars):
    # Obtain the switch information, like IP address
    sessionid=requests.Session()
    queryStr="select * from ztpdevices where id='{}'".format(id)
    deviceInfo=classes.classes.sqlQuery(queryStr,"selectone")
    baseurl="https://{}/rest/v1/".format(deviceInfo['ipaddress'])
    url="system/users?attributes=user_group&depth=2&filter=name%3A" + username
    credentials={'username': username,'password': password }
    encpassword=classes.classes.encryptPassword(sysvars['secret_key'], password)
    try:
        response=sessionid.post(baseurl + "login", params=credentials, verify=False, timeout=5)
        if response.status_code==200:
            try:
                response = sessionid.get(baseurl + url, verify=False, timeout=5)
                response=json.loads(response.content) 
                # Check if the user belongs to the administrative user-group
                if response[0]['user_group']['name']=="administrators":
                    # We are good to go. Change the status of the ztpdevice to 91 (remove the ztp user)
                    # In addition, add the admin user to the ztpdevice database so that we can continue accessing the switch
                    queryStr="update ztpdevices set adminuser='{}', adminpassword='{}', enableztp='91', ztpstatus='Validation is successful, proceeding with process' where id='{}'".format(username,encpassword,id)
                    classes.classes.sqlQuery(queryStr,"selectone")
                    status=["Validation is successful, proceeding with process",id]
                else:
                    status=["Validation is not successful. Verify your credentials",id]
            except:
                sessionid.post(baseurl + "logout", verify=False, timeout=5)
                # print("Error obtaining response from get call")
                status=["Unable to validate, please verify your credentials",id]
                return status
            sessionid.post(baseurl + "logout", verify=False, timeout=5)
            return status
        else:
            return ["Unable to verify credentials. Retrying",id]
    except:
        return ["Unable to verify credentials. Retrying",id]

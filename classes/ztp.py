# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# Generic ZTP classes

import classes.classes
import requests
import os
from jinja2 import Template
sessionid = requests.Session()

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    
def ztpprofiledbAction(formresult):
    # This definition is for all the profiles database actions for ZTP
    globalsconf=classes.classes.globalvars()
    searchAction="None"
    constructQuery=""
    if(bool(formresult)==True): 
        try:
            formresult['pageoffset']
            pageoffset=formresult['pageoffset']
        except:
            pageoffset=0
        if(formresult['action']=="Submit profile"):
            queryStr="insert into ztpprofiles (name,username,password,vrf,dns) values \
            ('{}','{}','{}','{}','{}')".format(formresult['name'],formresult['username'], \
            classes.classes.encryptPassword(globalsconf['secret_key'], formresult['password']),formresult['vrf'],formresult['dns'])
            profileid=classes.classes.sqlQuery(queryStr,"insert")
        elif  (formresult['action']=="Submit changes"):
            queryStr="update ztpprofiles set name='{}',username='{}',password='{}', vrf='{}', dns='{}' where id='{}' "\
            .format(formresult['name'],formresult['username'],classes.classes.encryptPassword(globalsconf['secret_key'], formresult['password']),formresult['vrf'],formresult['dns'],formresult['profileid'])
            classes.classes.sqlQuery(queryStr,"update")
        elif (formresult['action']=="Delete"):
            queryStr="delete from ztpprofiles where id='{}'".format(formresult['profileid'])
            classes.classes.sqlQuery(queryStr,"delete")
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""    
        if formresult['searchName'] or formresult['searchVRF'] or formresult['searchDNS']:
            constructQuery= " where "
        if formresult['searchName']:
            constructQuery += " name like'%" + formresult['searchName'] + "%' AND "
        if formresult['searchVRF']:
            constructQuery += " vrf like '%" + formresult['searchVRF'] + "%' AND "
        if formresult['searchDNS']:
            constructQuery += " dns like'%" + formresult['searchDNS'] + "%' AND "

        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from ztpprofiles " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)

        totalentries=navResult['totalentries']
        entryperpage=formresult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from ztpprofiles " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from ztpprofiles"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=25
        pageoffset=0
        queryStr="select * from ztpprofiles LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}

def ztpdevicedbAction(formresult):
    # This definition is for all the devices database actions for ZTP
    globalsconf=classes.classes.globalvars()
    searchAction="None"
    constructQuery=""
    if(bool(formresult)==True):
        # Check if IPAM is enabled, if it is and the gateway and netmask value exists (ipamgateway and ipamnetmask), we have to assign it to the appropriate vars
        if globalsconf['ipamenabled']:
            if 'ipamgateway' in formresult:
                gateway=formresult['ipamgateway']
            if 'ipamnetmask' in formresult:
                netmask=formresult['ipamnetmask']
        else:
            if 'gateway' in formresult:
                gateway=formresult['gateway']
            if 'netmask' in formresult:
                netmask=formresult['netmask']
        if 'softwareimage' in formresult:
            softwareimage=formresult['softwareimage']
        else:
            softwareimage=0
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
        
        try:
            formresult['pageoffset']
            pageoffset=formresult['pageoffset']
        except:
            pageoffset=0
        if(formresult['action']=="Submit device"):
            queryStr="insert into ztpdevices (name,macaddress,ipamsubnet,ipaddress,netmask,gateway,profile,softwareimage,template,templateparameters,vsfenabled,vsfrole,vsfmember,vsfmaster,switchtype,link1,link2, \
            enableztp, ztpstatus) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','Disabled')".format(formresult['name'],formresult['macaddress'], \
            ipamsubnet,formresult['ipaddress'],netmask,gateway,formresult['profile'],softwareimage,template,formresult['parameterValues'], \
            vsfenabled,vsfrole,vsfmember,vsfmaster,switchtype,link1,link2,0,'Disabled')
            deviceid=classes.classes.sqlQuery(queryStr,"insert")
        elif  (formresult['action']=="Submit changes"):
            queryStr="update ztpdevices set name='{}', macaddress='{}', ipamsubnet='{}',ipaddress='{}',netmask='{}', gateway='{}', profile='{}', softwareimage='{}', template='{}', templateparameters='{}', \
            vsfenabled='{}', vsfrole='{}', vsfmember='{}',vsfmaster='{}',switchtype='{}', link1='{}', link2='{}' where id='{}' ".format(formresult['name'],formresult['macaddress'], ipamsubnet, formresult['ipaddress'], \
            netmask,gateway,formresult['profile'],softwareimage,template,formresult['parameterValues'],vsfenabled,vsfrole, \
            vsfmember,vsfmaster,int(switchtype),link1,link2,formresult['deviceid'])
            classes.classes.sqlQuery(queryStr,"update")
        elif (formresult['action']=="Delete"):
            queryStr="delete from ztpdevices where id='{}'".format(formresult['deviceid'])
            classes.classes.sqlQuery(queryStr,"delete")
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""    
        if formresult['searchName'] or formresult['searchMacaddress'] or formresult['searchIpaddress'] or formresult['searchGateway']  or formresult['searchProfile']  or formresult['searchImage']   or formresult['searchTemplate']:
            constructQuery= " where "
        if formresult['searchName']:
            constructQuery += " name like'%" + formresult['searchName'] + "%' AND "
        if formresult['searchMacaddress']:
            constructQuery += " macaddress like'%" + formresult['searchMacaddress'] + "%' AND "
        if formresult['searchIpaddress']:
            constructQuery += " ipaddress like '%" + formresult['searchIpaddress'] + "%' AND "
        if formresult['searchGateway']:
            constructQuery += " gateway like'%" + formresult['searchGateway'] + "%' AND "
        if formresult['searchProfile']:
            constructQuery += " profile='" + formresult['searchProfile'] + "' AND "
        if formresult['searchImage']:
            constructQuery += " softwareimage='" + formresult['searchImage'] + "' AND "
        if formresult['searchTemplate']:
            constructQuery += " template='" + formresult['searchTemplate'] + "' AND "

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
    # Obtain ZTP profile information
    queryStr="select id, name from ztpprofiles"
    profileResult=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'profileResult': profileResult, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}

def ztpimagedbAction(formresult, filename, message):
    # This definition is for all the images database actions for ZTP
    globalsconf=classes.classes.globalvars()
    searchAction="None"
    constructQuery=""
    if(bool(formresult)==True): 
        try:
            formresult['pageoffset']
            pageoffset=formresult['pageoffset']
        except:
            pageoffset=0
        if(formresult['action']=="Submit image" and message==""):
            queryStr="insert into ztpimages (name,devicefamily,filename,version) values ('{}','{}','{}','{}')".format(formresult['name'],formresult['devicefamily'], filename, formresult['version'])
            imageid=classes.classes.sqlQuery(queryStr,"insert")
        elif (formresult['action']=="Submit changes"):
            if filename!="":
                imagename=filename
            else:
                imagename=formresult['filename']
            queryStr="update ztpimages set name='{}',devicefamily='{}',filename='{}', version='{}', filename='{}' where id='{}' "\
            .format(formresult['name'],formresult['devicefamily'], filename,formresult['version'],imagename,formresult['imageid'])
            classes.classes.sqlQuery(queryStr,"update")
        elif (formresult['action']=="Delete"):
            queryStr="delete from ztpimages where id='{}'".format(formresult['imageid'])
            classes.classes.sqlQuery(queryStr,"delete")
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""    
        if formresult['searchName'] or formresult['searchDevicefamily'] or formresult['searchVersion']:
            constructQuery= " where "
        if formresult['searchName']:
            constructQuery += " name like'%" + formresult['searchName'] + "%' AND "
        if formresult['searchDevicefamily']:
            constructQuery += " devicefamily like '%" + formresult['searchDevicefamily'] + "%' AND "
        if formresult['searchVersion']:
            constructQuery += " version like'%" + formresult['searchVersion'] + "%' AND "

        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from ztpimages " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)

        totalentries=navResult['totalentries']
        entryperpage=formresult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from ztpimages " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from ztpimages"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=5
        pageoffset=0
        queryStr="select * from ztpimages LIMIT {} offset {}".format(entryperpage,pageoffset)
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
    queryStr="select * from ztpprofiles where id='{}'".format(deviceResult['profile'])
    profileResult=classes.classes.sqlQuery(queryStr,"selectone")
    with open('bash/initztp.cfg', 'r') as myfile:
        data = myfile.read()
    profileResult['password']=classes.classes.decryptPassword(sysvars['secret_key'],profileResult['password'])
    template = Template(data)
    initConfig = template.render(username=profileResult['username'], password=profileResult['password'], vrf=profileResult['vrf'], ipaddress=deviceResult['ipaddress'], netmask=deviceResult['netmask'], gateway=deviceResult['gateway'])

    outFileName="/home/tftpboot/" + deviceResult['macaddress'] + ".cfg"
    outFile=open(outFileName, "w")
    outFile.write(initConfig)
    outFile.close()

    queryStr="update ztpdevices set enableztp='1',ztpstatus='Enabled, start initialization' where id='{}'".format(formresult['id'])
    classes.classes.sqlQuery(queryStr,"update")
    return "ZTP Provisioning enabled"

def ztpDeactivate(formresult):
    queryStr="update ztpdevices set enableztp='0',ztpstatus='Disabled' where id='{}'".format(formresult['id'])
    classes.classes.sqlQuery(queryStr,"update")
    filename="/home/tftpboot/" + formresult['macaddress'] + ".cfg"
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except OSError as e:
            print (e.filename,e.strerror)
    return "ZTP Provisioning disabled"

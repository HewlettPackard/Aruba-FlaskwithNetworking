# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

from flask import current_app, Blueprint, request, json, redirect, render_template
import os
from urllib.parse import quote
from jinja2 import Template, Environment, meta
ztp = Blueprint('ztp', __name__)

from datetime import datetime


ALLOWED_EXTENSIONS = set(['swi','SWI'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import classes.classes as classes

@ztp.route("/ztpdevice", methods=['GET','POST'])
def ztpdevice ():
    authOK=classes.checkAuth("ztpdeviceaccess","submenu")
    parameterValues={}
    link1=[]
    link2=[]
    formresult=""
    if authOK!=0:
        sysvars=classes.globalvars()
        if request.form:
            formresult=request.form.to_dict()
            # If there are template parameters in the formresult, we need to convert those and get them into a proper dictionary because Python does not really understand form array submission
            for key in request.form.keys():
                for value in request.form.getlist(key):
                    if "parameterValues" in key: 
                        parameterKey=(key[key.find('[')+len('['):key.rfind(']')])
                        parameterValues.update( {parameterKey : value} )
                    elif "link1" in key:
                        link1.append(quote(value,safe=''))
                    elif "link2" in key:
                        link2.append(quote(value,safe=''))
            formresult.update( {'link1' : json.dumps(link1)} )
            formresult.update( {'link2' : json.dumps(link2)} )
            formresult.update( {'parameterValues' : json.dumps(parameterValues)} )
        result=classes.ztpdevicedbAction(formresult)
        # And collect all the different ztp status information
        queryStr="select distinct ztpstatus from ztpdevices"
        ztpstatusInfo=classes.sqlQuery(queryStr,"select")
        queryStr="select id, name, filename from ztpimages"
        imageResult=classes.sqlQuery(queryStr,"select")
        queryStr="select id, name from ztptemplates"
        templateResult=classes.sqlQuery(queryStr,"select")
        # Also need to check whether the IPAM is reachable. If not, we have to disable some buttons on the forms
        if "ipamenabled" in sysvars:
            # IPAM is enabled. Check whether IPAM is online
            if sysvars['ipamsystem']=="PHPIPAM":
                info={'phpipamauth': sysvars['phpipamauth'],'ipamipaddress':sysvars['ipamipaddress'],'phpipamappid':sysvars['phpipamappid'],'ipamuser':sysvars['ipamuser'],'ipampassword':sysvars['ipampassword']}
                ipamstatus=classes.checkPhpipam(info)
            elif sysvars['ipamsystem']=="Infoblox":
                info={'ipamipaddress':sysvars['ipamipaddress'],'ipamuser':sysvars['ipamuser'],'ipampassword':sysvars['ipampassword']}
                ipamstatus=classes.checkInfoblox(info)
            else:
                ipamstatus="Online"
        else:
            ipamstatus="Online"
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("ztpdevice.html",result=result['result'],formresult=formresult,imageResult=imageResult, templateResult=templateResult, ipamstatus=ipamstatus, ztpstatusInfo=ztpstatusInfo, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@ztp.route("/ztptemplate", methods=['GET','POST'])
def ztptemplate ():
    authOK=classes.checkAuth("ztptemplateaccess","submenu")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant device information from the database
        result=classes.ztptemplatedbAction(formresult)
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("ztptemplate.html",result=result['result'],formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@ztp.route("/ztpimage", methods=['GET','POST'])
def ztpimage ():
    authOK=classes.checkAuth("ztpdeviceaccess","submenu")
    message=""
    filename=""
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        if formresult:
            if formresult['action']=="Submit image" or formresult['action']=="Submit changes":
                # check if the post request has the file part
                if request.files['softwareimage']:
                    file = request.files['softwareimage']
                    if file.filename == '':
                        message='No file selected for uploading'
                    if file and allowed_file(file.filename):
                        file.save(os.path.join('/var/www/html/images/', file.filename))
                        message=''
                        filename=file.filename
                    else:
                        message='Allowed file type is swi'
            # Obtain the relevant device information from the database
            result=classes.ztpimagedbAction(formresult,filename,message)
        else:
            # Obtain the relevant device information from the database
            result=classes.ztpimagedbAction(formresult,'','')
        if authOK['hasaccess']==True:
            authOK['hasaccess']="true"
            return render_template("ztpimage.html",result=result['result'], formresult=formresult, totalentries=int(result['totalentries']),pageoffset=int(result['pageoffset']),entryperpage=int(result['entryperpage']), authOK=authOK, sysvars=sysvars)
        else:
            return render_template("noaccess.html",authOK=authOK, sysvars=sysvars)
    else:
        return render_template("login.html")

@ztp.route("/ztpdeviceInfo", methods=['GET','POST'])
def ztpdeviceInfo ():
    formresult=request.form
    sysvars=classes.globalvars()
    queryStr="select * from ztpdevices where id='{}'".format(formresult['id'])
    # Obtain the relevant ZTP device information from the database
    result=classes.sqlQuery(queryStr,"selectone")
    # If ipam is enabled, we also need to get the subnet information
    if "ipamenabled" in sysvars:
        # IPAM is enabled. First check whether IPAM is online
        if sysvars['ipamsystem']=="PHPIPAM":
            info={'phpipamauth': sysvars['phpipamauth'],'ipamipaddress':sysvars['ipamipaddress'],'phpipamappid':sysvars['phpipamappid'],'ipamuser':sysvars['ipamuser'],'ipampassword':sysvars['ipampassword']}
            ipamstatus=classes.checkPhpipam(info)
        elif sysvars['ipamsystem']=="Infoblox":
            info={'ipamipaddress':sysvars['ipamipaddress'],'ipamuser':sysvars['ipamuser'],'ipampassword':sysvars['ipampassword']}
            ipamstatus=classes.checkInfoblox(info)
        else:
            ipamstatus="Online"
        if ipamstatus=="Online":
            # IPAM is online, obtain the subnet information, based on which IPAM is used (PHPIPAM or Infoblox)
            if sysvars['ipamsystem']=="PHPIPAM":
                ipamResult=classes.PHPipamget('subnets')       
                # If there is already a subnet selected, we also have to obtain the IP subnet and IP address information
                if result['ipamsubnet']:
                    ipamsubnet=classes.PHPipamget('subnets/{}'.format(result['ipamsubnet']))
                    # Obtain the active IP addresses from the subnet
                    ipamIpaddress=classes.PHPipamget('subnets/{}/addresses'.format(result['ipamsubnet']))
                    response={'sysvars':sysvars,'deviceInfo':result,'subnets':ipamResult,'ipamsubnet':ipamsubnet,'ipamIpaddress': ipamIpaddress }
                else:
                    response={'sysvars':sysvars,'deviceInfo':result,'subnets':ipamResult }
            elif sysvars['ipamsystem']=="Infoblox":
                ipamResult=classes.getInfoblox("network")
                # If there is already a subnet selected, we also have to obtain the IP subnet and IP address information
                if result['ipamsubnet']:
                    ipamsubnet=classes.getInfoblox("network?_return_fields%2B=options,members")
                    ipamIpaddress=classes.getInfoblox('ipv4address?status=USED&network={}&_return_as_object=1'.format(result['ipamsubnet']))
                    response={'sysvars':sysvars,'deviceInfo':result,'subnets':ipamResult,'ipamsubnet':ipamsubnet,'ipamIpaddress': ipamIpaddress }
                else:
                    response={'sysvars':sysvars,'deviceInfo':result,'subnets':ipamResult }
            else:
                response={'sysvars':sysvars,'deviceInfo':result}
        else:
             response={'sysvars':sysvars,'deviceInfo':result}
    else:
        response={'sysvars':sysvars,'deviceInfo':result}
    return json.dumps(response)

@ztp.route("/ipamgetSubnet", methods=['GET','POST'])
def ipamgetSubnet ():
    sysvars=classes.globalvars()
    if "ipamenabled" in sysvars:
        if sysvars['ipamsystem']=="PHPIPAM":
            ipamsubnet=classes.PHPipamget('subnets')
        elif sysvars['ipamsystem']=="Infoblox":
            ipamsubnet=classes.getInfoblox("network?_return_fields=network,comment")
    else:
        ipamsubnet={}
    response={'sysvars':sysvars,'ipamsubnet':ipamsubnet }
    return json.dumps(response)

@ztp.route("/ipamgetIPaddress", methods=['GET','POST'])
def ipamgetIPaddress ():
    sysvars=classes.globalvars()
    formresult=request.form
    if sysvars['ipamsystem']=="PHPIPAM":
        ipamsubnet=classes.PHPipamget('subnets/{}'.format(formresult['subnetid']))
        # Obtain the active IP addresses from the subnet
        ipamIpaddress=classes.PHPipamget('subnets/{}/addresses'.format(formresult['subnetid']))
        response={'ipamsubnet':ipamsubnet,'ipamIpaddress': ipamIpaddress,'sysvars': sysvars }
    elif sysvars['ipamsystem']=="Infoblox":
        ipamsubnet=classes.getInfoblox("network?network={}&_return_fields%2B=options,members".format(formresult['subnetid']))
        ipamIpaddress=classes.getInfoblox('ipv4address?status=USED&network={}&_return_as_object=1'.format(formresult['subnetid']))
        response={'ipamsubnet':ipamsubnet,'ipamIpaddress': ipamIpaddress,'sysvars': sysvars }
    return json.dumps(response)

@ztp.route("/ztptemplateInfo", methods=['GET','POST'])
def ztptemplateInfo ():
    formresult=request.form
    sysvars=classes.globalvars()
    queryStr="select * from ztptemplates where id='{}'".format(formresult['id'])
    # Obtain the relevant ZTP template information from the database
    result=classes.sqlQuery(queryStr,"selectone")
    return json.dumps(result)

@ztp.route("/ztpimageInfo", methods=['GET','POST'])
def ztpimageInfo ():
    formresult=request.form
    sysvars=classes.globalvars()
    queryStr="select * from ztpimages where id='{}'".format(formresult['id'])
    # Obtain the relevant ZTP image information from the database
    result=classes.sqlQuery(queryStr,"selectone")
    return json.dumps(result)

@ztp.route("/vsfmasterInfo", methods=['GET','POST'])
def vsfmasterInfo ():
    sysvars=classes.globalvars()
    queryStr="select * from ztpdevices where vsfrole='Master'"
    # Obtain the relevant VSF information from the database
    result=classes.sqlQuery(queryStr,"select")
    return json.dumps(result)

@ztp.route("/ztptemplateparameterInfo", methods=['GET','POST'])
def ztptemplateparameterInfo ():
    formresult=request.form
    sysvars=classes.globalvars()
    templatevariables=[]
    queryStr="select * from ztptemplates where id='{}'".format(formresult['id'])
    # Obtain the relevant ZTP template information from the database
    result=classes.sqlQuery(queryStr,"selectone")
    # Now extract all the {{ }} blocks and put them in a dictionary
    env = Environment()
    ast = env.parse(result['template'])
    templatevars=meta.find_undeclared_variables(ast)
    for items in templatevars:
        templatevariables.append({items:''})
    return json.dumps(templatevariables)

@ztp.route("/ztpActivate", methods=['GET','POST'])
def ztpActivate ():
    authOK=classes.checkAuth("ztpdevice","feature")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant device information from the database
        result=classes.ztpActivate(formresult)
        return json.dumps(result)
    else:
        return render_template("login.html")

@ztp.route("/ztpDeactivate", methods=['GET','POST'])
def ztpDeactivate ():
    authOK=classes.checkAuth("ztpdevice","feature")
    if authOK!=0:
        sysvars=classes.globalvars()
        formresult=request.form
        # Obtain the relevant device information from the database
        result=classes.ztpDeactivate(formresult)
        return json.dumps(result)
    else:
        return render_template("login.html")

@ztp.route("/checkIpamstatus", methods=['GET','POST'])
def checkIpamstatus ():
    sysvars=classes.globalvars()
    if "ipamenabled" in sysvars:
        # IPAM is enabled. Check whether IPAM is online
        if sysvars['ipamsystem']=="PHPIPAM":
            info={'phpipamauth': sysvars['phpipamauth'],'ipamipaddress':sysvars['ipamipaddress'],'phpipamappid':sysvars['phpipamappid'],'ipamuser':sysvars['ipamuser'],'ipampassword':sysvars['ipampassword']}
            ipamstatus=classes.checkPhpipam(info)
        elif sysvars['ipamsystem']=="Infoblox":
            info={'ipamipaddress':sysvars['ipamipaddress'],'ipamuser':sysvars['ipamuser'],'ipampassword':sysvars['ipampassword']}
            ipamstatus=classes.checkInfoblox(info)
        else:
            ipamstatus="Online"
    else:
        ipamstatus="Online"
    return ipamstatus

@ztp.route("/ztplog", methods=['GET','POST'])
def ztplog ():
    sysvars=classes.globalvars()
    queryStr="select * from ztpdevices where id='{}'".format(request.args.get('deviceid'))
    # Obtain the relevant ZTP logging information from the database
    deviceInfo=classes.sqlQuery(queryStr,"selectone")
    queryStr="select * from ztplog where ztpdevice='{}'".format(request.args.get('deviceid'))
    # Obtain the relevant ZTP logging information from the database
    logInfo=classes.sqlQuery(queryStr,"selectone")
    if logInfo:
        logInfo=json.loads(logInfo['logging'])
    else:
        logInfo=""
    return render_template("ztplog.html",deviceInfo=deviceInfo,logInfo=logInfo)

@ztp.route("/clearztpLog", methods=['GET','POST'])
def clearztpLog ():
    sysvars=classes.globalvars()
    formresult=request.form
    queryStr="delete from ztplog where ztpdevice='{}'".format(formresult['deviceid'])
    # Remove the ZTP log for this device
    result=classes.sqlQuery(queryStr,"selectone")
    return "ok"

@ztp.route("/showdevice", methods=['GET','POST'])
def showdevice ():
    sysvars=classes.globalvars()
    vsfmasterInfo={}
    vsfInfo={}
    softwareInfo={}
    templateInfo={}
    templateOutput=""
    if "ipamsystem" in sysvars:
        ipamsystem=sysvars['ipamsystem']
    else:
        ipamsystem=""
    queryStr="select * from ztpdevices where id='{}'".format(request.args.get('deviceid'))
    deviceInfo=classes.sqlQuery(queryStr,"selectone")
    # If there is a software image attached, we need to obtain the image information
    if deviceInfo['softwareimage']!=0:
        queryStr="select * from ztpimages where id='{}'".format(deviceInfo['softwareimage'])
        softwareInfo=classes.sqlQuery(queryStr,"selectone")
    # If there is a template assigned to the device, obtain the template information
    if deviceInfo['template']!=0:
        queryStr="select * from ztptemplates where id='{}'".format(deviceInfo['template'])
        templateInfo=classes.sqlQuery(queryStr,"selectone")
        # Generate the configuration
        jinjaTemplate=Template(templateInfo['template'])
        # Template is loaded successfully. Now try to push the parameters into the template
        templateOutput=jinjaTemplate.render(json.loads(deviceInfo['templateparameters']))
    # If VSF is enabled for this device, we also have to obtain the information of all the other members in the VSF
    if deviceInfo['vsfenabled']==1:
        # If this is the master switch, we have to obtain all the member information
        if deviceInfo['vsfmaster']==0:
            # This is the master switch, obtain the member information
            queryStr="select * from ztpdevices where vsfmaster='{}' or id='{}' order by vsfmember".format(deviceInfo['id'], deviceInfo['id'])
            vsfInfo=classes.sqlQuery(queryStr,"select")
            vsfmasterInfo=deviceInfo
        else:
            # This is not the master switch, we need to obtain the master switch information, and other VSF members, if they exist
            queryStr="select * from ztpdevices where id='{}'".format(deviceInfo['vsfmaster'])
            vsfmasterInfo=classes.sqlQuery(queryStr,"selectone")
            # Obtain the other member switch information
            queryStr="select * from ztpdevices where vsfmaster='{}' or id='{}' order by vsfmember".format(deviceInfo['vsfmaster'],deviceInfo['vsfmaster'])
            vsfInfo=classes.sqlQuery(queryStr,"select")
            if vsfmasterInfo['softwareimage']!=0:
                queryStr="select * from ztpimages where id='{}'".format(vsfmasterInfo['softwareimage'])
                softwareInfo=classes.sqlQuery(queryStr,"selectone")
            # If there is a template assigned to the device, obtain the template information
            if vsfmasterInfo['template']!=0:
                queryStr="select * from ztptemplates where id='{}'".format(vsfmasterInfo['template'])
                templateInfo=classes.sqlQuery(queryStr,"selectone")
                # Generate the configuration
                jinjaTemplate=Template(templateInfo['template'])
                # Template is loaded successfully. Now try to push the parameters into the template
                templateOutput=jinjaTemplate.render(json.loads(vsfmasterInfo['templateparameters']))
    return render_template("showztpdevice.html",deviceInfo=deviceInfo, vsfInfo=vsfInfo, vsfmasterInfo=vsfmasterInfo,softwareInfo=softwareInfo, templateInfo=templateInfo, ipam=ipamsystem, templateOutput=templateOutput)

@ztp.route("/showdeviceStatus", methods=['GET','POST'])
def showdeviceStatus ():
    queryStr="select ipaddress,netmask,gateway,ztpstatus, vrf from ztpdevices where id='{}'".format(request.form['id'])
    deviceInfo=classes.sqlQuery(queryStr,"selectone")
    return json.dumps(deviceInfo)

@ztp.route("/ztpCredentials", methods=['GET','POST'])
def ztpCredentials ():
    sysvars=classes.globalvars()
    formresult=request.form
    response=classes.verifyCredentials(formresult['deviceid'],formresult['username'],formresult['password'],sysvars)
    return json.dumps(response)

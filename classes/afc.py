# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
# Aruba Fabric Composer classes
import requests
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict

import classes.classes
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def obtainafcToken(afcipaddress,afcusername,afcpassword):
    response={}
    try:
        url="https://" + afcipaddress + "/api/auth/token"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        headers['accept'] = "application/json; version=1.0"
        headers["X-Auth-Username"] = afcusername
        headers["X-Auth-Password"] = afcpassword
        headers["Content-Length"] = "0"
        response = requests.post(url, headers=headers, verify=False)
        return response.text
    except ConnectionError:
        response.update({"message":"Connection error, no response from AFC"})
        return response
    except Exception as err:
        response.update({"message":"Failed to establish a connection to AFC"})
        return response


def checkafcToken(afcipaddress, afctoken):
    response={}
    try:
        url="https://" + afcipaddress + "/api/ping"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        headers['accept'] = "application/json; version=1.0"
        headers["Authorization"] = afctoken
        try:
            result = requests.get(url, headers=headers, verify=False, timeout=2)
        except:
            response.update({"message":"No response from AFC"})
            return response
        if result:
            response.update({"status_code": result.status_code})
        else:
            response.update({"message":"No response from AFC"})
        return response
    except ConnectionError:
        response.update({"message":"Connection error, no response from AFC"})
        return response
    except Exception as err:
        response.update({"message":"Failed to establish a connection to AFC"})
        return response
    except:
        response.update({"message":"Failed to establish a connection to AFC"})
        return response


def getRestafc(url):
    afcvars=classes.classes.obtainVars('sysafc')
    response={}
    if len(afcvars)>0:
        if isinstance(afcvars,str):
            afcvars=json.loads(afcvars)
        if not "afctoken" in afcvars:
            response= obtainafcToken(afcvars['afcipaddress'],afcvars['afcusername'], afcvars['afcpassword'])
            if isinstance(response,str):
                response=json.loads(response)
            afcvars.update({"afctoken":response['result']})
            queryStr="update systemconfig set datacontent='{}' where configtype='sysafc'".format(json.dumps(afcvars))
            classes.classes.sqlQuery(queryStr,"update")
        url="https://" + afcvars['afcipaddress'] + "/" + url
        result={}
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        headers['accept'] = "application/json; version=1.0"
        headers["Authorization"] = afcvars['afctoken']
        response=checkafcToken(afcvars['afcipaddress'],afcvars['afctoken'])
        if "status_code" in response:
            if response['status_code']==204:
                # Token seems to be valid, we can issue the query
                response = requests.get(url, headers=headers, verify=False)
                response = response.json()
                if response['result']=="Authentication credential is not valid; please log in again":
                    # Authorization token is still not valid. We need to refresh
                    response= obtainafcToken(afcvars['afcipaddress'], afcvars['afcusername'], afcvars['afcpassword'])
                    if isinstance(response,str):
                        response = json.loads(response)
                    if "count" in response:
                        # Result is the afctoken. We need to update the afcvars
                        afcvars.update({"afctoken":response['result']})
                        queryStr="update systemconfig set datacontent='{}' where configtype='sysafc'".format(json.dumps(afcvars))
                        classes.classes.sqlQuery(queryStr,"update")
                    # And issue the get request again
                    headers["Authorization"] = afcvars['afctoken']
                    response = requests.get(url, headers=headers, verify=False)
                    response = response.json()
            else:
                # Statuscode is not 204, try to refresh the token
                response= obtainafcToken(afcipaddress, afcusername, afcpassword)
                if isinstance(response,str):
                    response = json.loads(response)
                if "count" in response:
                    # Result is the afctoken. We need to update the afcvars
                    afcvars.update({"afctoken":response['result']})
                    queryStr="update systemconfig set datacontent='{}' where configtype='sysafc'".format(json.dumps(afcvars))
                    classes.classes.sqlQuery(queryStr,"update")
                    # And issue the get request again
                    headers["Authorization"] = afcvars['afctoken']
                    response = requests.get(url, headers=headers, verify=False)
                    response = response.json()
                else:
                    # There is something wrong with the connectivity, return an error
                    response.update({"message":"Unable to obtain information, verify AFC credentials"})
    else:
        response.update({"message":"No AFC integration information available"})
    return response


def getafcSwitches(formresult):
    afcswitches=[]
    formresult=formresult.to_dict(flat=True)
    try:
        queryStr="select jsondata,message from afc where infotype='fabrics'"
        fabricInfo=classes.classes.sqlQuery(queryStr,"selectone")
        afcfabrics=json.loads(fabricInfo['jsondata'])
    except:
        afcfabrics=[]
    try:
        queryStr="select jsondata,message from afc where infotype='switches'"
        switchInfo=classes.classes.sqlQuery(queryStr,"selectone")
        afcSwitches=json.loads(switchInfo['jsondata'])     
    except Exception as e:
        print(e)
        afcSwitches=[]
    totalentries=0
    if formresult and len(afcSwitches)>0:
        entryperpage=int(formresult['entryperpage'])
        if not "pageoffset" in formresult:
            pageoffset=0
        else:
            pageoffset=int(formresult['pageoffset'])-1
        afcfabric=formresult['afcfabric']
        try:
            if switchInfo['jsondata']!='"Authentication token header required"':
                # First go through the list and filter on the fabric (if this is selected)
                if afcfabric=="allfabrics":
                    if len(afcSwitches)>0:
                        totalentries=len(afcSwitches)
                        afcswitches=[afcSwitches[i:i+entryperpage] for i in range(0, len(afcSwitches), entryperpage)][pageoffset]
                    else:
                        totalentries=0
                elif afcfabric=="unassigned":
                    # We need to filter out the switches that are not a member of the any fabric
                    if len(afcSwitches)>0:
                        for items in afcSwitches:
                            if items['fabric_uuid']=="":
                                # This switch is not assigned to any fabric. Add it to the (new) list of dicts
                                afcswitches.append(items)
                        totalentries=len(afcswitches)
                        if totalentries>0:
                            afcswitches=[afcswitches[i:i+entryperpage] for i in range(0, len(afcswitches), entryperpage)][pageoffset]
                else:
                    # A fabric is selected, we need to filter out the switches that are not a member of the selected fabric
                    # the afcfabric uuid is the fabric uuid, this needs to be assigned to the switches
                    if len(afcSwitches)>0:
                        for items in afcSwitches:
                            if items['fabric_uuid']==afcfabric:
                                # This switch is assigned to the fabric. Add it to the (new) list of dicts
                                afcswitches.append(items)
                        totalentries=len(afcswitches)
                        if totalentries>0:
                            afcswitches=[afcswitches[i:i+entryperpage] for i in range(0, len(afcswitches), entryperpage)][pageoffset]

            else:
                # There is no valid information in the switch Information
                afcswitches=[]
                jsonData={}
                jsonData['message']=switchInfo['jsondata']
                afcswitches.append(jsonData)
                afcfabric="allfabrics"
        except:
            entryperpage=10
            pageoffset=0
            afcswitches=[]
            jsonData={}
            jsonData['message']="No switch information"
            afcswitches.append(jsonData)
            afcfabric="allfabrics"
    else:
        entryperpage=10
        pageoffset=0
        try:
            queryStr="select jsondata,message from afc where infotype='switches'"
            switchInfo=classes.classes.sqlQuery(queryStr,"selectone")
            if switchInfo['jsondata']!='"Authentication token header required"':
                jsonData=json.loads(switchInfo['jsondata'])
                if len(jsonData)>0:
                    totalentries=len(jsonData)
                    # and we should only show the first 10 switches in the list
                    afcswitches=[jsonData[i:i+entryperpage] for i in range(0, len(jsonData), entryperpage)][pageoffset]
            else:
                afcswitches=[]
                jsonData={}
                jsonData['message']=switchInfo['jsondata']
                afcswitches.append(jsonData)
            afcfabric="allfabrics"
        except:
            afcswitches=[]
            jsonData={}
            jsonData['message']="No switch information"
            afcswitches.append(jsonData)
            afcfabric="allfabrics"
    return {'afcswitches':afcswitches, 'afcfabrics': afcfabrics, 'afcfabric': afcfabric, 'totalentries': totalentries, 'pageoffset': pageoffset, 'entryperpage': entryperpage}


def afcauditInfo(formresult):
    formresult=formresult.to_dict(flat=True)
    totalentries=0
    if formresult:
        entryperpage=formresult['entryperpage']
        if not "pageoffset" in formresult:
            pageoffset=0
        else:
            pageoffset=int(formresult['pageoffset'])-1
        # Need to check if there are any search criteria. If not just select the last entries from the table
        if formresult['searchRecordtype']!="" or formresult['searchStreamid']!="" or formresult['searchSeverity']!="" or formresult['searchDescription']!="":
            constructQuery = " where"
        else:
            constructQuery = "    " 
        if formresult['searchRecordtype']:
            constructQuery += " record_type like'%" + formresult['searchRecordtype'] + "%' AND "
        if formresult['searchStreamid']:
            constructQuery += " stream_id like '%" + formresult['searchStreamid'] + "%' AND "
        if formresult['searchSeverity']:
            constructQuery += " severity='" + formresult['searchSeverity'] + "' AND "
        if formresult['searchDescription']:
            constructQuery += " description like'%" + formresult['searchDescription'] + "%' AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from afcaudit " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=navResult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from afcaudit " + constructQuery[:-4] + " ORDER BY log_date DESC LIMIT {} offset {}".format(entryperpage,pageoffset)
        afcauditInfo=classes.classes.sqlQuery(queryStr,"select")
    else:
        entryperpage=10
        pageoffset=0
        queryStr="select count(*) as totalCount from afcaudit"
        auditCount=classes.classes.sqlQuery(queryStr,"selectone")
        totalentries=auditCount['totalCount']
        queryStr="SELECT * FROM afcaudit ORDER BY log_date DESC LIMIT {} OFFSET 0".format(entryperpage)
        afcauditInfo=classes.classes.sqlQuery(queryStr,"select")
    return {'auditInfo':afcauditInfo, 'totalentries': totalentries, 'pageoffset': pageoffset, 'entryperpage': entryperpage}




def afcswitchInfo(uuid):
    afcswitchInfo={}
    afcswitchInfo['info']={}
    afcswitchInfo['portInfo']={}
    queryStr="select jsondata,message from afc where infotype='switches'"
    switchInfo=classes.classes.sqlQuery(queryStr,"selectone")
    jsonData=json.loads(switchInfo['jsondata'])
    # Obtain the right switch from the list
    for items in jsonData:
        if items['uuid']==uuid:
            # This is the switch, return the information to the calling function
            # Extract the port information and order the interface list
            portInfo=sorted(items['ports'], key=lambda d: int(d['silkscreen']))
            afcswitchInfo['info']=items.copy()
            afcswitchInfo['portInfo']=portInfo.copy()
    return afcswitchInfo


def afcvmwareInventory():
    # Obtain the host information
    queryStr="select jsondata,message from afc where infotype='vmwareinventory'"
    vmInfo=classes.classes.sqlQuery(queryStr,"selectone")
    if vmInfo==None:
        vmInfo={}
        vmInfo['jsondata']=[]
        vmInfo['message']="No VMWare inventory information available"
        vmTree=[]
    else:
        vmTree=[]
        jsonData=json.loads(vmInfo['jsondata'])
        for items in jsonData:
            for items2 in items['hosts']:
                vmConstruct = {}
                # Host info
                vmDict={}
                vmConstruct['name'] = items2['name']
                vmConstruct['itemtype']="host"
                vmConstruct['power_state'] = items2['power_state']
                vmConstruct['uuid'] = items2['uuid']
                vmDict2={}
                vmDict3={}
                vmDict4={}
                vmDict5={}
                vmConstruct['children']=[]
                for index, items3 in enumerate(items2['nics']):
                    #  We need to create dictionaries in this list. This dictionary contains a data dictionary and children list(s)
                    vmDict[index]={}
                    vmDict[index]['itemtype']="nic"
                    vmDict[index]['name'] = items3['name'];
                    vmDict[index]['uuid'] = items3['uuid'];
                    vmDict[index]['mac_address'] = items3['mac_address'];
                    vmDict[index]['ip_address'] = items3['ip_address'];
                    vmDict[index]['vlan'] = items3['vlan'];   
                    vmDict[index]['vni'] = items3['vni'];
                    vmDict[index]['vtep'] = items3['vtep'];
                    vmConstruct['children'].append(vmDict[index].copy())
                    for index2, items4 in enumerate(items3['portgroups']):
                        vmConstruct['children'][index]['children']=[]
                        vmDict2[index2]={}
                        vmDict2[index2]['itemtype']="portgroup"
                        vmDict2[index2]['name'] = items4['name'];
                        vmDict2[index2]['uuid'] = items4['uuid'];
                        vmDict2[index2]['type'] = items4['type'];
                        vmDict2[index2]['vlans'] = items4['vlans'];
                        vmConstruct['children'][index]['children'].append(vmDict2[index2].copy())
                        # There is only one vswitch assigned to a port group, therefore no for-next
                        vmConstruct['children'][index]['children'][index2]['children']=[]
                        vmDict3['itemtype']="vswitch"
                        vmDict3['name']=items4['vswitch']['name']
                        vmDict3['uuid']=items4['vswitch']['uuid']
                        vmDict3['type']=items4['vswitch']['type']
                        vmConstruct['children'][index]['children'][index2]['children'].append(vmDict3.copy())
                        vmConstruct['children'][index]['children'][index2]['children'][0]['children']=[]
                        for index3, items5 in enumerate(items4['vswitch']['nic']):
                            vmDict4[index3]={}
                            vmDict4[index3]['itemtype']="vnic"
                            vmDict4[index3]['name'] = items5['name'];
                            vmDict4[index3]['link_speed'] = items5['link_speed'];
                            vmDict4[index3]['connection_status'] = items5['connection_status'];
                            vmDict4[index3]['uuid'] = items5['uuid'];
                            vmDict4[index3]['mac_address'] = items5['mac_address'];
                            vmDict4[index3]['children']=[]                           
                            if len(items5['switch'])>0:
                                vmDict5={}
                                vmDict5['itemtype']="switch"
                                vmDict5['name'] = items5['switch']['hostname'];
                                vmDict5['switch_port_id'] = items5['switch_port_id'];
                                vmDict5['uuid'] = items5['switch']['uuid'];
                                vmDict5['ip_address'] = items5['switch']['ip_address'];
                                vmDict5['mac_address'] = items5['switch']['mac_address'];
                                vmDict5['serial_number'] = items5['switch']['serial_number'];
                                vmDict5['description'] = items5['switch']['description'];
                                vmDict5['role'] = items5['switch']['role'];
                                vmDict5['fabric'] = items5['switch']['fabric'];
                                vmDict5['fabric_class'] = items5['switch']['fabric_class'];
                                vmDict4[index3]['children'].append(vmDict5.copy())
                            vmConstruct['children'][index]['children'][index2]['children'][0]['children'].append(vmDict4[index3].copy())
                vmTree.append(vmConstruct) 
    return json.dumps(vmTree)








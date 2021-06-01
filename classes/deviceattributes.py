# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
# System Administration classes

import classes.classes
import requests, json
import psutil, sys, os, platform, subprocess


def deviceattributesdbAction(formresult):
    # This definition is for all the database actions for the device attributes
    constructQuery=""
    dbUpdate=True
    message=""
    if(bool(formresult)==True):
        if "attributelist" in formresult:
            if formresult['attributelist']:
                try:
                    attributelist = formresult['attributelist'].split(",")
                except:
                    # There is an error in the list, we should not update or insert
                    message="Error in the list format"
                    dbUpdate=False
            else:
                attributelist=[]
        else:
            attributelist=[]

        if(formresult['action']=="Submit device attribute"):
            # First check if the device attribute name already exists
            queryStr="select * from deviceattributes where name='{}'".format(formresult['name'])
            if classes.classes.checkdbExist(queryStr)==0:
                queryStr="insert into deviceattributes (name, type, attributelist, isassigned) values ('{}','{}','{}','[]')".format(formresult['name'],formresult['attributetype'], json.dumps(attributelist))
                classes.classes.sqlQuery(queryStr,"insert")
            else:
                message="Device attribute already exists"
            result=classes.classes.sqlQuery("select * from deviceattributes","select")
        elif  (formresult['action']=="Submit changes"):
            queryStr="update deviceattributes set name='{}', type='{}',attributelist='{}' where id='{}'".format(formresult['name'],formresult['attributetype'], json.dumps(attributelist),formresult['id'])
            classes.classes.sqlQuery(queryStr,"update")
        elif (formresult['action']=="Delete"):
            # First check if the attribute is assigned
            queryStr="select isassigned from deviceattributes where id='{}'".format(formresult['id'])
            result=classes.classes.sqlQuery(queryStr,"selectone")
            if result['isassigned']=="[]":
                queryStr="delete from deviceattributes where id='{}'".format(formresult['id'])
                classes.classes.sqlQuery(queryStr,"delete")
            else:
                message="Cannot remove attribute, it is assigned"
        try:
            searchAction=formresult['searchAction']
        except:
            searchAction=""   
        if formresult['searchName'] or formresult['searchType'] or formresult['searchAssigned']:
            constructQuery=" where "
        if formresult['searchName']:
            constructQuery += " name like'%" + formresult['searchName'] + "%' AND " 
        if formresult['searchType']:
            constructQuery += " type='" + formresult['searchType'] + "' AND " 
        if formresult['searchAssigned']:
            if formresult['searchAssigned']=="0":
                constructQuery += " isassigned='[]' AND " 
            else:
                constructQuery += " isassigned!='[]' AND "
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr="select COUNT(*) as totalentries from deviceattributes " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)
        totalentries=navResult['totalentries']
        entryperpage=formresult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from deviceattributes " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from deviceattributes"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=25
        pageoffset=0
        queryStr="select * from deviceattributes LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage, 'message':message}

def assignedAttributes(deviceid):
    attrList=[]
    queryStr="select deviceattributes from devices where id='{}'".format(deviceid)
    attrResult=classes.classes.sqlQuery(queryStr,"selectone")
    if (attrResult['deviceattributes']):
        for items in json.loads(attrResult['deviceattributes']):
            # For each assigned attribute, obtain the information from the attributes table
            queryStr="select * from deviceattributes where id='{}'".format(items['id'])
            attrInfo=classes.classes.sqlQuery(queryStr,"selectone")
            # Now check which type attribute (boolean, value or list)
            if attrInfo['type']=="boolean":
                booleanDict={"id": attrInfo['id'], "name": attrInfo['name'], "type": "Boolean", "value":  items['value'] }
                attrList.append(booleanDict.copy())
            elif attrInfo['type']=="value":
                valueDict={"id": attrInfo['id'], "name": attrInfo['name'], "type": "Value", "value":  items['value'] }
                attrList.append(valueDict.copy())
            elif attrInfo['type']=="list":
                listDict={"id": attrInfo['id'], "name": attrInfo['name'], "type": "List", "value":  items['value'], "values": attrInfo['attributelist']  }
                attrList.append(listDict.copy())
    return attrList


def assignswitchAttribute(deviceid, id):
    # First obtain the switch attribute list
    queryStr="select deviceattributes from devices where id='{}'".format(deviceid)
    attrResult=classes.classes.sqlQuery(queryStr,"selectone")
    # Now append the attribute to the switch attribute list and store the attribute again
    attrResult=json.loads(attrResult['deviceattributes'])
    switchAttribute={"id": int(id),"value":""}
    attrResult.append(switchAttribute.copy())
    queryStr="update devices set deviceattributes='{}' where id='{}'".format(json.dumps(attrResult),deviceid)
    result=classes.classes.sqlQuery(queryStr,"selectone")
    # Finally we need update the deviceattributes and check whether the device is in the assigned list.
    queryStr="select isassigned from deviceattributes where id='{}'".format(id)
    isassigned=classes.classes.sqlQuery(queryStr,"selectone")
    isassigned=json.loads(isassigned['isassigned'])
    if not deviceid in isassigned:
        isassigned.append(deviceid)
        queryStr="update deviceattributes set isassigned='{}' where id={}".format(json.dumps(isassigned),int(id))
        classes.classes.sqlQuery(queryStr,"selectone")
    return result


def removeswitchAttribute(deviceid, id):
    queryStr="select deviceattributes from devices where id='{}'".format(deviceid)
    attrResult=classes.classes.sqlQuery(queryStr,"selectone")
    # Now append the attribute to the switch attribute list and store the attribute again
    attrResult=json.loads(attrResult['deviceattributes'])
    attrResult[:] = [d for d in attrResult if d.get('id') != int(id)]
    queryStr="update devices set deviceattributes='{}' where id='{}'".format(json.dumps(attrResult),deviceid)
    result=classes.classes.sqlQuery(queryStr,"selectone")
    # Finally, remove the device id from the device attributes list
    queryStr="select isassigned from deviceattributes where id='{}'".format(id)
    isassigned=classes.classes.sqlQuery(queryStr,"selectone")
    isassigned=json.loads(isassigned['isassigned'])
    if deviceid in isassigned:
        isassigned.remove(deviceid)
        queryStr="update deviceattributes set isassigned='{}' where id={}".format(json.dumps(isassigned),int(id))
        classes.classes.sqlQuery(queryStr,"selectone")
    return result


def showassignedAttributes(deviceid):
    attrList=[]
    queryStr="select deviceattributes from devices where id='{}'".format(deviceid)
    attrResult=classes.classes.sqlQuery(queryStr,"selectone")
    attrResult=json.loads(attrResult['deviceattributes'])
    for items in attrResult:
        queryStr="select name, type from deviceattributes where id='{}'".format(items['id'])
        attrInfo=classes.classes.sqlQuery(queryStr,"selectone")
        # Add the device attribute name and type to the items variable, then append to the attrList
        items['name'] = attrInfo['name']
        items['type'] = attrInfo['type']
        attrList.append(items.copy())
    return attrList
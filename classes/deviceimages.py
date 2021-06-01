# (C) Copyright 2021 Hewlett Packard Enterprise Development LP.
# Generic Device Images classes

import classes.classes
import requests
import os
from jinja2 import Template, Environment
sessionid = requests.Session()

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def imagedbAction(formresult, filename, message):
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
            queryStr="insert into deviceimages (name,devicefamily,filename,version) values ('{}','{}','{}','{}')".format(formresult['name'],formresult['devicefamily'], filename, formresult['version'])
            imageid=classes.classes.sqlQuery(queryStr,"insert")
        elif (formresult['action']=="Submit changes"):
            if filename!="":
                imagename=filename
            else:
                imagename=formresult['filename']
            queryStr="update deviceimages set name='{}',devicefamily='{}',filename='{}', version='{}', filename='{}' where id='{}' "\
            .format(formresult['name'],formresult['devicefamily'], filename,formresult['version'],imagename,formresult['imageid'])
            classes.classes.sqlQuery(queryStr,"update")
        elif (formresult['action']=="Delete"):
            queryStr="delete from deviceimages where id='{}'".format(formresult['imageid'])
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
        queryStr="select COUNT(*) as totalentries from deviceimages " + constructQuery[:-4]
        navResult=classes.classes.navigator(queryStr,formresult)

        totalentries=navResult['totalentries']
        entryperpage=formresult['entryperpage']
        # If the entry per page value has changed, need to reset the pageoffset
        if formresult['entryperpage']!=formresult['currententryperpage']:
            pageoffset=0
        else:
            pageoffset=navResult['pageoffset']
        # We have to construct the query based on the formresult information (entryperpage, totalpages, pageoffset)
        queryStr = "select * from deviceimages " + constructQuery[:-4] + " LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    else:
        queryStr="select COUNT(*) as totalentries from deviceimages"
        navResult=classes.classes.sqlQuery(queryStr,"selectone")
        entryperpage=10
        pageoffset=0
        queryStr="select * from deviceimages LIMIT {} offset {}".format(entryperpage,pageoffset)
        result=classes.classes.sqlQuery(queryStr,"select")
    return {'result':result, 'totalentries': navResult['totalentries'], 'pageoffset': pageoffset, 'entryperpage': entryperpage}
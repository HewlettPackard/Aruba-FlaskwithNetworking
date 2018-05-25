# (C) Copyright 2018 Hewlett Packard Enterprise Development LP.

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import json

import classes as classes

app=Flask(__name__)
Bootstrap(app)

app.config['BOOTSTRAP_SERVE_LOCAL']=True

#Make Python definitions calleable in the Jinja template
app.jinja_env.globals.update(decryptPass=classes.decrypt)
app.jinja_env.globals.update(getREST=classes.getRESTcx)

@app.route("/", methods=['GET', 'POST'])
def index ():
    formresult=request.form
    if(bool(formresult)==True):
       if(formresult['action']=="Submit device"):
          queryStr="insert into devices (description,ipaddress,username,password) values ('%s','%s','%s','%s')"\
          % (formresult['description'],formresult['ipaddress'],formresult['username'],classes.encrypt("ArubaRocks", formresult['password']))
          classes.sqlQuery(queryStr)
          result1=classes.sqlQuery("select * from devices")
       elif  (formresult['action']=="Submit changes"):
          queryStr="update devices set description='%s',ipaddress='%s',username='%s',password='%s' where id=%s "\
          % (formresult['description'],formresult['ipaddress'],formresult['username'],classes.encrypt("ArubaRocks", formresult['password']),formresult['id'])
          classes.sqlQuery(queryStr)
          result1=classes.sqlQuery("select * from devices")
       elif (formresult['action']=="Delete"):
          queryStr="delete from devices where id=%s" % (formresult['id'])
          classes.sqlQuery(queryStr)
          result1=classes.sqlQuery("select * from devices")
       elif (formresult['action']=="order by ipaddress"):
          result1=classes.sqlQuery("select * from devices order by ipaddress ASC")
       elif (formresult['action']=="order by description"):
          result1=classes.sqlQuery("select * from devices order by description ASC")
       else:
          result1=classes.sqlQuery("select * from devices")
    else:
        result1=classes.sqlQuery("select * from devices")
    #Convert the sql query result in a tuple list with dictionaries
    resultlist=[]
    for info in result1:
        #Discover the model and software release of the device
        response=classes.discoverModel(info['id'])
        #If the result is a dictionary and there is no keyname named 'message', then there is version info available, otherwise the value of swInfo should be '-'
        if isinstance(response,dict) or not 'message' in response:
            resultlist.append(dict({'id':int(info['id']),'ipaddress':info['ipaddress'],'description':info['description'],'type':response['ostype'],'platform_name':response['platform_name'],'swversion':response['swversion'],'username':info['username'],'password':info['password']}))
        else:
            #The response is not a dictionary or there is an error, setting default values for the parameters
            resultlist.append(dict({'id':int(info['id']),'ipaddress':info['ipaddress'],'description':info['description'],'type':'Unknown','platform_name':'Unknown','swversion':'Unknown','username':info['username'],'password':info['password']}))
        
    return render_template("index.html",result=resultlist, formresult=formresult)
# (C) Copyright 2018 Hewlett Packard Enterprise Development LP.

@app.route("/monitorgetData", methods=['GET', 'POST'])
def monitorgetData ():
    # Based on the Switch Operating System we have to use different mechanisms to obtain the information
    # Check what the operating system is with the discoverModel definition. This can be done based on the responses from the device.
    # Check if the switch is an ArubaOS-CX switch first and return the CPU value if it exists
    response=classes.getRESTcx("system/subsystems?attributes=resource_utilization&depth=2",request.args.get('devicelist'))
    if isinstance(response,list):
        # Typically, we are receiving multiple entries for the utilization, based on the subsystem (chassis, base, management, etc)
        # We should obtain all the entries that actually contain the values and average them out
        counter=0
        cpuVal=0
        # For next loop through the list. There is usually more than one entry
        for resourceList in response:
            # For next loop per resource_utilization dictionary. 
            for key in resourceList:
                # For next loop through the items per resource_utilization dictionary
                for value in resourceList[key]:
                   if value=="cpu":
                       if resourceList[key][value]:
                           # If the CPU key has a value we have to increase the counter and sum the cpu values
                           cpuVal=cpuVal+resourceList[key][value]
                           counter=counter+1
        # Now that all CPU utilizations are summed up, average out
        averageCPU=int(cpuVal/counter)
        counter=0
        cpuVal=0
        response="CPU: {} %".format(averageCPU)
    else:
        # There was no correct response from the ArubaOS-CX call. Now trying ArubaOS-Switch
        response=classes.getRESTswitch("system/status/cpu",request.args.get('devicelist'))
        if isinstance(response,dict):
            # The response is a dictionary, this means that there is content. If the response is returning a message, then there is an error
            # and we don't show the information
            if not 'message' in response:
                response="CPU: {} %".format(str(response['cpu']))
            else:
                response="Online"
        else:
            return "Unknown"
    return response

if (__name__) == "__main__":
    app.run(host='172.16.1.10', port=8080, debug=True)
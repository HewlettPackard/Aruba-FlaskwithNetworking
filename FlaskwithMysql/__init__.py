# (C) Copyright 2018 Hewlett Packard Enterprise Development LP
 
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

import classes as classes

app=Flask(__name__)
Bootstrap(app)

app.config['BOOTSTRAP_SERVE_LOCAL']=True
app.jinja_env.globals.update(checkStatus=classes.checkStatus)

@app.route("/", methods=['GET', 'POST'])
def index ():
    formresult=request.form
    if(bool(formresult)==True):
       if(formresult['action']=="Submit device"):
          queryStr="insert into devices (description,ipaddress,type,username,password) values ('%s','%s','%s','%s','%s')"\
          % (formresult['description'],formresult['ipaddress'],formresult['type'],formresult['username'],classes.encrypt("ArubaRocks", formresult['password']))
          classes.sqlQuery(queryStr)
       elif  (formresult['action']=="Submit changes"):
          queryStr="update devices set description='%s',ipaddress='%s',type='%s',username='%s',password='%s' where id=%s "\
          % (formresult['description'],formresult['ipaddress'],formresult['type'],formresult['username'],classes.encrypt("ArubaRocks", formresult['password']),formresult['id'])
          classes.sqlQuery(queryStr)
       elif (formresult['action']=="Delete"):
          queryStr="delete from devices where id=%s" % (formresult['id'])
          classes.sqlQuery(queryStr)
    result=classes.sqlQuery("select * from devices")
    return render_template("index.html",result=result, formresult=formresult)

if (__name__) == "__main__":
    app.run(host='172.16.1.10', port=8080, debug=True)
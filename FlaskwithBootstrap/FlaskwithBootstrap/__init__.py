# (C) Copyright 2018 Hewlett Packard Enterprise Development LP

from flask import Flask, render_template, request, json
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
import classes as classes

app=Flask(__name__)
Bootstrap(app)

app.config['BOOTSTRAP_SERVE_LOCAL']=True

@app.route("/", methods=['GET', 'POST'])

def index ():
    return render_template("index.html")

@app.route("/vlan")

def  vlan():
    url="https://172.16.1.1/rest/v1"
    creds={"username":"admin","password":"enable"}
    sessionid=classes.logincx(url,creds)
    try:
        vlans=classes.getvlancx(url,sessionid).json()
        classes.logoutcx(url,sessionid)
        return render_template("vlans.html",vlans=vlans)
    except:
        return render_template("vlans.html")


if (__name__) == "__main__":
    app.run(host='172.16.1.10', port=8080, debug=True)
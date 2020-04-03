# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# PHPIPAM classes

import classes.classes
import requests

import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def PHPipamtoken():
    globalsconf=classes.classes.globalvars()
    url=globalsconf['phpipamauth'] + "://" + globalsconf['ipamipaddress'] + "/api/" + globalsconf['phpipamappid'] + "/user/"
    res = requests.post(url, auth=(globalsconf['ipamuser'], globalsconf['ipampassword']), verify=False)
    result=json.loads(res.content.decode("utf-8"))
    return result['data']['token']

def PHPipamget(url):
    globalsconf=classes.classes.globalvars()
    header={'token':PHPipamtoken()}
    url=globalsconf['phpipamauth'] + "://" + globalsconf['ipamipaddress'] + "/api/" + globalsconf['phpipamappid'] + "/" + url + "/"
    res = requests.get(url,headers=header, verify=False)
    response=res.content.decode("utf-8")
    # PHPipam can return some HTML information (errors) so we need to check on that, strip that information and then convert the response to json
    if "<b>Warning</b>" in response:
        # There is an issue with the response. Need to strip that information and then convert to json
        # First check where the "code": 200  is found in the string. Then check the index of the first {, this is the start of the json response
        position=response.find('\"code\"')
        position=response.rfind('{', 0, position)
        response=json.loads(response[position:])
    else:
        response=json.loads(response)
    return response
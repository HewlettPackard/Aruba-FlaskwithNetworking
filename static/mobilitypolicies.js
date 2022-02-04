// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(".mobilityPolicies").on('click', async function () {
    deviceid = $(this).attr('data-deviceid');
    $('#mobilityroles').hide();
    $('#mobilityPolicies').show();
    $('#mobilityInterfaces').hide();
    $('#liProgress').hide();
    $('#addDeviceForm').hide();
    $('#editDeviceForm').hide();
    // This is an async function, we have to wait until the information is returned from the Python call. 
    // Definition found in mobility.py
    policyInfo = await $.ajax({
        url: "/mcpolicyInfo",
        type: "POST",
        data: { deviceid: deviceid, policy:'' },
        success: function () {
        },
        error: function () {
            showmessageBar("Error finding policy information");
        }
    });

    deviceInfo = await $.ajax({
        url: "/deviceInfo",
        type: "POST",
        data: { id: deviceid },
        success: function () {


        },
        error: function () {
            showmessageBar("Error finding policy information");
        }
    });
    policyInfo = JSON.parse(policyInfo);
    deviceInfo = JSON.parse(deviceInfo);
    showPolicies(policyInfo, deviceInfo,"")
});

$(document).on("change", "#filterPolicy", async function () {
    var policy_select = document.getElementById('filterPolicy');
    var policy = policy_select.options[policy_select.selectedIndex].value;
    var deviceid = document.getElementById('filterdeviceid').value;
    policyInfo = await $.ajax({
        url: "/mcpolicyInfo",
        type: "POST",
        data: { deviceid: deviceid, policy:policy },
        success: function () {
        },
        error: function () {
            showmessageBar("Error finding policy information");
        }
    });
    deviceInfo = await $.ajax({
        url: "/deviceInfo",
        type: "POST",
        data: { id: deviceid },
        success: function () {


        },
        error: function () {
            showmessageBar("Error finding device information");
        }
    });
    policyInfo = JSON.parse(policyInfo);
    deviceInfo = JSON.parse(deviceInfo);
    showPolicies(policyInfo, deviceInfo, policy)
});

function showPolicies(policyInfo, deviceInfo, policy) {
    //Build the table. There are many different ACL types (session, MAC, standard, extended, route, etc)
    policyHTML = "<form method='post'><table class='tablewithborder'>";
    policyHTML +="<input type='hidden' name='deviceid' id='filterdeviceid' value='" + deviceInfo['id'] + "'>";
    policyHTML += "<tr class='tableTitle'>";
    policyHTML += "<td><font class='font12pxwhite'>Select Policy type:</font> <select name='filterPolicy' id='filterPolicy' class='filterPolicy'>";
    policyHTML += "<option value=''>Select</option>";
    if (policy == "acl_sess") { policyHTML += "<option value='acl_sess' selected>Session</option>"; }
    else {
        policyHTML += "<option value='acl_sess'>Session</option>";
    }
    if (policy == "acl_mac") { policyHTML += "<option value='acl_mac' selected>MAC</option>"; }
    else {
        policyHTML += "<option value='acl_mac'>MAC</option>";
    }
    if (policy == "acl_std") { policyHTML += "<option value='acl_std' selected>Standard</option>"; }
    else {
        policyHTML += "<option value='acl_std'>Standard</option>";
    }
    if (policy == "acl_ext") { policyHTML += "<option value='acl_ext' selected>Extended</option>"; }
    else {
        policyHTML += "<option value='acl_ext'>Extended</option>";
    }
    if (policy == "acl_qinq") { policyHTML += "<option value='acl_qinq' selected>QinQ</option>"; }
    else {
        policyHTML += "<option value='acl_qinq'>QinQ</option>";
    }
    if (policy == "acl_route") { policyHTML += "<option value='acl_route' selected>Routed</option>"; }
    else {
        policyHTML += "<option value='acl_route'>Routed</option>";
    }
    policyHTML += "</select></td> ";
    policyHTML += "<td><font class='font13pxwhite'><center>Configured policies for " + deviceInfo['ipaddress'] + " (" + deviceInfo['description'] + ")</center></font></td></tr>";
    policyHTML += "<tr class='tableTitle'><td nowrap><font class='font12pxwhite'>Policy name</font></td>";
    policyHTML += "<td nowrap><font class='font12pxwhite'>ACL's</font></td></tr>";
    //Fill the table if there is no filter selection
    if (policy == "") {
        for (var i = 0; i < policyInfo.length; i++) {
            for (var key in policyInfo[i]) {
                // The key value is the policy type
                if (policyInfo[i][key] != null){
                    for (j = 0; j < policyInfo[i][key].length; j++) {
                        policyHTML += "<tr><td class='whiteBG' nowrap><font class='font11px'>" + policyInfo[i][key][j]['accname'] + " (" + key + ")</font></td><td class='whiteBG'><font class='font11px'>";
                        if (policyInfo[i][key][j]['acl_sess__v4policy']) {
                            for (k = 0; k < policyInfo[i][key][j]['acl_sess__v4policy'].length; k++) {
                                if (policyInfo[i][key][j]['acl_sess__v4policy'][k]['service-name']) {
                                    policyHTML += policyInfo[i][key][j]['acl_sess__v4policy'][k]['service-name'] + "||";
                                }
                                else if (policyInfo[i][key][j]['acl_sess__v4policy'][k]['svc']) {
                                    policyHTML += policyInfo[i][key][j]['acl_sess__v4policy'][k]['svc'] + "||";
                                }
                            }
                        }
                        if (policyHTML.slice(-2) === "||") {
                            policyHTML=policyHTML.slice(0, -2);
                        }
                        if (policyInfo[i][key][j]['acl_sess__v6policy']) {
                            for (k = 0; k < policyInfo[i][key][j]['acl_sess__v6policy'].length; k++) {
                                if (policyInfo[i][key][j]['acl_sess__v6policy'][k]['service-name']) {
                                    policyHTML += policyInfo[i][key][j]['acl_sess__v6policy'][k]['service-name'] + "||";
                                }
                                else if (policyInfo[i][key][j]['acl_sess__v6policy'][k]['svc']) {
                                    policyHTML += policyInfo[i][key][j]['acl_sess__v6policy'][k]['svc'] + "||";
                                }
                            }
                        }
                        if (policyHTML.slice(-2) === "||") {
                            policyHTML=policyHTML.slice(0, -2);
                        }
                        policyHTML += "</font></td></tr>";
                    }
                }
            }
        }
    }
    else {
        if (policyInfo[policy] != null) {
            for (j = 0; j < policyInfo[policy].length; j++) {
                policyHTML += "<tr><td class='whiteBG' nowrap><font class='font11px'>" + policyInfo[policy][j]['accname'] + " (" + policy + ")</font></td><td class='whiteBG'><font class='font11px'>";
                if (policyInfo[policy][j]['acl_sess__v4policy']) {
                    for (k = 0; k < policyInfo[policy][j]['acl_sess__v4policy'].length; k++) {
                        if (policyInfo[policy][j]['acl_sess__v4policy'][k]['service-name']) {
                            policyHTML += policyInfo[policy][j]['acl_sess__v4policy'][k]['service-name'] + "||";
                        }
                        else if (policyInfo[policy][j]['acl_sess__v4policy'][k]['svc']) {
                            policyHTML += policyInfo[policy][j]['acl_sess__v4policy'][k]['svc'] + "||";
                        }
                    }
                }
                if (policyHTML.slice(-2) === "||") {
                    policyHTML=policyHTML.slice(0, -2);
                }
                if (policyInfo[policy][j]['acl_sess__v6policy']) {
                    for (k = 0; k < policyInfo[policy][j]['acl_sess__v6policy'].length; k++) {
                        if (policyInfo[policy][j]['acl_sess__v6policy'][k]['service-name']) {
                            policyHTML += policyInfo[policy][j]['acl_sess__v6policy'][k]['service-name'] + "||";
                        }
                        else if (policyInfo[policy][j]['acl_sess__v6policy'][k]['svc']) {
                            policyHTML += policyInfo[policy][j]['acl_sess__v6policy'][k]['svc'] + "||";
                        }
                    }
                }
                if (policyHTML.slice(-2) === "||") {
                    policyHTML=policyHTML.slice(0, -2);
                }
                policyHTML += "</font></td></tr>";
            }
        }
    }


    policyInfo += "</form></table>";
    document.getElementById("mobilityPolicies").innerHTML = policyHTML;
}
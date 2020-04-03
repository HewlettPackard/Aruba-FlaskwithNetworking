// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

$(".mobilityPolicies").on('click', async function () {
    deviceid = $(this).attr('data-deviceid');
    document.getElementById("mobilityRoles").style.display = "none";
    document.getElementById("mobilityPolicies").style.display = "block";
    document.getElementById("mobilityInterfaces").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    // This is an async function, we have to wait until the information is returned from the Python call. 
    // Definition found in mobility.py
    policyInfo = await $.ajax({
        url: "/mcpolicyInfo",
        type: "POST",
        data: { deviceid: deviceid },
        success: function () {
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error finding policy information";
        }
    });

    deviceInfo = await $.ajax({
        url: "/deviceInfo",
        type: "POST",
        data: { id: deviceid },
        success: function () {


        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error finding device information";
        }
    });
    policyInfo = JSON.parse(policyInfo);
    deviceInfo = JSON.parse(deviceInfo);
    //Build the table. There are many different ACL types (session, MAC, standard, extended, route, etc)
    policyHTML = "<table class='fwtable'>";
    policyHTML += "<tr style='background-color:black;'>";
    policyHTML += "<td style='color:orange;'><font class='font11px'>Select Policy type:</font> <select name='filterPolicy' id='filterPolicy' class='filterPolicy'>";
    policyHTML += "<option value=''>Select</option>";
    policyHTML += "<option value='acl_sess'>Session</option>";
    policyHTML += "<option value='acl_mac'>MAC</option>";
    policyHTML += "<option value='acl_std'>Standard</option>";
    policyHTML += "<option value='acl_ext'>Extended</option>";
    policyHTML += "<option value='acl_qinq'>QinQ</option>";
    policyHTML += "<option value='acl_route'>Routed</option>";
    policyHTML += "</select ></td > ";

    policyHTML += "<td colspan='2' align='center' style='color:orange;'>Configured policies for " + deviceInfo['ipaddress'] + " (" + deviceInfo['description'] + ")</td></tr > ";
    policyHTML += "<tr><td nowrap><font class='font13px'>Policy name</font></td>";
    policyHTML += "<td nowrap><font class='font13px'>ACL's</font></td>";
    policyHTML += "<td width='5%'><input type='button' name='addPolicy' value='Add policy' class='addPolicy'/></td></tr>";
    if (policyInfo[0]['acl_sess']) {
        for (counter = 0; counter < policyInfo[0]['acl_sess'].length; counter++) {
            policyHTML += "<td nowrap><font class='font11px'>" + policyInfo[0]['acl_sess'][counter]['accname'] + " (session)</font></td><td><font class='font11px'>";
            if (policyInfo[0]['acl_sess'][counter]['acl_sess__v4policy']) {
                for (counter2 = 0; counter2 < policyInfo[0]['acl_sess'][counter]['acl_sess__v4policy'].length; counter2++) {
                    if (policyInfo[0]['acl_sess'][counter]['acl_sess__v4policy'][counter2]['service-name']) {
                        policyHTML += policyInfo[0]['acl_sess'][counter]['acl_sess__v4policy'][counter2]['service-name'] + "||";
                    }
                    else if (policyInfo[0]['acl_sess'][counter]['acl_sess__v4policy'][counter2]['svc']) {
                        policyHTML += policyInfo[0]['acl_sess'][counter]['acl_sess__v4policy'][counter2]['svc'] + "||";
                    }
                }
            }

            if (policyInfo[0]['acl_sess'][counter]['acl_sess__v6policy']) {
                for (counter2 = 0; counter2 < policyInfo[0]['acl_sess'][counter]['acl_sess__v6policy'].length; counter2++) {
                    if (policyInfo[0]['acl_sess'][counter]['acl_sess__v6policy'][counter2]['service-name']) {
                        policyHTML += policyInfo[0]['acl_sess'][counter]['acl_sess__v6policy'][counter2]['service-name'] + "||";
                    }
                    else if (policyInfo[0]['acl_sess'][counter]['acl_sess__v6policy'][counter2]['svc']) {
                        policyHTML += policyInfo[0]['acl_sess'][counter]['acl_sess__v6policy'][counter2]['svc'] + "||";
                    }
                }
            }

            policyHTML += "</font></td><td nowrap><font class='font11px'><input type='button' name='editPolicy' value='Edit' class='editPolicy'/><input type='button' name='deletePolicy' value='Delete' class='deletePolicy'/></font></td></tr>";
        }
    }

    if (policyInfo[1]['acl_mac']) {
        for (counter = 0; counter < policyInfo[1]['acl_mac'].length; counter++) {
            policyHTML += "<td nowrap><font class='font11px'>" + policyInfo[1]['acl_mac'][counter]['accname'] + " (MAC)</font></td><td><font class='font11px'>";
            if (policyInfo[1]['acl_mac'][counter]['acl_mac__policy']) {
                for (counter2 = 0; counter2 < policyInfo[1]['acl_mac'][counter]['acl_mac__policy'].length; counter2++) {
                    if (policyInfo[1]['acl_mac'][counter]['acl_mac__policy'][counter2]['src']=="mask") {
                        policyHTML += "<b>" + policyInfo[1]['acl_mac'][counter]['acl_mac__policy'][counter2]['action'] + "</b> " + policyInfo[1]['acl_mac'][counter]['acl_mac__policy'][counter2]['srcmac1'] + "(" + policyInfo[1]['acl_mac'][counter]['acl_mac__policy'][counter2]['srcmask']  + ")||" ;
                    }
                    else {
                        policyHTML += "<b>" + policyInfo[1]['acl_mac'][counter]['acl_mac__policy'][counter2]['action'] + "</b> " + policyInfo[1]['acl_mac'][counter]['acl_mac__policy'][counter2]['srcmac'] + "||";
                    }
                }
            }
            policyHTML += "</font></td><td nowrap><font class='font11px'><input type='button' name='editPolicy' value='Edit' class='editPolicy'/><input type='button' name='deletePolicy' value='Delete' class='deletePolicy'/></font></td></tr>";
        }
    }
    if (policyInfo[2]['acl_std']) {
        for (counter = 0; counter < policyInfo[2]['acl_std'].length; counter++) {
            policyHTML += "<td nowrap><font class='font11px'>" + policyInfo[2]['acl_std'][counter]['accname'] + " (Standard)</font></td><td><font class='font11px'>";
            if (policyInfo[2]['acl_std'][counter]['acl_std__v4policy']) {
                for (counter2 = 0; counter2 < policyInfo[2]['acl_std'][counter]['acl_std__v4policy'].length; counter2++) {
                    if (policyInfo[2]['acl_std'][counter]['acl_std__v4policy'][counter2]['src'] == "host") {
                        policyHTML += "<b>" + policyInfo[2]['acl_std'][counter]['acl_std__v4policy'][counter2]['action'] + "</b> " + policyInfo[2]['acl_std'][counter]['acl_std__v4policy'][counter2]['srcaddr'] + "(" + policyInfo[2]['acl_std'][counter]['acl_std__v4policy'][counter2]['src'] + ")||";
                    }
                }
            }
            if (policyInfo[2]['acl_std'][counter]['acl_std__v6policy']) {
                for (counter2 = 0; counter2 < policyInfo[2]['acl_std'][counter]['acl_std__v6policy'].length; counter2++) {
                    if (policyInfo[2]['acl_std'][counter]['acl_std__v6policy'][counter2]['src'] == "host") {
                        policyHTML += "<b>" + policyInfo[2]['acl_std'][counter]['acl_std__v6policy'][counter2]['action'] + "</b> " + policyInfo[2]['acl_std'][counter]['acl_std__v6policy'][counter2]['srcaddr'] + "(" + policyInfo[2]['acl_std'][counter]['acl_std__v6policy'][counter2]['src'] + ")||";
                    }
                }
            }
            policyHTML += "</font></td><td nowrap><font class='font11px'><input type='button' name='editPolicy' value='Edit' class='editPolicy'/><input type='button' name='deletePolicy' value='Delete' class='deletePolicy'/></font></td></tr>";
        }
    }

    if (policyInfo[3]['acl_ext']) {
        for (counter = 0; counter < policyInfo[3]['acl_ext'].length; counter++) {
            policyHTML += "<td nowrap><font class='font11px'>" + policyInfo[3]['acl_ext'][counter]['accname'] + " (Extended)</font></td><td><font class='font11px'>";
            if (policyInfo[3]['acl_ext'][counter]['acl_ext__v4']) {
                for (counter2 = 0; counter2 < policyInfo[3]['acl_ext'][counter]['acl_ext__v4'].length; counter2++) {
                    policyHTML += "<b>" + policyInfo[3]['acl_ext'][counter]['acl_ext__v4'][counter2]['action'] + "</b> " + policyInfo[3]['acl_ext'][counter]['acl_ext__v4'][counter2]['srcaddr'];
                    policyHTML += " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v4'][counter2]['srcip'] + " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v4'][counter2]['src_oper'];
                    policyHTML += " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v4'][counter2]['srcport'] + " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v4'][counter2]['srcportnum'];
                    policyHTML += " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v4'][counter2]['dstip'] + " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v4'][counter2]['dstip'] + "||";
                }
            }
            if (policyInfo[3]['acl_ext'][counter]['acl_ext__v6']) {
                for (counter2 = 0; counter2 < policyInfo[3]['acl_ext'][counter]['acl_ext__v6'].length; counter2++) {
                    policyHTML += "<b>" +policyInfo[3]['acl_ext'][counter]['acl_ext__v6'][counter2]['action'] + "</b> " + policyInfo[3]['acl_ext'][counter]['acl_ext__v6'][counter2]['srcaddr'];
                    policyHTML += " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v6'][counter2]['srcip'] + " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v6'][counter2]['src_oper'];
                    policyHTML += " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v6'][counter2]['srcport'] + " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v6'][counter2]['srcportnum'];
                    policyHTML += " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v6'][counter2]['dstip'] + " " + policyInfo[3]['acl_ext'][counter]['acl_ext__v6'][counter2]['dstip'] + "||";
                }
            }
            policyHTML += "</font></td><td nowrap><font class='font11px'><input type='button' name='editPolicy' value='Edit' class='editPolicy'/><input type='button' name='deletePolicy' value='Delete' class='deletePolicy'/></font></td></tr>";
        }
    }

    if (policyInfo[4]['acl_qinq']) {
        for (counter = 0; counter < policyInfo[4]['acl_qinq'].length; counter++) {
            policyHTML += "<td nowrap><font class='font11px'>" + policyInfo[4]['acl_qinq'][counter]['accname'] + " (MAC)</font></td><td><font class='font11px'>";
            policyHTML += "</font></td><td nowrap><font class='font11px'><input type='button' name='editPolicy' value='Edit' class='editPolicy'/><input type='button' name='deletePolicy' value='Delete' class='deletePolicy'/></font></td></tr>";
        }
    }

    if (policyInfo[5]['acl_route']) {
        for (counter = 0; counter < policyInfo[5]['acl_route'].length; counter++) {
            policyHTML += "<td nowrap><font class='font11px'>" + policyInfo[5]['acl_route'][counter]['accname'] + " (Routed)</font></td><td><font class='font11px'>";
            policyHTML += "</font></td><td nowrap><font class='font11px'><input type='button' name='editPolicy' value='Edit' class='editPolicy'/><input type='button' name='deletePolicy' value='Delete' class='deletePolicy'/></font></td></tr>";
        }
    }

    policyInfo += "</table>";
    document.getElementById("mobilityPolicies").innerHTML = policyHTML;

    $(".addPolicy").click(async function () {
        document.getElementById("policyAction").style.display = "block";
        console.log("add policy");
    });


    $(".editPolicy").click(async function () {
        document.getElementById("policyAction").style.display = "block";
        console.log("edit policy");
    });

    $(".deletePolicy").click(async function () {
        document.getElementById("policyAction").style.display = "block";
        console.log("delete policy");
    });

    $(document).on("change", "#filterPolicy", async function () {
        var policy_select = document.getElementById('filterPolicy');
        var policy = policy_select.options[policy_select.selectedIndex].value;
        console.log(policy);
    });



});
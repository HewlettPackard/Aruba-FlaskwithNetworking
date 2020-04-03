// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

$(".mobilityInterfaces").click(async function () {
    deviceid = $(this).attr('data-deviceid');
    document.getElementById("mobilityInterfaces").style.display = "block";
    document.getElementById("interfaceAction").style.display = "none";
    document.getElementById("mobilityRoles").style.display = "none";
    document.getElementById("roleAction").style.display = "none";
    document.getElementById("mobilityPolicies").style.display = "none";
    document.getElementById("policyAction").style.display = "none";
    document.getElementById("addDeviceForm").style.display = "none";
    document.getElementById("editDeviceForm").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    // This is an async function, we have to wait until the information is returned from the Python call. 
    // Definition found in mobility.py
    interfaceInfo = await $.ajax({
        url: "/mcinterfaceInfo",
        type: "POST",
        data: { deviceid: deviceid },
        success: function () {


        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error finding interface information";
        }
    });
    mobilityInfo = await $.ajax({
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
    interfaceInfo = JSON.parse(interfaceInfo);
    deviceInfo = JSON.parse(mobilityInfo);
    //Build the table
    interfaceHTML = "<table class='fwtable'>";
    interfaceHTML += "<tr style='background-color:black;'><td colspan='7' align='center' style='color:orange;'>Configured interfaces for " + deviceInfo['ipaddress'] + " (" + deviceInfo['description'] + ")</td></tr>";
    interfaceHTML += "<tr><td nowrap><font class='font13px'>VLAN ID</font></td>";
    interfaceHTML += "<td nowrap><font class='font13px'>VLAN name</font></td>";
    interfaceHTML += "<td nowrap><font class='font13px'>IP Address (subnet mask)</font></td>";
    interfaceHTML += "<td nowrap><font class='font13px'>VRRP IP Address</font></td>";
    interfaceHTML += "<td nowrap><font class='font13px'>DHCP Pool</font></td>";
    interfaceHTML += "<td nowrap><font class='font13px'>Inside NAT</font></td>";
    interfaceHTML += "<td width='5%'><input type='button' name='addInterface' value='Add interface' class='addInterface'/></td></tr>";
    console.log(interfaceInfo);

    if (interfaceInfo[1]['vlan_name_id']) {
        for (counter = 0; counter < interfaceInfo[1]['vlan_name_id'].length; counter++) {
            var noInterface = 0;
            interfaceHTML += "<td nowrap><font class='font11px'>" + interfaceInfo[1]['vlan_name_id'][counter]['vlan-ids'] + "</font></td>";
            interfaceHTML += "<td nowrap><font class='font11px'>" + interfaceInfo[1]['vlan_name_id'][counter]['name'] + "</font></td>";
            //Need to get the right interface information from the interface VLAN dictionary
            for (counter2 = 0; counter2 < interfaceInfo[0]['int_vlan'].length; counter2++) {
                if (interfaceInfo[0]['int_vlan'][counter2]['id'] == interfaceInfo[1]['vlan_name_id'][counter]['vlan-ids']) {
                    interfaceHTML += "<td nowrap><font class='font11px'>" + interfaceInfo[0]['int_vlan'][counter2]['int_vlan_ip']['ipaddr'] + " (" + interfaceInfo[0]['int_vlan'][counter2]['int_vlan_ip']['ipmask'] + ")</font></td>";
                    interfaceHTML += "<td nowrap><font class='font11px'></font></td>";
                    interfaceHTML += "<td nowrap><font class='font11px'></font></td>";
                    interfaceHTML += "<td nowrap><font class='font11px'></font></td>";
                    var noInterface = 1;
                }
            }
            if (noInterface == 0) {
                interfaceHTML += "<td colspan='4'></td>";
            }
            interfaceHTML += "<td nowrap><font class='font11px'><input type='button' name='editInterface' value='Edit' id='" + interfaceInfo[1]['vlan_name_id'][counter]['vlan-ids'] + "' class='editInterface'/><input type='button' name='deleteInterface' value='Delete' class='deleteInterface'/></font></td></tr>";
        }
    }
    interfaceInfo += "</table>";
    document.getElementById("mobilityInterfaces").innerHTML = interfaceHTML;

    $(".addInterface").click(async function () {
        document.getElementById("interfaceAction").style.display = "block";
        console.log("add interface");
    });


    $(".editInterface").click(async function () {
        document.getElementById("interfaceAction").style.display = "block";
        console.log("edit interface");
    });

    $(".deleteInterface").click(async function () {
        console.log("delete interface");
    });


});
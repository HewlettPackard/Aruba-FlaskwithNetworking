// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

$(".mobilityRoles").click(async function () {
    deviceid = $(this).attr('data-deviceid');
    document.getElementById("mobilityRoles").style.display = "block";
    document.getElementById("mobilityPolicies").style.display = "none";
    document.getElementById("mobilityInterfaces").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    // This is an async function, we have to wait until the information is returned from the Python call. 
    // Definition found in mobility.py
    roleInfo = await $.ajax({
        url: "/mcroleInfo",
        type: "POST",
        data: { deviceid: deviceid },
        success: function () {
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error finding role information";
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
    roleInfo = JSON.parse(roleInfo);
    deviceInfo = JSON.parse(deviceInfo);

    //Build the table
    roleHTML = "<table class='fwtable'>";
    roleHTML += "<tr style='background-color:black;'><td colspan='3' align='center' style='color:orange;'>Configured roles for " + deviceInfo['ipaddress'] + " (" + deviceInfo['description'] + ")</td></tr>";
    roleHTML += "<tr><td nowrap><font class='font13px'>Role name</font></td>";
    roleHTML += "<td nowrap><font class='font13px'>ACL's</font></td>";
    roleHTML += "<td width='5%'><input type='button' name='addRole' value='Add role' class='addRole'/></td></tr>";
    for (counter = 0; counter < roleInfo.length; counter++) {
        roleHTML += "<td nowrap><font class='font11px'>" + roleInfo[counter]['rname']+ "</font></td><td><font class='font11px'>";
        //Need to get the ACL information from the ACL array
        for (counter2 = 0; counter2 < roleInfo[counter]['role__acl'].length; counter2++) {
            roleHTML += roleInfo[counter]['role__acl'][counter2]['pname'] + " (" + roleInfo[counter]['role__acl'][counter2]['acl_type'] + ")&nbsp;&nbsp;&nbsp;";
        }
        roleHTML += "</font></td><td nowrap><font class='font11px'><input type='button' name='editRole' value='Edit' class='editRole'/><input type='button' name='deleteRole' value='Delete' class='deleteRole'/></font></td></tr>";
    }
    roleInfo += "</table>";
    document.getElementById("mobilityRoles").innerHTML = roleHTML;

$(".addRole").click(async function () {
    document.getElementById("roleAction").style.display = "block";
    console.log("add role");
});


$(".editRole").click(async function () {
    document.getElementById("roleAction").style.display = "block";
    console.log("edit role");
});

$(".deleteRole").click(async function () {
    document.getElementById("roleAction").style.display = "block";
    console.log("delete role");
});
    




});
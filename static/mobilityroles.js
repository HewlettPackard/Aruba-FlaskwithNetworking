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
    roleHTML = "<table class='tablewithborder'>";
    roleHTML += "<tr><td colspan='2'><font class='font13pxwhite'><center>Configured roles for " + deviceInfo['ipaddress'] + " (" + deviceInfo['description'] + ")</center></font></td></tr>";
    roleHTML += "<tr><td nowrap><font class='font13pxwhite'>Role name</font></td>";
    roleHTML += "<td nowrap><font class='font13pxwhite'>ACL's</font></td></tr>";
    for (counter = 0; counter < roleInfo.length; counter++) {
        roleHTML += "<td class='whiteBG' nowrap><font class='font11px'>" + roleInfo[counter]['rname']+ "</font></td><td class='whiteBG'><font class='font11px'>";
        //Need to get the ACL information from the ACL array
        for (counter2 = 0; counter2 < roleInfo[counter]['role__acl'].length; counter2++) {
            roleHTML += roleInfo[counter]['role__acl'][counter2]['pname'] + " (" + roleInfo[counter]['role__acl'][counter2]['acl_type'] + ")&nbsp;&nbsp;&nbsp;";
        }
        roleHTML += "</font></td></tr>";
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
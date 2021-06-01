// (C) Copyright 2020 Hewlett Packard Enterprise Development LP.


$(document).on("click", "#runningBackup", function () {
    document.getElementById("editBackup").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("configentryperpage")) {
        var e = document.getElementById("configentryperpage");
        var configentryperpage = e.options[e.selectedIndex].value;
    }
    else {
        configentryperpage = 10;
    }
    if (document.getElementById("configpageoffset")) {
        var e = document.getElementById("configpageoffset");
        var configpageoffset = e.options[e.selectedIndex].value;
    }
    else {
        configpageoffset = 0;
    }
    var e = document.getElementById("searchowner");
    var owner = e.options[e.selectedIndex].value;
    var e = document.getElementById("searchbackuptype");
    var backuptype = e.options[e.selectedIndex].value;
    var currentconfigentryperpage = document.getElementById("currentconfigentryperpage").value;
    var re = new RegExp(name + "=([^;]+)");
    var suarray = re.exec(document.cookie);
    sysuser = suarray[1];
    $("div[data-configmgr='configmgr']").load('configmgr?deviceid=' + document.getElementById('configurationManager').getAttribute('data-deviceid') + '&sysuser=' + sysuser + '&ostype=' + document.getElementById('configurationManager').getAttribute('data-ostype') + '&owner=' + owner + '&backuptype=' + encodeURIComponent(backuptype) + '&searchdescription=' + document.getElementById("searchdescription").value + '&configentryperpage=' + configentryperpage + '&configpageoffset=' + configpageoffset + '&action=runningConfig');
});

$(document).on("click", "#startupBackup", function () {
    document.getElementById("editBackup").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("configentryperpage")) {
        var e = document.getElementById("configentryperpage");
        var configentryperpage = e.options[e.selectedIndex].value;
    }
    else {
        configentryperpage = 10;
    }
    if (document.getElementById("configpageoffset")) {
        var e = document.getElementById("configpageoffset");
        var configpageoffset = e.options[e.selectedIndex].value;
    }
    else {
        configpageoffset = 0;
    }
    var e = document.getElementById("searchowner");
    var owner = e.options[e.selectedIndex].value;
    var e = document.getElementById("searchbackuptype");
    var backuptype = e.options[e.selectedIndex].value;
    var currentconfigentryperpage = document.getElementById("currentconfigentryperpage").value;
    var re = new RegExp(name + "=([^;]+)");
    var suarray = re.exec(document.cookie);
    sysuser = suarray[1];
    $("div[data-configmgr='configmgr']").load('configmgr?deviceid=' + document.getElementById('configurationManager').getAttribute('data-deviceid') + '&sysuser=' + sysuser + '&ostype=' + document.getElementById('configurationManager').getAttribute('data-ostype') + '&owner=' + owner + '&backuptype=' + encodeURIComponent(backuptype) + '&searchdescription=' + document.getElementById("searchdescription").value + '&configentryperpage=' + configentryperpage + '&configpageoffset=' + configpageoffset + '&action=startupConfig');
});

function configentryperPage() {
    document.getElementById("editBackup").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("configentryperpage")) {
        var e = document.getElementById("configentryperpage");
        var configentryperpage = e.options[e.selectedIndex].value;
    }
    else {
        configentryperpage = 10;
    }
    var configpageoffset = 0;
    var e = document.getElementById("searchowner");
    var owner = e.options[e.selectedIndex].value;
    var e = document.getElementById("searchbackuptype");
    var backuptype = e.options[e.selectedIndex].value;
    var currentconfigentryperpage = document.getElementById("currentconfigentryperpage").value;
    var masterbackup = e.options[e.selectedIndex].value;
    var currentconfigentryperpage = document.getElementById("currentconfigentryperpage").value;
    $("div[data-configmgr='configmgr']").load('configmgr?deviceid=' + document.getElementById('deviceid').value + '&owner=' + owner + '&masterbackup=' + masterbackup + '&backuptype=' + encodeURIComponent(backuptype) + '&searchconfigDescription=' + document.getElementById("searchdescription").value + '&configentryperpage=' + configentryperpage + '&configpageoffset=' + configpageoffset + '&action=searchConfig');
}

function configpageNumber() {
    document.getElementById("editBackup").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("configentryperpage")) {
        var e = document.getElementById("configentryperpage");
        var configentryperpage = e.options[e.selectedIndex].value;
    }
    else {
        configentryperpage = 10;
    }
    if (document.getElementById("configpageoffset")) {
        var e = document.getElementById("configpageoffset");
        var configpageoffset = e.options[e.selectedIndex].value;
    }
    else {
        configpageoffset = 0;
    }
    var e = document.getElementById("searchowner");
    var owner = e.options[e.selectedIndex].value;
    var e = document.getElementById("searchbackuptype");
    var backuptype = e.options[e.selectedIndex].value;
    var currentconfigentryperpage = document.getElementById("currentconfigentryperpage").value;
    var masterbackup = e.options[e.selectedIndex].value;
    var currentconfigentryperpage = document.getElementById("currentconfigentryperpage").value;
    $("div[data-configmgr='configmgr']").load('configmgr?deviceid=' + document.getElementById('configurationManager').getAttribute('data-deviceid') + '&owner=' + owner + '&masterbackup=' + masterbackup + '&backuptype=' + encodeURIComponent(backuptype) + '&searchconfigDescription=' + document.getElementById("searchdescription").value + '&configentryperpage=' + configentryperpage + '&configpageoffset=' + configpageoffset + '&action=searchConfig');
}

function changeSearch() {
    document.getElementById("editBackup").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("configentryperpage")) {
        var e = document.getElementById("configentryperpage");
        var configentryperpage = e.options[e.selectedIndex].value;
    }
    else {
        configentryperpage = 10;
    }
    if (document.getElementById("configpageoffset")) {
        var e = document.getElementById("configpageoffset");
        var configpageoffset = e.options[e.selectedIndex].value;
    }
    else {
        configpageoffset = 0;
    }
    var e = document.getElementById("searchowner");
    var searchowner = e.options[e.selectedIndex].value;
    var e = document.getElementById("searchbackuptype");
    var searchbackuptype = e.options[e.selectedIndex].value;
    var e = document.getElementById("searchmasterbackup");
    var searchmasterbackup = e.options[e.selectedIndex].value;
    var currentconfigentryperpage = document.getElementById("currentconfigentryperpage").value;
    $("div[data-configmgr='configmgr']").load('configmgr?deviceid=' + document.getElementById('configurationManager').getAttribute('data-deviceid') + '&searchowner=' + searchowner + '&searchmasterbackup=' + encodeURIComponent(searchmasterbackup) + '&searchbackuptype=' + encodeURIComponent(searchbackuptype) + '&searchdescription=' + document.getElementById("searchdescription").value + '&configentryperpage=' + configentryperpage + '&configpageoffset=' + configpageoffset + '&action=searchConfig');
}

$(document).on("click", "#restoreConfig", function () {
    var result = confirm("Are you sure that you want to restore this item?");
    if (result) {
        document.getElementById("editBackup").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
        console.log("Restore config");
    }
});

$(document).on("click", "#submitbackupChanges", async function () {
    document.getElementById("editBackup").style.display = "block";
    document.getElementById("liProgress").style.display = "none";
    id = $(this).attr('data-id');
    tableRow = $(this).attr('data-tableRow');
    masterbackup = $(this).attr('data-masterbackup');
    backuptype = $(this).attr('data-backuptype');
    backupDescription = document.getElementById("backupDescription").value;
    backupContent = document.getElementById("backupContent").value;
    deviceid = document.getElementById('configurationManager').getAttribute('data-deviceid');
    var re = new RegExp(name + "=([^;]+)");
    var suarray = re.exec(document.cookie);
    sysuser = suarray[1];
    backupInfo = await $.ajax({
        url: "/changebranchBackup",
        type: "POST",
        data: { id: id, backupDescription: backupDescription, backupContent: backupContent, sysuser: sysuser},
        success: function () {
            // Obtaining the backup was successful
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error finding backup information";
        }
    });
    backupInfo = JSON.parse(backupInfo);
    utctime = new Date(1000 * backupInfo['utctime']);
    utctime = utctime.toLocaleString();
    document.getElementById('backupContent').value = backupContent;
    document.getElementById('backupDescription').value = backupDescription;
    $("#backupDescription").prop('disabled', false);
    document.getElementById('backupTitle').innerHTML = "<font class='font13pxwhite'>Edit branch backup from master backup ID " + masterbackup + "</font>";
    document.getElementById("backupAction").style.display = "block";
    var x = document.getElementById('backupTable').rows[parseInt(tableRow, 10)].cells;
    x[parseInt(0, 10)].innerHTML = "<font class='font12px'>" + id + "</font>";
    x[parseInt(1, 10)].innerHTML = "<font class='font12px'>" + utctime + "</font>";
    x[parseInt(2, 10)].innerHTML = "<font class='font12px'>" + backupDescription + "</font>";
    x[parseInt(3, 10)].innerHTML = "<font class='font12px'>" + backuptype + "</font>";
    x[parseInt(4, 10)].innerHTML = "<font class='font12px'>Branch</font>";
    x[parseInt(5, 10)].innerHTML = "<font class='font12px'>" + sysuser + "</font>";
    x[parseInt(6, 10)].innerHTML = "<input type='submit' name='action' class='button' value='Restore' class='button' id=restoreConfig' data-id='ID' /><input type='submit' class='button' name='action' value='View' class='button' id='viewConfig' data-id='" + backupInfo['id'] + "' /><input type='submit' name='action' value='Edit' class='button' id='editConfig' data-id='" + backupInfo['id'] + "' data-masterbackup='" + backupInfo['masterbackup'] + "' /><input type='submit' name='action' value='Delete' id='deleteConfig' class='button' data-id='" + backupInfo['id'] + "'>";
});

$(document).on("click", "#editConfig", async function () {
    document.getElementById("editBackup").style.display = "block";
    document.getElementById("liProgress").style.display = "none";

    id = $(this).attr('data-id');
    tableRow = $(this).closest('tr').index();
    backupInfo = await $.ajax({
        url: "/backupInfo",
        type: "POST",
        data: { id: id },
        success: function () {
            // Obtaining the backup was successful
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error finding backup information";
        }
    });
    backupInfo = JSON.parse(backupInfo);
    document.getElementById('backupContent').value = backupInfo['configuration'];
    document.getElementById('backupDescription').value = backupInfo['description'];
    $("#backupDescription").prop('disabled', false);
    $("#backupContent").prop('disabled', false);
    document.getElementById('backupTitle').innerHTML = "<font class='font13pxwhite'>Edit branch backup from master backup ID " + backupInfo['masterbackup'] + "</font>";
    document.getElementById("backupAction").style.display = "block";
    document.getElementById('backupAction').innerHTML = "<input type='button' name='backupAction' value='Submit branch backup changes' class='button' id='submitbackupChanges' data-tableRow='" + tableRow + "' data-id='" + backupInfo['id'] + "' data-masterbackup='" + backupInfo['masterbackup'] + "'  data-backuptype='" + backupInfo['backuptype'] + "'>";
});

$(document).on("click", "#createbranchBackup", async function () {
    document.getElementById("editBackup").style.display = "block";
    document.getElementById("liProgress").style.display = "none";
    masterbackup = $(this).attr('data-masterbackup');
    var re = new RegExp(name + "=([^;]+)");
    var suarray = re.exec(document.cookie);
    sysuser = suarray[1];
    backupInfo = await $.ajax({
        url: "/createbranchBackup",
        type: "POST",
        data: { masterbackup: masterbackup },
        success: function () {
            // Obtaining the master backup was successful
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error finding backup information";
        }
    });
    backupInfo = JSON.parse(backupInfo);
    document.getElementById('backupContent').value = backupInfo['configuration'];
    document.getElementById('backupDescription').value = "Backup branch from master backup id " + masterbackup;
    $("#backupDescription").prop('disabled', false);
    document.getElementById("branchmasterbackup").value = masterbackup;
    document.getElementById("branchbackuptype").value = backupInfo['backuptype'];
    document.getElementById("branchdeviceid").value = backupInfo['deviceid'];
    document.getElementById('backupTitle').innerHTML = "<font class='font13pxwhite'>Edit branch backup</font>";  
    document.getElementById('backupAction').innerHTML = "<input type='button' name='backupAction' value='Submit branch backup' class='button' id='submitbranchBackup'>";
});


$(document).on("click", "#submitbranchBackup", async function () {
    document.getElementById("editBackup").style.display = "block";
    document.getElementById("liProgress").style.display = "none";
    var re = new RegExp(name + "=([^;]+)");
    var suarray = re.exec(document.cookie);
    sysuser = suarray[1];
    backupInfo = await $.ajax({
        url: "/submitbranchBackup",
        type: "POST",
        data: { masterbackup: document.getElementById("branchmasterbackup").value, sysuser: sysuser, deviceid: document.getElementById("branchdeviceid").value, backupcontent: document.getElementById("backupContent").value, backupdescription: document.getElementById("backupDescription").value, backuptype: document.getElementById("branchbackuptype").value },
        success: function () {
            // Obtaining the master backup was successful
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error finding backup information";
        }
    });
    var table = document.getElementById('backupTable');
    document.getElementById("editBackup").style.display = "none";
    backupInfo = JSON.parse(backupInfo);
    utctime = new Date(1000 * backupInfo['utctime']);
    utctime = utctime.toLocaleString();
    var branchHTML = "<tr>";
    branchHTML += "<td><font class='font12px'>" + backupInfo['id'] + " </font></td>";
    branchHTML += "<td><font class='font12px'>" + utctime + "</font></td>";
    branchHTML += "<td><font class='font12px'>" + backupInfo['description'] + "</font></td>";
    branchHTML += "<td><font class='font12px'>" + backupInfo['backuptype'] + "</font></td>";
    branchHTML += "<td><font class='font12px'>Branch</font></td >";
    branchHTML += "<td><font class='font12px'>" + backupInfo['owner'] + "</font></td>";
    branchHTML += "<td align='right'>";
    branchHTML += "<input type='submit' name='action' value='Restore' class='button' id='restoreConfig' data-id='" + backupInfo['id'] + "' /><input type='submit' name='action' value='View' class='button' id='viewConfig' data-id='" + backupInfo['id'] + "' /><input type='submit' name='action' value='Edit' class='button' id='editConfig' data-id='" + backupInfo['id'] + "' data-masterbackup='" + backupInfo['masterbackup'] + "'/><input type='submit' name='action' value='Delete' id='deleteConfig' class='button' data-id='" + backupInfo['id'] + "'>";
    branchHTML += "</td></tr>";
    $(table).append(branchHTML);
});



$(document).on("click", "#changebranchBackup", async function () {
    //document.getElementById("editBackup").style.display = "block";
    document.getElementById("liProgress").style.display = "none";
    backupContent = document.getElementById('backupContent').value;
    backupDescription = document.getElementById('backupDescription').value;
    var re = new RegExp(name + "=([^;]+)");
    var suarray = re.exec(document.cookie);
    sysuser = suarray[1];
    id = $(this).attr('data-id');
    masterbackup = $(this).attr('data-masterbackup');
    backuptype = $(this).attr('data-backuptype');
    deviceid = document.getElementById('configurationManager').getAttribute('data-deviceid');
    backupInfo = await $.ajax({
        url: "/changebranchBackup",
        type: "POST",
        data: { id: id, backupContent: backupContent, backupDescription:backupDescription, sysuser: sysuser },
        success: function () {
            // Saving the backup was successful
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Branch backup could not be stored";
        }
    });
  });


$(document).on("click", "#viewConfig", async function () {
    document.getElementById("editBackup").style.display = "block";
    document.getElementById("backupAction").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    id = $(this).attr('data-id');
    backupInfo = await $.ajax({
        url: "/backupInfo",
        type: "POST",
        data: { id: id },
        success: function () {
            // Obtaining the backup was successful
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error finding backup information";
        }
    });
    backupInfo = JSON.parse(backupInfo);
    document.getElementById('backupContent').value = backupInfo['configuration'];
    document.getElementById('backupDescription').value = backupInfo['description'];
    $("#backupDescription").prop('disabled', true);
    $("#backupContent").prop('disabled', true);
    document.getElementById('backupTitle').innerHTML = "<font class='font13pxwhite'>View backup</font>";
});

$(document).on("click", "#deleteConfig", function () {
    var result = confirm("Are you sure that you want to delete this item?");
    if (result) {
        document.getElementById("editBackup").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
        if (document.getElementById("configentryperpage")) {
            var e = document.getElementById("configentryperpage");
            var configentryperpage = e.options[e.selectedIndex].value;
        }
        else {
            configentryperpage = 10;
        }
        if (document.getElementById("configpageoffset")) {
            var e = document.getElementById("configpageoffset");
            var configpageoffset = e.options[e.selectedIndex].value;
        }
        else {
            configpageoffset = 0;
        }
        var e = document.getElementById("searchowner");
        var owner = e.options[e.selectedIndex].value;
        var e = document.getElementById("backuptype");
        var backuptype = e.options[e.selectedIndex].value;
        id = $(this).attr('data-id');
        var currentconfigentryperpage = document.getElementById("currentconfigentryperpage").value;
        $("div[data-configmgr='configmgr']").load('configmgr?id=' + id + '&deviceid=' + document.getElementById('configurationManager').getAttribute('data-deviceid') + '&owner=' + owner + '&backuptype=' + encodeURIComponent(backuptype) + '&searchconfigDescription=' + document.getElementById("searchconfigDescription").value + '&configentryperpage=' + configentryperpage + '&configpageoffset=' + configpageoffset + '&action=deleteBackup');
    }
});

$('.configdeviceStatus').ready(function () {

    var refresh = function () {
        if (document.getElementById('configurationManager')) {
             if (document.getElementById('deviceStatus' + document.getElementById('configurationManager').getAttribute('data-deviceid'))) {
                if (document.getElementById('deviceStatus' + document.getElementById('configurationManager').getAttribute('data-deviceid')).getAttribute('data-status') == 1) {
                    $("#runningBackup").prop('disabled', false);
                    $("#runningBackup").css('pointer-events', 'auto');
                    $("#startupBackup").prop('disabled', false);
                    $("#startupBackup").css('pointer-events', 'auto');
                }
                else {
                    $("#runningBackup").prop('disabled', true);
                    $("#runningBackup").css('pointer-events', 'none');
                    $("#startupBackup").prop('disabled', true);
                    $("#startupBackup").css('pointer-events', 'none');
                }
            }
        }

    }
    setInterval(refresh, 1000);
    refresh();
});

   
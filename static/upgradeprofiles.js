// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    $('.editField input').keyup(function () {
        var fieldisEmpty = false;
        $('.editField input').keyup(function () {
            $('.editField input').each(function () {
                if ($(this).val().length == 0) {
                    fieldisEmpty = true;
                }
            });
            if (fieldisEmpty) {
                $('.editActions input').attr('disabled', 'disabled');
            } else {
                $('.editActions input').attr('disabled', false);
            }
        });
    });

    $('.addField input').keyup(function () {
        var fieldisEmpty = false;
        $('.addField input').keyup(function () {
            $('.addField input').each(function () {
                if ($(this).val().length == 0) {
                    fieldisEmpty = true;
                }
            });
            if (fieldisEmpty) {
                $('.addActions input').attr('disabled', 'disabled');
            } else {
                $('.addActions input').attr('disabled', false);
            }
        });
    });


    $(".addScheduler").click(async function () {
        document.getElementById("addSchedule").style.display = "block";
        document.getElementById("editSchedule").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
        document.getElementById("monitorUpgrade").style.display = "none";
    });

    $(".editScheduler").click(async function () {
        scheduleid = $(this).attr('data-scheduleid');
        document.getElementById("editSchedule").style.display = "block";
        document.getElementById("addSchedule").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
        document.getElementById("monitorUpgrade").style.display = "none";
        tableRow = $(this).closest('tr').index();
        scheduleInfo = await $.ajax({
            url: "/scheduleInfo",
            type: "POST",
            data: { id: scheduleid },
            success: function () {
                // Obtaining the device image information was successful
            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                progressInfo.innerHTML = "Error finding scheduler information";
            }
        });
        scheduleInfo = JSON.parse(scheduleInfo);
    });  

 });



$(document).on("click", "#submitUpgrade", async function () {
    if ($("#addrebootafterUpgrade").prop("checked")) {
        var reboot = 1;
    }
    else {
        var reboot = 0;
    }
    scheduleInfo = await $.ajax({
        url: "/deviceupgradeActions",
        type: "POST",
        data: { action: "submitUpgrade", switchid: $('#deviceupgrade').attr('data-deviceid'), schedule: document.getElementById("adddatetime").value, software: $("#addsoftwareimage option:selected").val(), imagepartition: $("#addupgradepartition option:selected").val(), activepartition: $("#addactivepartition option:selected").val(), reboot: reboot },
        success: function () {
            document.getElementById("addUpgrade").style.display = "none";
        },
        error: function () {
            // Error handling
        }
    });
    scheduleInfo = JSON.parse(scheduleInfo);
    if (scheduleInfo['message'] != "") {
        document.getElementById("liProgress").style.display = "block";
        progressInfo.innerHTML = scheduleInfo['message'];
    }
    $('#upgradeExists').data('id', scheduleInfo['activeUpdate']['id']);
    monitorUpgrade(scheduleInfo);
});


$(document).on("click", "#searchScheduler", function () {
    document.getElementById("editSchedule").style.display = "none";
    document.getElementById("addSchedule").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("entryperpage")) {
        var e = document.getElementById("entryperpage");
        var entryperpage = e.options[e.selectedIndex].value;
    }
    else {
        entryperpage = 10;
    }
    if (document.getElementById("pageoffset")) {
        var e = document.getElementById("pageoffset");
        var pageoffset = e.options[e.selectedIndex].value;
    }
    else {
        pageoffset = 0;
    }
    $("div[data-imagemgr='imagemgr']").load('upgradescheduler?entryperpage=' + entryperpage + '&pageoffset=' + pageoffset + '&action=searchImage');
});



$(document).on("click", ".editdeviceupgrade", async function () {
    scheduleInfo = await $.ajax({
        url: "/checkupgradeStatus",
        type: "POST",
        data: { id: $('#upgradeExists').data('id') },
        success: function () {
            // Obtaining the device image information was successful
            document.getElementById("liProgress").style.display = "none";
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            progressInfo.innerHTML = "Error finding scheduler information";
        }
    });
    if (scheduleInfo != "") {
        scheduleInfo = JSON.parse(scheduleInfo);
        $("#editupgradepartition").val(scheduleInfo['imagepartition']);
        $("#editactivepartition").val(scheduleInfo['activepartition']);
        $("#editsoftwareimage").val(scheduleInfo['software']);
        $('#upgradeExists').data('id', scheduleInfo['id']);

        if (scheduleInfo['schedule'] != "null") {
            document.getElementById("editdatetime").value = scheduleInfo['schedule'];
        }
        if (scheduleInfo['reboot'] == 1) {
            $("#editrebootafterUpgrade").prop("checked", true);
        }
    }
    document.getElementById("editUpgrade").style.display = "block";
    if ($('#initmonitorUpgrade').length) {
        document.getElementById("initmonitorUpgrade").style.display = "none";
    }
    document.getElementById("monitorUpgrade").style.display = "none";
});


$(document).on("click", ".removedeviceUpgrade", async function () {
    id = $('#upgradeExists').data('id');
    scheduleInfo = await $.ajax({
        url: "/deleteUpgrade",
        type: "POST",
        data: { id: id },
        success: function () {
            //Clear the data value of the upgrade status because I don't want the app to check the scheduled upgrade anymore. It has been deleted.
            $('#upgradeExists').data('id', '');
            document.getElementById("liProgress").style.display = "block";
            progressInfo.innerHTML = "Scheduled upgrade has been removed";
            if ($('#initmonitorUpgrade').length) {
                document.getElementById("initmonitorUpgrade").style.display = "none";
            }
            document.getElementById("monitorUpgrade").style.display = "none";
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            progressInfo.innerHTML = "Error removing schedule upgrade";
        }
    });
}); 


$(document).on("click", "#submitupgradeChanges", async function () {
    if ($("#editrebootafterUpgrade").prop("checked")) {
        var reboot = 1;
    }
    else {
        var reboot = 0;
    }
    scheduleInfo = await $.ajax({
        url: "/deviceupgradeActions",
        type: "POST",
        data: { action: "submitupgradeChanges", id: $('#upgradeExists').data('id'), switchid: $('#deviceupgrade').attr('data-deviceid'), schedule: document.getElementById("editdatetime").value, software: $("#editsoftwareimage option:selected").val(), imagepartition: $("#editupgradepartition option:selected").val(), activepartition: $("#editactivepartition option:selected").val(), reboot: reboot },
        success: function () {
            document.getElementById("editUpgrade").style.display = "none";
            document.getElementById("monitorUpgrade").style.display = "block";
        },
        error: function () {
            //Error handling
        }
    });
    scheduleInfo = JSON.parse(scheduleInfo);
    if (scheduleInfo['message'] != "") {
        document.getElementById("liProgress").style.display = "block";
        progressInfo.innerHTML = scheduleInfo['message'];
    }
    // Update the fields in the form. If the initmonitorupgrade div exists, we need to update the initmonitorupgrade entries
    $('#monitorupgradepartition').empty().append("<font class='font11px'>" + scheduleInfo['activeUpdate']['imagepartition'].charAt(0).toUpperCase() + scheduleInfo['activeUpdate']['imagepartition'].slice(1) + "</font>");
    $('#monitoractivepartition').empty().append("<font class='font11px'>" + scheduleInfo['activeUpdate']['activepartition'].charAt(0).toUpperCase() + scheduleInfo['activeUpdate']['activepartition'].slice(1) + "</font>");
    $('#monitordatetime').empty().append("<font class='font11px'>" + scheduleInfo['activeUpdate']['schedule'] + "</font>");
    if (scheduleInfo['activeUpdate']['reboot'] == 1) {
        $("#monitorrebootafterUpgrade").prop("checked", true);
    }
    monitorUpgrade(scheduleInfo);
});


async function switchReboot(deviceid, id) {
    rebootInfo = await $.ajax({
        url: "/switchReboot",
        type: "POST",
        data: { deviceid: deviceid, id:id },
        success: function () {
            // Switch rebooted successfully
            $('.upgradeStatus').empty().append("<font class='font11px'>Switch has been rebooted</font>");
            if ($('#rebootSwitch' + id)) {
                $('#rebootSwitch' + id).empty();
                document.getElementById("showSchedule").style.display = "none";
            }
            if ($("#showschedulerebootSwitch").length > 0) {
                $("#showschedulerebootSwitch").empty().append("<font class='font11px'>Switch has been rebooted</font>");
            }
        },
        error: function () {
            //document.getElementById("liProgress").style.display = "block";
            //progressInfo.innerHTML = "Error rebooting switch";
        }
    });
}


async function removescheduleUpgrade(id) {
    scheduleInfo = await $.ajax({
        url: "/deleteUpgrade",
        type: "POST",
        data: { id: id },
        success: function () {
            //Clear the data value of the upgrade status because I don't want the app to check the scheduled upgrade anymore. It has been deleted.
            $('#scheduletableRow'+ id).remove();
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            progressInfo.innerHTML = "Error removing schedule upgrade";
        }
    });
} 




function entryperPage() {
    document.getElementById("editSchedule").style.display = "none";
    document.getElementById("addSchedule").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("entryperpage")) {
        var e = document.getElementById("entryperpage");
        var entryperpage = e.options[e.selectedIndex].value;
    }
    else {
        entryperpage = 10;
    }
    var pageoffset = 0;
    $("div[data-imagemgr='imagemgr']").load('upgradescheduler?entryperpage=' + entryperpage + '&pageoffset=' + pageoffset + '&action=searchImage');
}

function pageNumber() {
    document.getElementById("editSchedule").style.display = "none";
    document.getElementById("addSchedule").style.display = "none";
    document.getElementById("liProgress").style.display = "none";
    if (document.getElementById("entryperpage")) {
        var e = document.getElementById("entryperpage");
        var entryperpage = e.options[e.selectedIndex].value;
    }
    else {
        entryperpage = 10;
    }
    if (document.getElementById("pageoffset")) {
        var e = document.getElementById("pageoffset");
        var pageoffset = e.options[e.selectedIndex].value;
    }
    else {
        pageoffset = 0;
    }
    $("div[data-imagemgr='imagemgr']").load('upgradescheduler?entryperpage=' + entryperpage + '&pageoffset=' + pageoffset + '&action=searchImage');
}


function checkupgradeForm(elementinfo) {
    // Need to check if all the required fields are filled in. If that's the case, enable the submit button
    // Update button based on the action (is it add or edit)
    if ($(elementinfo).data("action") == "add") {
        if ($("#addupgradepartition").val() && $("#addactivepartition").val() && $("#addsoftwareimage").val()) {
            // Everything is selected, enable the submit button
            $("#submitUpgrade").prop('disabled', false);
            $("#submitUpgrade").css('opacity', '1');
            $("#submitUpgrade").css('pointer-events', 'auto');
        }
        else {
            $("#submitUpgrade").prop('disabled', true);
            $("#submitUpgrade").css('opacity', '1');
            $("#submitUpgrade").css('pointer-events', 'none');


        }
    }
};

function monitorUpgrade(scheduleInfo) {
    document.getElementById("monitorUpgrade").style.display = "block";
    document.getElementById("editupgradeEnable").style.display = "none";
    $('#upgradeExists').data('id', scheduleInfo['activeUpdate']['id']);
    $('#editUpgrade').data('id', scheduleInfo['activeUpdate']['id']);
    $('#monitorupgradepartition').empty().append("<font class='font11px'>" + scheduleInfo['activeUpdate']['imagepartition'].charAt(0).toUpperCase() + scheduleInfo['activeUpdate']['imagepartition'].slice(1)  + "</font>");
    $('#monitoractivepartition').empty().append("<font class='font11px'>" + scheduleInfo['activeUpdate']['activepartition'].charAt(0).toUpperCase() + scheduleInfo['activeUpdate']['activepartition'].slice(1) + "</font>");    

    if (scheduleInfo['activeUpdate']['schedule']) {
        $('#monitordatetime').empty().append("<font class='font11px'>" + scheduleInfo['activeUpdate']['schedule'].toString().slice(0, -3) + "</font>");
    }
    else {
        $('#monitordatetime').empty();
    }
    if (scheduleInfo['activeUpdate']['reboot'] == 1) {
        $("#monitorrebootafterUpgrade").prop("checked", true);
    }
    swInfo = scheduleInfo['images'].filter(function (swInfo) { return swInfo.id == scheduleInfo['activeUpdate']['software'] });
    $('#monitorsoftwareimage').empty().append("<font class='font11px'>" + swInfo[0]['name'] + " (" + swInfo[0]['filename'] + ")</font>"); 
}


async function showupgradeDetails(id) {
    $('#showSchedule').data('id', id);
    var refresh = async function () {

        if ($('#showSchedule').data('id') == id) {



            var upgradestatus = { '0': 'Not started', '1': 'Upgrade initiated', '5': 'Copy software onto the switch', '10': 'Software copied successfully', '20': 'Software copied successfully: switch is rebooted', '50': 'There is another software upgrade in progress', '100': 'Software upgrade completed successfully', '110': 'Software upgrade completed successfully: reboot is required' };
            scheduleInfo = await $.ajax({
                url: "/upgradeStatus",
                type: "POST",
                data: { id: id },
                success: function () {
                    // Obtaining the software update information was successful
                },
                error: function () {
                    document.getElementById("liProgress").style.display = "block";
                    progressInfo.innerHTML = "Error finding software upgrade information";
                }
            });
            scheduleInfo = JSON.parse(scheduleInfo);
            switchInfo = scheduleInfo['switchresult'];
            document.getElementById("showSchedule").style.display = "block";
            //Fill all the showschedule divs with information
            $('#showscheduleTitle').empty().append("<font class='font13pxwhite'><center>Software upgrade information for " + switchInfo['description'] + " (" + switchInfo['ipaddress'] + ")</center></font>");
            if (scheduleInfo['softwareinfo']) {
                softwareInfo = scheduleInfo['softwareinfo'].replace("\\", "");
                softwareInfo = JSON.parse(softwareInfo);
            }
            else {
                softwareInfo = { primary_version: "", secondary_version: "", default_image: "" };
            }
            if (scheduleInfo['softwareinfoafter']) {
                softwareinfoAfter = scheduleInfo['softwareinfoafter'].replace("\\", "");
                softwareinfoAfter = JSON.parse(softwareinfoAfter);
            }
            else {
                softwareinfoAfter = { primary_version: "", secondary_version: "", default_image: "" };
            }
            $('.bprimaryImage').empty().append("<font class='font10px'>" + softwareInfo['primary_version'].charAt(0).toUpperCase() + softwareInfo['primary_version'].slice(1) + "</font>");
            $('.bsecondaryImage').empty().append("<font class='font10px'>" + softwareInfo['secondary_version'].charAt(0).toUpperCase() + softwareInfo['secondary_version'].slice(1) + "</font>");
            $('.bdefaultImage').empty().append("<font class='font10px'>" + softwareInfo['default_image'].charAt(0).toUpperCase() + softwareInfo['default_image'].slice(1) + "</font>");
            $('.aprimaryImage').empty().append("<font class='font10px'>" + softwareinfoAfter['primary_version'].charAt(0).toUpperCase() + softwareinfoAfter['primary_version'].slice(1) + "</font>");
            $('.asecondaryImage').empty().append("<font class='font10px'>" + softwareinfoAfter['secondary_version'].charAt(0).toUpperCase() + softwareinfoAfter['secondary_version'].slice(1) + "</font>");
            $('.adefaultImage').empty().append("<font class='font10px'>" + softwareinfoAfter['default_image'].charAt(0).toUpperCase() + softwareinfoAfter['default_image'].slice(1) + "</font>");
            if (scheduleInfo['schedule']) {
                $('.upgradeSchedule').empty().append("<font class='font10px'>" + scheduleInfo['schedule'].toString().slice(0, -3) + "</font>");
            }
            else {
                $('.upgradeSchedule').empty().append("<font class='font10px'>No schedule</font>");
            }
            if (scheduleInfo['starttime']) {
                $('.upgradeStart').empty().append("<font class='font10px'>" + scheduleInfo['starttime'].toString().slice(0, -3) + "</font>");
            }
            if (scheduleInfo['endtime']) {
                $('.upgradeEnd').empty().append("<font class='font10px'>" + scheduleInfo['endtime'].toString().slice(0, -3) + "</font>");
            }
            if (scheduleInfo['starttime'] && scheduleInfo['endtime']) {
                var duration = Math.abs((new Date(scheduleInfo['endtime']) - new Date(scheduleInfo['starttime'])) / 1000);
                var days = Math.floor(duration / (3600 * 24));
                duration -= days * 3600 * 24;
                var hours = Math.floor(duration / 3600);
                duration -= hours * 3600;
                var minutes = Math.floor(duration / 60);
                duration -= minutes * 60;
                $('.upgradeduration').empty().append("<font class='font10px'>" + days + " days, " + hours + " hours, " + minutes + " minutes, " + duration + " seconds</font>");
            }
            else {
                $('.upgradeDuration').empty().append("<font class='font10px'>Upgrade has not finished yet</font>");
            }
            if (scheduleInfo['reboot'] == 1) {
                $('.rebootafterUpgrade').empty().append("<font class='font10px'>Yes</font>");
            }
            else {
                $('.rebootafterUpgrade').empty().append("<font class='font10px'>No</font>");
            };
            if (scheduleInfo['status'] == 110) {
                // This was an upgrade without reboot. Need to add a button that allows manual reboot
                $('.showschedulerebootSwitch').empty().append("<input type='button' name='rebootSwitch' class='button' class='switchReboot' onClick='switchReboot(" + scheduleInfo['switchid'] + "," + scheduleInfo['id'] + ");' value='Reboot'>");
            }
            $('.upgradeStatus').empty().append("<font class='font10px'>" + upgradestatus[scheduleInfo['status']] + "</font>");


        }


    }
    setInterval(refresh, 5000);
    refresh();
}


$('.statusOverview').ready(function () {
    var refresh = async function () {
        statusOverview = document.getElementsByClassName('statusOverview');
        for (var i = 0; i < statusOverview.length; i++) {
            id = statusOverview.item(i).getAttribute('data-id');
            await $.ajax({
                type: "POST",
                data: { 'id': id },
                url: "/upgradeStatus",
                success: function (response) {
                    var upgradestatus = {'0': 'Not started', '1': 'Upgrade initiated', '5': 'Copy software onto the switch', '10': 'Software copied successfully', '20': 'Software copied successfully: switch is rebooted', '50': 'There is another software upgrade in progress', '100': 'Software upgrade completed successfully', '110': 'Software upgrade completed successfully: reboot is required' };
                    response = JSON.parse(response);
                    //Update the status
                    if (typeof response['status'] !== 'undefined') {
                        $('#upgradestatus' + id).empty().append("<font class='font10px'>" + upgradestatus[response['status']] + "</font>");
                    }
                    if (response["softwareinfo"] !== "") {
                        var softwareinfo = JSON.parse(response['softwareinfo']);
                        if ("current_version" in softwareinfo) {
                            $('#softwareinfo' + id).empty().append("<font class='font10px'>" + softwareinfo['current_version'] + "</font>");
                        }
                        else {
                            if (softwareinfo['default_image'] == "Primary") {
                                $('#softwareinfo' + id).empty().append("<font class='font10px'>" + softwareinfo['primary_version'] + "</font>");
                            }
                            else {
                                $('#softwareinfo' + id).empty().append("<font class='font10px'>" + softwareinfo['secondary_version'] + "</font>");
                            }
                        }

                    }
                    if (response["softwareinfoafter"] !== "") {
                        var softwareinfoafter = JSON.parse(response['softwareinfoafter']);
                        if ("current_version" in softwareinfoafter) {
                            $('#softwareinfoafter' + id).empty().append("<font class='font10px'>" + softwareinfoafter['current_version'] + "</font>");
                        }
                        else {
                            if (softwareinfoafter['default_image'] == "Primary") {
                                $('#softwareinfoafter' + id).empty().append("<font class='font10px'>" + softwareinfoafter['primary_version'] + "</font>");
                            }
                            else {
                                $('#softwareinfoafter' + id).empty().append("<font class='font10px'>" + softwareinfoafter['secondary_version'] + "</font>");
                            }
                        }
                    }
                    if ( response['status'] > 99) {
                        var duration = Math.abs((new Date(response['endtime']) - new Date(response['starttime'])) / 1000);
                        var days = Math.floor(duration / (3600 * 24));
                        duration -= days * 3600 * 24;
                        var hours = Math.floor(duration / 3600);
                        duration -= hours * 3600;
                        var minutes = Math.floor(duration / 60);
                        duration -= minutes * 60;
                        $('#upgradeduration' + id).empty().append("<font class='font10px'>" + days + " days, " + hours + " hours, " + minutes + " minutes, " + duration + " seconds</font>");
                    }
                    else {
                        $('#upgradeduration' + id).empty();
                    }
                    if (response['status'] > 0) {
                        if ($('#removescheduleSpan' + id)) {
                            $('#removescheduleSpan' + id).empty();
                        }
                    }
                },
                error: function () {
                    console.log("There is an error obtaining status information");
                }
            })
        }
    };
    setInterval(refresh, 5000);
    refresh();
});

$('.upgradeStatus').ready(function () {
    // Only check if the upgrade is selected. The initmonitorUpgrade or monitorUpgrade div have to exist
    var refresh = async function () {
        if ($('#upgradeExists').data('id')) {
            // If the status is >0 or <100, then there is an active upgrade and we need to disable the edit button. In addition, show the upgrade status
            scheduleInfo = await $.ajax({
                url: "/checkupgradeStatus",
                type: "POST",
                data: { id: $('#upgradeExists').data('id') },
                success: function () {
                    // Obtaining the device image information was successful
                    document.getElementById("liProgress").style.display = "none";
                },
                error: function () {
                    document.getElementById("liProgress").style.display = "block";
                    progressInfo.innerHTML = "Error finding scheduler information";
                }
            });
            if (scheduleInfo != "null") {
                scheduleInfo = JSON.parse(scheduleInfo);
                if (scheduleInfo['status'] > 0) {
                    //The backup job is already running. Need to display the progress and remove the edit button
                    var upgradestatus = { '1': 'Upgrade initiated', '5': 'Copy software onto the switch', '10': 'Software copied successfully', '20': 'Software copied successfully: switch is rebooted', '50': 'There is another software upgrade in progress', '100': 'Software upgrade completed successfully', '110': 'Software upgrade completed successfully: reboot is required' };
                    $('.upgradeStatus').html("<font class='font11px'>" + upgradestatus[scheduleInfo['status']] + "</font>");
                    $("#submitupgradeChanges").prop('disabled', true);
                    if ($('#initmonitorUpgrade').length) {
                        document.getElementById("initeditupgradeEnable").style.display = "none";
                    }
                    document.getElementById("editupgradeEnable").style.display = "none";
                    // Depending on the status we might need to update some other fields
                    if (scheduleInfo['status'] > 99) {
                        swInfo = JSON.parse(scheduleInfo['softwareinfoafter']);
                        // Upgrade was successful. We also need to update all the other fields in the status
                        $('.monitordefaultImage').empty().append("<font class='font11px'>" + swInfo['default_image'].charAt(0).toUpperCase() + swInfo['default_image'].slice(1) + "</font>");
                        $('.monitorprimaryImage').empty().append("<font class='font11px'>" + swInfo['primary_version'].charAt(0).toUpperCase() + swInfo['primary_version'].slice(1) + "</font>");
                        $('.monitorsecondaryImage').empty().append("<font class='font11px'>" + swInfo['secondary_version'].charAt(0).toUpperCase() + swInfo['secondary_version'].slice(1) + "</font>");
                        $('.monitorupgradepartition').empty().append("<font class='font11px'>Completed</font>");
                        $('.monitoractivepartition').empty().append("<font class='font11px'>Completed</font>");
                        $('.monitorsoftwareimage').empty().append("<font class='font11px'>Completed</font>");
                        $('.monitordatetime').empty().append("<font class='font11px'>Completed</font>");
                        if (scheduleInfo['status'] == 110) {
                            // This was an upgrade without reboot. Need to add a button that allows manual reboot
                            $('.upgradeStatus').html("<font class='font11px'>" + upgradestatus[scheduleInfo['status']] + "</font><input type='button' name='rebootSwitch' class='button' class='switchReboot' onClick='switchReboot(" + scheduleInfo['switchid'] + "," + scheduleInfo['id'] + ");' value='Reboot'>");
                        }
                        if (scheduleInfo['status'] > 0) {
                            if ($('#removescheduleSpan' + id)) {
                                $('#removescheduleSpan' + id).empty();
                            }
                        }

                    }
                }
                else {
                    //We should not show the edit button immediately because it could be that the scheduler has not set the status to >0 yet.
                    if (scheduleInfo['schedule'] !== "" || scheduleInfo['schedule'] !== None) {
                        $("#submitupgradeChanges").prop('disabled', false);
                        if ($('#initmonitorUpgrade').length) {
                            document.getElementById("initeditupgradeEnable").style.display = "inline";
                        }
                        document.getElementById("editupgradeEnable").style.display = "inline";
                    }
                }
            }
        }
    };
    setInterval(refresh, 3000);
    refresh();
});







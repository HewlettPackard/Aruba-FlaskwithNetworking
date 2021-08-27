// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    $('.requiredField input').keyup(function () {
        var fieldisEmpty = false;
        $('.requiredField input').keyup(function () {
            $('.requiredField input').each(function () {
                if ($(this).val().length == 0) {
                    fieldisEmpty = true;
                }
            });
            if (fieldisEmpty) {
                $('.requiredActions').attr('disabled', 'disabled');
                $('.requiredActions').css('text-decoration', 'none');
                $('.requiredActions').css('opacity', '0.1');
            } else {
                $('.requiredActions').attr('disabled', false);
                $('.requiredActions').css('opacity', '1');
            }
        });
    });
});



$('.profilestatusOverview').ready(function () {
    var refresh = async function () {
        profilestatusOverview = document.getElementsByClassName('profilestatusOverview');
        for (var i = 0; i < profilestatusOverview.length; i++) {
            profileid = profilestatusOverview.item(i).getAttribute('data-profileid');
            await $.ajax({
                type: "POST",
                data: { 'profileid': profileid },
                url: "/upgradeprofileStatus",
                success: function (response) {
                    var upgradestatus = { '0': 'Not started', '1': 'Upgrade initiated', '5': 'Copy software onto the switch', '10': 'Software copied successfully', '20': 'Software copied successfully: switch is rebooted', '50': 'There is another software upgrade in progress', '60': 'Upgrade profile is active', '100': 'Software upgrade completed successfully', '110': 'Software upgrade completed successfully: reboot is required' };
                    response = JSON.parse(response);
                    //Update the status
                    if (typeof response['status'] !== 'undefined') {
                        $('#upgradeprofilestatus' + profileid).empty().append("<font class='font10px'>" + upgradestatus[response['status']] + "</font>");
                    }
                    //if (response['status'] > 99) {
                    //    var duration = Math.abs((new Date(response['endtime']) - new Date(response['starttime'])) / 1000);
                    //    var days = Math.floor(duration / (3600 * 24));
                    //    duration -= days * 3600 * 24;
                    //    var hours = Math.floor(duration / 3600);
                    //    duration -= hours * 3600;
                    //    var minutes = Math.floor(duration / 60);
                    //    duration -= minutes * 60;
                    //    $('#upgradeduration' + id).empty().append("<font class='font10px'>" + days + " days, " + hours + " hours, " + minutes + " minutes, " + duration + " seconds</font>");
                    //}
                    //else {
                    //    $('#upgradeduration' + id).empty();
                    //}
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


$(document).on("click", ".addProfile", async function () {
    $('#phprofileInfo').attr('data-addoredit', 'add');
    $('#phprofileInfo').attr('data-divname', 'addDevice');
    $('#phprofileInfo').attr('data-assignedDevices', '[]');
    $('#phprofileInfo').attr('data-availableDevices', '[]');
    $("#selectdevicesDiv").empty();
    $("#editProfile").empty();
    $("#assignsoftwareDiv").empty();
    $("#assigneddevicesDiv").empty();
    $("#availabledevicesDiv").empty();
    $('#addProfile').attr('style', 'display: block');
    $('#assigneddevicesDiv').attr('style', 'display: none');
    $('#availabledevicesDiv').attr('style', 'display: none');
    $('#assignsoftwareDiv').attr('style', 'display: none');
    $('#showprofileInfo').attr('style', 'display: none');
    var profileInfo = {};
    profileInfo['divname'] = "selectDevices";
    await selectDevices(profileInfo);
});


$(document).on("mouseenter mouseleave", ".attributeTooltip", async function (event) {
    if (event.type == "mouseenter") {
        var left = event.pageX - 310;
        var top = event.pageY + 10;
        assignedattrInfo = await $.ajax({
            url: "/showassignedAttributes",
            type: "POST",
            data: { deviceid: $(this).attr('data-deviceid') },
            success: function () {
            },
            error: function () {
                // Error obtaining device attribute list
                $('#transparentOverlay').attr('style', 'display: none');
            }
        });
        $("#showdaTooltip").css({
            position: 'absolute',
            zIndex: 5000,
            left: left,
            top: top,
            paddingLeft: 0,
            paddingTop: 0,
            paddingRight: 0,
            paddingBottom: 0,
            backgroundColor: 'transparent',
            "text-align": "center",
            width: '350px',
        });
        // Construct the innerHTML
        attrsetHTML = "<table class='tablewithborder' style='max-width: 350px;'>";
        attrsetHTML += "<tr class='tableTitle'>";
        attrsetHTML += "<td width='40%' align='left' nowrap><font class='font12pxwhite'>Attribute name</font></td>";
        attrsetHTML += "<td width='20%' align='left' nowrap><font class='font12pxwhite'>Type</font></td>";
        attrsetHTML += "<td width='40%' align='left' nowrap><font class='font12pxwhite'>Value</font></td>";
        attrsetHTML += "</tr>";
        assignedattrInfo = JSON.parse(assignedattrInfo);
        for (var i = 0; i < assignedattrInfo.length; i++) {
            attrsetHTML += "<tr>";
            attrsetHTML += "<td class='whiteBG' nowrap><font class='font10px'>" + assignedattrInfo[i]['name'] + "</font></td>";
            attrsetHTML += "<td class='whiteBG'><font class='font10px'>" + assignedattrInfo[i]['type'].charAt(0).toUpperCase() + assignedattrInfo[i]['type'].slice(1) + "</font></td>";
            if (assignedattrInfo[i]['type'] == "boolean" && assignedattrInfo[i]['value'] == "1") {
                attrsetHTML += "<td class='whiteBG' nowrap><font class='font10px'>True</font></td>";
            }
            else if (assignedattrInfo[i]['type'] == "boolean" && assignedattrInfo[i]['value'] == "0") {
                attrsetHTML += "<td class='whiteBG' nowrap><font class='font10px'>True</font></td>"
            }
            else {
                attrsetHTML += "<td class='whiteBG' nowrap><font class='font10px'>" + assignedattrInfo[i]['value'] + "</font></td>";
            }
            attrsetHTML += "</tr>";
        }
        attrsetHTML += "</table>";
        $('#showdaTooltip').empty().append(attrsetHTML);
        $('#showdaTooltip').show();
    } else {
        $('#showdaTooltip').empty();
        $('#showdaTooltip').hide();
    }
}); 


$(document).on("mouseenter mouseleave", ".showupgradeprofileDevices", async function (event) {
    if (event.type == "mouseenter") {
        var left = event.pageX - 200;
        var top = event.pageY + 10;
        profileDevices = await $.ajax({
            url: "/upgradeprofileDevices",
            type: "POST",
            data: { profileid: $(this).attr('data-profileid') },
            success: function () {
            },
            error: function () {
                // Error obtaining device list from profile
                $('#transparentOverlay').attr('style', 'display: none');
            }
        });
        $("#showdaTooltip").css({
            position: 'absolute',
            zIndex: 5000,
            left: left,
            top: top,
            paddingLeft: 0,
            paddingTop: 0,
            paddingRight: 0,
            paddingBottom: 0,
            backgroundColor: 'transparent',
            "text-align": "center",
            width: '450px',
        });
        // Construct the innerHTML
        profileDevices = JSON.parse(profileDevices);
        if (typeof profileDevices === 'string' || profileDevices instanceof String) {
            console.log(typeof (profileDevices['deviceattributes']));
            profileDevices = JSON.parse(profileDevices);
        }
        pdHTML = "<table class='tablewithborder' style='max-width: 450px;' align='left'>";
        pdHTML += "<tr class='tableTitle'>";
        pdHTML += "<td width='30%' align='center' nowrap><font class='font12pxwhite'>IP address</font></td>";
        pdHTML += "<td width='50%' align='center'><font class='font12pxwhite'>Description</font></td>";
        pdHTML += "<td width='20%' align='center'><font class='font12pxwhite'>OS</font></td>";
        pdHTML += "</tr>";
        for (var i = 0; i < profileDevices.length; i++) {
            pdHTML += "<tr>";
            pdHTML += "<td class='whiteBG'><font class='font10px'>" + profileDevices[i]['ipaddress'] + "</font></td>";
            pdHTML += "<td class='whiteBG' nowrap><font class='font10px'>" + profileDevices[i]['description'] + "</font></td>";
            pdHTML += "<td class='whiteBG' nowrap><font class='font10px'>" + profileDevices[i]['ostype'] + "</font></td>";         
            pdHTML += "</tr>";
        }
        pdHTML += "</table>";
        $('#showdaTooltip').empty().append(pdHTML);
        $('#showdaTooltip').show();
    } else {
        $('#showdaTooltip').hide();
    }
});



function manageattributeDivs(showDiv) {
    $('.sbip').attr('style', 'display: none');
    $('.sbdescription').attr('style', 'display: none');
    $('.sbattribute').attr('style', 'display: none');
    $('.sbattributeValue').attr('style', 'display: none');
    $('.sbattributeList').attr('style', 'display: none');
    $('.sbattributeBoolean').attr('style', 'display: none');
    $('#showdaTooltip').hide();
    $('.searchDevice').attr('style', 'display: inline-block');
    if (showDiv != "") {
        $('.' + showDiv).attr('style', 'display: inline-block');
    }
}

async function editProfile(profileid) {
    $('#phprofileInfo').attr('data-addoredit', 'edit');
    $('#phprofileInfo').attr('data-divname', 'editProfile');
    $('#phprofileInfo').attr('data-availableDevices', '[]');
    $('#phprofileInfo').attr('data-profileid', profileid);
    showmessageBar("Obtaining profile information");
    $('#transparentOverlay').attr('style', 'display: block');
    $('#editProfile').attr('style', 'display: block');
    $('#availabledevicesDiv').attr('style', 'display: none');
    $('#showprofileInfo').attr('style', 'display: none');
    profileInfo = await $.ajax({
        url: "/upgradeprofileInfo",
        type: "POST",
          data: {profileid: profileid},
          success: function () {
             // Obtaining the upgrade profile was successful
          },
          error: function () {
              showmessageBar("Error finding upgrade profile information");
              $('#transparentOverlay').attr('style', 'display: none');
          }
      });
    profileInfo = JSON.parse(profileInfo);
    $('#editprofileid').val(profileInfo['id']);
    $('#editprofilename').val(profileInfo['name']);
    $('#editupgradepartition').val(profileInfo['upgradepartition']);
    $('#editactivepartition').val(profileInfo['activepartition']);
    console.log(profileInfo['schedule']);
    $('#editscheduletime').val(profileInfo['schedule'].toString().slice(0, -3));
    if (profileInfo['reboot'] == 1) {
        $("#editrebootafterUpgrade").prop("checked", true);
    }
    profileInfo['action'] == "";
    $('#phprofileInfo').attr('data-assignedDevices', profileInfo['devicelist']);
    $('#phprofileInfo').attr('data-softwareimages', profileInfo['softwareimages']);
    await devicesAssigned(profileInfo['devicelist'], "[]", profileInfo);
    await assignsoftwaretoSwitches(profileInfo);
}


async function selectDevices(profileInfo) {
    $('#phprofileInfo').attr('data-divname', 'selectDevices');
    $('#phprofileInfo').attr('data-availableDevices','[]');
    $('#availabledevicesDiv').empty();
    $('#availabledevicesDiv').attr('style', 'display: none');
    $('#assignsoftwareDiv').empty();
    $('#assignsoftwareDiv').attr('style', 'display: none');
    deviceAttributes = await (getdeviceAttributes());
    if (typeof profileInfo === 'string' || profileInfo instanceof String) {
        profileInfo = JSON.parse(profileInfo);
    }
    pHTML = "<hr>";
    pHTML += "<table class='tablenoborder' id='" + $('#phprofileInfo').attr('data-addoredit') + "profileTable'>";
    pHTML += "<tr><td width='10%' nowrap><font class='font11px'>Search devices</font></td>";
    pHTML += "<td width='10%'><select name='searchType' id='searchType' onchange='showsearchOptions()'>";
    pHTML += "<option value=''>Select search criteria</option>";
    pHTML += "<option value='ipaddress'>IP address</option>";
    pHTML += "<option value='description'>Description</option>";
    pHTML += "<option value='attribute'>Device attribute</option>";
    pHTML += "</select></td>";
    pHTML += "<td nowrap>";
    pHTML += "<div class='sbip' style='display: none;'><font class='font11px'>IP address&nbsp;</font><input type='text' name='sbip' id='sbip'></div>";
    pHTML += "<div class='sbdescription' style='display:none;'><font class='font11px'>Device description&nbsp;</font><input type='text' name='sbdescription' id='sbdescription'></div >";
    pHTML += "<div class='sbattribute' style='display:none;'><font class='font11px'>Select attribute&nbsp;</font>";
    pHTML += "<select name='step1deviceAttribute' class='selectdeviceAttribute' onchange='selectattributeValue()'>";
    pHTML += "<option value=''>Select</option>";
    for (var i = 0; i < deviceAttributes.length; i++) {
        pHTML += "<option value='" + deviceAttributes[i]['id'] + "' data-name='" + deviceAttributes[i]['name'] + "' data-type='" + deviceAttributes[i]['type'] + "' data-attributelist='" + deviceAttributes[i]['attributelist'] + "'>" + deviceAttributes[i]['name'] + " (" + deviceAttributes[i]['type'].charAt(0).toUpperCase() + deviceAttributes[i]['type'].slice(1) + ")</option>";
    }
    pHTML += "</select>";
    pHTML += "</div>";
    pHTML += "<div class='sbattributeValue' style='display:none;'></div><div class='sbattributeBoolean' style='display:none;'></div><div class='sbattributeList' style='display:none;'></div>";
    pHTML += "</td>";
    pHTML += "<td align='left'><div class='searchDevice' style='display:none;'><button type='button' name='searchDevice' class='transparent-button' id='searchDevice' value='Find device(s)' ' onclick='findDevices()'><img src='static/images/search.svg' width='12' height='12' class='showtitleTooltip' data-title='Find device(s)'></button></div></td>";
    pHTML += "<td width='50%'></td></tr></table>";
    pHTML += "<hr>";
    pHTML += "<div id='searchdeviceResult' style='display:none;'></div>"
    $('#selectdevicesDiv').empty().append(pHTML);
    $('#selectdevicesDiv').attr('style', 'display: block');
}


async function showsearchOptions() {
    if ($("#searchType option:selected").val() == "ipaddress") {
        manageattributeDivs("sbip");
        $("#sbip").val('');
    }
    else if ($("#searchType option:selected").val() == "description") {
        manageattributeDivs("sbdescription");
        $("#sbdescription").val('');
    }
    else if ($("#searchType option:selected").val() == "attribute") {
        manageattributeDivs("sbattribute");
        $(".selectdeviceAttribute").val('');
    }
    else {
        manageattributeDivs("");
    }
}


async function getdeviceAttributes() {
    attributeInfo = await $.ajax({
        url: "/deviceattributesList",
        type: "POST",
        data: {},
        success: function () {
            // Obtaining the device attribute list was successful
        },
        error: function () {
            showmessageBar("Error finding device attributes");
            $('#transparentOverlay').attr('style', 'display: none');
        }
    });
    attributeInfo = JSON.parse(attributeInfo);
    return attributeInfo;
}

async function backtofindDevices(profileInfo) {
    $('#showdaTooltip').hide();
    $('#transparentOverlay').attr('style', 'display: block');
    assigneddeviceInfo = JSON.parse($('#phprofileInfo').attr('data-assignedDevices'));
    if ($('#phprofileInfo').attr('data-availableDevices')) {
        availabledeviceInfo = JSON.parse($('#phprofileInfo').attr('data-availableDevices'));
    }
    else {
        availabledeviceInfo = [];
    }
    selectDevices(profileInfo);
    //if ($.isEmptyObject(availabledeviceInfo) ==false) {
    //    await availableDevices(availabledeviceInfo);
    //}
    if ($.isEmptyObject(assigneddeviceInfo) == false) {
        await devicesAssigned(assigneddeviceInfo, '[]', profileInfo);
    }
    $('#transparentOverlay').attr('style', 'display: none');
}


async function findDevices() {
    $('#showdaTooltip').hide();
    $('#transparentOverlay').attr('style', 'display: block');
    var ipaddress, description, ostype, attribute, attributeType, searchType, attributevalueValue, attributebooleanValue, attributelistValue;
    if ($("#searchType option:selected").val() == "ipaddress") {
        searchType = "ipaddress";
        ipaddress = $("#sbip").val();
        description = attribute = attributeType = attributevalueValue = attributebooleanValue = attributelistValue = ostype = "";
    }
    else if ($("#searchType option:selected").val() == "description") {
        searchType = "description";
        description = $("#sbdescription").val();
        ipaddress = attribute = attributeType = attributevalueValue = attributebooleanValue = attributelistValue = ostype = "";
    }
    else if ($("#searchType option:selected").val() == "ostype") {
        searchType = "ostype";
        ostype = $("#sbostype").val();
        ipaddress = description = attribute = attributeType = attributevalueValue = attributebooleanValue = attributelistValue = "";
    }
    else if ($("#searchType option:selected").val() == "attribute") {
        attribute = $(".selectdeviceAttribute option:selected").val();
        searchType = "attribute";
        if ($(".selectdeviceAttribute option:selected").attr('data-type') == "list") {
            attributeType = "list";
            attributelistValue = $("#attributelistValue option:selected").val() ;
            ipaddress = description = attributevalueValue = attributebooleanValue  = "";
        }
        else if ($(".selectdeviceAttribute option:selected").attr('data-type') == "boolean") {
            attributeType = "boolean";
            attributebooleanValue = $("#attributebooleanValue option:selected").val();
            ipaddress = description = attributevalueValue = attributelistValue = "";
        }
        else if ($(".selectdeviceAttribute option:selected").attr('data-type') == "value") {
            attributeType = "value";
            attributevalueValue = $("#attributevalueValue").val();
            ipaddress = description = attributebooleanValue = attributelistValue = "";
        }
    }
    else {
        manageattributeDivs("");
    }
    searchResult = await $.ajax({
        url: "/upgradeprofilesearchDevice",
        type: "POST",
        data: {searchType: searchType, ipaddress: ipaddress, description: description, ostype: ostype, attribute: attribute, attributeType: attributeType, attributevalueValue: attributevalueValue, attributebooleanValue: attributebooleanValue, attributelistValue: attributelistValue},
        success: function () {
            // Obtaining the device information was successful
        },
        error: function () {
            showmessageBar("Error finding devices for upgrade profile");
            $('#transparentOverlay').attr('style', 'display: none');
        }
    });
    // Filling the table
    console.log(searchResult);
    assigneddeviceInfo = $('#phprofileInfo').attr('data-assignedDevices');
    if (typeof assigneddeviceInfo === 'string' || assigneddeviceInfo instanceof String) {
        assigneddeviceInfo = JSON.parse(assigneddeviceInfo);
    }
    searchResult = JSON.parse(searchResult);   
    // If there are already assigned devices, we need to filter those out of the searchResult
    if (typeof assigneddeviceInfo === 'object' && typeof searchResult === 'object') {
        for (var i = 0; i < searchResult.length; i++) {
            for (var ii = 0; ii < assigneddeviceInfo.length; ii++) {
                if (searchResult[i]['id'] == assigneddeviceInfo[ii]['id']) {
                    //This is the item that we have to remove from the object
                    searchResult.splice(i, 1);
                }
            }
        }
    }
    $('#phprofileInfo').attr('data-availableDevices', JSON.stringify(searchResult));
    $('#phprofileInfo').attr('divname','findDevice');
    if (assigneddeviceInfo.length > 0) {
        profileInfo = {};
        await devicesAssigned(assigneddeviceInfo, searchResult, profileInfo);
    } 
    await availableDevices(searchResult);
    $('#transparentOverlay').attr('style', 'display: none');
}


async function selectattributeValue() {
    $('#showdaTooltip').hide();
    $('.sbattributeValue').attr('style', 'display: none');
    $('.sbattributeBoolean').attr('style', 'display: none');
    $('.sbattributeList').attr('style', 'display: none');
    if ($(".selectdeviceAttribute option:selected").attr('data-type') == "list") {
        pHTML = "";
        pHTML += "<font class='font11px'>&nbsp;&nbsp;Value&nbsp;</font><select name='attributelistValue' id='attributelistValue'>";
        attributeList = JSON.parse($(".selectdeviceAttribute option:selected").attr('data-attributelist'));
        for (var i = 0; i < attributeList.length; i++) {
            pHTML += "<option value='" + attributeList[i] + "'>" + attributeList[i] + "</option>";
        }
        pHTML += "</select>";
        $('.sbattributeList').empty().append(pHTML);
        $('.sbattributeList').attr('style', 'display: inline-block');
    }
    else if ($(".selectdeviceAttribute option:selected").attr('data-type') == "boolean") {
        pHTML = "";
        pHTML += "<font class='font11px'>&nbsp;&nbsp;Value&nbsp;</font><select name='attributebooleanValue' id='attributebooleanValue'>";
        pHTML += "<option value=''>Select</option>";
        pHTML += "<option value='0'>False</option>";
        pHTML += "<option value='1'>True</option>";
        pHTML += "</select>";
        $('.sbattributeBoolean').empty().append(pHTML);
        $('.sbattributeBoolean').attr('style', 'display: inline-block');
    }
    else if ($(".selectdeviceAttribute option:selected").attr('data-type') == "value") {
        pHTML = "";
        pHTML += "<font class='font11px'>&nbsp;&nbsp;Value&nbsp;</font><input type='text' name='attributevalueValue' id='attributevalueValue'>";
        $('.sbattributeValue').empty().append(pHTML);
        $('.sbattributeValue').attr('style', 'display: inline-block');
    }
}


async function assigntoProfile(deviceInfo) {
    $('#showdaTooltip').hide();
    $('#phprofileInfo').attr('data-divname', 'assigntoProfile');
    showmessageBar("Assign " + deviceInfo['ipaddress'] + " to profile");
    profileInfo = {};
    $('#assignsoftwareDiv').empty();
    $('#assignsoftwareDiv').attr('style', 'display: none');
    $('#transparentOverlay').attr('style', 'display: block');
    $('#showdaTooltip').attr('style', 'display: none');
    //Obtain the already assigned switch information and append the assigned switch
    assigneddeviceInfo = $('#phprofileInfo').attr('data-assignedDevices');
    availabledeviceInfo = $('#phprofileInfo').attr('data-availableDevices');
    if (typeof assigneddeviceInfo === 'string' || assigneddeviceInfo instanceof String) {
        assigneddeviceInfo = JSON.parse(assigneddeviceInfo);
    }
    if (typeof availabledeviceInfo === 'string' || availabledeviceInfo instanceof String) {
        availabledeviceInfo = JSON.parse(availabledeviceInfo);
    }
    if (typeof deviceInfo === 'string' || deviceInfo instanceof String) {
        deviceInfo = JSON.parse(deviceInfo);
    }
    assigneddeviceInfo.push(deviceInfo);
    $('#phprofileInfo').attr('data-assignedDevices', JSON.stringify(assigneddeviceInfo));
    for (var i = 0; i < availabledeviceInfo.length; i++) {
        if (availabledeviceInfo[i]['id'] == deviceInfo['id']) {
            //This is the item that we have to remove from the object
            availabledeviceInfo.splice(i, 1);
        }
    }
    if ($.isEmptyObject(assigneddeviceInfo)==false) {
        await devicesAssigned(assigneddeviceInfo, searchResult, profileInfo);
    }
    $('#phprofileInfo').attr('data-availableDevices', JSON.stringify(availabledeviceInfo));
    $('#phprofileInfo').attr('data-assignedDevices', JSON.stringify(assigneddeviceInfo));
    await availableDevices(availabledeviceInfo);
    $('#transparentOverlay').attr('style', 'display: none');
}


async function removefromProfile(deviceInfo, profileInfo) {
    $('#showdaTooltip').hide();
    if ($('#phprofileInfo').attr('data-divname') != "editProfile") {
        $('#phprofileInfo').attr('data-divname', 'removefromProfile');
    }
    console.log($('#phprofileInfo').attr('data-divname'));
    //Obtain the already assigned switch information and remove the selected switch
    assigneddeviceInfo = JSON.parse($('#phprofileInfo').attr('data-assignedDevices'));
    $('#assignsoftwareDiv').empty();
    $('#assignsoftwareDiv').attr('style', 'display: none');
    if ($('#phprofileInfo').attr('data-availableDevices') != "") {
        availabledeviceInfo = JSON.parse($('#phprofileInfo').attr('data-availableDevices'));
    }
    else {
        availabledeviceInfo = [];
    }
    if (typeof deviceInfo === 'string' || deviceInfo instanceof String) {
        deviceInfo = JSON.parse(deviceInfo);
    }
    for (var i = 0; i < assigneddeviceInfo.length; i++) {
        if (assigneddeviceInfo[i]['id'] == deviceInfo['id']) {
            //This is the item that we have to remove from the object
            assigneddeviceInfo.splice(i,1);
        }
    }
    showmessageBar("Remove " + deviceInfo['ipaddress'] + " from profile");
    $('#transparentOverlay').attr('style', 'display: block');
    $("#phprofileInfo").attr('data-assignedDevices', JSON.stringify(assigneddeviceInfo));
    if ($.isEmptyObject(assigneddeviceInfo) == false && $('#phprofileInfo').attr('data-divname')=="editProfile" ) {
        await assignsoftwaretoSwitches(profileInfo);
        await devicesAssigned(assigneddeviceInfo, searchResult, profileInfo);
    }
    else if ($.isEmptyObject(assigneddeviceInfo) == false && $('#phprofileInfo').attr('data-divname') == "removefromProfile") {
        await devicesAssigned(assigneddeviceInfo, searchResult, profileInfo);
    }
    else {
        $('#assigneddevicesDiv').empty();
        $('#assignedDevices').attr('style', 'display: none');
        $('#transparentOverlay').attr('style', 'display: none');
        $('#liProgress').attr('style', 'display: none');
    }
    availabledeviceInfo.push(deviceInfo);
    $('#phprofileInfo').attr('data-availableDevices', JSON.stringify(availabledeviceInfo));
    await availableDevices(availabledeviceInfo);
    $('#transparentOverlay').attr('style', 'display: none');
}


async function assignsoftwaretoSwitches(profileInfo) {
    $('#showdaTooltip').hide();
    showmessageBar("Obtain device information");
    $('#transparentOverlay').attr('style', 'display: block');
    $('#selectdevicesDiv').attr('style', 'display: none');
    $('#availabledevicesDiv').attr('style', 'display: none');
    //extract device id's from the assigned devices list
    assignedDevices = $('#phprofileInfo').attr('data-assignedDevices');
    if (typeof assignedDevices === 'string' || assignedDevices instanceof String) {
        assignedDevices = JSON.parse(assignedDevices);
    }
    deviceList = [];
    for (var i = 0; i < assignedDevices.length; i++) {
        deviceList.push(assignedDevices[i]['id']);
    }
    searchResult = await $.ajax({
        url: "/getsoftwareimageList",
        type: "POST",
        data: { devicelist: deviceList},
        success: function () {
            // Obtaining the software image information was successful
        },
        error: function () {
            showmessageBar("Error finding software for upgrade profile");
            $('#transparentOverlay').attr('style', 'display: none');
        }
    });
    if ($('#phprofileInfo').attr('data-divname') != "editProfile") {
        $('#assigneddevicesDiv').attr('style', 'display: none');
        pHTML = "<table class='tablenoborder'><tr>";
        pHTML += "<td colspan='5' align='center'><font class='font13pxgrey'>Selected device(s)</font></td></tr>";
        pHTML += "<tr style='background-color:grey;'>";
        pHTML += "<td width='20%' nowrap><font class='font12pxwhite'>IP Address</font></td>";
        pHTML += "<td width='20%'><font class='font12pxwhite'>Description</font></td>";
        pHTML += "<td width='10%' no wrap><font class='font12pxwhite'>Attributes</font></td>";
        pHTML += "<td width='10%' no wrap><font class='font12pxwhite'>Status</font></td><td></td></tr>";
        for (var i = 0; i < assignedDevices.length; i++) {
            pHTML += "<tr><td><font class='font11pxgrey'>" + assignedDevices[i]['ipaddress'] + "</font></td><td><font class='font11pxgrey'>" + assignedDevices[i]['description'] + "</font></td>";
            pHTML += "<td><img src='static/images/tag.svg' class='attributeTooltip' width='12' height='12' data-deviceid='" + assignedDevices[i]['id'] + "'></td>";
            pHTML += "<td>";
            if (searchResult['offlineDevices'].includes(assignedDevices[i]['id']) == true) {
                pHTML += "<font class='font11pxred'>Offline</font>";
            }
            else {
                pHTML += "<font class='font11pxgreen'>Online</font>";
            }
            pHTML += "</td >";
            pHTML += "<td></td>";
            pHTML += "</tr>";
        }
        pHTML += "</table>";
        profileImages = [];
    }
    else {
        pHTML = "";
        var profileImages = profileInfo['softwareimages'].split(',').map(function (i) {
            return parseInt(i, 10);
        })       
    }
    pHTML += "<table class='tablenoborder'>";
    pHTML += "<tr><td colspan='3' align='center'><font class='font13pxgrey'>Available software images</font></td></tr>";
    pHTML += "<tr style='background-color:grey;'><td width='20%'><font class='font12pxwhite'>Device family</font></td><td width='25%'><font class='font12pxwhite'>Available software images</font></td><td></td></tr>";
    for (var i = 0; i < searchResult['swInfo'].length; i++) {
        pHTML += "<tr>";
        pHTML += "<td><font class='font12pxgrey'>" + searchResult['swInfo'][i][0]['devicefamily'] + "</font></td>";
        pHTML += "<td><select name='softwareimage[]' id='softwareimage'>";
        for (var ii = 0; ii < searchResult['swInfo'][i].length; ii++) {
            if (profileImages.includes(searchResult['swInfo'][i][ii]['id'])) {
                pHTML += "<option value='" + searchResult['swInfo'][i][ii]['id'] + "' selected>" + searchResult['swInfo'][i][ii]['name'] + " (" + searchResult['swInfo'][i][ii]['filename'] + ")</option>";
            }
            else {
                pHTML += "<option value='" + searchResult['swInfo'][i][ii]['id'] + "'>" + searchResult['swInfo'][i][ii]['name'] + " (" + searchResult['swInfo'][i][ii]['filename'] + ")</option>";
            }
        }
        pHTML += "</select></td></tr>";      
    }
    pHTML += "<tr><td colspan='3' align='center'>";
    pHTML += "<input type='button' name='backtodeviceselection' onclick='backtofindDevices(" + JSON.stringify(profileInfo) + ")' value='Back to device selection'>";
    pHTML += "<input type='button' name='submitProfile' class='submitProfile' value='Submit profile' onclick='checkForm()'>";  
    pHTML += "</td></tr>";
    pHTML += "</table>"; 
    pHTML += "<input type='hidden' name='profileAction' value='" + $('#phprofileInfo').attr('data-addoredit') + "'>";
    pHTML += "<input type='hidden' name='softwareImages' id='softwareImages' value=''>";
    pHTML += "<input type='hidden' name='assignedDevices' id='assignedDevices' value='" + JSON.stringify(assignedDevices) + "'>";
    pHTML += "<input type='hidden' name='offlineDevices' id='offlinedevices' value='" + searchResult['offlineDevices'] + "'>";
    $('#assignsoftwareDiv').empty().append(pHTML);
    $('#assignsoftwareDiv').attr('style', 'display: block');
    $('#transparentOverlay').attr('style', 'display: none');
    $('#liProgress').attr('style', 'display: none');    
}


async function devicesAssigned(deviceInfo, searchResult, profileInfo) {
    $('#showdaTooltip').hide();
    if (typeof deviceInfo === 'string' || deviceInfo instanceof String) {
        deviceInfo = JSON.parse(deviceInfo);
    }
    if (typeof searchResult === 'string' || searchResult instanceof String) {
        searchResult = JSON.parse(searchResult);
    }
    aHTML = "<table class='tablenoborder'><tr>";
    aHTML += "<td colspan='6' align='center'><font class='font13pxgrey'>Assigned device(s)</font></td></tr>";
    aHTML += "<tr style='background-color:grey;'>";
    aHTML += "<td width='10%' nowrap><font class='font12pxwhite'>IP Address</font></td>";
    aHTML += "<td width='20%'><font class='font12pxwhite'>Description</font></td>";
    aHTML += "<td width='20%'><font class='font12pxwhite'>OS type</font></td>";
    aHTML += "<td width='5%' align='center'><font class='font12pxwhite'>Attributes</font></td>";
    aHTML += "<td width='20%'><font class='font12pxwhite'>Status</font></td>";
    aHTML += "<td width='20%' no wrap align='right'><font class='font12pxwhite'>Action</font></td></tr>";
    for (var i = 0; i < deviceInfo.length; i++) {
        aHTML += "<tr><td><font class='font11pxgrey'>" + deviceInfo[i]['ipaddress'] + "</font></td><td><font class='font11pxgrey'>" + deviceInfo[i]['description'] + "</font></td><td><font class='font11pxgrey'>" + deviceInfo[i]['ostype'] + "</font></td>";
        aHTML += "<td align='center'><img src='static/images/tag.svg' class='attributeTooltip' width='12' height='12' data-deviceid='" + deviceInfo[i]['id'] + "'></td>";
        isOnline = await $.ajax({
            url: "/deviceStatus",
            type: "POST",
            data: { deviceid: deviceInfo[i]['id'], ostype: deviceInfo[i]['ostype']},
            success: function () {
                // Obtaining the software image information was successful
            },
            error: function () {
                showmessageBar("Error finding device status of " + deviceInfo[i]['ipaddress']);
                $('#transparentOverlay').attr('style', 'display: none');
            }
         });
        aHTML += "<td>";
        if (typeof isOnline === 'string' || isOnline instanceof String) {
            isOnline = JSON.parse(isOnline);
        }
        if (isOnline['status'] == "Offline") {
            aHTML += "<font class='font11pxred'>Offline</font>";
        }
        else {
            aHTML += "<font class='font11pxgreen'>Online</font>";
        }
        aHTML += "</td>";
        aHTML += "<td align='right'><button type='button' name='removefr0mProfile' class='transparent-button' value='Remove from profile' onclick='removefromProfile(" + JSON.stringify(deviceInfo[i]) + "," + JSON.stringify(profileInfo) + ")'><img src='static/images/subtract.svg' width='12' height='12' class='showtitleTooltip' data-title='Remove from profile'></button></td></tr>";
    }
    if (deviceInfo.length > 0  && $('#phprofileInfo').attr('data-divname') !="editProfile") {
        aHTML += "<tr>";
        aHTML += "<td colspan='6' align='center'><input type='button' name='assignSoftware' class='assignSoftware' value='Assign software' onclick='assignsoftwaretoSwitches(" + JSON.stringify(profileInfo) + ")'></td></tr>";
    }
    aHTML += "</tr></table>";
    $('#assigneddevicesDiv').empty().append(aHTML);
    $('#assigneddevicesDiv').attr('style', 'display: block');
    $('#transparentOverlay').attr('style', 'display: none');
    $('#liProgress').attr('style', 'display: none');
}

async function checkForm() {
    // We only need to verify whether the profile name has been entered
    if ($('#' + $('#phprofileInfo').attr('data-addoredit') + 'profilename').val().length > 0) {
        $('#transparentOverlay').attr('style', 'display: none');
        $('#liProgress').attr('style', 'display: none');
        //assign all the software images to a single array
        var values = $("select[name='softwareimage\\[\\]']")
            .map(function () { return $(this).val(); }).get();
        $('#softwareImages').val(values);
        document.getElementById("manageProfile").submit();
    }
    else {
        showmessageBar("Enter a profile name");
        $('#' + $('#phprofileInfo').attr('data-addoredit') + 'profilename').attr('style', 'background-color : red');
    }
    
}

async function availableDevices(deviceInfo) {
    $('#showdaTooltip').hide();
    if (typeof deviceInfo === 'string' || deviceInfo instanceof String) {
        deviceInfo = JSON.parse(deviceInfo);
    }
    pHTML = "";
    if (deviceInfo.length > 0) {
        pHTML = "<table class='tablenoborder'><tr>";
        pHTML += "<td colspan='5' align='center'><font class='font13pxgrey'>Device search result</font></td></tr>";
        pHTML += "<tr style='background-color:grey;'>";
        pHTML += "<td width='10%' nowrap><font class='font12pxwhite'>IP Address</font></td>";
        pHTML += "<td width='25%'><font class='font12pxwhite'>Description</font></td>";
        pHTML += "<td width='5%' align='center'><font class='font12pxwhite'>Attributes</font></td>";
        pHTML += "<td width='55'></td>";
        pHTML += "<td width='5%' no wrap align='right'><font class='font12pxwhite'>Action</font></td></tr>";
        for (var i = 0; i < deviceInfo.length; i++) {
            pHTML += "<tr><td><font class='font11pxgrey'>" + deviceInfo[i]['ipaddress'] + "</font></td><td><font class='font11pxgrey'>" + deviceInfo[i]['description'] + "</font></td>";
            pHTML += "<td align='center'><img src='static/images/tag.svg' class='attributeTooltip' width='12' height='12' data-deviceid='" + deviceInfo[i]['id'] + "'></td><td></td>";
            pHTML += "<td align='right'><button type='button' name='assign2Profile' class='transparent-button' value='Assign to profile' onclick='assigntoProfile(" + JSON.stringify(deviceInfo[i]) + ");'><img src='static/images/add.svg' width='12' height='12' class='showtitleTooltip' data-title='Assign to profile'></button></td></tr>";
        }
        // If there are no assigned devices, we need to be able to go back and select devices
        assignedDevices = JSON.parse($('#phprofileInfo').attr('data-assigneddevices'));
        if (assignedDevices.length == 0 && $('#phprofileInfo').attr('data-divname') != "selectDevices") {
            pHTML += "<tr><td colspan='5' align='center'>";
            pHTML += "<input type='button' name='backtodeviceselection' onclick='backtofindDevices(" + JSON.stringify(profileInfo) + ")' value='Back to device selection'>";
            pHTML += "</td></tr>";
        }
        pHTML += "</tr></table>";
        $('#availabledevicesDiv').empty().append(pHTML);
        $('#availabledevicesDiv').attr('style', 'display: block');
    }
    else {
        $('#availabledevicesDiv').empty();
    }
}


$('.actionButtons').ready(function () {
    $('#showdaTooltip').hide();
    var refresh = async function () {
        actionButtons=document.getElementsByClassName('actionButtons');
        for (var i = 0; i < actionButtons.length; i++) {
            profileid=actionButtons.item(i).getAttribute('data-profileid');
            //Check the status of the upgrade profile. If it is 0, then the profile has not started we can enable the remove button
            profileInfo = await $.ajax({
                url: "/upgradeprofileStatus",
                type: "POST",
                data: { profileid: profileid },
                success: function () {
                    // Obtaining the profile information was successful
                },
                error: function () {
                    $('#transparentOverlay').attr('style', 'display: none');
                }
            });
            profileInfo = JSON.parse(profileInfo);
            pHTML = "<input type='hidden' name='profileid' value='" + profileInfo['id'] + "'>";
            pHTML += "<button type='button' id='showprofileDetails" + profileInfo['id'] + "' class='transparent-button showProfile' value='Show details' onClick='highlightRow(this);showProfile(" + profileInfo['id'] + ");'><img src='static/images/info.svg' width='12' height='12' class='showtitleTooltip' data-title='Show profile'></button>";
            if (profileInfo['status'] === 0) {
                // Software upgrades have not started yet for this profile. Enable the edit and delete button
                pHTML += "<button type='button' id='editprofileUpgrade" + profileInfo['id'] + "' onclick='editProfile(" + profileInfo['id'] + ");' class='transparent-button' value='Edit'><img src='static/images/edit.svg' width='12' height='12' class='showtitleTooltip' data-title='Edit profile'></button>";
                pHTML += "<button type='submit' name='profileAction' id='removeprofileUpgrade" + profileInfo['id'] + "' onclick=\"return confirm('Are you sure you want to delete upgrade profile " + profileInfo['name'] + "?')\" data-profileid='" + profileInfo['id'] + "' class='transparent-button removeprofileButton' value='Remove'><img src='static/images/trash.svg' width='12' height='12' class='showtitleTooltip' data-title='Delete profile'></button>";

            }
            else if (profileInfo['status'] > 99) {
                //Software upgrade job has finished, enable the delete button, disable the edit button
                pHTML += "<button type='button' disabled style='text-decoration:none;' id='editprofileUpgrade" + profileInfo['id'] + "' onclick='editProfile(" + profileInfo['id'] + ");' class='transparent-button' value='Edit'><img src='static/images/edit.svg' width='12' height='12' class='showtitleTooltip' data-title='Upgrade job has finished'></button>";
                pHTML += "<button type='submit' name='profileAction' id='removeprofileUpgrade" + profileInfo['id'] + "' onclick=\"return confirm('Are you sure you want to delete upgrade profile " + profileInfo['name'] + "?')\" data-profileid='" + profileInfo['id'] + "' class='transparent-button removeprofileButton' value='Remove'><img src='static/images/trash.svg' width='12' height='12' class='showtitleTooltip' data-title='Delete profile'></button>";
            }
            else {
                //Software upgrade job is in progress, disable edit and delete button
                pHTML += "<button type='button' disabled style='text-decoration:none;' id='editprofileUpgrade" + profileInfo['id'] + "' onclick='editProfile(" + profileInfo['id'] + ");' class='transparent-button' value='Edit'><img src='static/images/edit.svg' width='12' height='12' class='showtitleTooltip' data-title='Upgrade job in progress'></button>";
                pHTML += "<button type='submit' disabled style='text-decoration:none;' id='removeprofileUpgrade" + profileInfo['id'] + "' name='profileAction' data-profileid='" + profileInfo['id'] + "' class='transparent-button removeprofileButton' value='Remove'><img src='static/images/trash.svg' width='12' height='12' class='showtitleTooltip' data-title='Upgrade job in progress'></button>";
            }
            $('#actionButtons'+ profileInfo['id']).empty().append(pHTML);
        }
    };
    setInterval(refresh, 1000);
    refresh();
});


async function showProfile(profileid) {
    var upgradestatus = { '0': 'Not started', '1': 'Upgrade initiated', '5': 'Copy software onto the switch', '10': 'Software copied successfully', '20': 'Software copied successfully: switch is rebooted', '50': 'There is another software upgrade in progress', '60': 'Upgrade profile is active', '100': 'Software upgrade completed successfully', '110': 'Software upgrade completed successfully: reboot is required' };
    $('#showdaTooltip').hide();
    $('#showprofileInfo').attr('style', 'display: block');
    $('#addProfile').attr('style', 'display: none');
    $('#assigneddevicesDiv').attr('style', 'display: none');
    $('#availabledevicesDiv').attr('style', 'display: none');
    $('#assignsoftwareDiv').attr('style', 'display: none');
    var refresh = function () {
        $('#showprofileInfo').load('viewupgradeprofileInfo?profileid=' + profileid);
    }
    setInterval(refresh, 5000);
    refresh();
}

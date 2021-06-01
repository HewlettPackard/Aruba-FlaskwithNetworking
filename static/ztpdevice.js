// (C) Copyright 2020 Hewlett Packard Enterprise Development LP.




$(document).ready(function () {

    $(document).on('change', ".selectTemplateparameters", async function () {
        document.getElementById("liProgress").style.display = "none";
        selectId = $(this).closest(".selectTemplateparameters").attr("id");
        formId = $('#' + selectId).closest('form')[0].id;
        templateDiv = $('#' + formId + ' .templateparametersDiv').attr("id");
        var e = document.getElementById(selectId);
        var templateId = e.options[e.selectedIndex].value;
        if (templateId != 0) {
            templateInfo = await $.ajax({
                url: "/ztptemplateparameterInfo",
                type: "POST",
                data: { id: templateId },
                success: function () {
                    // Obtaining the ZTP template was successful
                },
                error: function () {
                    document.getElementById("liProgress").style.display = "block";
                    document.getElementById("progresstooltip").style.display = "none";
                    progressInfo.innerHTML = "Error finding ZTP template information";
                }
            });
            templateInfo = JSON.parse(templateInfo);
            templateHTML = "<table class='tablenoborder' cellpadding='2'><tr style='background-color: grey'><td colspan='2'><center><font class='font13pxwhite'>Template parameters</white></center></td></tr>";
            for (var i = 0; i < templateInfo.length; i++) {
                templateHTML += "<tr><td width='10%'><font class='font12pxgrey'>" + Object.keys(templateInfo[i]) + "</font></td ><td><input type='text' name='parameterValues[" + Object.keys(templateInfo[i]) + "]'></td></tr>";
            }
            templateHTML += "</table>";
            document.getElementById(templateDiv).style.display = "block";
            document.getElementById(templateDiv).innerHTML = templateHTML;
        }
    });


    $(document).on('change', ".Enablevsf", async function () {
        document.getElementById("liProgress").style.display = "none";
        selectId = $(this).closest(".Enablevsf").attr("id");
        formId = $('#' + selectId).closest('form')[0].id;
        Enablevsf = $('#' + formId + ' .Enablevsf').attr("id");
        //Get the status of the VSF checkbox. If disabled, all the VSF fields have to be disabled

        if (document.getElementById(Enablevsf).checked == true) {
            //VSF is activated. Enable all the VSF related fields
            $('.selectLink1').attr('disabled', false);
            $('.selectLink2').attr('disabled', false);
            $('#editSelectswitchtype option:not(:selected)').attr('disabled', false);
            if ($(".selectVsfrole").val() == "Master") {
                //Master is selected, disable the member id and master switch field
                $('.selectVsfmember').attr('disabled', true);
                $('.selectVsfmaster').attr('disabled', true);
                $('.selectTemplateparameters').attr('disabled', false);
            }
            else {
                $('.selectVsfmember').attr('disabled', false);
                $('.selectVsfmaster').attr('disabled', false);
                $('.selectSoftwareimage').attr('disabled', true);
                $('.selectTemplateparameters').attr('disabled', true);
            }
            $('.selectVsfrole').attr('disabled', false);
            $('.selectVsflink1').attr('disabled', false);
            $('.selectVsflink2').attr('disabled', false);
        }
        else {
            //VSF is deactivated. Disable all the VSF related fields and enable the template and software image field
            $('.selectVsfrole').attr('disabled', true);
            $('.selectVsfmember').attr('disabled', true);
            $('.selectVsfmaster').attr('disabled', true);
            $('.selectVsflink1').attr('disabled', true);
            $('.selectVsflink2').attr('disabled', true);
            $('.selectLink1').attr('disabled', true);
            $('.selectLink2').attr('disabled', true);
            $('.selectSoftwareimage').attr('disabled', false);
            $('.selectTemplateparameters').attr('disabled', false);
            if (document.getElementById("editztpdhcp").checked == true) {
                $('#editSelectswitchtype option:not(:selected)').attr('disabled', true);
            }
            else {
                    $('#editSelectswitchtype option:not(:selected)').attr('disabled', false);
                }
        }

    });

    $(document).on('change', ".ztpdhcp", function () {
        if (document.getElementById("editztpdhcp").checked == true) {
            if ($('#editipamsubnet').length) {
                $('#editipamsubnet option:not(:selected)').attr('disabled', true);
            }
            if ($('#editipamipaddress').length) {
                $('#editipamipaddress option:not(:selected)').attr('disabled', true);
            }
            if ($('#editIpaddress').length) {
                $('#editIpaddress').attr('disabled', true);
            }
            if ($('#editNetmask').length) {
                $('#editNetmask').attr('disabled', true);
            }
            if ($('#editGateway').length) {
                $('#editGateway').attr('disabled', true);
            }
            if ($('#edituplinkVlan').length) {
                $('#edituplinkVlan').attr('disabled', true);
            }
            if ($('#edittaggedVlan').length) {
                $('#edittaggedVlan').attr('disabled', true);
            }
            if ($('#editSelectswitchtype').length && document.getElementById("editEnablevsf").checked == false) {
                $('#editSelectswitchtype option:not(:selected)').attr('disabled', true);
            }
        }
        else {
            if ($('#editipamsubnet').length) {
                $('#editipamsubnet option:not(:selected)').attr('disabled', false);
                $('#editipamsubnet').attr('disabled', false);
            }
            if ($('#editipamipaddress').length) {
                $('#editipamipaddress option:not(:selected)').attr('disabled', false);
            }
            if ($('#editIpaddress').length) {
                $('#editIpaddress').attr('disabled', false);
            }
            if ($('#editNetmask').length) {
                $('#editNetmask').attr('disabled', false);
            }
            if ($('#editGateway').length) {
                $('#editGateway').attr('disabled', false);
            }
            if ($('#edituplinkVlan').length) {
                $('#edituplinkVlan').attr('disabled', false);
            }
            if ($('#edittaggedVlan').length) {
                $('#edittaggedVlan').attr('disabled', false);
            }
            if ($('#editSelectswitchtype').length) {
                $('#editSelectswitchtype option:not(:selected)').attr('disabled', false);
            }
        }
        if (document.getElementById("addztpdhcp").checked == true) {
            if ($('#addipamsubnet').length) {
                $('#addipamsubnet option:not(:selected)').attr('disabled', true);
            }
            if ($('#addipamipaddress').length) {
                $('#addipamipaddress option:not(:selected)').attr('disabled', true);
            }
            if ($('#addIpaddress').length) {
                $('#addIpaddress').attr('disabled', true);
            }
            if ($('#addNetmask').length) {
                $('#addNetmask').attr('disabled', true);
            }
            if ($('#addGateway').length) {
                $('#addGateway').attr('disabled', true);
            }
            if ($('#adduplinkVlan').length) {
                $('#adduplinkVlan').attr('disabled', true);
            }
            if ($('#addtaggedVlan').length) {
                $('#addtaggedVlan').attr('disabled', true);
            }
            if ($('#addSelectswitchtype').length && document.getElementById("addEnablevsf").checked == false) {
                $('#addSelectswitchtype option:not(:selected)').attr('disabled', true);
            }
        }
        else {
            if ($('#addipamsubnet').length) {
                $('#addipamsubnet option:not(:selected)').attr('disabled', false);
            }
            if ($('#addipamipaddress').length) {
                $('#addipamipaddress option:not(:selected)').attr('disabled', false);
            }
            if ($('#addIpaddress').length) {
                $('#addIpaddress').attr('disabled', false);
            }
            if ($('#addNetmask').length) {
                $('#addNetmask').attr('disabled', false);
            }
            if ($('#addGateway').length) {
                $('#addGateway').attr('disabled', false);
            }
            if ($('#adduplinkVlan').length) {
                $('#adduplinkVlan').attr('disabled', false);
            }
            if ($('#addtaggedVlan').length) {
                $('#addtaggedVlan').attr('disabled', false);
            }
            if ($('#addSelectswitchtype').length) {
                $('#addSelectswitchtype option:not(:selected)').attr('disabled', false);
            }
        }
    });

    $(document).on('change', ".selectVsfrole", async function () {
        document.getElementById("liProgress").style.display = "none";
        selectId = $(this).closest(".selectVsfrole").attr("id");
        formId = $('#' + selectId).closest('form')[0].id;
        vsfmasterId = $('#' + formId + ' .selectVsfmaster').attr("id");
        var vsfrole = document.getElementById(selectId);
        if (vsfrole.options[vsfrole.selectedIndex].value == "Master") {
            //Master is selected, disable the member id and master switch field
            $('#' + vsfmasterId).empty();
            $('#' + vsfmasterId).append('<option value="">Select</option>');
            $(".selectVsfmember").val(0).change();
            $('.selectVsfmember').attr('disabled', true);
            $('.selectVsfmaster').attr('disabled', true);
            $('.selectSoftwareimage').attr('disabled', false);
            $('.selectTemplateparameters').attr('disabled', false);
            $('.selectSoftwareimage').attr('disabled', false);
        }
        else {
            $('.selectVsfmember').attr('disabled', false);
            $('.selectVsfmember option:not(:selected)').attr('disabled', false);
            $('.selectVsfmaster').attr('disabled', false);
            $('.selectVsfmaster option:not(:selected)').attr('disabled', false);
            $('.selectSoftwareimage').attr('disabled', true);
            $('.selecttemplateparameters').attr('disabled', true);
            $('.selectSoftwareimage').attr('disabled', true);
            $('.selectTemplateparameters').attr('disabled', true);
            // Get the master VSF switches from the database and fill the select options
            response = await $.ajax({
                type: "POST",
                url: "/vsfmasterInfo",
                success: function (response) {
                    response = JSON.parse(response);
                    $('#' + vsfmasterId).empty();
                    $('#' + vsfmasterId).append('<option value="">Select</option>');
                    for (var i = 0; i < response.length; i++) {
                        $('#' + vsfmasterId).append('<option value="' + response[i]['id'] + '">' + response[i]['name'] + ' (' + response[i]['ipaddress'] + ')</option>');
                    }
                }
            });

        }
    });

    $(document).on('change', ".selectSwitchtype", function () {
        document.getElementById("liProgress").style.display = "none";
        selectId = $(this).closest(".selectSwitchtype").attr("id");
        formId = $('#' + selectId).closest('form')[0].id;
        link1 = $('#' + formId + ' .selectVsflink1').attr("id");
        link2 = $('#' + formId + ' .selectVsflink2').attr("id");
        var switchType = document.getElementById(selectId);
        if (switchType.options[switchType.selectedIndex].value == "24") {
            $('#' + link1).empty();
            $('#' + link2).empty();
            $('#' + link1).append('<option value="">Select</option>');
            $('#' + link2).append('<option value="">Select</option>');
            $('#' + link1).append('<option value="1/1/25">1/1/25</option>');
            $('#' + link1).append('<option value="1/1/26">1/1/26</option>');
            $('#' + link1).append('<option value="1/1/27">1/1/27</option>');
            $('#' + link1).append('<option value="1/1/28">1/1/28</option>');
            $('#' + link2).append('<option value="1/1/25">1/1/25</option>');
            $('#' + link2).append('<option value="1/1/26">1/1/26</option>');
            $('#' + link2).append('<option value="1/1/27">1/1/27</option>');
            $('#' + link2).append('<option value="1/1/28">1/1/28</option>');
        }
        else if (switchType.options[switchType.selectedIndex].value == "48") {
            $('#' + link1).empty();
            $('#' + link2).empty();
            $('#' + link1).append('<option value="">Select</option>');
            $('#' + link2).append('<option value="">Select</option>');
            $('#' + link1).append('<option value="1/1/49">1/1/49</option>');
            $('#' + link1).append('<option value="1/1/50">1/1/50</option>');
            $('#' + link1).append('<option value="1/1/51">1/1/51</option>');
            $('#' + link1).append('<option value="1/1/52">1/1/52</option>');
            $('#' + link2).append('<option value="1/1/49">1/1/49</option>');
            $('#' + link2).append('<option value="1/1/50">1/1/50</option>');
            $('#' + link2).append('<option value="1/1/51">1/1/51</option>');
            $('#' + link2).append('<option value="1/1/52">1/1/52</option>');
        }
    });


    $(document).on('change', ".ipamsubnet", async function () {
        document.getElementById("liProgress").style.display = "none";
        selectId = $(this).closest(".ipamsubnet").attr("id");
        formId = $('#' + selectId).closest('form')[0].id;
        ipaddressField = $('#' + formId + ' .ipamipaddress').attr("id");
        netmaskField = $('#' + formId + ' .ipamnetmask').attr("id");
        gatewayField = $('#' + formId + ' .ipamgateway').attr("id");
        gatewayDiv = $('#' + formId + ' .ipamgatewayDiv').attr("id");
        var e = document.getElementById(selectId);
        var subnetid = e.options[e.selectedIndex].value;
        // Need to push the subnet ID value to the select field, as well as the subnet mask and default gateway.
        // Identified the fields that we need to fill with information. Now obtain the IP address information from PHPipam from the selected subnet ID
        response = await $.ajax({
            type: "POST",
            data: { 'subnetid': subnetid },
            url: "/ipamgetIPaddress",
            success: function (response) {
                response = JSON.parse(response);
                sysvars = response['sysvars'];
                var ipArray = [];
                if (sysvars['ipamsystem'] == "PHPIPAM") {
                    ipamIpaddress = response['ipamIpaddress']['data'];
                    ipamsubnet = response['ipamsubnet']['data'];
                    // Create an array that contains the IP addresses that are in use. Distill from the ipamIpaddress object
                    if (typeof ipamIpaddress !== 'undefined') {
                        for (var j = 0; j < ipamIpaddress.length; j++) {
                            ipArray.push(ipamIpaddress[j]['ip']);
                        }
                    }
                    document.getElementById(netmaskField).value = ipamsubnet['calculation']['Subnet bitmask'];
                    if ("gateway" in ipamsubnet) {
                        document.getElementById(gatewayDiv).innerHTML = "<font class='font12px'>" + ipamsubnet['gateway']['ip_addr'] + "</font>";
                        document.getElementById(gatewayField).value = ipamsubnet['gateway']['ip_addr'];
                        // Assign the gateway value to the gateway field
                    }
                    else {
                        document.getElementById(gatewayDiv).innerHTML = "";
                        document.getElementById(gatewayField).value = "";
                    }
                    // We need to get the range of available IP addresses in the select field.
                    // In the data['calculation'] object you find "Min host IP" and "Max host IP". We need to create a select for this
                    // One other thing is that we need to exclude the IP addresses that are reserved or blocked
                    //First we convert the decimals to hex values
                    $('#' + ipaddressField).empty();
                    ip_start = ipamsubnet['calculation']['Min host IP'].split(".");
                    ip_end = ipamsubnet['calculation']['Max host IP'].split(".");
                    startip = "0x" + "00".substr(0, 2 - parseInt(ip_start[0]).toString(16).length) + parseInt(ip_start[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[1]).toString(16).length) + parseInt(ip_start[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[2]).toString(16).length) + parseInt(ip_start[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[3]).toString(16).length) + parseInt(ip_start[3]).toString(16);
                    endip = "0x" + "00".substr(0, 2 - parseInt(ip_end[0]).toString(16).length) + parseInt(ip_end[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[1]).toString(16).length) + parseInt(ip_end[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[2]).toString(16).length) + parseInt(ip_end[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[3]).toString(16).length) + parseInt(ip_end[3]).toString(16);
                }
                else if (sysvars['ipamsystem'] == "Infoblox") {
                    ipamIpaddress = response['ipamIpaddress']['result'];
                    ipamsubnet = response['ipamsubnet'][0];
                    // Create an array that contains the IP addresses that are in use. Distill from the ipamIpaddress object
                    if (typeof ipamIpaddress !== 'undefined') {
                        for (var j = 0; j < ipamIpaddress.length; j++) {
                            ipArray.push(ipamIpaddress[j]['ip_address']);
                        }
                    }
                    document.getElementById(netmaskField).value = ipamsubnet['network'].split("/")[1];
                    // Check if there are router options in the ipamsubnet
                    for (var k = 0; k < ipamsubnet['options'].length; k++) {
                        if (ipamsubnet['options'][k]['name'] == "routers") {
                            document.getElementById(gatewayDiv).innerHTML = "<font class='font12px'>" + ipamsubnet['options'][k]['value'] + "</font>";
                            document.getElementById(gatewayField).value = ipamsubnet['options'][k]['value'];
                            // Assign the gateway value to the gateway field
                        }
                        else {
                            document.getElementById(gatewayDiv).innerHTML = "";
                            document.getElementById(gatewayField).value = "";
                        }
                    }

                    cidrRange = cidrToRange(ipamsubnet['network']);
                    $('#' + ipaddressField).empty();
                    ip_start = cidrRange[0].split(".");
                    ip_end = cidrRange[1].split(".");
                    startip = "0x" + "00".substr(0, 2 - parseInt(ip_start[0]).toString(16).length) + parseInt(ip_start[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[1]).toString(16).length) + parseInt(ip_start[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[2]).toString(16).length) + parseInt(ip_start[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[3]).toString(16).length) + parseInt(ip_start[3] + 1).toString(16);
                    endip = "0x" + "00".substr(0, 2 - parseInt(ip_end[0]).toString(16).length) + parseInt(ip_end[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[1]).toString(16).length) + parseInt(ip_end[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[2]).toString(16).length) + parseInt(ip_end[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[3]).toString(16).length) + parseInt(ip_end[3]).toString(16);
                }
                for (var i = startip; i < endip; i++) {
                    // If the IP address is already used, it should not be selectable  
                    ipAddress = (i >>> 24) + '.' + (i >> 16 & 255) + '.' + (i >> 8 & 255) + '.' + (i & 255);
                    if (!ipArray.includes(ipAddress)) {
                        $('#' + ipaddressField).append('<option value=\"' + ipAddress + '\">' + ipAddress + '</option>');
                    }
                }
            }
        });
    });

    $('.editShow').ready(
        function () {
            editShow = document.getElementsByClassName('editShow');
            for (var i = 0; i < editShow.length; i++) {
                deviceid = editShow.item(i).getAttribute('data-deviceid');
                ipamstatus = editShow.item(i).getAttribute('data-ipamstatus');
                enableztp = editShow.item(i).getAttribute('data-enableztp');
                // If ZTP is enabled, we should show the "Show configuration" button. This is reflected in the enableztp status
                // If it's 0 then we can set the edit button, otherwise we should only show the "show" button
                if (enableztp == "0") {
                    //Show the edit button
                    editshowHTML = "<input type='button' name='editDevice' value='Edit' data-deviceid='" + deviceid + "' class='editDevice' id='editDevice" + deviceid + "'";
                    editshowHTML += "onclick = 'highlightdeviceRow(" + editShow.item(i).id + ");'";
                    if (ipamstatus == "Offline") {
                        editshowHTML += " style='opacity:0.3;pointer-events:none;'";
                    }
                    editshowHTML += ">";
                    editshowHTML += "<input type='button' name='showDevice' value='Show' data-deviceid='" + deviceid + "' class='showDevice' id='showDevice" + deviceid + "'";
                    editshowHTML += "onclick = 'highlightdeviceRow(" + editShow.item(i).id + ");'>";
                }
                else {
                    //Show the show button
                    editshowHTML = "<input type='button' name='showDevice' value='Show' data-deviceid='" + deviceid + "' class='showDevice' id='showDevice" + deviceid + "'";
                    editshowHTML += "onclick = 'highlightdeviceRow(" + editShow.item(i).id + ");'>";
                }
                document.getElementById('editShow' + deviceid).innerHTML = editshowHTML;


            }

            
        });



    $('.ztpStatus').ready(
        function () {
            try {
                setInterval(async function () {
                    ztpStatus = document.getElementsByClassName('ztpStatus');
                    for (var i = 0; i < ztpStatus.length; i++) {
                        try {
                            deviceid = ztpStatus.item(i).getAttribute('data-deviceid');
                            enableztp = ztpStatus.item(i).getAttribute('data-enableztp');
                            response = await $.ajax({
                                type: "POST",
                                data: { 'id': deviceid },
                                url: "/ztpdeviceInfo",
                                success: function (response) {
                                    try {


                                        response = JSON.parse(response);
                                        deviceInfo = response['deviceInfo'];
                                        if (deviceInfo['ipaddress'] == "0.0.0.0") {
                                            document.getElementById('ipaddress' + deviceInfo['id']).innerHTML = "<font class='font12px'>DHCP</font>";
                                            document.getElementById('gateway' + deviceInfo['id']).innerHTML = "<font class='font12px'>DHCP</font>";
                                            document.getElementById('vrf' + deviceInfo['id']).innerHTML = "<font class='font12px'>DHCP</font>";
                                        }
                                        else {
                                            document.getElementById('ipaddress' + deviceInfo['id']).innerHTML = "<font class='font12px'>" + deviceInfo['ipaddress'] + "/" + deviceInfo['netmask'] + "</font>";
                                            document.getElementById('gateway' + deviceInfo['id']).innerHTML = "<font class='font12px'>" + deviceInfo['gateway'] + "</font>";
                                            if (deviceInfo['vrf'] == "0") {
                                                document.getElementById('vrf' + deviceInfo['id']).innerHTML = "<font class='font12px'>Not set</font>";
                                            }
                                            else if (deviceInfo['vrf'] == "default") {
                                                document.getElementById('vrf' + deviceInfo['id']).innerHTML = "<font class='font12px'>Default</font>";
                                            }
                                            else if (deviceInfo['vrf'] == "default") {
                                                document.getElementById('vrf' + deviceInfo['id']).innerHTML = "<font class='font12px'>Management</font>";
                                            }
                                        }
                                        // If the ztpenabled status is 9, we have to popup (only when the popup does not exist yet) and allow admin to test the credentials
                                        // If the credentials are good, we can set the status to 91 and let the daemon complete the setup
                                        document.getElementById('ztpStatus' + deviceInfo['id']).setAttribute('data-deviceid', deviceInfo['id']);
                                        // The status should only change if it is different from the original status
                                        if (deviceInfo['enableztp'] == 9) {
                                            if ($('#checkusername' + deviceInfo['id']).length === 0) {
                                                sleep(2000);
                                                credentialCheck = "<font class='font12px'>Username <input type='text' name='checkuser' id='checkusername" + deviceInfo['id'] + "' data-deviceid='" + deviceInfo['id'] + "' size='10'>";
                                                credentialCheck += "&nbsp;&nbsp;Password <input type='password' name='checkPassword' id='checkpassword" + deviceInfo['id'] + "' size='15'><input type='button' name='checkCredentials' class='checkCredentials' value='Verify administrative access' data-deviceid='" + deviceInfo['id'] + "'></font>";
                                                document.getElementById('ztpStatus' + deviceInfo['id']).innerHTML = credentialCheck;
                                            }
                                        }
                                        else {
                                            document.getElementById('ztpStatus' + deviceInfo['id']).innerHTML = "<font class='font12px'>" + deviceInfo['ztpstatus'] + "</font>";
                                        }
                                    }
                                    catch{
                                        //ignore error
                                    }
                                },
                                error: function () {
                                    //ignore error
                                }

                            });

                        }
                        catch (e) {
                            //Ignore this error
                        }
                    }
                }, 5000);
            }
            catch{
                console.log("There was an error");
            }
        });

    $('.ipamStatus').ready(
        function () {
            setInterval(async function () {
                    try {
                        response = await $.ajax({
                            type: "POST",
                            url: "/checkIpamstatus",
                            success: function (response) {
                                if (response == "Online") {
                                    document.getElementById("liProgress").style.display = "none";
                                    $(".editDevice").prop('disabled', false);
                                    $(".addDevice").prop('disabled', false);
                                    $(".editDevice").css("opacity", "1");
                                    $(".addDevice").css("opacity", "1");

                                }
                                else {
                                    $(".editDevice").prop('disabled', true);
                                    $(".addDevice").prop('disabled', true);
                                    $(".editDevice").css("opacity", "0.3");
                                    $(".addDevice").css("opacity", "0.3");
                                    document.getElementById("liProgress").style.display = "block";
                                    document.getElementById("progresstooltip").style.display = "none";
                                    progressInfo.innerHTML = "IPAM is not reachable";
                                }

                            }
                        });
                    }
                    catch (e) {
                        //Ignore this error
                    }
             }, 3000);
        });



    $(document).on("click", ".enableZTP", async function (enableZTP) {
        ztpStatus = await $.ajax({
            url: "/ztpActivate",
            type: "POST",
            data: { id: $(this).attr('data-deviceid'), macaddress: $(this).attr('data-macaddress')},
            success: function (ztpStatus) {
                // Activating the ZTP device was successful
                response = JSON.parse(ztpStatus);
                document.getElementById('ztpStatus' + response[1]).innerHTML = "<font class='font12px'>Enabled, start initialization</font>";
                //Also need to change the button from edit to show
                console.log(response);
                editshowHTML = "<input type='button' class='button showztplog' value='Show log' id='showztplog" + response[1] + "' data-deviceid='" + response[1] + "' onclick='highlightdeviceRow(this);'>";
                editshowHTML +="<input type='button' name='disableZTP' value='Disable ZTP' id='disableZTP" + response[1] + "' data-macaddress='{{info['macaddress']}}' data-deviceid='{{info['id']}}' class='disableZTP' onclick='highlightdeviceRow(this);'>";
                editshowHTML += "<input type='button' name='showDevice' value='Show' data-deviceid='" + response[1] + "' class='showDevice' id='showDevice" + response[1] + "' onclick='highlightdeviceRow(this);'>";

                //editshowHTML = "<input type='button' name='showDevice' value='Show' data-deviceid='" + response[1] + "' class='showDevice' id='showDevice" + response[1] + "'";
                //editshowHTML += "onclick = 'highlightdeviceRow(" + $("#ztpStatus" + response[1]).attr('id') + ");'>";
                document.getElementById('editOrshow' + response[1]).innerHTML = editshowHTML;

            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                document.getElementById("progresstooltip").style.display = "none";
                progressInfo.innerHTML = "Error activating the ZTP Device";
            }
        });
        document.getElementById("enableZTP" + $(this).attr('data-deviceid')).className = "disableZTP";
        document.getElementById("enableZTP" + $(this).attr('data-deviceid')).value = "Disable ZTP";
        document.getElementById('enableZTP' + $(this).attr('data-deviceid')).setAttribute('id', 'disableZTP' + $(this).attr('data-deviceid'));
        document.getElementById('disableZTP' + $(this).attr('data-deviceid')).setAttribute('data-macaddress', $(this).attr('data-macaddress'));
        document.getElementById("addDevice").style.display = "none";
        document.getElementById("editDevice").style.display = "none";
        document.getElementById("ztplog").style.display = "none"; 
    });

    $(document).on("click", ".checkCredentials", async function () {
        deviceid = $(this).attr('data-deviceid');
        username = document.getElementById("checkusername" + deviceid).value;
        password = document.getElementById("checkpassword" + deviceid).value;

        ztpStatus = await $.ajax({
            url: "/ztpCredentials",
            type: "POST",
            data: { deviceid: deviceid, username: username , password: password },
            success: function (response) {
                // Credential verification was successful, but there might be a validation error. This is checked in the Python definition
                response = JSON.parse(response);
                document.getElementById('ztpStatus' + response[1]).innerHTML = "<font class='font12px'>" + response[0] + "</font>";
            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                document.getElementById("progresstooltip").style.display = "none";
                progressInfo.innerHTML = "Credential verification failure";
            }
        });
    });

    $(document).on("click", "#clearLog", async function () {
        deviceid = $(this).attr('data-deviceid');
        var tableHeaderRowCount = 2;
        var table = document.getElementById('ztplogtable');
        var rowCount = table.rows.length;
        for (var i = tableHeaderRowCount; i < rowCount; i++) {
            table.deleteRow(tableHeaderRowCount);
        }
        ztpStatus = await $.ajax({
            url: "/clearztpLog",
            type: "POST",
            data: { deviceid: deviceid },
            success: function (response) {
                // Cleared ZTP log
            },
            error: function () {
                // Error clearing ZTP log
            }
         });
    });

    $(document).on("click", ".disableZTP", async function (disableZTP) {

        ztpStatus = await $.ajax({
            url: "/ztpDeactivate",
            type: "POST",
            data: { id: $(this).attr('data-deviceid'), macaddress: $(this).attr('data-macaddress') },
            success: function (ztpStatus) {
                // Deactivating the ZTP device was successful
                response = JSON.parse(ztpStatus);
                document.getElementById('ztpStatus' + response[1]).innerHTML = "<font class='font12px'>Disabled</font>";
                // Change the button to Edit button
                editshowHTML = "<input type='button' name='editDevice' value='Edit' data-deviceid='" + response[1] + "' class='editDevice' id='editDevice" + response[1] + "'";
                editshowHTML += "onclick = 'highlightdeviceRow(" + $("#ztpStatus" + response[1]).attr('id') + ");'";
                editshowHTML += ">";
                editshowHTML += "<input type='button' name='showDevice' value='Show' data-deviceid='" + response[1] + "' class='showDevice' id='showDevice" + response[1] + "'";
                editshowHTML += "onclick = 'highlightdeviceRow(" + $("#ztpStatus" + response[1]).attr('id') + ");'>";
                document.getElementById('editOrshow' + response[1]).innerHTML = editshowHTML;
            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                document.getElementById("progresstooltip").style.display = "none";
                progressInfo.innerHTML = "Error deactivating the ZTP Device";
            }
        });
        document.getElementById("disableZTP" + $(this).attr('data-deviceid')).className = "enableZTP";
        document.getElementById("disableZTP" + $(this).attr('data-deviceid')).value = "Enable ZTP";
        document.getElementById('disableZTP' + $(this).attr('data-deviceid')).setAttribute('id', 'enableZTP' + $(this).attr('data-deviceid'));
        document.getElementById('enableZTP' + $(this).attr('data-deviceid')).setAttribute('data-macaddress', $(this).attr('data-macaddress'));
        document.getElementById("addDevice").style.display = "none";
        document.getElementById("editDevice").style.display = "none";
        document.getElementById("ztplog").style.display = "none"; 
    });


      $(document).on('click', '.showDevice', function ()
        {
          document.getElementById("editDevice").style.display = "none";
          document.getElementById("addDevice").style.display = "none";
          document.getElementById("liProgress").style.display = "none";
          document.getElementById("ztplog").style.display = "none"; 
          document.getElementById("showdevice").style.display = "block";
          deviceid = $(this).attr('data-deviceid');
          document.getElementById('showdevice').setAttribute('data-deviceid', deviceid);
          $('#showdevice').load('showdevice?deviceid=' + document.getElementById('showdevice').getAttribute('data-deviceid'));
          setInterval(async function () {
              deviceid = document.getElementById('showdevice').getAttribute('data-deviceid');
              response = await $.ajax({
                  type: "POST",
                  data: { 'id': deviceid },
                  url: "/showdeviceStatus",
                  success: function (response) {
                      response = JSON.parse(response);
                      if (document.getElementById("showztpstatus")) {
                          if (response['vrf'] == "default" || response['vrf'] == "mgmt") {
                              vrf = response['vrf'];
                          }
                          else {
                              vrf = "Not set";
                          }
                          document.getElementById("showztpstatus").innerHTML = response['ztpstatus'];
                          document.getElementById("showIpaddress").innerHTML = response['ipaddress'] + "/" + response['netmask'];
                          document.getElementById("showGateway").innerHTML = response['gateway'];
                          document.getElementById("showVRF").innerHTML = vrf;
                      }
                  },

                  error: function () {
                      //ignore error
                      }
              });
          }, 5000);

        });

   
    $(document).on('click', '.editDevice',async function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById("editDevice").style.display = "block";
        document.getElementById("addDevice").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
        document.getElementById("ztplog").style.display = "none";
        document.getElementById("showdevice").style.display = "none";
        response = await $.ajax({
            url: "/ztpdeviceInfo",
            type: "POST",
            data: { id: deviceid },
            success: function () {
                // Obtaining the ZTP device was successful
            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                document.getElementById("progresstooltip").style.display = "none";
                progressInfo.innerHTML = "Error finding ZTP Device information";
            }
        });
        response = JSON.parse(response);
        deviceInfo = response['deviceInfo'];
        sysvars = response['sysvars'];
        ztpvlan=JSON.parse(deviceInfo['ztpvlan']);

        if ("ipamenabled" in sysvars) {
            var ipArray = [];
            if ("ipamIpaddress" in response) {
                if (sysvars['ipamsystem'] == "PHPIPAM") {
                    ipamIpaddress = response['ipamIpaddress']['data'];
                    // Create an array that contains the IP addresses that are in use. Distill from the ipamIpaddress object
                    if (typeof ipamIpaddress !== 'undefined') {
                        for (var j = 0; j < ipamIpaddress.length; j++) {
                            ipArray.push(ipamIpaddress[j]['ip']);
                        }
                    }
                }
                else if (sysvars['ipamsystem'] == "Infoblox") {
                    ipamIpaddress = response['ipamIpaddress']['result'];
                    // Create an array that contains the IP addresses that are in use. Distill from the ipamIpaddress object
                    if (typeof ipamIpaddress !== 'undefined') {
                        for (var j = 0; j < ipamIpaddress.length; j++) {
                            ipArray.push(ipamIpaddress[j]['ip_address']);
                        }
                    }
                }
            }
            else {
                document.getElementById("liProgress").style.display = "block";
                document.getElementById("progresstooltip").style.display = "none";
                progressInfo.innerHTML = "IPAM is not reachable";
            }
            document.getElementById('editipamnetmaskvalue').value = deviceInfo['netmask'];
            document.getElementById('editipamgatewayvalue').value = deviceInfo['gateway'];
            document.getElementById('editipamgatewayDiv').innerHTML = "<font class='font12px'>" + deviceInfo['gateway'] + "</font>";

            // Only show IPv4 subnets
            if (sysvars['ipamsystem'] == "PHPIPAM") {
                $('#editipamsubnet').empty();
                // Only fill the select list if ZTP DHCP is disabled
                for (var i = 0; i < response['subnets']['data'].length; i++) {
                    if (response['subnets']['data'][i]['subnet'].includes(":") == false) {
                        // It's an IPv4 subnet
                        if (parseInt(response['subnets']['data'][i]['id']) == deviceInfo['ipamsubnet']) {
                            $('#editipamsubnet').append('<option value=\"' + response['subnets']['data'][i]['id'] + '\" selected>' + response['subnets']['data'][i]['description'] + ' (' + response['subnets']['data'][i]['subnet'] + '/' + response['subnets']['data'][i]['mask'] + ')</option>');
                        }
                        else {
                            $('#editipamsubnet').append('<option value=\"' + response['subnets']['data'][i]['id'] + '\">' + response['subnets']['data'][i]['description'] + ' (' + response['subnets']['data'][i]['subnet'] + '/' + response['subnets']['data'][i]['mask'] + ')</option>');
                        }
                    }
                }
            }
            else if (sysvars['ipamsystem'] == "Infoblox") {
                $('#editipamsubnet').empty();
                for (var i = 0; i < response['subnets'].length; i++) {
                    if (response['subnets'][i]['network'] == deviceInfo['ipamsubnet']) {
                        $('#editipamsubnet').append('<option value=\"' + response['subnets'][i]['network'] + '\" selected>' + response['subnets'][i]['network'] + ' (' + response['subnets'][i]['comment'] + ')</option>');
                    }
                    else {
                        $('#editipamsubnet').append('<option value=\"' + response['subnets'][i]['network'] + '\">' + response['subnets'][i]['network'] + ' (' + response['subnets'][i]['comment'] + ')</option>');
                    }
                }
            }

            // If a subnet has already been selected, we can fill the IP address fields
            if ("ipamsubnet" in response) {
                // This is the calculation method for PHPIPAM
 
                if (sysvars['ipamsystem'] == "PHPIPAM") {
                    if (response['ipamsubnet']['code'] == "200") {
                        ip_start = response['ipamsubnet']['data']['calculation']['Min host IP'].split(".");
                        ip_end = response['ipamsubnet']['data']['calculation']['Max host IP'].split(".");
                        startip = "0x" + "00".substr(0, 2 - parseInt(ip_start[0]).toString(16).length) + parseInt(ip_start[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[1]).toString(16).length) + parseInt(ip_start[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[2]).toString(16).length) + parseInt(ip_start[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[3]).toString(16).length) + parseInt(ip_start[3]).toString(16);
                        endip = "0x" + "00".substr(0, 2 - parseInt(ip_end[0]).toString(16).length) + parseInt(ip_end[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[1]).toString(16).length) + parseInt(ip_end[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[2]).toString(16).length) + parseInt(ip_end[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[3]).toString(16).length) + parseInt(ip_end[3]).toString(16);
                    }
                    else {
                        startip = "0x0";
                        endip = "0x0";
                    }
               }
                else if (sysvars['ipamsystem'] == "Infoblox") {
                    cidrRange = cidrToRange(deviceInfo['ipamsubnet']);
                    ip_start = cidrRange[0].split(".");
                    ip_end = cidrRange[1].split(".");
                    startip = "0x" + "00".substr(0, 2 - parseInt(ip_start[0]).toString(16).length) + parseInt(ip_start[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[1]).toString(16).length) + parseInt(ip_start[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[2]).toString(16).length) + parseInt(ip_start[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[3]).toString(16).length) + parseInt(ip_start[3]).toString(16);
                    endip = "0x" + "00".substr(0, 2 - parseInt(ip_end[0]).toString(16).length) + parseInt(ip_end[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[1]).toString(16).length) + parseInt(ip_end[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[2]).toString(16).length) + parseInt(ip_end[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[3]).toString(16).length) + parseInt(ip_end[3]).toString(16);
                }
                for (var i = startip; i < endip; i++) {
                    // If the IP address is already used, it should not be selectable 
                    ipAddress = (i >>> 24) + '.' + (i >> 16 & 255) + '.' + (i >> 8 & 255) + '.' + (i & 255);
                    if (!ipArray.includes(ipAddress)) {
                        if (ipAddress == deviceInfo['ipaddress']) {
                            $('#editipamipaddress').append('<option value=\"' + ipAddress + '\" selected>' + ipAddress + '</option>');
                        }
                        else {
                            $('#editipamipaddress').append('<option value=\"' + ipAddress + '\">' + ipAddress + '</option>');
                        }
                    }

                }
            }
        }
        else {
            document.getElementById('editIpaddress').value = deviceInfo['ipaddress'];
            document.getElementById('editNetmask').value = deviceInfo['netmask'];
            document.getElementById('editGateway').value = deviceInfo['gateway'];
        }
        document.getElementById('deviceid').value = deviceInfo['id'];
        document.getElementById('editName').value = deviceInfo['name'];
        document.getElementById('editMacaddress').value = deviceInfo['macaddress'];
        if (deviceInfo['vrf'] == "") {
            document.getElementById('editVrf').value = 0;
        }
        else {
            document.getElementById('editVrf').value = deviceInfo['vrf'];
        }     
        document.getElementById('editSoftwareimage').value = deviceInfo['softwareimage'];
        document.getElementById('editTemplate').value = deviceInfo['template'];
        document.getElementById('editVsfrole').value = deviceInfo['vsfrole'];
        document.getElementById('editVsfmaster').value = deviceInfo['vsfmaster'];
        document.getElementById('editVsfmember').value = deviceInfo['vsfmember'];
        document.getElementById('editSelectswitchtype').value = deviceInfo['switchtype'];
        document.getElementById('edituplinkVlan').value = ztpvlan['uplinkVlan'];
        if (ztpvlan['taggedVlan'] == 1) {
            document.getElementById("edittaggedVlan").checked = true;
        }
 
        if (deviceInfo['vsfenabled'] == 1 ) {
            //VSF is enabled. We need to obtain the master switch information and push this to the select
            // Get the master VSF switches from the database and fill the select options
            var vsfmasterId = "editVsfmaster";
            response = await $.ajax({
                type: "POST",
                url: "/vsfmasterInfo",
                success: function (response) {
                    response = JSON.parse(response);
                    for (var i = 0; i < response.length; i++) {
                        if (response[i]['id'] == deviceInfo['vsfmaster']) {
                            $('#' + vsfmasterId).append('<option selected value="' + response[i]['id'] + '">' + response[i]['name'] + ' (' + response[i]['ipaddress'] + ')</option>');
                        }
                        else {
                        $('#' + vsfmasterId).append('<option value="' + response[i]['id'] + '">' + response[i]['name'] + ' (' + response[i]['ipaddress'] + ')</option>');
                        }

                    }
                }
            });



            document.getElementById("editEnablevsf").checked = true;
            if (deviceInfo['vsfrole']== "Master") {
                //Master is selected, disable the master switch and member id field
                $('#editVsfmaster').empty();
                $('#editVsfmaster').append('<option value="0">Select</option>');
                $('.selectVsfmember option:not(:selected)').attr('disabled', true);
            }
            else {
                //Device is not master, disable the software image, template, member id and master switch field
                $('.selectVsfmember').attr('disabled', false);
                $('.selectVsfmaster').attr('disabled', false);
                $('.selectSoftwareimage').attr('disabled', true);
                $('.selecttemplateparameters').attr('disabled', true);
            }
                if (deviceInfo['switchtype'] == "24") {
                    $('#editSelectlink1').empty();
                    $('#editSelectlink2').empty();
                    $('#editSelectlink1').append('<option value="">Select</option>');
                    $('#editSelectlink2').append('<option value="">Select</option>');
                    $('#editSelectlink1').append('<option value="1/1/25">1/1/25</option>');
                    $('#editSelectlink1').append('<option value="1/1/26">1/1/26</option>');
                    $('#editSelectlink1').append('<option value="1/1/27">1/1/27</option>');
                    $('#editSelectlink1').append('<option value="1/1/28">1/1/28</option>');
                    $('#editSelectlink2').append('<option value="1/1/25">1/1/25</option>');
                    $('#editSelectlink2').append('<option value="1/1/26">1/1/26</option>');
                    $('#editSelectlink2').append('<option value="1/1/27">1/1/27</option>');
                    $('#editSelectlink2').append('<option value="1/1/28">1/1/28</option>');
                }
                else if (deviceInfo['switchtype'] == "48") {
                    $('#editSelectlink1').empty();
                    $('#editSelectlink2').empty();
                    $('#editSelectlink1').append('<option value="">Select</option>');
                    $('#editSelectlink2').append('<option value="">Select</option>');
                    $('#editSelectlink1').append('<option value="1/1/49">1/1/49</option>');
                    $('#editSelectlink1').append('<option value="1/1/50">1/1/50</option>');
                    $('#editSelectlink1').append('<option value="1/1/51">1/1/51</option>');
                    $('#editSelectlink1').append('<option value="1/1/52">1/1/52</option>');
                    $('#editSelectlink2').append('<option value="1/1/49">1/1/49</option>');
                    $('#editSelectlink2').append('<option value="1/1/50">1/1/50</option>');
                    $('#editSelectlink2').append('<option value="1/1/51">1/1/51</option>');
                    $('#editSelectlink2').append('<option value="1/1/52">1/1/52</option>');
                }
            $.each(JSON.parse(deviceInfo['link1']), function (i, e) {
                    $("#editSelectlink1 option[value='" + unescape(e) + "']").prop("selected", true);
                });
            $.each(JSON.parse(deviceInfo['link2']), function (i, e) {
                    $("#editSelectlink2 option[value='" + unescape(e) + "']").prop("selected", true);
                });

            $('.selectVsfrole').attr('disabled', false);
            $('.selectVsflink1').attr('disabled', false);
            $('.selectVsflink2').attr('disabled', false);
        }
        else {
            //VSF is disabled. Disable all the VSF fields
            document.getElementById("editEnablevsf").checked = false;
            $('.selectSoftwareimage').attr('disabled', false);
            $('.selectVsfrole').attr('disabled', true);
            $('.selectVsflink1').attr('disabled', true);
            $('.selectVsflink2').attr('disabled', true);
            $('.selectVsfmember').attr('disabled', true);
            $('.selectVsfmaster').attr('disabled', true);
            $('.selecttemplateparameters').attr('disabled', false);

        }

        if (deviceInfo['ztpdhcp'] == 1) {
            document.getElementById("editztpdhcp").checked = true;
            if ($('#editipamsubnet').length) {
                $('#editipamsubnet option:not(:selected)').attr('disabled', true);
            }
            if ($('#editipamipaddress').length) {
                $('#editipamipaddress option:not(:selected)').attr('disabled', true);
            }
            if ($('#editIpaddress').length) {
                $('#editIpaddress option:not(:selected)').attr('disabled', true);
            }
            if ($('#editNetmask').length) {
                $('#editNetmask option:not(:selected)').attr('disabled', true);
            }
            if ($('#editGateway').length) {
                $('#editGateway option:not(:selected)').attr('disabled', true);
            }
            if ($('#editVrf').length) {
                $('#editVrf option:not(:selected)').attr('disabled', true);
            }
        }

        // If there is a template assigned to the device, we need to get the parameter information and build the table
        if (deviceInfo['template']!=0) {
            templateparameters = JSON.parse(deviceInfo['templateparameters']);     
            templateHTML = "<table class='tablenoborder' cellpadding='2'><tr><td colspan='2' style='background-color: grey;'><center><font class='font13pxwhite'>Template parameters</font></center></td></tr>";
            $.each(templateparameters, function (k, v) {
                templateHTML += "<tr><td width='10%'><font class='font13pxgrey'>" + k + "</font></td><td><input type='text' name='parameterValues[" + k + "]' value='" + v + "'></td></tr>";
            });
            templateHTML += "</table>";
            document.getElementById('edittemplateparametersDiv').style.display = "block";
            document.getElementById('edittemplateparametersDiv').innerHTML = templateHTML;
        }
        else {
            //There are no template parameters, however we have to provide a hidden input field to the form
            templateHTML = "<input type='hidden' name='templateparameters' value=''>";
            document.getElementById('edittemplateparametersDiv').innerHTML = templateHTML;
        }
    });
});

function cidrToRange(CIDR) {
    //Beginning IP address
    var beg = CIDR.substr(CIDR, CIDR.indexOf('/'));
    var end = beg;
    var off = (1 << (32 - parseInt(CIDR.substr(CIDR.indexOf('/') + 1)))) - 1;
    var sub = beg.split('.').map(function (a) { return parseInt(a) });

    //An IPv4 address is just an UInt32...
    var buf = new ArrayBuffer(4); //4 octets 
    var i32 = new Uint32Array(buf);

    //Get the UInt32, and add the bit difference
    i32[0] = (sub[0] << 24) + (sub[1] << 16) + (sub[2] << 8) + (sub[3]) + off;

    //Recombine into an IPv4 string:
    var end = Array.apply([], new Uint8Array(buf)).reverse().join('.');
    return [beg, end];

}

function highlightdeviceRow(e) {
    var tr = e.parentNode.parentNode;
    var table = e.parentNode.parentNode.parentNode;
    //set current backgroundColor
    var len = table.childNodes.length;
    for (var i = 0; i < len; i++) {
        if (table.childNodes[i].nodeType == 1) {
            table.childNodes[i].style.backgroundColor = 'transparent';
        }
    }
    tr.style.backgroundColor = 'darkorange';
    var tableTitles = document.getElementsByClassName('tableTitle');
    for (var i = 0; i < tableTitles.length; i++) {
        tableTitles[i].style.backgroundColor = 'grey';
    }
}

function cleardeviceRow(e) {
    var tr = e.parentNode.parentNode;
    var table = e.parentNode.parentNode.parentNode;
    var len = table.childNodes.length;
    for (var i = 0; i < len; i++) {
        if (table.childNodes[i].nodeType == 1) {
            table.childNodes[i].style.backgroundColor = 'transparent';
        }
    }
    var tableTitles = document.getElementsByClassName('tableTitle');
    for (var i = 0; i < tableTitles.length; i++) {
        tableTitles[i].style.backgroundColor = 'grey';
    }
}

$(document).on("click", "#searchDevice", function () {
    document.getElementById("editDevice").style.display = "none";
    document.getElementById("addDevice").style.display = "none";
    document.getElementById("ztplog").style.display = "none"; 
    document.getElementById("showdevice").style.display = "none";
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
    $("div[data-devicemgr='devicemgr']").load('ztpdevice?configentryperpage=' + configentryperpage + '&configpageoffset=' + configpageoffset + '&action=searchDevice');
    });



$(document).on("click", "#addztpDevice", async function () {
    document.getElementById("addDevice").style.display = "block";
    document.getElementById("editDevice").style.display = "none";
    document.getElementById("ztplog").style.display = "none"; 
    document.getElementById("liProgress").style.display = "none";
    document.getElementById("showdevice").style.display = "none";
    formId = "adddeviceForm";
    response = await $.ajax({
        url: "/ipamgetSubnet",
        type: "POST",
        success: function () {
            // Obtaining the IPAM information was successful
        },
        error: function () {
            document.getElementById("liProgress").style.display = "block";
            document.getElementById("progresstooltip").style.display = "none";
            progressInfo.innerHTML = "Error finding IPAM information";
        }


    });
    response = JSON.parse(response);
    sysvars = response['sysvars'];
    if ("ipamenabled" in sysvars) {
        $('#addipamsubnet').empty();
        $('#addipamsubnet').append('<option value=\"\" selected>Select subnet</option>');
        if (sysvars['ipamsystem'] == "PHPIPAM") {
            ipamsubnet = response['ipamsubnet']['data'];
            // Only show IPv4 subnets
            for (var i = 0; i < ipamsubnet.length; i++) {
                if (ipamsubnet[i]['subnet'].includes(":") == false) {
                    // It's an IPv4 subnet
                    $('#addipamsubnet').append('<option value=\"' + ipamsubnet[i]['id'] + '\">' + ipamsubnet[i]['description'] + ' (' + ipamsubnet[i]['subnet'] + '/' + ipamsubnet[i]['mask'] + ')</option>');
                }
            }
        }
        else if (sysvars['ipamsystem'] == "Infoblox") {
            ipamsubnet = response['ipamsubnet'];
            for (var i = 0; i < ipamsubnet.length; i++) {
                $('#addipamsubnet').append('<option value=\"' + ipamsubnet[i]['network'] + '\">' + ipamsubnet[i]['network'] + ' (' + ipamsubnet[i]['comment'] + ')</option>');
            }
        }
    }    
});


$(document).on("click", ".showztplog", function () {
    document.getElementById("addDevice").style.display = "none";
    document.getElementById("editDevice").style.display = "none";
    document.getElementById("liProgress").style.display = "none"; 
    document.getElementById("showdevice").style.display = "none";
    document.getElementById("ztplog").style.display = "block"; 
    deviceid = $(this).attr('data-deviceid');
    document.getElementById('ztplog').setAttribute('data-deviceid', deviceid);
    var refresh = function (deviceid) {
        $('#ztplog').load('ztplog?deviceid=' + document.getElementById('ztplog').getAttribute('data-deviceid'));
    }
    setInterval(refresh, 5000);
    refresh();  
});


function sleep(milliseconds) {
    const date = Date.now();
    let currentDate = null;
    do {
        currentDate = Date.now();
    } while (currentDate - date < milliseconds);
}



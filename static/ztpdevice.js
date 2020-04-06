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
            templateHTML = "<table class='tablenoborder' cellpadding='2'><tr style='background-color: black;line-height:20px;'><td colspan='2' style='color: darkorange;'><center>Template parameters</center></td></tr>";
            for (var i = 0; i < templateInfo.length; i++) {
                templateHTML += "<tr><td width='10%'><font class='font12px'>" + Object.keys(templateInfo[i]) + "</font></td ><td><input type='text' name='parameterValues[" + Object.keys(templateInfo[i]) + "]'></td></tr>";
            }
            templateHTML += "</table>";
            document.getElementById(templateDiv).style.display = "block";
            document.getElementById(templateDiv).innerHTML = templateHTML;
            //document.getElementsById(templateDiv)[0].style.display = "block";
            //document.getElementsById(templateDiv)[0].innerHTML = templateHTML;
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
            $('.selectSwitchtype').attr('disabled', false);
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
            $('.selectSwitchtype').attr('disabled', true);
            $('.selectSoftwareimage').attr('disabled', false);
            $('.selectTemplateparameters').attr('disabled', false);
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
            $('.selectVsfmember').attr('disabled', true);
            $('.selectVsfmaster').attr('disabled', true);
            $('.selectSoftwareimage').attr('disabled', false);
            $('.selectTemplateparameters').attr('disabled', false);
            $('.selectSoftwareimage').attr('disabled', false);
        }
        else {
            $('.selectVsfmember').attr('disabled', false);
            $('.selectVsfmaster').attr('disabled', false);
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
                    startip = "0x" + "00".substr(0, 2 - parseInt(ip_start[0]).toString(16).length) + parseInt(ip_start[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[1]).toString(16).length) + parseInt(ip_start[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[2]).toString(16).length) + parseInt(ip_start[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[3]).toString(16).length) + parseInt(ip_start[3]+1).toString(16);
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



    $('.ztpStatus').ready(
        function () {
            setInterval(async function () {
                ztpStatus = document.getElementsByClassName('ztpStatus');
                for (var i = 0; i < ztpStatus.length; i++) {
                   try {
                       deviceid = ztpStatus.item(i).getAttribute('data-deviceid');
                       response = await $.ajax({
                           type: "POST",
                           data: { 'id': deviceid },
                           url: "/ztpdeviceInfo",
                           success: function (response) {
                               response = JSON.parse(response);
                               deviceInfo = response['deviceInfo'];                            
                               document.getElementById('ztpStatus' + deviceid).innerHTML = "<font class='font12px'>" + deviceInfo['ztpstatus'] + "</font>";
                               document.getElementById('ztpStatus' + deviceid).setAttribute('data-deviceid', deviceid);
                           }
                       });
                   }
                   catch (e) {
                       //Ignore this error
                    }                 
                }
            }, 3000);
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
            success: function () {
                // Activating the ZTP device was successful
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
        //document.getElementById('editDevice' + $(this).attr('data-deviceid')).setAttribute('disabled', 'disabled');
        //document.getElementById('editDevice' + $(this).attr('data-deviceid')).style.opacity = "0.3";
        //document.getElementById('deleteDevice' + $(this).attr('data-deviceid')).setAttribute('disabled', 'disabled');
        //document.getElementById('deleteDevice' + $(this).attr('data-deviceid')).style.opacity = "0.6";
        document.getElementById("addDevice").style.display = "none";
        document.getElementById("editDevice").style.display = "none";
    });

    $(document).on("click", ".disableZTP", async function (disableZTP) {

        ztpStatus = await $.ajax({
            url: "/ztpDeactivate",
            type: "POST",
            data: { id: $(this).attr('data-deviceid'), macaddress: $(this).attr('data-macaddress') },
            success: function () {
                // Deactivating the ZTP device was successful
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
        //document.getElementById('editDevice' + $(this).attr('data-deviceid')).removeAttribute('disabled');
        //document.getElementById('editDevice' + $(this).attr('data-deviceid')).style.opacity = "1";
        //document.getElementById('deleteDevice' + $(this).attr('data-deviceid')).removeAttribute('disabled');
        //document.getElementById('deleteDevice' + $(this).attr('data-deviceid')).style.opacity = "1";
        document.getElementById("addDevice").style.display = "none";
        document.getElementById("editDevice").style.display = "none";
    });


    $('.editField input').keyup(function () {
        var fieldisEmpty = false;
        $('.editField input').keyup(function () {
            $('.editField input').each(function () {
                if ($(this).val().length == 0) {
                    fieldisEmpty = true;
                }
                else {
                    fieldisEmpty = false;
                }
            });

            // We also need to check the select values of the netmask and profile. If these are not selected, then we still need to disable the submit button

            $('.editselectField select').each(function () {
                if (!$(this).val()) {
                    fieldisEmpty = true;
                }
                else {
                    fieldisEmpty = false;
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
                if (!$(this).val()) {
                    fieldisEmpty = true;
                }
                else {
                    fieldisEmpty = false;
                }
            });

            // We also need to check the select values of the netmask and profile. If these are not selected, then we still need to disable the submit button

            $('.editselectField select').each(function () {
                if (!$(this).val()) {
                    fieldisEmpty = true;
                }
                else {
                    fieldisEmpty = false;
                }
            });

            if (fieldisEmpty) {
                $('.addActions input').attr('disabled', 'disabled');
            } else {
                $('.addActions input').attr('disabled', false);
            }
        });
    });

    $('.editselectField select').on('change', function () {
        $('.editselectField select').each(function () {
            if (!$(this).val()) {
                fieldisEmpty = true;
            }
            else {
                fieldisEmpty = false;
            }
        });

        // We also need to check the required text input. these are empty, then we still need to disable the submit button

        $('.editField input').each(function () {
            if (!$(this).val()) {
                fieldisEmpty = true;
            }
            else {
                fieldisEmpty = false;
            }
        });

        if (fieldisEmpty) {
            $('.addActions input').attr('disabled', 'disabled');
        } else {
            $('.addActions input').attr('disabled', false);
        }
    })

    $('.addselectField select').on('change', function () {
        $('.addselectField select').each(function () {
            if (!$(this).val()) {
                fieldisEmpty = true;
            }
            else {
                fieldisEmpty = false;
            }
        });

        // We also need to check the required text input. these are empty, then we still need to disable the submit button

        $('.addField input').each(function () {
            if (!$(this).val()) {
                fieldisEmpty = true;
            }
            else {
                fieldisEmpty = false;
            }
        });

        if (fieldisEmpty) {
            $('.addActions input').attr('disabled', 'disabled');
        } else {
            $('.addActions input').attr('disabled', false);
        }
    })

    $(".editDevice").click(async function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById("editDevice").style.display = "block";
        document.getElementById("addDevice").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
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
                    if (parseInt(response['subnets'][i]['network']) == deviceInfo['ipamsubnet']) {
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
                    ip_start = response['ipamsubnet']['data']['calculation']['Min host IP'].split(".");
                    ip_end = response['ipamsubnet']['data']['calculation']['Max host IP'].split(".");
                    startip = "0x" + "00".substr(0, 2 - parseInt(ip_start[0]).toString(16).length) + parseInt(ip_start[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[1]).toString(16).length) + parseInt(ip_start[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[2]).toString(16).length) + parseInt(ip_start[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_start[3]).toString(16).length) + parseInt(ip_start[3]).toString(16);
                    endip = "0x" + "00".substr(0, 2 - parseInt(ip_end[0]).toString(16).length) + parseInt(ip_end[0]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[1]).toString(16).length) + parseInt(ip_end[1]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[2]).toString(16).length) + parseInt(ip_end[2]).toString(16) + "00".substr(0, 2 - parseInt(ip_end[3]).toString(16).length) + parseInt(ip_end[3]).toString(16);
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
        document.getElementById('editProfile').value = deviceInfo['profile'];
        document.getElementById('editSoftwareimage').value = deviceInfo['softwareimage'];
        document.getElementById('editTemplate').value = deviceInfo['template'];
        document.getElementById('editVsfrole').value = deviceInfo['vsfrole'];
        document.getElementById('editVsfmaster').value = deviceInfo['vsfmaster'];
        document.getElementById('editVsfmember').value = deviceInfo['vsfmember'];
        document.getElementById('editSelectswitchtype').value = deviceInfo['switchtype'];
 
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
                //Master is selected, disable the software image, template, member id and master switch field
                $('#' + vsfmasterId).empty();
                $('#' + vsfmasterId).append('<option value="0">Select</option>');
                $('.selectVsfmember').attr('disabled', true);
                $('.selectVsfmaster').attr('disabled', true);
                $('.selectSoftwareimage').attr('disabled', false);
                $('.selecttemplateparameters').attr('disabled', false);

            }
            else {
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
            $('.selectSwitchtype').attr('disabled', true);
            $('.selectVsfrole').attr('disabled', true);
            $('.selectVsflink1').attr('disabled', true);
            $('.selectVsflink2').attr('disabled', true);
            $('.selectVsfmember').attr('disabled', true);
            $('.selectVsfmaster').attr('disabled', true);
            $('.selecttemplateparameters').attr('disabled', false);

        }

        // If there is a template assigned to the device, we need to get the parameter information and build the table
        if (deviceInfo['template']!=0) {
            templateparameters = JSON.parse(deviceInfo['templateparameters']);     
            templateHTML = "<table class='tablenoborder' cellpadding='2'><tr style='background-color: black;line-height:20px;'><td colspan='2' style='color: darkorange;'><center>Template parameters</center></td></tr>";
            $.each(templateparameters, function (k, v) {
                templateHTML += "<tr><td width='10%'><font class='font12px'>" + k + "</font></td ><td><input type='text' name='parameterValues[" + k + "]' value='" + v + "'></td></tr>";
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
    document.getElementById("liProgress").style.display = "none";
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
            //ipaddressField = $('#' + formId + ' .ipamipaddress').attr("id");
            //netmaskField = $('#' + formId + ' .ipamnetmask').attr("id");
            //gatewayField = $('#' + formId + ' .ipamgateway').attr("id");
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





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


    $(".portaccess").click(function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById('monitordevice').setAttribute('data-deviceid', deviceid);
        document.getElementById("monitordevice").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "block";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
        document.getElementById("deviceupgrade").style.display = "none";
        var refresh = function () {
            $('#portaccess').load('portAccess?deviceid=' + document.getElementById('monitordevice').getAttribute('data-deviceid'));
        }
        setInterval(refresh, 5000);
        refresh();
    });


    $(".deviceupgrade").click(function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById('deviceupgrade').setAttribute('data-deviceid', deviceid);
        document.getElementById("monitordevice").style.display = "none";
        document.getElementById("liProgress").style.display = "none";
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
        document.getElementById("deviceupgrade").style.display = "block";
        $('#deviceupgrade').load('deviceUpgrade?deviceid=' + deviceid);
    });



    $(".monitordevice").click(function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById('monitordevice').setAttribute('data-deviceid', deviceid);
        document.getElementById("monitordevice").style.display = "block";
        document.getElementById("liProgress").style.display = "none";
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
        document.getElementById("deviceupgrade").style.display = "none";
        $("div[data-selectinterface='selectinterface']").load('selectInterface?deviceid=' + document.getElementById('monitordevice').getAttribute('data-deviceid'));
        var refresh = function () {
            $("div[data-updateinfo='updatedeviceinfo']").load('updatedeviceinfo?deviceid=' + document.getElementById('monitordevice').getAttribute('data-deviceid'));
            $("div[data-cpuchart='graphData-CPU']").load('showGraph?entity=cpu&deviceid=' + document.getElementById('monitordevice').getAttribute('data-deviceid') );
            $("div[data-memchart='graphData-Memory']").load('showGraph?entity=memory&deviceid=' + document.getElementById('monitordevice').getAttribute('data-deviceid') );
            $("div[data-chart='deviceinfo']").load('showDevice?deviceid=' + document.getElementById('monitordevice').getAttribute('data-deviceid'));
         }
        setInterval(refresh, 15000);
        refresh();
    });

    $(document).on("click", "#searchDevice", function () {
        document.getElementById("liProgress").style.display = "none";
        document.getElementById("monitordevice").style.display = "none";
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
        document.getElementById("deviceupgrade").style.display = "none";
    });

    $(document).on("click", "#addDevice", function () {
        document.getElementById("liProgress").style.display = "none";
        document.getElementById("monitordevice").style.display = "none";
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "block";
        document.getElementById("deviceupgrade").style.display = "none";
    });

    $(".editDevice").click(async function () {
        deviceid = $(this).attr('data-deviceid');
        $('#manageAttributes').attr('data-deviceid', deviceid);
        document.getElementById("liProgress").style.display = "none";
        document.getElementById("monitordevice").style.display = "none";
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
        document.getElementById("manageAttributes").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "block";
        document.getElementById("deviceupgrade").style.display = "none";
        
        deviceInfo = await $.ajax({
            url: "/deviceInfo",
            type: "POST",
            data: { id: deviceid },
            success: function () {
                // Obtaining switch information was successful
            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                progressInfo.innerHTML = "Error finding device information";
            }
        });
        deviceInfo = JSON.parse(deviceInfo);
        document.getElementById('editIpaddress').value = deviceInfo['ipaddress'];
        document.getElementById('editDescription').value = deviceInfo['description'];
        document.getElementById('titleeditIpaddress').innerHTML = deviceInfo['ipaddress'];
        document.getElementById('titleeditDescription').innerHTML = deviceInfo['description'];
        document.getElementById('editUsername').value = deviceInfo['username'];
        document.getElementById('editPassword').value = deviceInfo['password'];
        document.getElementById('orgIPaddress').value = deviceInfo['ipaddress'];
        document.getElementById('deviceid').value = deviceid;
        if (deviceInfo['topology'] == 1) {
            document.getElementById("editTopology").checked = true;
        }
        else {
            document.getElementById("editTopology").checked = false;
        }
        if (deviceInfo['telemetryenable'] == 1) {
            document.getElementById("editTelemetry").checked = true;
        }
        else {
            document.getElementById("editTelemetry").checked = false;
        }
        if (deviceInfo['ostype'] == "arubaos-switch") {
            //Telemetry is not supported on arubaos switches, therefore disable the checkbox
            $('#editTelemetry').attr('disabled', true);
            document.getElementById("editTelemetry").checked = false;
        }
        else {
              $('#editTelemetry').attr('disabled', false);
            }
    });

    $(".selectInterface").on('change', function () {
        document.getElementById("interfaceinfo").style.display = "block";
        var refresh = function () {
            $("div[data-interfaceinfo='interfaceinfo']").load('showInterface?deviceid=' + document.getElementById('monitordevice').getAttribute('data-deviceid') + '&interface=' + $('#interface').val());
        }
        setInterval(refresh, 5000);
        refresh();
    });

    $(".configuration").click(function () {
        document.getElementById('configurationManager').setAttribute('data-deviceid',$(this).attr('data-deviceid'));
        document.getElementById('configurationManager').setAttribute('data-ostype', $(this).attr('data-ostype'));
        document.getElementById("configurationManager").style.display = "block";
        document.getElementById("liProgress").style.display = "none";
        document.getElementById("monitordevice").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
        document.getElementById("deviceupgrade").style.display = "none";
        $("div[data-configmgr='configmgr']").load('configmgr?action=&owner=&masterbackup=&searchconfigDescription=&configentryperpage=10&configpageoffset=0&deviceid=' + document.getElementById('configurationManager').getAttribute('data-deviceid'));
    });

    $(document).on("click", "#accessAction", async function () {
        resetClient = await $.ajax({
            url: "/resetClient",
            type: "POST",
            data: { deviceid: this.getAttribute('data-deviceid'), macaddress: this.getAttribute('data-macaddress'), port: this.getAttribute('data-port'), authmethod: this.getAttribute('data-auth') },
            success: function () {
                console.log("Client cleared");
            },
            error: function () {
                console.log("Error clearing client");
            }
        });
    });


    $(document).on("click", "#editdeviceAttributes", async function () {
        manageAttributes($('#manageAttributes').attr('data-deviceid'));      
    });

    
    $(document).on("click", ".assignAttribute", async function () {
        await $.ajax({
            type: "POST",
            data: { 'deviceid': $(this).attr('data-deviceid'), 'id': $(this).attr('data-id') },
            url: "/assignswitchAttribute",
            success: function (response) {
            },
            error: function () {
                console.log("There is an error assigning the attribute");
            }
        })
        manageAttributes($(this).attr('data-deviceid'));
    });


    $(document).on("click", ".removeAttribute", async function () {
        await $.ajax({
            type: "POST",
            data: { 'deviceid': $(this).attr('data-deviceid'), 'id': $(this).attr('data-id') },
            url: "/removeswitchAttribute",
            success: function (response) {
            },
            error: function () {
                console.log("There is an error removing the attribute");
            }
        })
        manageAttributes($(this).attr('data-deviceid'));
    });


    $(document).on("click", ".submitAttributes", async function () {
        //Construct the array. This is the format:  [{"id": 4 , "value": "d"},{"id": 5 , "value": "" },{"id": 6 , "value": ""  }]
        var attributeList = [];
        $('.changeAttribute').each(function () {
            var attributeSet = "{\"id\":" + $(this).data('id') + ", \"value\": \"" + $(this).val() + "\"}";
            attributeList.push(attributeSet);
        });
        // Store the attribute in the device table
        attributeList = attributeList.toString();
        await $.ajax({
            type: "POST",
            data: { 'deviceid': $('#manageAttributes').attr('data-deviceid'), 'attributeList': attributeList },
            url: "/submitswitchAttributes",
            success: function (response) {
            },
            error: function () {
                console.log("There is an error obtaining status information");
            }
        })
    });

    $(document).on("click", "#searchAttribute", async function () {
        manageAttributes($(this).attr('data-deviceid'));  
    });


    $('.isOnline').ready(function () {
        var refresh = async function () {
            isOnline = document.getElementsByClassName('isOnline');
            for (var i = 0; i < isOnline.length; i++) {
                deviceid = isOnline.item(i).getAttribute('data-deviceid');
                ostype = isOnline.item(i).getAttribute('data-ostype');
                await $.ajax({
                    type: "POST",
                    data: { 'deviceid': deviceid, 'ostype': ostype },
                    url: "/deviceStatus",
                    success: function (response) {
                        response = JSON.parse(response);
                        // For some strange reason it could be that the status that is received from the call is not for the same device. If that is the case, we have to skip the update
                        if (response['deviceid'] == deviceid) {
                            //We can show the status
                            if (response['status'] == "Online") {
                                document.getElementById('isOnline' + deviceid).innerHTML = "<img src='static/images/ok.png' height='15' width='15'>";
                                $('#isOnline' + deviceid).attr('data-status', '2');
                                $('#isOnline' + deviceid).attr('data-ostype', ostype);
                                $("#portaccess" + deviceid).prop('disabled', false);
                                $("#portaccess" + deviceid).css('opacity', '1');
                                $("#portaccess" + deviceid).css('pointer-events', 'auto');
                                $("#monitor" + deviceid).prop('disabled', false);
                                $("#monitor" + deviceid).css('opacity', '1');
                                $("#monitor" + deviceid).css('pointer-events', 'auto');
                                $("#configuration" + deviceid).prop('disabled', false);
                                $("#configuration" + deviceid).css('opacity', '1');
                                $("#configuration" + deviceid).css('pointer-events', 'auto');
                            }
                            if (response['status'] == "Offline") {
                                document.getElementById('isOnline' + deviceid).innerHTML = "<img src='static/images/notok.png' height='15' width='15'>";
                                $('#isOnline' + deviceid).attr('data-status', '0');
                                $('#isOnline' + deviceid).attr('data-ostype', ostype);
                                $("#portaccess" + deviceid).prop('disabled', true);
                                $("#portaccess" + deviceid).css('opacity', '0.1');
                                $("#portaccess" + deviceid).css('pointer-events', 'none');
                                $("#monitor" + deviceid).prop('disabled', true);
                                $("#monitor" + deviceid).css('opacity', '0.1');
                                $("#monitor" + deviceid).css('pointer-events', 'none');
                                $("#configuration" + deviceid).prop('disabled', true);
                                $("#configuration" + deviceid).css('opacity', '0.1');
                                $("#configuration" + deviceid).css('pointer-events', 'none');
                            }
                            if (response['status'] == "Unstable") {
                                document.getElementById('isOnline' + deviceid).innerHTML = "<img src='static/images/risk.png' height='15' width='15'>";
                                $('#isOnline' + deviceid).attr('data-status', '1');
                                $('#isOnline' + deviceid).attr('data-ostype', ostype);
                                $("#portaccess" + deviceid).prop('disabled', true);
                                $("#portaccess" + deviceid).css('opacity', '0.1');
                                $("#portaccess" + deviceid).css('pointer-events', 'none');
                                $("#monitor" + deviceid).prop('disabled', true);
                                $("#monitor" + deviceid).css('opacity', '0.1');
                                $("#monitor" + deviceid).css('pointer-events', 'none');
                                $("#configuration" + deviceid).prop('disabled', true);
                                $("#configuration" + deviceid).css('opacity', '0.1');
                                $("#configuration" + deviceid).css('pointer-events', 'none');
                            }
                        }
                    },
                    error: function () {
                        console.log("There is an error obtaining status information");
                    }
                })
            }
        }
        setInterval(refresh, 3000);
        refresh();
    });


    $('.deviceStatus').ready(function () {
        var refresh = async function () {
            deviceStatus = document.getElementsByClassName('deviceStatus');
            for (var i = 0; i < deviceStatus.length; i++) {
                deviceid = deviceStatus.item(i).getAttribute('data-deviceid');
                ostype = deviceStatus.item(i).getAttribute('data-ostype');
                await $.ajax({
                    type: "POST",
                    data: { 'deviceid': deviceid, 'ostype': ostype },
                    url: "/deviceStatus",
                    success: function (response) {
                        response = JSON.parse(response);
                        if (response['status'] == "Online") {
                            document.getElementById('deviceStatus' + deviceid).innerHTML = "<img src='static/images/ok.png' height='15' width='15'>" + deviceid;
                            $('#deviceStatus' + deviceid).attr('data-status', '2');
                            $('#deviceStatus' + deviceid).attr('data-ostype', ostype);
                            $("#portaccess" + deviceid).prop('disabled', false);
                            $("#portaccess" + deviceid).css('opacity', '1');
                            $("#portaccess" + deviceid).css('pointer-events', 'auto');
                            $("#monitor" + deviceid).prop('disabled', false);
                            $("#monitor" + deviceid).css('opacity', '1');
                            $("#monitor" + deviceid).css('pointer-events', 'auto');
                            $("#softwareupgrade" + deviceid).prop('disabled', false);
                            $("#softwareupgrade" + deviceid).css('opacity', '1');
                            $("#softwareupgrade" + deviceid).css('pointer-events', 'auto');
                        }
                        if (response['status'] == "Offline") {
                            document.getElementById('deviceStatus' + deviceid).innerHTML = "<img src='static/images/notok.png' height='15' width='15'>" + deviceid;
                            $('#deviceStatus' + deviceid).attr('data-status', '0');
                            $('#deviceStatus' + deviceid).attr('data-ostype', ostype);
                            $("#portaccess" + deviceid).prop('disabled', true);
                            $("#portaccess" + deviceid).css('opacity', '0.1');
                            $("#portaccess" + deviceid).css('pointer-events', 'none');
                            $("#monitor" + deviceid).prop('disabled', true);
                            $("#monitor" + deviceid).css('opacity', '0.1');
                            $("#monitor" + deviceid).css('pointer-events', 'none');
                            $("#softwareugprade" + deviceid).prop('disabled', true);
                            $("#softwareupgrade" + deviceid).css('opacity', '0.1');
                            $("#softwareupgrade" + deviceid).css('pointer-events', 'none');
                        }
                        if (response['status'] == "Unstable") {
                            document.getElementById('deviceStatus' + deviceid).innerHTML = "<img src='static/images/risk.png' height='15' width='15'>" + deviceid;
                            $('#deviceStatus' + deviceid).attr('data-status', '1');
                            $('#deviceStatus' + deviceid).attr('data-ostype', ostype);
                            $("#portaccess" + deviceid).prop('disabled', true);
                            $("#portaccess" + deviceid).css('opacity', '0.1');
                            $("#portaccess" + deviceid).css('pointer-events', 'none');
                            $("#monitor" + deviceid).prop('disabled', true);
                            $("#monitor" + deviceid).css('opacity', '0.1');
                            $("#monitor" + deviceid).css('pointer-events', 'none');
                            $("#softwareugprade" + deviceid).prop('disabled', true);
                            $("#softwareupgrade" + deviceid).css('opacity', '0.1');
                            $("#softwareupgrade" + deviceid).css('pointer-events', 'none');
                        }
                    },
                    error: function () {
                        console.log("There is an error obtaining status information");
                }
                });
            }
        }
        setInterval(refresh, 3000);
        refresh();
    });

    async function manageAttributes(deviceid) {
        document.getElementById("manageAttributes").style.display = "block";
        if ($('#searchattributeName').val()) {
            searchattributeName = $('#searchattributeName').val();
        }
        else {
            searchattributeName = "";
        }
        if ($('#searchattributeType').val()) {
            searchattributeType = $('#searchattributeType option:selected').val();
        }
        else {
            searchattributeType = "";
        }
        attrInfo = await $.ajax({
            url: "/deviceattributesList",
            type: "POST",
            data: { 'searchattributeName': searchattributeName, 'searchattributeType':searchattributeType },
            success: function () {
            },
            error: function () {
                console.log("Error obtaining device attribute list");
            }
        });
        assignedattrInfo = await $.ajax({
            url: "/assignedAttributes",
            type: "POST",
            data: { deviceid: deviceid },
            success: function () {
            },
            error: function () {
                console.log("Error obtaining device attribute list");
            }
        });
        attrInfo = JSON.parse(attrInfo);
        assignedattrInfo = JSON.parse(assignedattrInfo);
        attrlistHTML = "";
        assignedsetHTML = "";
        assignedList = [];
        for (i = 0; i < assignedattrInfo.length; i++) {
            assignedList.push(assignedattrInfo[i]['id']);
        }
        if (assignedattrInfo.length > 0) {
            assignedsetHTML = showassignedAttributes(assignedattrInfo, deviceid);
        }
        // Before calling the available attributes, we need to make sure that the already assigned attributes are removed from the attrInfo
        const ids = assignedList,
            data = {
                records: attrInfo
            };
        attrlistHTML = showavailableAttributes(data.records.filter(i => !ids.includes(i.id)), deviceid);
        $('#manageAttributes').empty().append(assignedsetHTML + attrlistHTML);
        
        $('#searchattributeName').val(searchattributeName);

        $('#searchattributeType').val(searchattributeType).change();

    }


    function showassignedAttributes(assignedattrInfo, deviceid) {
        attrsetHTML = "<table class='tablenoborder'>";
        attrsetHTML += "<tr style='background-color:grey;' class='tableTitle'><td colspan='5'><font class='font13pxwhite'><center>Assigned device attributes</center></font></td></tr>";
        attrsetHTML += "<tr class='tableTitle'>";
        attrsetHTML += "<td width='5%' align='left' nowrap class='whiteBG'><font class='font12pxgrey'>Item</font></td>";
        attrsetHTML += "<td width='15%' align='left' nowrap class='whiteBG'><font class='font12pxgrey'>Attribute name</font></td>";
        attrsetHTML += "<td width='15%' align='left' nowrap class='whiteBG'><font class='font12pxgrey'>Type</font></td>";
        attrsetHTML += "<td width='60%' align='left' nowrap class='whiteBG'><font class='font12pxgrey'>Value</font></td>";
        attrsetHTML += "<td width='5%' align='right' nowrap class='whiteBG'><font class='font12pxgrey'>Action</font></td>";
        attrsetHTML += "</tr>";
        for (var i = 1; i <= assignedattrInfo.length; i++) {
            attrsetHTML += "<tr><td scope='row'><font class='font12px'>" + parseInt(i) + "</font></td>";
            attrsetHTML += "<td align='left'><font class='font12px'>" + assignedattrInfo[i - 1]['name'] + "</font></td>";
            attrsetHTML += "<td><font class='font12px'>" + assignedattrInfo[i - 1]['type'] + "</font></td>";

            if (assignedattrInfo[i - 1]['type'] == "List") {
                listValues = JSON.parse(assignedattrInfo[i - 1]['values']);
                attrsetHTML += "<td>";
                attrsetHTML += "<select name='listAttribute' class='changeAttribute' data-id='" + assignedattrInfo[i - 1]['id'] + "' data-deviceid='" + deviceid + "' data-type='list' data-originalvalue='" + assignedattrInfo[i - 1]['value'] + "'>";
                attrsetHTML += "<option value=''>Select</option>";
                for (var ii = 1; ii <= listValues.length; ii++) {
                    if (listValues[ii - 1] == assignedattrInfo[i - 1]['value']) {
                        attrsetHTML += "<option value='" + listValues[ii - 1] + "' selected>" + listValues[ii - 1] + "</option>";
                    }
                    else {
                        attrsetHTML += "<option value='" + listValues[ii - 1] + "'>" + listValues[ii - 1] + "</option>";
                    }
                }
                attrsetHTML += "</select>";
                attrsetHTML += "</td>";
            }
            else if (assignedattrInfo[i - 1]['type'] == "Boolean") {
                attrsetHTML += "<td>";
                attrsetHTML += "<select name='booleanAttribute' class='changeAttribute' data-id='" + assignedattrInfo[i - 1]['id'] + "' data-deviceid='" + deviceid + "' data-type='boolean' data-originalvalue='" + assignedattrInfo[i - 1]['value'] + "'>";
                if (assignedattrInfo[i - 1]['value'] == 0) {
                    attrsetHTML += "<option value='0' selected>False</option>";
                }
                else {
                    attrsetHTML += "<option value='0'>False</option>";
                }
                if (assignedattrInfo[i - 1]['value'] == 1) {
                    attrsetHTML += "<option value='1' selected>True</option>";
                }
                else {
                    attrsetHTML += "<option value='1'>True</option>";
                }
                attrsetHTML += "</select>";
                attrsetHTML += "</td>";
            }
            else if (assignedattrInfo[i - 1]['type'] == "Value") {
                attrsetHTML += "<td><input type='text' value='" + assignedattrInfo[i - 1]['value'] + "' class='changeAttribute' data-id='" + assignedattrInfo[i - 1]['id'] + "' data-deviceid='" + deviceid + "' data-type='value' data-originalvalue='" + assignedattrInfo[i - 1]['value'] + "'></td>";
            }
            attrsetHTML += "<td align='right'><font class='font12px'><input type='button' name='removeAttribute' value='Remove' class='removeAttribute' id='removeAttribute" + assignedattrInfo[i - 1][' value'] + "' data-id='" + assignedattrInfo[i - 1]['id'] + "' data-deviceid='" + deviceid + "'></td > ";
            attrsetHTML += "</tr>";
        }
        attrsetHTML += "<tr><td align='center' colspan='5'><font class='font12px'><input type='button' name='submitAttributes' value='Submit attribute assignments' class='submitAttributes' id='submitAttributes'></td></tr>";
        attrsetHTML += "</table>";
        return attrsetHTML;
    }

    function showavailableAttributes(attrInfo, deviceid) {
        attrsetHTML = "<table class='tablenoborder'>";
        attrsetHTML += "<tr style='background-color:grey;' class='tableTitle'><td colspan='5'><font class='font13pxwhite'><center>Available device attributes</center></font></td></tr>";
        attrsetHTML += "<tr class='tableTitle'>";
        attrsetHTML += "<td width='5%' align='left' nowrap class='whiteBG'><font class='font12pxgrey'>Item</font></td>";
        attrsetHTML += "<td width='15%' align='left' nowrap class='whiteBG'><font class='font12pxgrey'>Attribute name</font></td>";
        attrsetHTML += "<td width='15%' align='left' nowrap class='whiteBG'><font class='font12pxgrey'>Type</font></td>";
        attrsetHTML += "<td width='60%' align='left' nowrap class='whiteBG'><font class='font12pxgrey'>Value(s)</font></td>";
        attrsetHTML += "<td width='5%' align='right' nowrap class='whiteBG'><font class='font12pxgrey'>Action</font></td>";
        attrsetHTML += "</tr>";
        attrsetHTML += "<tr>";
        attrsetHTML += "<td align='left' nowrap class='whiteBG'></td>";
        attrsetHTML += "<td align='left' nowrap class='whiteBG'><input type='text' name='searchattributeName' id='searchattributeName'></td>";
        attrsetHTML += "<td align='left' nowrap class='whiteBG'>";
        attrsetHTML += "<select name='searchattributeType' id='searchattributeType'>";
        attrsetHTML += "<option value=''>Select</option>";
        attrsetHTML += "<option value='boolean'>Boolean</option>";
        attrsetHTML += "<option value='value'>Value</option>";
        attrsetHTML += "<option value='list'>List</option>";
        attrsetHTML += "</select></td>";
        attrsetHTML += "<td align='left' nowrap class='whiteBG'></td>";
        attrsetHTML += "<td align='right' class='whiteBG'><font class='font12px'><input type='button' name='searchAttribute' value='Search' class='searchAttribute' id='searchAttribute' data-deviceid='" + deviceid + "'></td>";
        attrsetHTML += "</tr>";
        if (attrInfo.length > 0) {
            for (var i = 1; i <= attrInfo.length; i++) {
                // If the attribute is already assigned, we should not show it in this list
                attrsetHTML += "<tr><td scope='row'><font class='font12px'>" + parseInt(i) + "</font></td>";
                attrsetHTML += "<td align='left'><font class='font12px'>" + attrInfo[i - 1]['name'] + "</font></td>";
                attrsetHTML += "<td><font class='font12px'>" + attrInfo[i - 1]['type'] + "</font></td>";
                if (attrInfo[i - 1]['type'] == "list") {
                    attrsetHTML += "<td><font class='font12px'>";
                    attrList = JSON.parse(attrInfo[i - 1]['attributelist']);
                    var listAttributes = "";
                    for (var ii = 1; ii <= attrList.length; ii++) {
                        listAttributes += attrList[ii - 1] + ", ";
                    }
                    attrsetHTML += listAttributes.substring(0, listAttributes.length - 2) + "</font></td>";
                }

                else {
                    attrsetHTML += "<td><font class='font12px'></font></td>";
                }

                attrsetHTML += "<td align='right'><font class='font12px'><input type='button' name='assignAttribute' value='Assign' class='assignAttribute' id='assignAttribute" + attrInfo[i - 1]['id'] + "' data-id='" + attrInfo[i - 1]['id'] + "'  data-deviceid='" + deviceid + "'></td>";
                attrsetHTML += "</tr>";
            }
        }
        attrsetHTML += "</table>";
        return attrsetHTML;
    }


    $('.showattributeTooltip').mouseover(async function (event) {
        //var left = event.pageX - $(this).offset().left + 100;
        //var top = event.pageY - $(this).offset().top + 130;
        var left = event.pageX-310;
        var top = event.pageY+10;
        assignedattrInfo = await $.ajax({
            url: "/showassignedAttributes",
            type: "POST",
            data: { deviceid: $(this).attr('data-deviceid') },
            success: function () {
            },
            error: function () {
                console.log("Error obtaining device attribute list");
            }
        });
        $("#showdaTooltip").css({
            position: 'absolute',
            zIndex: 5000,
            left: left,
            top: top,
            width: '350px',
        });
        // Construct the innerHTML
        attrsetHTML = "<table class='tablewithborder' style='max-width: 300px;'>";
        attrsetHTML += "<tr class='tableTitle'>";
        attrsetHTML += "<td width='20%' align='left' nowrap><font class='font12pxwhite'>Attribute name</font></td>";
        attrsetHTML += "<td width='20%' align='left' nowrap><font class='font12pxwhite'>Type</font></td>";
        attrsetHTML += "<td width='60%' align='left' nowrap><font class='font12pxwhite'>Value</font></td>";
        attrsetHTML += "</tr>";
        assignedattrInfo = JSON.parse(assignedattrInfo);
        for (var i = 0; i < assignedattrInfo.length; i++) {
            attrsetHTML += "<tr>";
            attrsetHTML += "<td class='whiteBG'><font class='font12pxgrey'>" + assignedattrInfo[i]['name'] + "</font></td>";
            attrsetHTML += "<td class='whiteBG'><font class='font12pxgrey'>" + assignedattrInfo[i]['type'].charAt(0).toUpperCase() + assignedattrInfo[i]['type'].slice(1) + "</font></td>";
            if (assignedattrInfo[i]['type'] == "boolean" && assignedattrInfo[i]['value'] == "1") {
                attrsetHTML += "<td class='whiteBG'><font class='font12pxgrey'>True</font></td>";
            }
            else if (assignedattrInfo[i]['type'] == "boolean" && assignedattrInfo[i]['value'] == "0") {
                attrsetHTML += "<td class='whiteBG'><font class='font12pxgrey'>True</font></td>"
            }
            else {
                attrsetHTML += "<td class='whiteBG'><font class='font12pxgrey'>" + assignedattrInfo[i]['value'] + "</font></td>";
            }
            attrsetHTML += "</tr>";      
        }
        attrsetHTML += "</table>";
        $('#showdaTooltip').empty().append(attrsetHTML);
        $('#showdaTooltip').show();
    });

    $('.showattributeTooltip').mouseout(function () {
        $('#showdaTooltip').hide();
    });


});



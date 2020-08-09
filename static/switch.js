// (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

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
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "block";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
        var refresh = function () {
            $('#portaccess').load('portAccess?deviceid=' + document.getElementById('monitordevice').getAttribute('data-deviceid'));
        }
        setInterval(refresh, 5000);
        refresh();
    });



    $(".monitordevice").click(function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById('monitordevice').setAttribute('data-deviceid', deviceid);
        document.getElementById("monitordevice").style.display = "block";
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
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
        document.getElementById("monitordevice").style.display = "none";
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
    });

    $(document).on("click", "#addDevice", function () {
        document.getElementById("monitordevice").style.display = "none";
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "block";
    });

    $(".editDevice").click(async function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById("monitordevice").style.display = "none";
        document.getElementById("configurationManager").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "block";
        
        deviceInfo = await $.ajax({
            url: "/deviceInfo",
            type: "POST",
            data: { id: deviceid },
            success: function () {
                // Obtaining switch information was successful
            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                document.getElementById("progresstooltip").style.display = "none";
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
        document.getElementById("monitordevice").style.display = "none";
        document.getElementById("portaccess").style.display = "none";
        document.getElementById("interfaceinfo").style.display = "none";
        document.getElementById("editDeviceForm").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "none";
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
                                if (ostype == "arubaos-switch") {
                                    $("#portaccess" + deviceid).prop('disabled', false);
                                    $("#portaccess" + deviceid).css('opacity', '1');
                                    $("#portaccess" + deviceid).css('pointer-events', 'auto');
                                    $("#monitor" + deviceid).prop('disabled', false);
                                    $("#monitor" + deviceid).css('opacity', '1');
                                    $("#monitor" + deviceid).css('pointer-events', 'auto');
                                }
                                else {
                                    $("#monitor" + deviceid).prop('disabled', false);
                                    $("#monitor" + deviceid).css('opacity', '1');
                                    $("#monitor" + deviceid).css('pointer-events', 'auto');
                                }
                            }
                            if (response['status'] == "Offline") {
                                document.getElementById('isOnline' + deviceid).innerHTML = "<img src='static/images/notok.png' height='15' width='15'>";
                                $('#isOnline' + deviceid).attr('data-status', '0');
                                $('#isOnline' + deviceid).attr('data-ostype', ostype);
                                if (ostype == "arubaos-switch") {
                                    $("#portaccess" + deviceid).prop('disabled', true);
                                    $("#portaccess" + deviceid).css('opacity', '0.1');
                                    $("#portaccess" + deviceid).css('pointer-events', 'none');
                                    $("#monitor" + deviceid).prop('disabled', true);
                                    $("#monitor" + deviceid).css('opacity', '0.1');
                                    $("#monitor" + deviceid).css('pointer-events', 'none');
                                }
                                else {
                                    $("#monitor" + deviceid).prop('disabled', true);
                                    $("#monitor" + deviceid).css('opacity', '0.1');
                                    $("#monitor" + deviceid).css('pointer-events', 'none');
                                }
                            }
                            if (response['status'] == "Unstable") {
                                document.getElementById('isOnline' + deviceid).innerHTML = "<img src='static/images/risk.png' height='15' width='15'>";
                                $('#isOnline' + deviceid).attr('data-status', '1');
                                $('#isOnline' + deviceid).attr('data-ostype', ostype);
                                if (ostype == "arubaos-switch") {
                                    $("#portaccess" + deviceid).prop('disabled', true);
                                    $("#portaccess" + deviceid).css('opacity', '0.1');
                                    $("#portaccess" + deviceid).css('pointer-events', 'none');
                                    $("#monitor" + deviceid).prop('disabled', true);
                                    $("#monitor" + deviceid).css('opacity', '0.1');
                                    $("#monitor" + deviceid).css('pointer-events', 'none');
                                }
                                else {
                                    $("#monitor" + deviceid).prop('disabled', true);
                                    $("#monitor" + deviceid).css('opacity', '0.1');
                                    $("#monitor" + deviceid).css('pointer-events', 'none');
                                }
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
                            if (ostype == "arubaos-switch") {
                                $("#portaccess" + deviceid).prop('disabled', false);
                                $("#portaccess" + deviceid).css('opacity', '1');
                                $("#portaccess" + deviceid).css('pointer-events', 'auto');
                                $("#monitor" + deviceid).prop('disabled', false);
                                $("#monitor" + deviceid).css('opacity', '1');
                                $("#monitor" + deviceid).css('pointer-events', 'auto');
                            }
                            else {
                                $("#monitor" + deviceid).prop('disabled', false);
                                $("#monitor" + deviceid).css('opacity', '1');
                                $("#monitor" + deviceid).css('pointer-events', 'auto');
                            }
                        }
                        if (response['status'] == "Offline") {
                            document.getElementById('deviceStatus' + deviceid).innerHTML = "<img src='static/images/notok.png' height='15' width='15'>" + deviceid;
                            $('#deviceStatus' + deviceid).attr('data-status', '0');
                            $('#deviceStatus' + deviceid).attr('data-ostype', ostype);
                            if (ostype == "arubaos-switch") {
                                $("#portaccess" + deviceid).prop('disabled', true);
                                $("#portaccess" + deviceid).css('opacity', '0.1');
                                $("#portaccess" + deviceid).css('pointer-events', 'none');
                                $("#monitor" + deviceid).prop('disabled', true);
                                $("#monitor" + deviceid).css('opacity', '0.1');
                                $("#monitor" + deviceid).css('pointer-events', 'none');
                            }
                            else {
                                $("#monitor" + deviceid).prop('disabled', true);
                                $("#monitor" + deviceid).css('opacity', '0.1');
                                $("#monitor" + deviceid).css('pointer-events', 'none');
                            }
                        }
                        if (response['status'] == "Unstable") {
                            document.getElementById('deviceStatus' + deviceid).innerHTML = "<img src='static/images/risk.png' height='15' width='15'>" + deviceid;
                            $('#deviceStatus' + deviceid).attr('data-status', '1');
                            $('#deviceStatus' + deviceid).attr('data-ostype', ostype);
                            if (ostype == "arubaos-switch") {
                                $("#portaccess" + deviceid).prop('disabled', true);
                                $("#portaccess" + deviceid).css('opacity', '0.1');
                                $("#portaccess" + deviceid).css('pointer-events', 'none');
                                $("#monitor" + deviceid).prop('disabled', true);
                                $("#monitor" + deviceid).css('opacity', '0.1');
                                $("#monitor" + deviceid).css('pointer-events', 'none');
                            }
                            else {
                                $("#monitor" + deviceid).prop('disabled', true);
                                $("#monitor" + deviceid).css('opacity', '0.1');
                                $("#monitor" + deviceid).css('pointer-events', 'none');
                            }
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


 
});
// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

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

    $.getScript('static/mobilityinterfaces.js');
    $.getScript('static/mobilityroles.js');
    $.getScript('static/mobilitypolicies.js');

    $(".editDevice").click(async function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById("mobilityInterfaces").style.display = "none";
        document.getElementById("interfaceAction").style.display = "none";
        document.getElementById("mobilityRoles").style.display = "none";
        document.getElementById("roleAction").style.display = "none";
        document.getElementById("mobilityPolicies").style.display = "none";
        document.getElementById("policyAction").style.display = "none";
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
                showmessageBar("Error finding device information");
            }
        });
        deviceInfo = JSON.parse(deviceInfo);
        document.getElementById('editIpaddress').value = deviceInfo['ipaddress'];
        document.getElementById('editDescription').value = deviceInfo['description'];
        document.getElementById('titleeditIpaddress').innerHTML = deviceInfo['ipaddress'];
        document.getElementById('titleeditDescription').innerHTML = deviceInfo['description'];
        document.getElementById('editUsername').value = deviceInfo['username'];
        document.getElementById('editPassword').value = deviceInfo['password'];
        document.getElementById('deviceid').value = deviceid;
    });


    $(document).on("click", "#addDevice", function () {
        document.getElementById("mobilityInterfaces").style.display = "none";
        document.getElementById("interfaceAction").style.display = "none";
        document.getElementById("mobilityRoles").style.display = "none";
        document.getElementById("roleAction").style.display = "none";
        document.getElementById("mobilityPolicies").style.display = "none";
        document.getElementById("policyAction").style.display = "none";
        document.getElementById("addDeviceForm").style.display = "block";
        document.getElementById("editDeviceForm").style.display = "none";
    });
      
});


$('.mcStatus').ready(function () {

    var refresh = async function () {

        mcStatus = document.getElementsByClassName('mcStatus');
        for (var i = 0; i < mcStatus.length; i++) {
            deviceid = mcStatus.item(i).getAttribute('data-deviceid');
            await $.ajax({
                type: "POST",
                data: { 'deviceid': deviceid },
                url: "/mcStatus",
                success: function (response) {
                    response = JSON.parse(response);
                    if (response['status'] == "Online") {
                        document.getElementById('mcStatus' + deviceid).innerHTML = "<img src='static/images/status-good.svg' height='12' width='12' class='showtitleTooltip' data-title='Device is online'>";
                        $("#mobilityInterfaces" + deviceid).prop('disabled', false);
                        $("#mobilityInterfaces" + deviceid).css('opacity', '1');
                        $("#mobilityInterfaces" + deviceid).css('pointer-events', 'auto');
                        $("#mobilityRoles" + deviceid).prop('disabled', false);
                        $("#mobilityRoles" + deviceid).css('opacity', '1');
                        $("#mobilityRoles" + deviceid).css('pointer-events', 'auto');
                        $("#mobilityPolicies" + deviceid).prop('disabled', false);
                        $("#mobilityPolicies" + deviceid).css('opacity', '1');
                        $("#mobilityPolicies" + deviceid).css('pointer-events', 'auto');
                    }
                    else {
                        document.getElementById('mcStatus' + deviceid).innerHTML = "<img src='static/images/status-critical.svg' height='12' width='12' class='showtitleTooltip' data-title='Device is unreachable'>";
                        $("#mobilityInterfaces" + deviceid).prop('disabled', true);
                        $("#mobilityInterfaces" + deviceid).css('opacity', '0.1');
                        $("#mobilityInterfaces" + deviceid).css('pointer-events', 'none');
                        $("#mobilityRoles" + deviceid).prop('disabled', true);
                        $("#mobilityRoles" + deviceid).css('opacity', '0.1');
                        $("#mobilityRoles" + deviceid).css('pointer-events', 'none');
                        $("#mobilityPolicies" + deviceid).prop('disabled', true);
                        $("#mobilityPolicies" + deviceid).css('opacity', '0.1');
                        $("#mobilityPolicies" + deviceid).css('pointer-events', 'none');
                    }
                }

            });

        }
    }
    setInterval(refresh, 10000);
    refresh();
});
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

    $(".editDevice").click(async function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById("adddeviceForm").style.display = "none";
        document.getElementById("editdeviceForm").style.display = "block";

        deviceInfo = await $.ajax({
            url: "/deviceInfo",
            type: "POST",
            data: { id: deviceid },
            success: function () {
                // Obtaining ClearPass information was successful
            },
            error: function () {
                document.getElementById("liProgress").style.display = "block";
                document.getElementById("progresstooltip").style.display = "none";
                progressInfo.innerHTML = "Error finding device information";
            }
        });
        deviceInfo = JSON.parse(deviceInfo);
        console.log(deviceInfo);
        document.getElementById('editIpaddress').value = deviceInfo['ipaddress'];
        document.getElementById('editDescription').value = deviceInfo['description'];
        document.getElementById('titleeditIpaddress').innerHTML = deviceInfo['ipaddress'];
        document.getElementById('titleeditDescription').innerHTML = deviceInfo['description'];
        document.getElementById('editUsername').value = deviceInfo['username'];
        document.getElementById('editPassword').value = deviceInfo['password'];
        document.getElementById('editsharedSecret').value = deviceInfo['secinfo'];
        document.getElementById('editdeviceid').value = deviceid;
    });


    $(document).on("click", "#addDevice", function () {
        document.getElementById("adddeviceForm").style.display = "block";
        document.getElementById("editdeviceForm").style.display = "none";
    });

});

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

$(document).ready(function () {
    $('.field input').keyup(function () {
        var fieldisEmpty = false;
        $('.field input').keyup(function () {
            $('.field input').each(function () {
                if ($(this).val().length == 0) {
                    fieldisEmpty = true;
                }
            });
            if (fieldisEmpty) {
                $('.actions input').attr('disabled', 'disabled');
            } else {
                $('.actions input').attr('disabled', false);
            }
        });
    });

});

$('.cpStatus').ready(function () {

    var refresh = async function () {

        cpStatus = document.getElementsByClassName('cpStatus');
        for (var i = 0; i < cpStatus.length; i++) {
            deviceid = cpStatus.item(i).getAttribute('data-deviceid');
            await $.ajax({
                type: "POST",
                data: { 'deviceid': deviceid},
                url: "/cpStatus",
                success: function (response) {
                    response = JSON.parse(response);
                    if (response['status'] == "Online") {
                        document.getElementById('cpStatus' + deviceid).innerHTML = "<img src='static/images/ok.png' height='15' width='15'>";
                    }
                    else {
                        document.getElementById('cpStatus' + deviceid).innerHTML = "<img src='static/images/notok.png' height='15' width='15'>";
                    }
                }

            });

        }
    }
    setInterval(refresh, 10000);
    refresh();
});
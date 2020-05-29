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
        document.getElementById("showTrust").style.display = "none";
        document.getElementById("showEndpoints").style.display = "none";
        document.getElementById("showServices").style.display = "none";

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
        document.getElementById("showTrust").style.display = "none";
        document.getElementById("showEndpoints").style.display = "none";
        document.getElementById("showServices").style.display = "none";
    });




    $(".showTrust").on('click', function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById("showTrust").style.display = "block";
        document.getElementById("showEndpoints").style.display = "none";
        document.getElementById("showServices").style.display = "none";
        document.getElementById("adddeviceForm").style.display = "none";
        document.getElementById("editdeviceForm").style.display = "none";
        $('#showTrust').load('cpTrusts?deviceid=' + deviceid + "&trEntryperpage=25&trPageoffset=0&searchSubject=&searchValid=&searchStatus=");
    });

    $(".showServices").on('click', function () {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById("showTrust").style.display = "none";
        document.getElementById("showEndpoints").style.display = "none";
        document.getElementById("showServices").style.display = "block";
        document.getElementById("adddeviceForm").style.display = "none";
        document.getElementById("editdeviceForm").style.display = "none";
        $('#showServices').load('cpServices?deviceid=' + deviceid + "&seEntryperpage=25&sePageoffset=0&searchName=&searchType=&searchTemplate=&searchStatus=");
    });

    $(".showEndpoints").on('click', function (event) {
        deviceid = $(this).attr('data-deviceid');
        document.getElementById("showTrust").style.display = "none";
        document.getElementById("showEndpoints").style.display = "block";
        document.getElementById("showServices").style.display = "none";
        document.getElementById("adddeviceForm").style.display = "none";
        document.getElementById("editdeviceForm").style.display = "none";
        $('#showEndpoints').load('cpEndpoints?deviceid=' + deviceid + "&epEntryperpage=25&epPageoffset=0&searchMacaddress=&searchDescription=&searchStatus=");
    });

});

function showEndpoints(deviceid) {
    var epp_select = document.getElementById('epEntryperpage');
    var epEntryperpage = epp_select.options[epp_select.selectedIndex].value;
    var currentepEntryperpage = document.getElementById('currentepEntryperpage').value;
    var epstatus_select = document.getElementById('searchStatus');
    var searchStatus = epstatus_select.options[epstatus_select.selectedIndex].value;
    var searchMacaddress = document.getElementById('searchMacaddress').value;
    var searchDescription = document.getElementById('searchDescription').value;
    if (epEntryperpage == currentepEntryperpage) {
        var po_select = document.getElementById('epPageoffset');
        var epPageoffset = po_select.options[po_select.selectedIndex].value;
    }
    else {
        epPageoffset = 0;
    }
    document.getElementById("showTrust").style.display = "none";
    document.getElementById("showEndpoints").style.display = "block";
    document.getElementById("showServices").style.display = "none";
    document.getElementById("adddeviceForm").style.display = "none";
    document.getElementById("editdeviceForm").style.display = "none";
    $('#showEndpoints').load('cpEndpoints?deviceid=' + deviceid + "&epEntryperpage=" + epEntryperpage + "&epPageoffset=" + epPageoffset + "&searchMacaddress=" + searchMacaddress + "&searchDescription=" + searchDescription + "&searchStatus=" + searchStatus);
}

function showTrusts(deviceid) {
    var epp_select = document.getElementById('trEntryperpage');
    var trEntryperpage = epp_select.options[epp_select.selectedIndex].value;
    var currenttrEntryperpage = document.getElementById('currenttrEntryperpage').value;
    var trstatus_select = document.getElementById('searchStatus');
    var searchStatus = trstatus_select.options[trstatus_select.selectedIndex].value;
    var vlstatus_select = document.getElementById('searchValid');
    var searchValid = vlstatus_select.options[vlstatus_select.selectedIndex].value;
    var searchSubject = document.getElementById('searchSubject').value;
    if (trEntryperpage == currenttrEntryperpage) {
        var po_select = document.getElementById('trPageoffset');
        var trPageoffset = po_select.options[po_select.selectedIndex].value;
    }
    else {
        trPageoffset = 0;
    }
    document.getElementById("showTrust").style.display = "block";
    document.getElementById("showEndpoints").style.display = "none";
    document.getElementById("showServices").style.display = "none";
    document.getElementById("adddeviceForm").style.display = "none";
    document.getElementById("editdeviceForm").style.display = "none";
    $('#showTrust').load('cpTrusts?deviceid=' + deviceid + "&trEntryperpage=" + trEntryperpage + "&trPageoffset=" + trPageoffset + "&searchStatus=" + searchStatus + "&searchValid=" + searchValid + "&searchSubject=" + searchSubject);
}

function showServices(deviceid) {
    var epp_select = document.getElementById('seEntryperpage');
    var seEntryperpage = epp_select.options[epp_select.selectedIndex].value;
    var currentseEntryperpage = document.getElementById('currentseEntryperpage').value;
    var sestatus_select = document.getElementById('searchStatus');
    var searchStatus = sestatus_select.options[sestatus_select.selectedIndex].value;
    var searchName = document.getElementById('searchName').value;
    var searchType = document.getElementById('searchType').value;
    var searchTemplate = document.getElementById('searchTemplate').value;
    if (seEntryperpage == currentseEntryperpage) {
        var po_select = document.getElementById('sePageoffset');
        var sePageoffset = po_select.options[po_select.selectedIndex].value;
    }
    else {
        sePageoffset = 0;
    }
    document.getElementById("showTrust").style.display = "none";
    document.getElementById("showEndpoints").style.display = "none";
    document.getElementById("showServices").style.display = "block";
    document.getElementById("adddeviceForm").style.display = "none";
    document.getElementById("editdeviceForm").style.display = "none";
    $('#showServices').load('cpServices?deviceid=' + deviceid + "&seEntryperpage=" + seEntryperpage + "&sePageoffset=" + sePageoffset + "&searchName=" + searchName + "&searchType=" + searchType + "&searchTemplate=" + searchTemplate + "&searchStatus=" + searchStatus);
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
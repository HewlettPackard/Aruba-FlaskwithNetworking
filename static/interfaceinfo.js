// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

$('.monitor-interface').ready(function () {
    var refresh = function () {
        if ($('#deviceid').length > 0) {
        deviceid = document.getElementById('deviceid').getAttribute('value');
        interface = document.getElementById('monitorinterface').getAttribute('value');
        ostype = document.getElementById('ostype').getAttribute('value');
        $("div[data-chart='interfaceinfo']").load('showInterface?deviceid=' + deviceid + '&interface=' + interface + '&ostype=' + ostype);
        }
    }
    setInterval(refresh, 5000);
    refresh();
});
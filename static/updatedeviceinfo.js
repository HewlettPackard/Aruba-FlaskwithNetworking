// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

$('.updatedeviceinfo').ready(function () {
    var refresh = function () {
        if ($('#deviceid').length > 0) {
            deviceid = document.getElementById('deviceid').getAttribute('value');
            ostype = document.getElementById('ostype').getAttribute('value');
            stacktype = document.getElementById('stacktype').getAttribute('value');
            $("div[data-updateinfo='updatedeviceinfo']").load('updatedeviceinfo?deviceid=' + deviceid + '&ostype=' + ostype + '&stacktype=' + stacktype);
        }
    }
    setInterval(refresh, 10000);
    refresh();
});
// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

$('.monitorGraph').ready(function () {
    var refresh = function () {
        if ($('#deviceid').length > 0) {
            deviceid = document.getElementById('deviceid').getAttribute('value');
            ostype = document.getElementById('ostype').getAttribute('value');
            stacktype = document.getElementById('stacktype').getAttribute('value');
            if (stacktype == "vsf" || stacktype == "bps") {
                memTitle = "Available%20Memory";
                cpuTitle = "Commander%20CPU%20Utilization";
            }
            else {
                memTitle = "Memory%20Utilization";
                cpuTitle = "CPU%20Utilization";
            }
            $("div[data-cpuchart='graphData-CPU']").load('showGraph?entity=cpu&title=' + cpuTitle + '&deviceid=' + deviceid + '&ostype=' + ostype + '&stacktype=' + stacktype);
            $("div[data-memchart='graphData-Memory']").load('showGraph?entity=memory&title=' + memTitle + '&deviceid=' + deviceid + '&ostype=' + ostype + '&stacktype=' + stacktype);
        }
    }
    setInterval(refresh, 5000);
    refresh();
});
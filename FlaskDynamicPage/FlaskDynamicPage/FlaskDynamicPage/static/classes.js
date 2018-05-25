// (C) Copyright 2018 Hewlett Packard Enterprise Development LP.

$('.monitorData').ready(function () {
    var refresh = function () {
        var devicelist = JSON.parse(document.getElementById('monitorData').getAttribute('value'));
        for (i = 0; i < devicelist.length; i++)
        {
            $("div[data-switchid='" + devicelist[i] + "']").load('monitorgetData?devicelist=' + devicelist[i]);
        }
    }
    setInterval(refresh, 3000);
    refresh();
});
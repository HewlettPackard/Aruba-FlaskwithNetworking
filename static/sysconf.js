// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {
    $('#secret_key').on('keyup', function () {
        if (this.value.length<= 15)
        {
            $('#submitChanges').attr('disabled', 'disabled');
        } else {
            $('#submitChanges').attr('disabled', false);
        }
    });
});


$('.cleanupProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='cleanupProcess']").load('monitorProcess?name=Cleanup');
    }
    setInterval(refresh, 5000);
    refresh();
});


$('#timezonecity').ready(function () {
    if ($('#tzcity').val()) {
        var region = $('#timezoneregion option:selected').val().toLowerCase();
        var city = $('#tzcity').val();
        timezoneregion = ["Africa", "America", "Asia", "Europe", "Indian", "Pacific", "Antarctica"];
        tzafrica = ["Abidjan", "Accra", "Algiers", "Bissau", "Cairo", "Casablanca", "Ceuta", "El_Aaiun", "Johannesburg", "Juba", "Khartoum", "Lagos", "Maputo", "Monrovia", "Nairobi", "Ndjamena", "Sao_Tome", "Tripoli", "Tunis", "Windhoek"];
        tzamerica = ["Adak", "Anchorage", "Araguaina", "Argentina/Buenos_Aires", "Argentina/Catamarca", "Argentina/Cordoba", "Argentina/Jujuy", "Argentina/La_Rioja", "Argentina/Mendoza", "Argentina/Rio_Gallegos", "Argentina/Salta", "Argentina/San_Juan", "Argentina/San_Luis", "Argentina/Tucuman", "Argentina/Ushuaia", "Asuncion", "Atikokan", "Bahia", "Bahia_Banderas", "Barbados", "Belem", "Belize", "Blanc-Sablon", "Boa_Vista", "Bogota", "Boise", "Cambridge_Bay", "Campo_Grande", "Cancun", "Caracas", "Cayenne", "Chicago", "Chihuahua", "Costa_Rica", "Creston", "Cuiaba", "Curacao", "Danmarkshavn", "Dawson", "Dawson_Creek", "Denver", "Detroit", "Edmonton", "Eirunepe", "El_Salvador", "Fort_Nelson", "Fortaleza", "Glace_Bay", "Goose_Bay", "Grand_Turk", "Guatemala", "Guayaquil", "Guyana", "Halifax", "Havana", "Hermosillo", "Indiana/Indianapolis", "Indiana/Knox", "Indiana/Marengo", "Indiana/Petersburg", "Indiana/Tell_City", "Indiana/Vevay", "Indiana/Vincennes", "Indiana/Winamac", "Inuvik", "Iqaluit", "Jamaica", "Juneau", "Kentucky/Louisville", "Kentucky/Monticello", "La_Paz", "Lima", "Los_Angeles", "Maceio", "Managua", "Manaus", "Martinique", "Matamoros", "Mazatlan", "Menominee", "Merida", "Metlakatla", "Mexico_City", "Miquelon", "Moncton", "Monterrey", "Montevideo", "Nassau", "New_York", "Nipigon", "Nome", "Noronha", "North_Dakota/Beulah", "North_Dakota/Center", "North_Dakota/New_Salem", "Nuuk", "Ojinaga", "Panama", "Pangnirtung", "Paramaribo", "Phoenix", "Port-au-Prince", "Port_of_Spain", "Porto_Velho", "Puerto_Rico", "Punta_Arenas", "Rainy_River", "Rankin_Inlet", "Recife", "Regina", "Resolute", "Rio_Branco", "Santarem", "Santiago", "Santo_Domingo", "Sao_Paulo", "Scoresbysund", "Ameica/St_Johns", "Tegucigalpa", "Thule", "Thunder_Bay", "Tijuana", "Toronto", "Vancouver", "Whitehorse", "Winnipeg", "Yakutat", "Yellowknife"];
        tzantarctica = ["Casey", "Davis", "DumontDUrville", "Macquarie", "Mawson", "Palmer", "Rothera", "Syowa", "Troll", "Vostok"];
        tzasia = ["Almaty", "Amman", "Anadyr", "Aqtau", "Aqtobe", "Ashgabat", "Atyrau", "Baghdad", "Baku", "Bangkok", "Barnaul", "Beirut", "Bishkek", "Brunei", "Chita", "Choibalsan", "Colombo", "Damascus", "Dhaka", "Dili", "Dubai", "Dushanbe", "Famagusta", "Gaza", "Hebron", "Ho_Chi_Minh", "Hong_Kong", "Hovd", "Irkutsk", "Jakarta", "Jayapura", "Jerusalem", "Kabul", "Kamchatka", "Karachi", "Kathmandu", "Khandyga", "Kolkata", "Krasnoyarsk", "Kuala_Lumpur", "Kuching", "Macau", "Magadan", "Makassar", "Manila", "Nicosia", "Novokuznetsk", "Novosibirsk", "Omsk", "Oral", "Pontianak", "Pyongyang", "Qatar", "Qostanay", "Qyzylorda", "Riyadh", "Sakhalin", "Samarkand", "Seoul", "Shanghai", "Singapore", "Srednekolymsk", "Taipei", "Tashkent", "Tbilisi", "Tehran", "Thimphu", "Tokyo", "Tomsk", "Ulaanbaatar", "Urumqi", "Ust-Nera", "Vladivostok", "Yakutsk", "Yangon", "Yekaterinburg", "Yerevan"];
        tzatlantic = ["Azores", "Bermuda", "Canary", "Cape_Verde", "Faroe", "Madeira", "Reykjavik", "South_Georgia", "Stanley"];
        tzaustralia = ["Adelaide", "Brisbane", "Broken_Hill", "Darwin", "Eucla", "Hobart", "Lindeman", "Lord_Howe", "Melbourne", "Perth", "Sydney"];
        tzeurope = ["Amsterdam", "Andorra", "Astrakhan", "Athens", "Belgrade", "Berlin", "Brussels", "Bucharest", "Budapest", "Chisinau", "Copenhagen", "Dublin", "Gibraltar", "Helsinki", "Istanbul", "Kaliningrad", "Kiev", "Kirov", "Lisbon", "London", "Luxembourg", "Madrid", "Malta", "Minsk", "Monaco", "Moscow", "Oslo", "Paris", "Prague", "Riga", "Rome", "Samara", "Saratov", "Simferopol", "Sofia", "Stockholm", "Tallinn", "Tirane", "Ulyanovsk", "Uzhgorod", "Vienna", "Vilnius", "Volgograd", "Warsaw", "Zaporozhye", "Zurich"];
        tzindian = ["Chagos", "Christmas", "Cocos", "Kerguelen", "Mahe", "Maldives", "Mauritius", "Reunion"];
        tzpacific = ["Apia", "Auckland", "Bougainville", "Chatham", "Chuuk", "Easter", "Efate", "Enderbury", "Fakaofo", "Fiji", "Funafuti", "Galapagos", "Gambier", "Guadalcanal", "Guam", "Honolulu", "Kiritimati", "Kosrae", "Kwajalein", "Majuro", "Marquesas", "Nauru", "Niue", "Norfolk", "Noumea", "Pago_Pago", "Palau", "Pitcairn", "Pohnpei", "Port_Moresby", "Rarotonga", "Tahiti", "Tarawa", "Tongatapu", "Wake", "Wallis"];
        tzcityHTML = "<option value=''>Select city</option>";
        $('#timezonecity').empty();
        if (city == "") {
            $('#timezonecity').append("<option value='' selected>Select city</option>");
        }

        var i = 0;
        for (i = 0; i < eval("tz" + region).length; i++) {
            if (eval("tz" + region)[i] == city) {
                $('#timezonecity').append("<option value='" + eval("tz" + region)[i] + "' selected>" + eval("tz" + region)[i] + "</option>");
            }
            else {
                $('#timezonecity').append("<option value='" + eval("tz" + region)[i] + "'>" + eval("tz" + region)[i] + "</option>");
            }

        }
    }
});


$('.topologyProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='topologyProcess']").load('monitorProcess?name=Topology');
    }
    setInterval(refresh, 5000);
    refresh();
});


$('.ztpProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='ztpProcess']").load('monitorProcess?name=ZTP');
    }
    setInterval(refresh, 5000);
    refresh();
});


$('.listenerProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='listenerProcess']").load('monitorProcess?name=Listener');
    }
    setInterval(refresh, 5000);
    refresh();
});


$('.telemetryProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='telemetryProcess']").load('monitorProcess?name=Telemetry');
    }
    setInterval(refresh, 5000);
    refresh();
});


$('.deviceupgradeProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='deviceupgradeProcess']").load('monitorProcess?name=Device-upgrade');
    }
    setInterval(refresh, 5000);
    refresh();
});

$('.datacollectorProcess').ready(function () {
    var refresh = function () {
        $("div[data-chart='datacollectorProcess']").load('monitorProcess?name=Data-collector');
    }
    setInterval(refresh, 5000);
    refresh();
});


$('#systemTime').ready(function () {
    if ($('#systemTime').length) {
    var refresh = function () {
        $.ajax({
            type: "POST",
            headers: { "Content-Type": "application/json" },
            url: "/getsysTime",
            success: function (response) {
                response = JSON.parse(response);
                document.getElementById("systemTime").innerHTML = response['month'] + " " + response['day'] + ", " + response['year'] + ": " + minTwoDigits(response['hour']) + ":" + minTwoDigits(response['minute']) + ":" + minTwoDigits(response['second']);
            }
        });
    }
    setInterval(refresh, 1000);
    refresh();
    }
});


$('#ipamstatus').ready(function () {
    var refresh = async function () {
        if (document.getElementById('ipamsystem')) {
            var e = document.getElementById("ipamsystem");
            var ipamsystem = e.options[e.selectedIndex].value;
            var ipamenabled = document.getElementById("ipamenabled");
            if ((ipamsystem == "Infoblox" || ipamsystem == "PHPIPAM") && ipamenabled.checked == true) {
                if (ipamsystem == "Infoblox") {
                    var ipamuser = document.getElementById('ipamuser').value;
                    var ipampassword = document.getElementById('ipampassword').value;
                    var ipamipaddress = document.getElementById('ipamipaddress').value;
                    var phpipamappid = "";
                    var phpipamauth = "";
                }
                else if (ipamsystem == "PHPIPAM") {
                    var ipamuser = document.getElementById('ipamuser').value;
                    var ipampassword = document.getElementById('ipampassword').value;
                    var ipamipaddress = document.getElementById('ipamipaddress').value;
                    var phpipamappid = document.getElementById('phpipamappid').value;
                }

                response = await $.ajax({
                    url: "/ipamStatus",
                    type: "POST",
                    data: { ipamsystem: ipamsystem, ipamipaddress: ipamipaddress, ipamuser: ipamuser, ipampassword: ipampassword, phpipamappid: phpipamappid },
                    success: function (response) {
                    }
                });
                if (response == "Online") {
                    document.getElementById("ipamStatus").innerHTML = "<font class='font12pxwhite'>Status: IPAM is reachable</font>";
                }
                else {
                    document.getElementById("ipamStatus").innerHTML = "<font class='font12pxwhite'>Status: IPAM is unreachable</font>";
                }
            }
            else {
                document.getElementById("ipamStatus").innerHTML = "<font class='font12pxwhite'>Status: IPAM not selected or activated...</font>";
            }
        }
    }
    setInterval(refresh, 5000);
    refresh();
});


$('#afcstatus').ready(function () {
    if ($('#afcipaddress').length) {
        var refresh = async function () {
            if ($('#afcipaddress').val().length && $('#afcusername').val().length && $('#afcpassword').val().length) {
                response = await $.ajax({
                    url: "/afcStatus",
                    type: "POST",
                    data: { afcipaddress: $('#afcipaddress').val(), afcuser: $('#afcusername').val(), afcpassword: $('#afcpassword').val(), afctoken: $('#afctoken').val() },
                    success: function (response) {
                        if (typeof response === 'string' || response instanceof String) {
                            response = JSON.parse(response);
                        }
                        if (response['count'] == 1) {
                            // Set the afctoken value in the form
                            $('#afctoken').val(response['result']);
                            document.getElementById("afcstatus").innerHTML = "<font class='font12pxwhite'>Status: Aruba Fabric Composer is reachable, token is obtained</font>";
                        }
                        else {
                            document.getElementById("afcstatus").innerHTML = "<font class='font12pxwhite'>Status: " + response['result'] + "</font>";
                        }
                    }
                });
            }
        }
        setInterval(refresh, 8000);
        refresh();
    }
});


$('#psmstatus').ready(function () {
    if ($('#psmipaddress').length) {
        var refresh = async function () {
            if ($('#psmipaddress').val().length && $('#psmusername').val().length && $('#psmpassword').val().length) {
                response = await $.ajax({
                    url: "/psmStatus",
                    type: "POST",
                    data: { psmipaddress: $('#psmipaddress').val(), psmuser: $('#psmusername').val(), psmpassword: $('#psmpassword').val(), psmtoken: $('#psmtoken').val() },
                    success: function (response) {
                        if (typeof response === 'string' || response instanceof String) {
                            response = JSON.parse(response);
                        }
                        if ("psmtoken" in response) {
                            // Set the psmtoken value in the form
                            $('#psmtoken').val(response['psmtoken']);
                            document.getElementById("psmstatus").innerHTML = "<font class='font12pxwhite'>Status: Pensando PSM is reachable, token is obtained</font>";
                        }
                        else {
                            document.getElementById("psmstatus").innerHTML = "<font class='font12pxwhite'>Status: " + response['result'] + "</font>";
                        }
                    }
                });
            }
        }
        setInterval(refresh, 8000);
        refresh();
    }
});


$(document).on('click', '.downloadLog', function () {
    response = $.ajax({
        url: "/downloadLog",
        type: "POST",
        data: { processName: $(this).attr("data-processname") },
        success: function (response) {
            response = JSON.parse(response);
            var logInfo = document.createElement('a');
            logFile = response[0] + ".txt";
            logInfo.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(response[1]));
            logInfo.setAttribute("download", logFile);
            if (document.createEvent) {
                var event = document.createEvent('MouseEvents');
                event.initEvent('click', true, true);
                logInfo.dispatchEvent(event);
            }
            else {
                logInfo.click();
            }          
        }
    });
});


$(document).on('click', '.clearLog', function () {
    response = $.ajax({
        url: "/clearprocessLog",
        type: "POST",
        data: { processName: $(this).attr("data-processname") },
        success: function (response) {
        }
    });
});


function minTwoDigits(n) {
    return (n < 10 ? '0' : '') + n;
}


function ipamConf() {
    var e = document.getElementById("ipamsystem");
    var ipamVal = e.options[e.selectedIndex].value;
    if (ipamVal == "Infoblox") {
        $("#ipamtr").show();
        $(".phpipamid").hide();
    }
    else if (ipamVal == "PHPIPAM") {
        $("#ipamtr").show();
        $(".phpipamid").show();
    }
    else {
        $("#ipamtr").hide();
    }  
}


$('#ldapstatus').ready(function () {
    if ($('#ldapuser').val() && $('#ldappassword').val() && $('#ldapsource').val() && $('#basedn').val()) {
        var refresh = async function () {
            $.ajax({
                type: "POST",
                data: { ldapuser: $('#ldapuser').val(), ldappassword: $('#ldappassword').val(), ldapsource: $('#ldapsource').val(), basedn: $('#basedn').val() },
                url: "/testldap",
                success: function (response) {
                    response = JSON.parse(response);
                    if (response['message'] == "LDAP connection successful") {
                        document.getElementById("ldapstatus").innerHTML = "<font class='font12pxwhite'>Status: " + response['message'];
                    }
                    else {
                        document.getElementById("ldapstatus").innerHTML = "<font class='font12pxwhite'>Status: " + response['message'];
                    }
                }
            });
        }
        setInterval(refresh, 5000);
        refresh();
    }
});


$(document).on('click', '#arubacentralauthstatus', async function () {
    await $.ajax(
        {
        type: "POST",
            url: "/checkauthentication",
            data: { arubacentralurl: $('#arubacentralurl').val(), arubacentralusername: $('#arubacentralusername').val(), arubacentraluserpassword: $('#arubacentraluserpassword').val(), arubacentralclientid: $('#arubacentralclientid').val(), arubacentralclientsecret: $('#arubacentralclientsecret').val(), arubacentralcustomerid: $('#arubacentralcustomerid').val() },
        success: function (response) {
            response = JSON.parse(response);
            document.getElementById("arubacentralauthenticationstatus").innerHTML = "<font class='font12pxwhite'>" + response['message'] + "</font>";
        }
    });
    await $.ajax({
        type: "POST",
        url: "/checkauthorization",
        success: function (response) {
            response = JSON.parse(response);
            document.getElementById("arubacentralauthorizationstatus").innerHTML = "<font class='font12pxwhite'>" + response['message'] + "</font>";
        }
    });
});


function closeForm() {
    document.getElementById("myForm").style.display = "none";
}


function changetimezoneRegion() {
    timezoneregion = ["Africa", "America", "Asia", "Europe", "Indian", "Pacific", "Antarctica"];
    tzafrica = ["Abidjan", "Accra", "Algiers", "Bissau", "Cairo", "Casablanca", "Ceuta", "El_Aaiun", "Johannesburg", "Juba", "Khartoum", "Lagos", "Maputo", "Monrovia", "Nairobi", "Ndjamena", "Sao_Tome", "Tripoli", "Tunis", "Windhoek"];
    tzamerica = ["Adak", "Anchorage", "Araguaina", "Argentina/Buenos_Aires", "Argentina/Catamarca", "Argentina/Cordoba", "Argentina/Jujuy", "Argentina/La_Rioja", "Argentina/Mendoza", "Argentina/Rio_Gallegos", "Argentina/Salta", "Argentina/San_Juan", "Argentina/San_Luis", "Argentina/Tucuman", "Argentina/Ushuaia", "Asuncion", "Atikokan", "Bahia", "Bahia_Banderas", "Barbados", "Belem", "Belize", "Blanc-Sablon", "Boa_Vista", "Bogota", "Boise", "Cambridge_Bay", "Campo_Grande", "Cancun", "Caracas", "Cayenne", "Chicago", "Chihuahua", "Costa_Rica", "Creston", "Cuiaba", "Curacao", "Danmarkshavn", "Dawson", "Dawson_Creek", "Denver", "Detroit", "Edmonton", "Eirunepe", "El_Salvador", "Fort_Nelson", "Fortaleza", "Glace_Bay", "Goose_Bay", "Grand_Turk", "Guatemala", "Guayaquil", "Guyana", "Halifax", "Havana", "Hermosillo", "Indiana/Indianapolis", "Indiana/Knox", "Indiana/Marengo", "Indiana/Petersburg", "Indiana/Tell_City", "Indiana/Vevay", "Indiana/Vincennes", "Indiana/Winamac", "Inuvik", "Iqaluit", "Jamaica", "Juneau", "Kentucky/Louisville", "Kentucky/Monticello", "La_Paz", "Lima", "Los_Angeles", "Maceio", "Managua", "Manaus", "Martinique", "Matamoros", "Mazatlan", "Menominee", "Merida", "Metlakatla", "Mexico_City", "Miquelon", "Moncton", "Monterrey", "Montevideo", "Nassau", "New_York", "Nipigon", "Nome", "Noronha", "North_Dakota/Beulah", "North_Dakota/Center", "North_Dakota/New_Salem", "Nuuk", "Ojinaga", "Panama", "Pangnirtung", "Paramaribo", "Phoenix", "Port-au-Prince", "Port_of_Spain", "Porto_Velho", "Puerto_Rico", "Punta_Arenas", "Rainy_River", "Rankin_Inlet", "Recife", "Regina", "Resolute", "Rio_Branco", "Santarem", "Santiago", "Santo_Domingo", "Sao_Paulo", "Scoresbysund", "Ameica/St_Johns", "Tegucigalpa", "Thule", "Thunder_Bay", "Tijuana", "Toronto", "Vancouver", "Whitehorse", "Winnipeg", "Yakutat", "Yellowknife"];
    tzantarctica = ["Casey", "Davis", "DumontDUrville", "Macquarie", "Mawson", "Palmer", "Rothera", "Syowa", "Troll", "Vostok"];
    tzasia = ["Almaty", "Amman", "Anadyr", "Aqtau", "Aqtobe", "Ashgabat", "Atyrau", "Baghdad", "Baku", "Bangkok", "Barnaul", "Beirut", "Bishkek", "Brunei", "Chita", "Choibalsan", "Colombo", "Damascus", "Dhaka", "Dili", "Dubai", "Dushanbe", "Famagusta", "Gaza", "Hebron", "Ho_Chi_Minh", "Hong_Kong", "Hovd", "Irkutsk", "Jakarta", "Jayapura", "Jerusalem", "Kabul", "Kamchatka", "Karachi", "Kathmandu", "Khandyga", "Kolkata", "Krasnoyarsk", "Kuala_Lumpur", "Kuching", "Macau", "Magadan", "Makassar", "Manila", "Nicosia", "Novokuznetsk", "Novosibirsk", "Omsk", "Oral", "Pontianak", "Pyongyang", "Qatar", "Qostanay", "Qyzylorda", "Riyadh", "Sakhalin", "Samarkand", "Seoul", "Shanghai", "Singapore", "Srednekolymsk", "Taipei", "Tashkent", "Tbilisi", "Tehran", "Thimphu", "Tokyo", "Tomsk", "Ulaanbaatar", "Urumqi", "Ust-Nera", "Vladivostok", "Yakutsk", "Yangon", "Yekaterinburg", "Yerevan"];
    tzatlantic = ["Azores", "Bermuda", "Canary", "Cape_Verde", "Faroe", "Madeira", "Reykjavik", "South_Georgia", "Stanley"];
    tzaustralia = ["Adelaide", "Brisbane", "Broken_Hill", "Darwin", "Eucla", "Hobart", "Lindeman", "Lord_Howe", "Melbourne", "Perth", "Sydney"];
    tzeurope = ["Amsterdam", "Andorra", "Astrakhan", "Athens", "Belgrade", "Berlin", "Brussels", "Bucharest", "Budapest", "Chisinau", "Copenhagen", "Dublin", "Gibraltar", "Helsinki", "Istanbul", "Kaliningrad", "Kiev", "Kirov", "Lisbon", "London", "Luxembourg", "Madrid", "Malta", "Minsk", "Monaco", "Moscow", "Oslo", "Paris", "Prague", "Riga", "Rome", "Samara", "Saratov", "Simferopol", "Sofia", "Stockholm", "Tallinn", "Tirane", "Ulyanovsk", "Uzhgorod", "Vienna", "Vilnius", "Volgograd", "Warsaw", "Zaporozhye", "Zurich"];
    tzindian = ["Chagos", "Christmas", "Cocos", "Kerguelen", "Mahe", "Maldives", "Mauritius", "Reunion"];
    tzpacific = ["Apia", "Auckland", "Bougainville", "Chatham", "Chuuk", "Easter", "Efate", "Enderbury", "Fakaofo", "Fiji", "Funafuti", "Galapagos", "Gambier", "Guadalcanal", "Guam", "Honolulu", "Kiritimati", "Kosrae", "Kwajalein", "Majuro", "Marquesas", "Nauru", "Niue", "Norfolk", "Noumea", "Pago_Pago", "Palau", "Pitcairn", "Pohnpei", "Port_Moresby", "Rarotonga", "Tahiti", "Tarawa", "Tongatapu", "Wake", "Wallis"];
    var region=$('#timezoneregion option:selected').val().toLowerCase();
    $('#timezonecity').empty();
    var i = 0;
    for (i = 0; i < eval("tz" + region).length; i++) {
         $('#timezonecity').append("<option value='" + eval("tz" + region)[i] + "'>" + eval("tz" + region)[i] + "</option>");
    }
}
// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

$(function () {

    $("#showProfile").hide();
    $("#showPolicy").hide();

   

    $(".provisionService").click(async function () {
        // Unhide the progress bar
        document.getElementById("liProgress").style.display = "block";
        document.getElementById("progresstooltip").style.display = "none";
        var progressBar = document.getElementById("progressBar");
        var progressInfo = document.getElementById("progressInfo");
        var logInfo = "";
        var logExists = 0;
        var provisionLog = [];
        progressBar.style.width = '0%';
        // Obtain service information. Especially the member information and workflow information is important
        serviceid = $(this).attr('id');
        // This is an async function, we have to wait until the information is returned from the Python call. serviceInfo definition found in dynseg.py
        serviceInfo=await $.ajax({
            url: "/serviceInfo",
            type: "POST",
            data: { serviceid: serviceid },
            success: function () {
                progressInfo.innerHTML = "Service information obtained";
            },
            error: function () {
                progressInfo.innerHTML = "Error finding service information";
             }
        });
        // Formatting the Member and Workflow information
        serviceInfo = JSON.parse(serviceInfo);
        // policyInfo contains information for pushing the profile, policy and service to clearpass
        // authMethod, authSource and rolename are important here. Rolename will be the secondary role that is defined in the profile
        // In the policy, update the endpoint and set user authenticated as rule, and then apply the profile
        // In the Service, apply the authentication method and source, and assign the policy
        policyInfo = JSON.parse(serviceInfo['policies']);
        memberInfo = serviceInfo['memberInfo'];
        var total = policyInfo.length*3 + memberInfo.length;
        // Loop through the memberlist and provision each switch
        for (var counter = 0; counter < memberInfo.length; counter++) {
            progressInfo.innerHTML = "Provision switch " + (counter + 1) + " of " + memberInfo.length;
            progressBar.style.width = ((counter + 1) / total) * 100 + '%';
            // Call the definition, found in dynseg.py for provisioning the switch
            provisionResult = await $.ajax({
                url: "/provisionSwitch",
                type: "POST",
                data: { deviceid: memberInfo[counter], workflow: JSON.stringify(serviceInfo['workflow'])},
                success: function () {
                },
                error: function () {
                    progressInfo.innerHTML = "Error provisioning switch " + memberInfo[counter];
                }
            });
            // Provisionresult returns some information. If provisioning was unsuccessful, we get additional information back from the called definition
            if (typeof JSON.parse(provisionResult)[1] != "undefined") {
               provisionLog.push(JSON.parse(provisionResult));
            }
         progressInfo.innerHTML = "Switch provisioning completed";
        }  
        //Now push the ClearPass profiles, policies and services
        //Profiles first
        for (var cpcounter = 0; cpcounter < policyInfo.length; cpcounter++) {
            progressInfo.innerHTML = "ClearPass provision profile " + policyInfo[cpcounter]['rname'];
            progressBar.style.width = ((cpcounter + counter + 1) / total) * 100 + '%';
            provisionResult = await $.ajax({
                url: "/provisionCPProfile",
                type: "POST",
                data: { policyInfo: policyInfo[cpcounter] },
                success: function () {
                },
                error: function () {
                    progressInfo.innerHTML = "Error provisioning ClearPass profile " + policyInfo[counter]['rname'];
                }
            });
        }
        counter = counter + cpcounter;
        //Policies next
        for (var cpcounter = 0; cpcounter < policyInfo.length; cpcounter++) {
            progressInfo.innerHTML = "ClearPass provision policy " + policyInfo[cpcounter]['rname'];
            progressBar.style.width = ((cpcounter + counter + 1) / total) * 100 + '%';
            provisionResult = await $.ajax({
                url: "/provisionCPPolicy",
                type: "POST",
                data: { policyInfo: policyInfo[cpcounter] },
                success: function () {
                },
                error: function () {
                    progressInfo.innerHTML = "Error provisioning ClearPass policy " + policyInfo[counter]['rname'];
                }
            });
        }
        counter = counter + cpcounter;
        //Finally the services
        for (var cpcounter = 0; cpcounter < policyInfo.length; cpcounter++) {
            progressInfo.innerHTML = "ClearPass provision service " + policyInfo[cpcounter]['rname'];
            progressBar.style.width = ((cpcounter + counter + 1) / total) * 100 + '%';
            provisionResult = await $.ajax({
                url: "/provisionCPService",
                type: "POST",
                data: { policyInfo: policyInfo[cpcounter] },
                success: function () {
                },
                error: function () {
                    progressInfo.innerHTML = "Error provisioning ClearPass service " + policyInfo[counter]['rname'];
                }
            });
        }
        // Check whether the provision has been successful. The format of the array is [[[memberinfo],[messages]][[memberinfo],[messages]]]
        // If the array contains message content, there was an error and we have to display this
        logInfo += "Provisioning result:<br>";
        for (logitems = 0; logitems < provisionLog.length; logitems++) {     
            if (provisionLog[logitems][1][1] != "") {
                logExists = 1;
                logInfo += "Switch " + provisionLog[logitems][0][1] + " (" + provisionLog[logitems][0][0] + "): " + provisionLog[logitems][1][1] + "<br>";
            }     

        }
        if (logExists == 1) {
            document.getElementById("progresstooltip").style.display = "inline-block";
            document.getElementById("progresstooltiptext").innerHTML = logInfo;
        }
     });
    


    $("#policyAction").click(function () {
        // Array with authentication methods and authentication sources
        methods = ["EAP PEAP", "EAP-TLS", "Allow All MAC", "Mac Auth", "PAP", "CHAP"];
        sources = ["Active Directory", "Local User Database", "Guest User Repository"];
        roleinfoselect = document.getElementById('roleinfoselect').value;
        roleinfoselect = JSON.parse(roleinfoselect);
        // Check if there is a policy defined. If it is defined, the roleinfo variable is assigned. If there is no policy, roleinfo is empty
        if (document.getElementById('policies').value !== undefined) {
            roleinfo = document.getElementById('policies').value;
         }
        else {
            roleinfo = "None";
        }
        selectdevAuth = $('#devAuth').val();
        selectauthMethod = $('#selectauthMethod').val();
        selectauthSource = $('#selectauthSource').val();
        policyAction = document.getElementById('policyAction').value;
        if (policyAction == "Add policy") {
            //Append the roleinfoselect to the roleinfo list of dicts
            //Format the selected role
            if (typeof roleinfoselect['role__vlan'] === 'undefined') {
                vlan = "";
              }
            else {
                vlan = roleinfoselect['role__vlan']['vlanstr'];
            }
            newrole = { "rname": roleinfoselect['rname'], "devauth": selectdevAuth, "authMethod": selectauthMethod, "authSource": selectauthSource, "vlan": vlan, "ACL": roleinfoselect['role__acl'] };
            // Merge the role information. Definition can be found in dynseg.py
            fetch('/mergeRole/' + roleinfo + "/" + JSON.stringify(newrole)).then(function (response) {
                response.json().then(function (roledata) {
                    document.getElementById('roleinfo').value = roledata;
                    document.getElementById('policies').value = JSON.stringify(roledata);
                    //Fill the table with the role information
                    roleHTML = "<table class='tablewithborder'>";
                    roleHTML += "<tr style='background-color:grey;'><td colspan='7' align='center' class='font13pxwhite'>Configured policies</td></tr>";
                    roleHTML += "<tr style='background-color:grey;'><td nowrap><font class='font12pxwhite'>Device authentication</font></td>";
                    roleHTML += "<td nowrap><font class='font12pxwhite'>Authentication source(s)</font></td>";
                    roleHTML += "<td nowrap><font class='font12pxwhite'>Authentication method(s)</font></td>";
                    roleHTML += "<td nowrap><font class='font12pxwhite'>Role</font></td>";
                    roleHTML += "<td nowrap><font class='font12pxwhite'>Filter rules</font></td>";
                    roleHTML += "<td nowrap><font class='font12pxwhite'>Egress VLAN</font></td>";
                    roleHTML += "<td width='1%'>&nbsp;</td></tr>";
                    for (i = 0; i < roledata.length; i++) {
                        if (roledata[i]['devauth'] == "dot1x") { devauth = "802.1x"; }
                        else if (roledata[i]['devauth'] == "macauth") { devauth = "MAC Authentication"; }
                        else { devauth = "";}
                        roleHTML += "<tr><td class='whiteBG'><font class='font12px'>" + devauth + "</font></td>";
                        roleHTML += "<td class='whiteBG'><font class='font12px'>";
                        for (j = 0; j < roledata[i]['authMethod'].length; j++) {
                            roleHTML += methods[roledata[i]['authMethod'][j]] + ", ";
                        }
                        //Remove last comma
                        roleHTML = roleHTML.substring(0, roleHTML.length - 2);
                        roleHTML += "</font></td>";
                        roleHTML += "<td class='whiteBG'><font class='font12px'>";
                        for (j = 0; j < roledata[i]['authSource'].length; j++) {
                           roleHTML += sources[roledata[i]['authSource'][j]] + ", ";
                        }
                        //Remove last comma
                        roleHTML=roleHTML.substring(0, roleHTML.length - 2);
                        roleHTML += "</font></td>";
                        roleHTML += "<td class='whiteBG'><font class='font12px'>" + roledata[i]['rname'] + "</font></td>";
                        roleHTML += "<td class='whiteBG'><font class='font12px'>";
                        for (j = 0; j < roledata[i]['ACL'].length; j++){
                            roleHTML += roledata[i]['ACL'][j]['pname'] + ", ";
                        }
                        roleHTML = roleHTML.substring(0, roleHTML.length - 2);
                        roleHTML += "</font></td > ";
                        roleHTML += "<td class='whiteBG'><font class='font12px'>" + roledata[i]['vlan'] + "</font></td>";
                        roleHTML += "<td class='whiteBG' width='1%' nowrap><input type='button' class='button' id='rolelistAction' value='Delete' data-roleEntry='" + i + "'></td>";
                        roleHTML += "</tr>";
                    }
                    roleHTML += "</table>";
                    document.getElementById('roletable').innerHTML = roleHTML;
                 });
            });

        }
    });

    $(document).on("click", "#rolelistAction", function () {
        methods = ["EAP PEAP", "EAP-TLS", "Allow All MAC", "Mac Auth", "PAP", "CHAP"];
        sources = ["Active Directory", "Local User Database", "Guest User Repository"];
        roledata = JSON.parse(document.getElementById('policies').value);
        roledata.splice(this.getAttribute('data-roleEntry'), 1);
        document.getElementById('policies').value = JSON.stringify(roledata)
        roleHTML = "<table class='tablewithborder'>";
        roleHTML += "<tr style='background-color:grey;'><td colspan='7' align='center' class='font13pxwhite'>Configured policies</td></tr>";
        roleHTML += "<tr style='background-color:grey;'><td nowrap><font class='font12pxwhite'>Device authentication</font></td>";
        roleHTML += "<td nowrap><font class='font12pxwhite'>Authentication source(s)</font></td>";
        roleHTML += "<td nowrap><font class='font12pxwhite'>Authentication method(s)</font></td>";
        roleHTML += "<td nowrap><font class='font12pxwhite'>Role</font></td>";
        roleHTML += "<td nowrap><font class='font12pxwhite'>Filter rules</font></td>";
        roleHTML += "<td nowrap><font class='font12pxwhite'>Egress VLAN</font></td>";
        roleHTML += "<td width='1%'>&nbsp;</td></tr>";
        for (i = 0; i < roledata.length; i++) {
            if (roledata[i]['devauth'] == "dot1x") { devauth = "802.1x"; }
            else if (roledata[i]['devauth'] == "macauth") { devauth = "MAC Authentication"; }
            else { devauth = ""; }
            roleHTML += "<tr><td class='whiteBG'><font class='font12px'>" + devauth + "</font></td>";
            roleHTML += "<td class='whiteBG'><font class='font12px'>";
            for (j = 0; j < roledata[i]['authMethod'].length; j++) {
                roleHTML += methods[roledata[i]['authMethod'][j]] + ", ";
            }
            //Remove last comma
            roleHTML = roleHTML.substring(0, roleHTML.length - 2);
            roleHTML += "</font></td>";
            roleHTML += "<td class='whiteBG'><font class='font12px'>";
            for (j = 0; j < roledata[i]['authSource'].length; j++) {
                roleHTML += sources[roledata[i]['authSource'][j]] + ", ";
            }
            //Remove last comma
            roleHTML = roleHTML.substring(0, roleHTML.length - 2);
            roleHTML += "</font></td>";
            roleHTML += "<td class='whiteBG'><font class='font12px'>" + roledata[i]['rname'] + "</font></td>";
            roleHTML += "<td class='whiteBG'><font class='font12px'>";
            for (j = 0; j < roledata[i]['ACL'].length; j++) {
                roleHTML += roledata[i]['ACL'][j]['pname'] + ", ";
            }
            roleHTML = roleHTML.substring(0, roleHTML.length - 2);
            roleHTML += "</font></td > ";
            roleHTML += "<td class='whiteBG'><font class='font12px'>" + roledata[i]['vlan'] + "</font></td>";
            roleHTML += "<td class='whiteBG'><input type='button' class='button' id='rolelistAction' value='Delete' data-roleEntry='" + i + "'></td>";
            roleHTML += "</tr>";
        }
        roleHTML += "</table>";
        document.getElementById('roletable').innerHTML = roleHTML;
    });

    $("#authMethod").change(function () {
        //Only allow submit policy when the role and authentication source is selected
        var mcrole_select = document.getElementById('mcrole');
        var mcrole = mcrole_select.options[mcrole_select.selectedIndex].value;
        var authSource_select = document.getElementById('selectauthSource');
        if (typeof authSource_select.options[authSource_select.selectedIndex] === 'undefined' || mcrole=="None") {
            document.getElementById('policyAction').setAttribute("disabled", "");
        }
        else {
            document.getElementById('policyAction').removeAttribute("disabled", "");
        }
    });

    $("#authSource").change(function () {
        //Only allow submit policy when the role and authentication method is selected
        var mcrole_select = document.getElementById('mcrole');
        var mcrole = mcrole_select.options[mcrole_select.selectedIndex].value;
        var authMethod_select = document.getElementById('selectauthMethod');
        if (typeof authMethod_select.options[authMethod_select.selectedIndex] === 'undefined' || mcrole == "None") {
            document.getElementById('policyAction').setAttribute("disabled", "");
        }
        else {
            document.getElementById('policyAction').removeAttribute("disabled", "");
        }

    });

     
    $("#mcrole").change(function () {
        //Tooltip information
        var mcrole_select = document.getElementById('mcrole');
        var mcrole = mcrole_select.options[mcrole_select.selectedIndex].value;
        roleinfoHTML = "";
        if (mcrole == "None") {
            roleinfoHTML = "Select role";
            document.getElementById('policyAction').setAttribute("disabled","");
            }
        else {
            //Fetch the role information from the controller.

            fetch('/serviceRole/' + document.getElementById('mcid').value + "/" + mcrole).then(function (response) {
                response.json().then(function (roledata) {
                    //Tooltip information
                    document.getElementById("roleinfoselect").value = JSON.stringify(roledata);
                    roleinfoHTML = "Role information of " + roledata['rname'] + ":<br><br>";
                    if (typeof roledata['role__vlan']!== 'undefined') {
                        roleinfoHTML += "Egress VLAN: " + roledata['role__vlan']['vlanstr'] + "<br><br>";
                    }
                    roleinfoHTML += "<b>Policies:</b> " + "<br>";
                    for (i = 0; i < roledata.role__acl.length;i++) {
                        roleinfoHTML += "ACL name (type): " + roledata.role__acl[i]['pname'] + " (" + roledata.role__acl[i]['acl_type'] + ")<br>";
                    }
                    document.getElementById('roleInfo').innerHTML = roleinfoHTML;
                });
            });

        }
        document.getElementById('roleInfo').innerHTML = roleinfoHTML;
    });




    $("#devAuth").change(function () {
        //Need to fill the authentication method and sources for the given policy and device authentication
        methods = ["EAP PEAP", "EAP-TLS", "Allow All MAC", "Mac Auth", "PAP", "CHAP"];
        sources = ["Active Directory", "Local User Database", "Guest User Repository"];
        if (document.getElementById('devAuth').value == "dot1x") {
            fetch('/devauth/' + document.getElementById('profile-id').value + "/dot1x").then(function (response) {
                response.json().then(function (authdata) {
                    dot1xmethod = JSON.parse(authdata.dot1xmethod);
                    dot1xsource = JSON.parse(authdata.dot1xsource);
                    methodHTML = "<select name='authmethod' id='selectauthMethod' multiple>";
                    sourceHTML = "<select name='authsource' id='selectauthSource' multiple>";
                    for (var i = 0; i < dot1xmethod.length; i++) {
                        for (var items in methods) {
                            if (dot1xmethod[i] == parseInt(items)) {
                                methodHTML += "<option value='" + dot1xmethod[i] + "'>" + methods[items] + "</option>";
                            }
                        }
                    }
                    methodHTML += "</select>";
                    for (var i = 0; i < dot1xsource.length; i++) {
                        for (var items in sources) {
                            if (dot1xsource[i] == parseInt(items)) {
                                sourceHTML += "<option value='" + dot1xsource[i] + "'>" + sources[items] + "</option>";
                            }
                        }
                    }
                    document.getElementById('authMethod').innerHTML = methodHTML;
                    document.getElementById('authSource').innerHTML = sourceHTML;
                    document.getElementById('policyAction').setAttribute("enabled", "");
                });
            });
        }
        else if (document.getElementById('devAuth').value == "macauth") {
            fetch('/devauth/' + document.getElementById('profile-id').value + "/macauth").then(function (response) {
                response.json().then(function (authdata) {
                    macauthmethod = JSON.parse(authdata.macauthmethod);
                    macauthsource = JSON.parse(authdata.macauthsource);
                    methodHTML = "<select name='authmethod' id='selectauthMethod' multiple>";
                    sourceHTML = "<select name='authsource' id='selectauthSource' multiple>";
                    for (var i = 0; i < macauthmethod.length; i++) {
                        for (var items in methods) {
                            if (macauthmethod[i] == parseInt(items)) {
                                methodHTML += "<option value='" + macauthmethod[i] + "'>" + methods[items] + "</option>";
                            }
                        }
                    }
                    methodHTML += "</select>";
                    for (var i = 0; i < macauthsource.length; i++) {
                        for (var items in sources) {
                            if (macauthsource[i] == parseInt(items)) {
                                sourceHTML += "<option value='" + macauthsource[i] + "'>" + sources[items] + "</option>";
                            }
                        }
                    }
                    document.getElementById('authMethod').innerHTML = methodHTML;
                    document.getElementById('authSource').innerHTML = sourceHTML;
                    document.getElementById('policyAction').setAttribute("enabled", "");
                });
            });
        }
        else {
            document.getElementById('policyAction').setAttribute("disabled", "");
        }
        
     });


    $("#profile").change(function () {
        var selectisEmpty = false;
        var fieldisEmpty = false;
        var profile_select = document.getElementById('profile');
        var profile = profile_select.options[profile_select.selectedIndex].value;
        document.getElementById('policyAction').setAttribute("disabled", "");
        document.getElementById('profile-id').value = profile;
        document.getElementById('roleInfo').innerHTML = "Select role";
        if (profile == "None") { selectisEmpty = true; }
        $('.field input').each(function () {
            if ($(this).val().length == 0) {
                fieldisEmpty = true;
            }
        });
        if (fieldisEmpty || selectisEmpty) {
            $('.actions input').attr('disabled', 'disabled');
        } else {
            $('.actions input').attr('disabled', false);
        }

        if (profile == "None") {
            $("#showProfile").hide();
            $("#showPolicy").hide();
            infoHTML = "Select a profile";
            document.getElementById('profileInfo').innerHTML = infoHTML;
        }
        else {
            $("#showProfile").show();
            $("#showPolicy").show();
             fetch('/profileInfo/' + profile).then(function (response) {
                 response.json().then(function (data) {
                     document.getElementById('mcid').value = data.primarycontroller['id'];
                     $("#dot1xmethod").val(data['dot1xmethod']);
                     $("#dot1xsource").val(data['dot1xsource']);
                     $("#macauthmethod").val(data['macauthmethod']);
                     $("#macauthsource").val(data['macauthsource']);
                     $("#primarycontroller").val(data['primarycontroller']);
                     //Tooltip information
                     profileinfoHTML = "Profile information of " + data['name'] + ":<br>";
                     profileinfoHTML += "ClearPass server: " + data['clearpass']['ipaddress'] + " (" + data['clearpass']['description'] + ")<br>";
                     profileinfoHTML += "Primary controller: " + data['primarycontroller']['ipaddress'] + " (" + data['primarycontroller']['description'] + ")<br>";
                     if (data['backupcontroller']) {
                         profileinfoHTML += "Backup controller: " + data['backupcontroller']['ipaddress'] + " (" + data['backupcontroller']['description'] + ")<br>";
                     }
                     document.getElementById('profileInfo').innerHTML = profileinfoHTML;
                     //Device authentication options
                     devAuth = "<option value='None'>Select</option>";
                     if (data['dot1x'] == "1") {
                         devAuth += "<option value='dot1x'>802.1x</option>";
                     }
                     if (data['macauth'] == "1") {
                         devAuth += "<option value='macauth'>MAC Authentication</option>";
                     }
                     document.getElementById('devAuth').innerHTML = devAuth;
                     //Fill Role select field

                     fetch('/mcROLE/' + data['primarycontroller']['id']).then(function (response) {
                         response.json().then(function (roledata) {
                             let optionHTML = "<option value='None'>Select</option>";
                             document.getElementById("mcrole").value = JSON.stringify(roledata);
                             for (let roleinfo of roledata.role) {
                                 optionHTML += "<option value='" + roleinfo.rname + "'>" + roleinfo.rname + "</option>";
                             }
                             mcrole.innerHTML = optionHTML;
                         });
                     });
                     
                   });
            });
        }
     }).trigger('change');


    $('.field input').keyup(function () {
        var selectisEmpty = false;
        var fieldisEmpty = false;
        $('.field input').keyup(function () {
            $('.field input').each(function () {
                if ($(this).val().length == 0) {
                    fieldisEmpty = true;
                }
            });
            var profile_select = document.getElementById('profile');
            var profile = profile_select.options[profile_select.selectedIndex].value;
            if (profile == "None") { selectisEmpty = true; }
            if (fieldisEmpty || selectisEmpty) {
                $('.actions input').attr('disabled', 'disabled');
            } else {
                $('.actions input').attr('disabled', false);
            }
        });
    });




});


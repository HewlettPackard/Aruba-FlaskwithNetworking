// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

$(function () {

    $("#primarycontroller").change(function () {
        var selectisEmpty = false;
        var fieldisEmpty = false;
        var pmc_select = document.getElementById('primarycontroller');
        var pmc = pmc_select.options[pmc_select.selectedIndex].value;
        if (pmc == "" || pmc == "None") { selectisEmpty = true; }
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

        
        if (pmc=="None") {
            $("#vlanForm").hide();
            $("#roleForm").hide();
        }}).trigger('change');

    $("#mcvlan").change(function () {
        var pmc_select = document.getElementById('primarycontroller');
        var pmc = pmc_select.options[pmc_select.selectedIndex].value;
        var vlan_select = document.getElementById('mcvlan');
        var vlan = vlan_select.options[vlan_select.selectedIndex].value;
         if (vlan=="None" || pmc == "None") {
             $("#vlanForm").hide();
        } else {
            $("#vlanForm").show();
        }
    }).trigger('change');

    $("#mcrole").change(function () {
        var pmc_select = document.getElementById('primarycontroller');
        var pmc = pmc_select.options[pmc_select.selectedIndex].value;
        var role_select = document.getElementById('mcrole');
        var role = role_select.options[role_select.selectedIndex].value;
        if (role == "None" || pmc == "None") {
            $("#roleForm").hide();
        } else {
            $("#roleForm").show();
        }
    }).trigger('change');

    $("#editVLAN").click(function () {
        document.getElementById('editVLAN').style.display = "none";
        document.getElementById('submitVLAN').style.display = "none";
        document.getElementById('changeVLAN').style.display = "block";
        document.getElementById('vlanAction').innerHTML = "Edit VLAN";
        $("#vlanid").prop('disabled', false);
        $("#vlanname").prop('disabled', false);
        $("#ipaddress").prop('disabled', false);
        $("#netmask").prop('disabled', false);
    }).trigger('change');

    $("#submitVLAN").click(function () {
        document.getElementById('editVLAN').style.display = "none";
        document.getElementById('submitVLAN').style.display = "block";
        document.getElementById('changeVLAN').style.display = "none";
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
            var pmc_select = document.getElementById('primarycontroller');
            var pmc = pmc_select.options[pmc_select.selectedIndex].value;
            if (pmc == "" || pmc == "None") { selectisEmpty = true; }
            if (fieldisEmpty || selectisEmpty) {
                $('.actions input').attr('disabled', 'disabled');
            } else {
                $('.actions input').attr('disabled', false);
            }
        });
    });

    $('.vlanfield input').keyup(function () {
        var vlanfieldisEmpty = false;
        $('.vlanfield input').each(function () {
            if ($(this).val().length == 0) {
                vlanfieldisEmpty = true;
                }
        });
        if (vlanfieldisEmpty) {
            $('.vlanactions input').attr('disabled', 'disabled');
            } else {
            $('.vlanactions input').attr('disabled', false);
            }
    });


    let pmc_select = document.getElementById('primarycontroller');
    let vlan_select = document.getElementById('mcvlan');
    let role_select = document.getElementById('mcrole');
    let submitVLAN = document.getElementById('submitVLAN');
    let changeVLAN = document.getElementById('changeVLAN');

    role_select.onchange = function () {
        role = role_select.value;
        mcid = pmc_select.value;
        infoHTML = "";
        fetch('/serviceROLE/' + mcid + '/' + role).then(function (response) {
            response.json().then(function (data) {
                console.log(data.action);
                if (data.action == "create") {
                    console.log("Create role");

                }
                else if (data.action == "select") {
                    //pass
                }
                else {
                    // Need to add innerhtml information...
                    infoHTML = "<form name='roleForm' id='roleForm'>";
                    infoHTML += "<input type='hidden' name='roleid' id='roleid' />";
                    infoHTML += "<table class='tablewithborder'><tr>";
                    infoHTML += "<td colspan='5' align='center' style='color: darkorange; background-color: black;padding: 5px;'>";
                    infoHTML += data[0]['role'] + " Role information</td></tr>";
                    for (i = 0; i < data[1].length; i++) {

                        infoHTML += "<tr><td><font class='font12px'>Policy name</font></td>";
                        infoHTML += "<td><input type='text' name='" + data[1][i]['pname'] + "' value='" +data[1][i]['pname'] + "' id='policyname'/></td>";
                        infoHTML += "<td><font class='font12px'>Policy type</font></td>";
                        infoHTML += "<td><input type='text' name='acl-" + data[1][i]['pname'] + "' value='" + data[1][i]['acl_type'] + "' id='policytype' /></td>";
                        infoHTML += "<td><input type='button' name='action' value='ACL' class='button' id='showACL'><input type='button' name='action' value='Edit' id='editPolicy' class='button'>";
                        infoHTML += "<input type='button' name='action' value='Delete' id='deletePolicy' class='button' onclick = 'return confirm('Are you sure you want to delete this item?')' ></td></tr >";
                    }
                    infoHTML += "</table></form >";
                    roleInfo.innerHTML = infoHTML;
                }
            });
        });
    }

    vlan_select.onchange = function () {
        vlan = vlan_select.value;
        mcid = pmc_select.value;
        fetch('/serviceVLAN/' + mcid + '/' + vlan).then(function (response) {
            response.json().then(function (data) {
                if (data.action == "create") {
                    console.log("Create VLAN");
                    $("#ipaddress").prop('disabled', false);
                    $("#netmask").prop('disabled', false);
                    $("#submitVLAN").prop('disabled', true);
                    document.getElementById("ipaddress").value = "";
                    document.getElementById("netmask").value = "";
                    document.getElementById('editVLAN').style.display = "none";
                    document.getElementById('submitVLAN').style.display = "block";
                    document.getElementById('createVLAN').style.display = "block";
                    document.getElementById('vlanAction').innerHTML = "Create VLAN";
                    document.getElementById('changeVLAN').style.display = "none";
                }
                else if (data.action == "select") {
                    //pass
                }
                else {
                    //Edit the VLAN information
                    $("#vlanid").prop('disabled', true);
                    $("#vlanname").prop('disabled', true);
                    $("#ipaddress").prop('disabled', true);
                    $("#netmask").prop('disabled', true);
                    document.getElementById('editVLAN').style.display = "block";
                    document.getElementById('vlanAction').innerHTML = "VLAN information";
                    document.getElementById('submitVLAN').style.display = "none";
                    document.getElementById('changeVLAN').style.display = "none";
                    ipaddress.value = data.int_vlan_ip.ipaddr;
                    netmask.value = data.int_vlan_ip.ipmask;
                    vlanid.value = data.id;
                    vlanname.value = data.name;
                    console.log(data);
                }
            });

        });
    }

    changeVLAN.onclick = function () {
        console.log("Clicked on submit changes");
    }

    submitVLAN.onclick = function () {
        console.log("Clicked on submit vlan");
    }

    pmc_select.onchange = function () {
        mcid = pmc_select.value;
        fetch('/mcVLAN/' + mcid).then(function (response) {
            response.json().then(function (data) {
                if (mcid == "None") {
                    let optionHTML = "<option value='None'>Select Primary Controller</option>";
                    mcvlan.innerHTML = optionHTML;
                }
                else {
                    let optionHTML = "<option value='None' id='hidevlanForm'>Select</option><option value='Create VLAN'>Create VLAN</option>";
                    document.getElementById("vlans").value = JSON.stringify(data);
                    for (let vlaninfo of data.vlan_name_id) {
                        //Javascript treats hypens as operators, so need to remove the hyphen
                        vlanid = vlaninfo['vlan-ids'];
                        optionHTML += "<option value='" + vlanid + "'>VLAN: " + vlanid + " (" + vlaninfo.name + ")</option>";
                    }
                    mcvlan.innerHTML = optionHTML;
                }
            });
        });
        fetch('/mcROLE/' + mcid).then(function (response) {
            response.json().then(function (data) {
                if (mcid == "None") {
                    let optionHTML = "<option value='None'>Select Primary Controller</option>";
                    mcrole.innerHTML = optionHTML;
                }
                else {
                    let optionHTML = "<option value='None' id='hideroleForm'>Select</option><option value='Create role'>Create role</option>";
                    document.getElementById("roles").value = JSON.stringify(data);
                    for (let roleinfo of data.role) {
                        optionHTML += "<option value='" + roleinfo.rname + "'>" + roleinfo.rname + "</option>";
                    }
                    mcrole.innerHTML = optionHTML;
                }
            });
        });
    }



});


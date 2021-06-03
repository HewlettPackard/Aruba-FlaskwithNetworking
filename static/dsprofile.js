// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {

    // If there is a change in the select, we have to check whether there is a selection in the select, but we also need to check whether
    // all the required input fields are filled in

    if ($('#clearpass').val() != "" && $('#primarycontroller').val() != "" && $('#name').val() != "" && $('#radiussecret').val() != "" && $('#ntpserver').val() != "")
    {
        $('.actions input').attr('disabled', false);
    }

    $("#primarycontroller,#clearpass").change(function () {
        var selectisEmpty = false;
        var fieldisEmpty = false;
        var clearpass_select = document.getElementById('clearpass');
        var clearpass = clearpass_select.options[clearpass_select.selectedIndex].value;
        var primarycontroller_select = document.getElementById('primarycontroller');
        var primarycontroller = primarycontroller_select.options[primarycontroller_select.selectedIndex].value;
        if (primarycontroller == "" || clearpass == "")
        { selectisEmpty = true; }
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
    });

    $('.field input').keyup(function () {
        var selectisEmpty = false;
        var fieldisEmpty = false;
         $('.field input').keyup(function () {
            $('.field input').each(function () {
                if ($(this).val().length == 0) {
                    fieldisEmpty = true;
                }
            });
             var clearpass_select = document.getElementById('clearpass');
             var clearpass = clearpass_select.options[clearpass_select.selectedIndex].value;
             var primarycontroller_select = document.getElementById('primarycontroller');
             var primarycontroller = primarycontroller_select.options[primarycontroller_select.selectedIndex].value;
             if (primarycontroller == "" || clearpass == "")
                 { selectisEmpty = true; }
            if (fieldisEmpty || selectisEmpty) {
                $('.actions input').attr('disabled', 'disabled');
            } else {
                $('.actions input').attr('disabled', false);
            }
        });
    });

});
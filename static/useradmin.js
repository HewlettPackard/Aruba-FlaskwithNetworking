// (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

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
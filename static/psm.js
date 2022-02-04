// (C) Copyright 2021 Hewlett Packard Enterprise Development LP.

$(document).ready(function () {


    $('.showattributeTooltip').mouseover(async function (event) {
        if ((event.pageX + 350) > self.innerWidth) {
            var left = event.pageX - 300;
        }
        else {
            var left = event.pageX + 10;
        }
        if (typeof ($('#' + this.id).attr('data-info')) !== 'undefined') {
            tooltipHeight = ($('#' + this.id).attr('data-info').match(/<tr/g) || []).length * 10;
            if (self.innerHeight < (tooltipHeight + event.pageY)) {

                var top = Math.abs(event.pageY - Math.abs((Math.abs(tooltipHeight) / 3) * 4) - 50);
            }
            else {
                var top = event.pageY - 25;
            }
        }
        else {
            var top = event.pageY - 25;
        }
        $("#showdaTooltip").css({
            position: 'absolute',
            zIndex: 5000,
            left: left,
            top: top,
            backgroundColor: 'transparent',
            width: '400px',
        });
        $('#showdaTooltip').empty().append($('#' + this.id).attr('data-info'));
        $('#showdaTooltip').show();
    });

    $('.showattributeTooltip').mouseout(function () {
        $('#showdaTooltip').hide();
    });


    


});



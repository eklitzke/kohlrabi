$(document).ready(function () {
    var canvasClasses = [];
    $('canvas').each(function (index, value) {
        var seen = false;
        for (var i = 0; i < canvasClasses.length; i++) {
            if (canvasClasses[i] == value.className) {
                seen = true;
            }
        }
        if (seen === false) {
            canvasClasses.push(value.className);
        }
    });

    $(canvasClasses).each(function (i, value) {
        var hue = i / canvasClasses.length;
        var rgbCode = $.Color([hue, 0.6, 0.65], 'HSV').toHEX();
        $('.' + canvasClasses[i]).each(function (idx, elem) {
            var ctx = elem.getContext('2d');
            ctx.fillStyle = rgbCode;
            ctx.fillRect(0, 0, elem.width, elem.height);
        });

    });

});

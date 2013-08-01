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


    $('.report_link').each(function (index, value) {
        $(this).click(function(event) {
            console.log('got a click durrr');
            var params = {};
            var variants = this.parentNode.getElementsByClassName('variant');
            var hasAny = false;
            for (var i = 0; i < variants.length; i++) {
                var variant = variants[i];
                var variantName = $(variant.getElementsByClassName('variant_name')).text();
                var variantValue = variant.getElementsByTagName('select')[0].value;
                if (variantValue) {
                    params[variantName] = variantValue;
                    hasAny = true;
                }
            }
            console.log(params);
            console.log(params.length)
            event.preventDefault();
            if (hasAny) {
                event.preventDefault();
                window.location = this.href + '?' + $.param(params);
            }
        });
    });
});

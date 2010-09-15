/* -*- indent-tabs-mode: nil; tab-width: 4; -*- */

$(document).ready(function () {
    var tbl = document.getElementById('kohlrabi_table');
    var thRow = tbl.getElementsByTagName('tr')[0];
    for (var i = 0; i < thRow.children.length; i++) {
        thRow.children[i].sortType = 'asc';
    }
    var r = tbl.getElementsByTagName('tr');
    var tdRows = [];
    for (var i = 1; i < r.length; i++) {
        tdRows.push(r[i]);
    }
    $('th').click(function (e) {
        var th = null;
        var sort;
        for (var i = 0; i < thRow.children.length; i++) {
            if (thRow.children[i] === this) {
                th = thRow.children[i];
                if ($(th).hasClass('number')) {
                    sort = 'numeric';
                }
                break;
            }
        }
        if (th) {
            /* this looks kind of weird, but the if check is hoisted outside of
             * the sort function for speed */
            if (sort == 'numeric') {
                tdRows.sort(function (a, b) {
                    var aVal = parseFloat(a.children[i].innerHTML);
                    var bVal = parseFloat(b.children[i].innerHTML);
                    return aVal - bVal;
                });
            } else {
                tdRows.sort(function (a, b) {
                    var aVal = a.children[i].innerHTML;
                    var bVal = b.children[i].innerHTML;
                    if (aVal == bVal)
                        return 0;
                    return aVal > bVal ? 1 : -1;
                });
            }
            if (th.sortType == 'desc') {
                th.sortType = 'asc';
            } else {
                tdRows.reverse();
                th.sortType = 'desc';
            }
            while (tbl.children.length > 1) {
                tbl.removeChild(tbl.lastChild);
            }
            for (var i = 0; i < tdRows.length; i++) {
                tbl.appendChild(tdRows[i]);
            }
        } else {
            alert('huh, which TH element is that?');
        }
    });

    var clickedRow = null;
    $('tr').click(function () {
        if (this.children[0].tagName == 'TH') {
            return;
        }
        if (clickedRow) {
            $(clickedRow).removeClass('clicked');
        }
        if (clickedRow !== this) {
            clickedRow = this;
            $(this).addClass('clicked');
        } else {
            clickedRow = null;
        }
    });
});

function establishInputFilter(input, offset) {
    var tbl = document.getElementById('kohlrabi_table');
    console.info(tbl);
    var lastVal = input.val();
    var filter = function () {
        var newVal = $(this).val();
        if (newVal !== lastVal) {
            lastVal = newVal;
            var r = new RegExp('^' + newVal);
            $('tr').each(function () {
                var td = this.children[offset];
                if (td.tagName == 'TD') {
                    if (r.test(td.innerHTML)) {
                        this.style.display = 'table-row';
                    } else {
                        this.style.display = 'none';
                    }
                } else {
                    console.info('lol');
                    console.info(this);
                }
            });
        }
    };
    input.change(filter);
    input.keyup(filter);
}

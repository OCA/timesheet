/* License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('hr_timesheet_sheet_attendance.matrixwidget', function (require) {
    "use strict";

    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var matrix_widget = require('web_widget_x2many_2d_matrix.widget');

    var _t = core._t;

    var AttendanceMatrixWidget = matrix_widget.WidgetX2Many2dMatrix.extend({
        _render: function () {
            var res = this._super();
            this._rpc({
                model: 'hr_timesheet.sheet',
                method: 'get_attendance_by_day',
                args: [this.recordData.id]
            }).then(function (data) {
                var row =  $('<tr>', {'class': 'attendance_row'});
                var title = $('<td>');
                title.text(_t('Attendance'));
                row.append(title);
                data.forEach(function(element) {
                    var cell = $('<td>', {'class':'text-right'});
                    cell.text(element.toFixed(2));
                    row.append(cell);
                });
                row.append('<td></td>');
                this.$el.find('tfoot').append(row);
            }.bind(this));
            return res;
        }
    });
    field_registry.add('attendace_matrix_widget', AttendanceMatrixWidget);

    return {
        AttendanceMatrixWidget: AttendanceMatrixWidget,
    };
});

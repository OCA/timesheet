odoo.define("hr_timesheet_sheet", function(require) {
    "use strict";

    var X2Many2dMatrixRenderer = require("web_widget_x2many_2d_matrix.X2Many2dMatrixRenderer");

    X2Many2dMatrixRenderer.include({
        /**
         * @override
         */
        _renderBodyCell: function() {
            var $cell = this._super.apply(this, arguments);
            if (this.getParent().model === "hr_timesheet.sheet") {
                var $span = $cell.find("span");
                if ($span.text() === "00:00") {
                    $span.addClass("text-muted");
                } else {
                    $span.wrap($("<strong />"));
                }
            }
            return $cell;
        },
    });
});

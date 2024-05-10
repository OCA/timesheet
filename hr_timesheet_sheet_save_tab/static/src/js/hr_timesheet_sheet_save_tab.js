odoo.define("web.FormRenderer.HrTimesheetSheet", function (require) {
    "use strict";
    var FormRenderer = require("web.FormRenderer");

    FormRenderer.include({
        _renderTagNotebook: function () {
            var $notebook = this._super.apply(this, arguments);
            if (this.state.model === "hr_timesheet.sheet") {
                $notebook.on("hide.bs.tab", this._onNotebookTabHidden.bind(this));
            }
            return $notebook;
        },
        _onNotebookTabHidden: function () {
            var self = this;
            var data = this.state.data;
            if (
                this.mode === "edit" &&
                (data.line_ids.isDirty() || data.timesheet_ids.isDirty())
            ) {
                var controller = this.getParent();
                return controller
                    .saveRecord(this.state.id, {stayInEdit: true})
                    .then(function () {
                        self.trigger_up("reload");
                    });
            }
        },
    });
});

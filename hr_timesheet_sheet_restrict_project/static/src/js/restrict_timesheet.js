odoo.define('hr_timesheet_sheet_restrict_project.restrict', function (require) {
'use strict';

    var core = require('web.core');

    var hr_timesheet_sheet = core.form_custom_registry.get('weekly_timesheet');
    hr_timesheet_sheet.include({
         init_add_project: function() {
           var self = this;
           var res = this._super();
           self.project_m2o.node.attrs.domain.push(['allow_timesheets', '=', true]);
           return res;
         }
    });


});

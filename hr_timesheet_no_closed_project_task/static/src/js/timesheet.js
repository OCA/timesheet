/* © 2015-2017 ACSONE SA/NV (http://acsone.eu)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('hr_timesheet_no_closed_project_task', function (require) {
    'use strict';

    var core = require('web.core');
    var hr_timesheet_sheet = require('hr_timesheet_sheet.sheet');

    core.form_custom_registry.get('weekly_timesheet').include({

        project_push_stage_domain: function () {
            this.task_m2o.node.attrs.domain.push(['stage_closed', '=', false]);
        },
        init_add_project: function () {
            var self = this;
            self._super.apply(self, arguments);
            self.project_push_stage_domain();
        },
        onchange_project_id: function () {
            var self = this;
            self._super.apply(self, arguments);
            self.project_push_stage_domain();
        }
    });
});

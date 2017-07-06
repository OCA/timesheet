odoo.define('hr_timesheet_task_required.sheet', function (require) {
    'use strict';

    var core = require('web.core');

    core.form_custom_registry.get('weekly_timesheet').include({

        init_add_project: function() {
            var self = this;
            self._super.apply(self, arguments);
            self.task_m2o.set({
                required: true,
            });
        },

        onclick_add_row_button: function(){
            var self = this;
            var id = self.task_m2o.get_value();
            if (id === false) {
                self.dfm.set({display_invalid_fields: true});
                return;
            }
            return self._super();
        }

    });

});

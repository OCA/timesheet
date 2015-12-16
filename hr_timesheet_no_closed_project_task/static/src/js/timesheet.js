openerp.hr_timesheet_no_closed_project_task = function(instance) { 

    var module = instance.hr_timesheet_sheet

    module.WeeklyTimesheet = module.WeeklyTimesheet.extend({
        
        init_add_account: function() {
            var self = this
            this._super.apply(this, arguments);
            self.account_m2o.node.attrs.domain.push(['project_ids.state', 'not in', ['close', 'cancelled']]);
            self.task_m2o.node.attrs.domain.push(['stage_id.closed', '=', false]);
        },
        onchange_account_id: function() {
            var self = this
            this._super.apply(this, arguments);
            self.task_m2o.node.attrs.domain.push(['stage_id.closed', '=', false]);
        }
    });
};

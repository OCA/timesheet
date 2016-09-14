openerp.hr_timesheet_task_required = function(instance) {

    var module = instance.hr_timesheet_sheet

    module.WeeklyTimesheet = module.WeeklyTimesheet.extend({
        init_add_account: function() {
        	var self = this;
            if (self.dfm)
                return;
            res = this._super();
            self.task_m2o.set({ required: true });
            return res;
        },
        onclick_add_row_button: function(){
            var self = this;
            var id = self.task_m2o.get_value();
            if (id === false) {
                self.dfm.set({display_invalid_fields: true});
                return;
            }
            return this._super();


        }
    });
};
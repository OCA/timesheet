//-*- coding: utf-8 -*-
//© 2017 Therp BV <http://therp.nl>
//License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

openerp.hr_timesheet_improvement = function(instance)
{
    instance.hr_timesheet_sheet.WeeklyTimesheet.include({
        ignore_fields: function()
        {
            var result = this._super.apply(this, arguments);
            // we don't want to try to write on the related fields
            result.push('account_name');
            result.push('date_aal');
            return result
        },
    });
}

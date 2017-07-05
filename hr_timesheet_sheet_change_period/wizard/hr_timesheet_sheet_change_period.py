# -*- coding: utf-8 -*-
# © ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class HrTimesheetSheetChangePeriod(models.TransientModel):
    """
    Wizard allowing to capture new timesheet dates
    """

    _name = "hr.timesheet.sheet.change.period.wizard"
    _description = "Timesheet Period Change Wizard"
    _rec_name = 'sheet_id'

    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    sheet_id = fields.Many2one(
        'hr_timesheet_sheet.sheet', string='Timesheet', readonly=True)

    @api.model
    def default_get(self, fields_list):
        defaults = super(HrTimesheetSheetChangePeriod, self).default_get(
            fields_list)
        sheet_obj = self.env['hr_timesheet_sheet.sheet']
        sheet = sheet_obj.browse(self.env.context['active_id'])
        defaults.update({
            'sheet_id': sheet.id,
            'date_from': sheet.date_from,
            'date_to': sheet.date_to,
        })
        return defaults

    @api.multi
    def change(self):
        self.ensure_one()
        vals = {'date_from': self.date_from, 'date_to': self.date_to}
        self.sheet_id.write(vals)
        return {'type': 'ir.actions.act_window_close'}

# Copyright 2015 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2019 Alexandre Díaz <alexandre.diaz@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import DATE_LENGTH

_logger = logging.getLogger(__name__)


class CrmPhonecall(models.Model):
    _inherit = "crm.phonecall"

    project_id = fields.Many2one(comodel_name="project.project")
    timesheet_ids = fields.One2many(
        comodel_name="account.analytic.line", inverse_name="phonecall_id"
    )

    @api.model
    def _timesheet_prepare(self, vals):
        """
        param: vals
        type: dict
        desc: crm.phonecall vals dict (It's like create and write methods)
        """
        if len(self) > 0:
            self.ensure_one()
        date = vals.get("date", fields.Date.to_string(self.date))
        if not date:
            raise UserError(_("Date field must be filled."))
        project_id = vals.get("project_id", self.project_id)
        user_id = vals.get("user_id", self.user_id.id)
        unit_amount = vals.get("duration", self.duration)
        res = {
            "date": date[:DATE_LENGTH],
            "user_id": user_id,
            "name": vals.get("name", self.name),
            "project_id": project_id,
            "unit_amount": unit_amount / 60.0,
        }
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("project_id") and vals.get("duration", 0) > 0:
                timesheet_data = self._timesheet_prepare(vals)
                vals["timesheet_ids"] = vals.get("timesheet_ids", [])
                vals["timesheet_ids"].append(Command.create(timesheet_data))
        records = super().create(vals_list)
        return records

    def write(self, vals):
        AccountAnalitycLineObj = self.env["account.analytic.line"]
        for record in self:
            timesheet = AccountAnalitycLineObj.search(
                [("phonecall_id", "=", record.id)]
            )
            project_id = vals.get("project_id", record.project_id.id)
            duration = vals.get("duration", record.duration) or 0
            can_create_ts = project_id and duration > 0
            if can_create_ts:
                vals.update(
                    {
                        "project_id": project_id,
                        "duration": duration,
                    }
                )
            if timesheet:
                if not can_create_ts:
                    vals["timesheet_ids"] = [Command.delete(timesheet.id)]
                else:
                    vals["timesheet_ids"] = [
                        Command.update(timesheet.id, self._timesheet_prepare(vals))
                    ]
            elif can_create_ts:
                vals["timesheet_ids"] = [Command.create(self._timesheet_prepare(vals))]
        return super().write(vals)

    def button_end_call(self):
        end_date = datetime.now()
        for call in self:
            if call.date:
                start_date = fields.Datetime.from_string(call.date)
                call.duration = self._end_call(start_date, end_date)
        return True

    def _end_call(self, start_dt, end_dt):
        if not isinstance(start_dt, datetime):
            raise UserError(_("Start date must be datetime."))
        if not isinstance(end_dt, datetime):
            raise UserError(_("End date must be datetime."))
        if end_dt < start_dt:
            return 0
        return (end_dt - start_dt).total_seconds() / 60.0

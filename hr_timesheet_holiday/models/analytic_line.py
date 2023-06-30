# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AnalyticLine(models.Model):
    """Restrict edit and delete on analytic lines generated by holidays"""

    _inherit = "account.analytic.line"

    leave_id = fields.Many2one(comodel_name="hr.leave", string="Leave id")

    @api.depends(
        "date",
        "user_id",
        "project_id",
        "sheet_id_computed.date_to",
        "sheet_id_computed.date_from",
        "sheet_id_computed.employee_id",
        "account_id.is_leave_account",
    )
    def _compute_sheet(self):
        """Links the timesheet line to the corresponding sheet"""
        for ts_line in self:
            if not ts_line.account_id.is_leave_account:
                return super(AnalyticLine, ts_line)._compute_sheet()
            else:
                sheets = self.env["hr_timesheet.sheet"].search(
                    [
                        ("date_start", ">=", ts_line.date),
                        ("date_end", "<=", ts_line.date),
                        ("employee_id.user_id.id", "=", ts_line.user_id.id),
                        ("state", "in", ["draft", "new"]),
                    ]
                )
                if sheets:
                    ts_line.sheet_id_computed = sheets[0]
                    ts_line.sheet_id = sheets[0]

    def write(self, vals):
        if not self.env.context.get("force_write", False):
            for rec in self:
                if rec.account_id.is_leave_account and rec.leave_id:
                    raise ValidationError(
                        _(
                            "This line is protected against editing because it "
                            "was created automatically by a leave request. "
                            "Please edit the leave request instead."
                        )
                    )
        return super(AnalyticLine, self).write(vals)

# Copyright 2018 ForgeFlow, S.L.
# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    sheet_id = fields.Many2one(comodel_name="hr_timesheet.sheet", string="Sheet")
    sheet_state = fields.Selection(string="Sheet State", related="sheet_id.state")

    def _get_sheet_domain(self):
        """Hook for extensions"""
        self.ensure_one()
        return [
            ("date_end", ">=", self.date),
            ("date_start", "<=", self.date),
            ("employee_id", "=", self.employee_id.id),
            ("company_id", "in", [self.company_id.id, False]),
            ("state", "in", ["new", "draft"]),
        ]

    def _determine_sheet(self):
        """Hook for extensions"""
        self.ensure_one()
        return self.env["hr_timesheet.sheet"].search(self._get_sheet_domain(), limit=1)

    def _compute_sheet(self):
        """Links the timesheet line to the corresponding sheet"""
        for timesheet in self.filtered("project_id"):
            sheet = timesheet._determine_sheet()
            if timesheet.sheet_id != sheet:
                timesheet.sheet_id = sheet

    @api.constrains("company_id", "sheet_id")
    def _check_company_id_sheet_id(self):
        for aal in self.sudo():
            if (
                aal.company_id
                and aal.sheet_id.company_id
                and aal.company_id != aal.sheet_id.company_id
            ):
                raise ValidationError(
                    _(
                        "You cannot create a timesheet of a different company "
                        "than the one of the timesheet sheet:"
                        "\n - %s of %s"
                        "\n - %s of %s"
                        % (
                            aal.sheet_id.complete_name,
                            aal.sheet_id.company_id.name,
                            aal.name,
                            aal.company_id.name,
                        )
                    )
                )

    @api.model
    def create(self, values):
        if not self.env.context.get("sheet_create") and "sheet_id" in values:
            del values["sheet_id"]
        res = super().create(values)
        res._compute_sheet()
        return res

    @api.model
    def _sheet_create(self, values):
        return self.with_context(sheet_create=True).create(values)

    def write(self, values):
        self._check_state_on_write(values)
        res = super().write(values)
        if self._timesheet_should_compute_sheet(values):
            self._compute_sheet()
        return res

    def unlink(self):
        self._check_state()
        return super().unlink()

    def _check_state_on_write(self, values):
        """Hook for extensions"""
        if self._timesheet_should_check_write(values):
            self._check_state()

    @api.model
    def _timesheet_should_check_write(self, values):
        """Hook for extensions"""
        return bool(set(self._get_timesheet_protected_fields()) & set(values.keys()))

    @api.model
    def _timesheet_should_compute_sheet(self, values):
        """Hook for extensions"""
        return any(f in self._get_sheet_affecting_fields() for f in values)

    @api.model
    def _get_timesheet_protected_fields(self):
        """Hook for extensions"""
        return [
            "name",
            "date",
            "unit_amount",
            "user_id",
            "employee_id",
            "department_id",
            "company_id",
            "task_id",
            "project_id",
            "sheet_id",
        ]

    @api.model
    def _get_sheet_affecting_fields(self):
        """Hook for extensions"""
        return ["date", "employee_id", "project_id", "company_id"]

    def _check_state(self):
        if self.env.context.get("skip_check_state"):
            return
        for line in self.exists().filtered("sheet_id"):
            if line.sheet_id.state not in ["new", "draft"]:
                raise UserError(
                    _(
                        "You cannot modify an entry in a confirmed timesheet sheet"
                        ": %s"
                    )
                    % (line.sheet_id.complete_name,)
                )

    def merge_timesheets(self):
        unit_amount = sum([t.unit_amount for t in self])
        amount = sum([t.amount for t in self])
        self[0].write({"unit_amount": unit_amount, "amount": amount})
        self[1:].unlink()
        return self[0]

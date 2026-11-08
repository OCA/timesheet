# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    project_id = fields.Many2one(
        string="Project",
        comodel_name="project.project",
        domain="[('company_id', '=', company_id)]",
    )

    def _get_complete_name_components(self):
        self.ensure_one()
        result = super()._get_complete_name_components()
        if self.review_policy == "project_manager" and self.project_id:
            result += [self.project_id.display_name]
        return result

    def _get_overlapping_sheet_domain(self):
        domain = super()._get_overlapping_sheet_domain()
        if self.review_policy == "project_manager" and self.project_id:
            domain += [("project_id", "=", self.project_id.id)]
        return domain

    @api.constrains(
        "date_start",
        "date_end",
        "company_id",
        "employee_id",
        "review_policy",
        "project_id",
    )
    def _check_overlapping_sheets_project_id(self):
        self._check_overlapping_sheets()

    @api.constrains("company_id", "project_id")
    def _check_company_id_project_id(self):
        for rec in self.sudo():
            if (
                rec.company_id
                and rec.project_id.company_id
                and rec.company_id != rec.project_id.company_id
            ):
                raise ValidationError(
                    self.env._(
                        "The Company in the Timesheet Sheet and in the Project "
                        "must be the same."
                    )
                )

    def _get_possible_reviewers(self):
        self.ensure_one()
        res = super()._get_possible_reviewers()
        if self.review_policy == "project_manager":
            res |= self.project_id.user_id
        return res

    def _get_timesheet_sheet_lines_domain(self):
        domain = super()._get_timesheet_sheet_lines_domain()
        if self.review_policy == "project_manager":
            domain += [("project_id", "=", self.project_id.id)]
        else:
            domain += [("project_id", "!=", False)]
        return domain

    @api.onchange("project_id")
    def _onchange_project_id(self):
        self.add_line_project_id = self.project_id
        self._compute_timesheet_ids()

    def _check_can_review(self):
        res = super()._check_can_review()
        if self.filtered(
            lambda sheet: not sheet.can_review
            and sheet.review_policy == "project_manager"
        ):
            raise UserError(self.env._("Only a Project Manager can review the sheet."))
        return res

    def reset_add_line(self):
        res = super().reset_add_line()
        self.write({"add_line_project_id": self.project_id.id})
        return res

    @api.constrains("review_policy", "project_id")
    def _check_review_policy(self):
        for rec in self:
            if rec.review_policy == "project_manager" and not rec.project_id:
                raise UserError(
                    self.env._(
                        'Review policy "By Project Manager" requires Project to be set'
                    )
                )

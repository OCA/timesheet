# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    project_id = fields.Many2one(
        string="Project",
        comodel_name="project.project",
        readonly=True,
        states={"new": [("readonly", False)]},
    )

    @api.depends("project_id.user_id")
    def _compute_project_manager_as_reviewer(self):
        self._compute_possible_reviewer_ids()

    @api.depends("project_id")
    def _compute_complete_name_project_id(self):
        self._compute_complete_name()

    def _get_complete_name_components(self):
        self.ensure_one()
        result = super()._get_complete_name_components()
        if self.review_policy == "project_manager":
            result += [self.project_id.name_get()[0][1]]
        return result

    def _get_overlapping_sheet_domain(self):
        domain = super()._get_overlapping_sheet_domain()
        if self.review_policy == "project_manager":
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
                    _(
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
        return self.onchange_add_project_id()

    def _check_can_review(self):
        super()._check_can_review()
        if self.filtered(
            lambda sheet: not sheet.can_review
            and sheet.review_policy == "project_manager"
        ):
            raise UserError(_("Only a Project Manager can review the sheet."))

    def reset_add_line(self):
        super().reset_add_line()
        self.write({"add_line_project_id": self.project_id.id})

    @api.model
    def create(self, vals):
        review_policy = vals.get(
            "review_policy", self.default_get(["review_policy"])["review_policy"]
        )
        if review_policy == "project_manager" and not vals.get("project_id"):
            raise UserError(
                _('Review policy "By Project Manager" requires Project to be set')
            )
        return super().create(vals)

    def write(self, vals):
        if (
            self.filtered(lambda x: x.review_policy == "project_manager")
            and "project_id" in vals
            and not vals.get("project_id")
        ):
            raise UserError(
                _('Review policy "By Project Manager" requires Project to be set')
            )
        return super().write(vals)

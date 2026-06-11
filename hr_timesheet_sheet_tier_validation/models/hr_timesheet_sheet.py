# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class HrTimesheetSheet(models.Model):
    _name = "hr_timesheet.sheet"
    _inherit = ["hr_timesheet.sheet", "tier.validation"]
    _state_from = ["confirm"]
    _state_to = ["done"]

    _tier_validation_manual_config = False

    @api.depends_context("uid")
    @api.depends("review_ids.status", "validation_status", "review_policy")
    def _compute_can_review(self):
        res = super()._compute_can_review()
        for sheet in self.filtered("review_ids"):
            if sheet.validation_status == "validated":
                sheet.can_review = sheet.env.user in sheet._get_possible_reviewers()
            else:
                sheet.can_review = bool(sheet._get_sequences_to_approve(sheet.env.user))
        return res

    @api.model
    def _search_can_review(self, operator, value):
        """Search tier reviews instead of timesheet review permissions.

        ``hr_timesheet.sheet`` already defines a search method for ``can_review``
        based on its review policy.  The tier validation systray also searches
        this field, but expects the tier validation semantics: only documents
        with an actionable pending review must be returned.
        """
        reviews = self.env["tier.review"].search(
            [
                ("model", "=", self._name),
                ("reviewer_ids", "=", self.env.user.id),
                ("status", "in", ["pending", "waiting"]),
                ("can_review", "=", True),
            ]
        )
        return [("id", "in", list(set(reviews.mapped("res_id"))))]

    def _allow_to_remove_reviews(self, values):
        res = super()._allow_to_remove_reviews(values)
        if values.get(self._state_field) == "draft":
            return True
        return res

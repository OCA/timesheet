from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        # We must avoid the recomputation of the unit amount rounded called by
        # the compute_project_id (especially when project has not been changed)
        return super(AccountMove, self.with_context(timesheet_no_recompute=True))._post(
            soft=soft
        )

    def unlink(self):
        return super(
            AccountMove, self.with_context(timesheet_no_recompute=True)
        ).unlink()

    def button_cancel(self):
        return super(
            AccountMove, self.with_context(timesheet_no_recompute=True)
        ).button_cancel()

    def button_draft(self):
        return super(
            AccountMove, self.with_context(timesheet_no_recompute=True)
        ).button_draft()

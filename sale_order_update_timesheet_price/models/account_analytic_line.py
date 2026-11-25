from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def copy(self, default=None):
        """
        This override is needed because in the timesheet_grid module of Odoo Enterprise
        a new timesheet is created by copy of another in some cases (see adjust_grid
        method). In these cases the _compute_so_line is not triggered and the so_line
        is taken from the copied timesheet and may not be the updated one.
        """
        res = super().copy(default=default)
        if self.env.context.get("is_timesheet"):
            res._compute_so_line()
        return res

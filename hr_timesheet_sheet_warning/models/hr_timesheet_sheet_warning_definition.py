# Copyright 2024 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class SheetWarning(models.Model):
    _name = "hr_timesheet.sheet.warning.definition"
    _description = "Timesheet Sheet Warning Definition"
    _order = "id desc"

    name = fields.Char(
        string="Description",
        required=True,
    )
    python_code = fields.Text(
        string="Warning Expression",
        help="Write Python code that defines when this warning should "
        "raise. The result of executing the expression must be "
        "a boolean.",
        default="# Available local variables:\n"
        "#  - sheet: A hr_timesheet.sheet record\n"
        "True",
    )
    active = fields.Boolean(default=True)
    warning_domain = fields.Char(
        string="Applicable Domain",
        default="[]",
        help="Domain based on Timesheet Sheet, "
        "to define if the warning is applicable or not.",
    )

    def _eval_warning_domain(self, sheet, domain):
        sheet_domain = [("id", "=", sheet.id)]
        return bool(
            self.env["hr_timesheet.sheet"].search_count(
                expression.AND([sheet_domain, domain])
            )
        )

    def is_warning_applicable(self, sheet):
        domain = safe_eval(self.warning_domain) or []
        if domain:
            return self._eval_warning_domain(sheet, domain)
        return True

    def evaluate_definition(self, sheet):
        self.ensure_one()
        try:
            res = safe_eval(self.python_code, globals_dict={"sheet": sheet})
        except Exception as error:
            raise UserError(
                _("Error evaluating %(name)s.\n %(error)s")
                % ({"name": self._name, "error": error})
            ) from error
        return res

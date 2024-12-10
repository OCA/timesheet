# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from psycopg2 import sql

from odoo import api, fields, models, tools

from ..models.hr_employee_hour import TYPE_SELECTION


class AbstractHrEmployeeHourReport(models.AbstractModel):
    """This class is intended to be overriden.

    As such, when you change/add a field or override a custom method, you must
    call back the init method to properly update your table initialisation.


    ```
    def init(self):
        return super().deferred_init()
    ```

    """

    _name = "hr.employee.hour.report.abstract"
    _description = "Abstract Employee Hour Report"
    _order = "date, name_id"
    _rec_name = "name_id"

    active = fields.Boolean(default=True)
    date = fields.Date()
    type = fields.Selection(TYPE_SELECTION)
    name_id = fields.Reference(
        selection="_reference_models", string="Name", required=True
    )
    employee_id = fields.Many2one("hr.employee", "Employee")
    manager_id = fields.Many2one("hr.employee", "Manager")
    user_id = fields.Many2one("res.users", "User")
    company_id = fields.Many2one("res.company", "Company")
    project_id = fields.Many2one("project.project", "Project")
    task_id = fields.Many2one("project.task", "Task")
    analytic_group_id = fields.Many2one("account.analytic.group")
    days_qty = fields.Float("Days")
    days_qty_abs = fields.Float("Days (abs)")
    hours_qty = fields.Float("Hours")
    hours_qty_abs = fields.Float("Hours (abs)")
    percentage = fields.Float()

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "%s" % (record.name_id.display_name)))
        return result

    @api.model
    def _reference_models(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    def process_names_from_result(self, result):
        """Process the display name of each name references"""
        names = [tuple(rec.get("name_id", ",").split(",")) for rec in result]
        ids_by_model = defaultdict(set)
        for model_name, res_id in names:
            if not model_name or not res_id:
                continue
            ids_by_model[model_name].add(int(res_id))
        names_by_name_value = {
            f"{model},{record.id}": record.display_name
            for model, ids in ids_by_model.items()
            for record in self.env[model].browse(ids)
        }
        return names_by_name_value

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        # Add the percentage values
        # Force addition of this fields if not in the view specification
        needed_fields = ["hours_qty_abs", "hours_qty_abs:sum"]
        if not set(fields).intersection(set(needed_fields)):
            fields.append("hours_qty_abs:sum")
        result = super().read_group(
            domain, fields, groupby, offset, limit, orderby, lazy
        )

        if len(result or ()) < 2:
            # Avoid processing if empty or only one result
            return result

        def get_grant_total(groups, key):
            """Return the sum of this key's values for all records"""
            return sum(rec.get(key, 0.0) for rec in groups)

        hours_total = get_grant_total(result, "hours_qty_abs")
        names_get_result = self.process_names_from_result(result)
        for rec in result:
            name = rec.get("name_id", None)
            if name:
                rec["name_id"] = names_get_result.get(name, f"ERROR: {name}")
            if hours_total:
                rec["percentage"] = (rec.get("hours_qty_abs", 0.0) / hours_total) * 100
        return result

    def select_hook_custom_fields(self):
        """Must end with a comma if not empty"""
        return """
            -- But keep absolute values for specific graph calculation
            SUM(heh.days_qty) AS days_qty_abs,
            SUM(heh.hours_qty) AS hours_qty_abs,
            -- Inject negative value for total calculation
            SUM(CASE
                  WHEN heh.type = 'contract' THEN -heh.days_qty
                  ELSE heh.days_qty
            END) AS days_qty,
            SUM(CASE
                  WHEN heh.type = 'contract'  THEN -heh.hours_qty
                  ELSE heh.hours_qty
            END) AS hours_qty,
        """

    def _select(self):
        return sql.SQL(
            f"""
            max(heh.id) AS id,
            heh.active,
            heh.name_id,
            heh.project_id,
            heh.task_id,
            heh.employee_id,
            heh.manager_id,
            heh.user_id,
            heh.company_id,
            heh.analytic_group_id,
            heh.date,
            heh.type,
            0.0 AS percentage,
            {self.select_hook_custom_fields()}""".rstrip().rstrip(
                ","
            )
        )

    def _from(self):
        return sql.SQL("hr_employee_hour AS heh")

    def where_types(self):
        return ["contract", "timesheet"]

    def _where(self):
        types = sql.SQL(", ").join(map(sql.Literal, self.where_types()))
        return sql.SQL("heh.type IN ({})").format(types)

    def group_by_hook_custom_fields(self):
        """Must end with a comma if not empty"""
        return ""

    def _group_by(self):
        return sql.SQL(
            f"""
            heh.active,
            heh.name_id,
            heh.project_id,
            heh.task_id,
            heh.employee_id,
            heh.manager_id,
            heh.user_id,
            heh.company_id,
            heh.analytic_group_id,
            heh.date,
            heh.type,
            {self.group_by_hook_custom_fields()}""".rstrip().rstrip(
                ","
            )
        )

    def init(self):
        request = sql.SQL(
            """CREATE OR REPLACE VIEW {} AS (
            SELECT {}
            FROM {}
            WHERE {}
            GROUP BY {}
        );"""
        ).format(
            sql.Identifier(self._table),
            self._select(),
            self._from(),
            self._where(),
            self._group_by(),
        )
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(request)


class HrEmployeeHourReport(models.Model):
    _name = "hr.employee.hour.report"
    _inherit = "hr.employee.hour.report.abstract"
    _description = "Employee Hour Report"
    _auto = False  # Will be processed in init method

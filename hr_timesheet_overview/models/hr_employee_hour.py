# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import _, api, fields, models
from odoo.tools import groupby

TYPE_SELECTION = [
    ("contract", _("Contract")),
    ("timesheet", _("Timesheet")),
]


def get_valid_search_fields(sep=None):
    """Returns unicity constrained fields for `HrEmployeeHour`"""
    fields = "date", "employee_id", "model_id", "res_id", "type"
    return sep.join(fields) if sep else fields


class HrEmployeeHour(models.Model):
    _name = "hr.employee.hour"
    _description = "HR Employee Hours per day"
    _rec_name = "name_id"
    _order = "date"

    active = fields.Boolean(default=True)
    date = fields.Date(readonly=True, required=True)
    name_id = fields.Reference(
        selection="_reference_models", string="Name", readonly=True
    )
    type = fields.Selection(TYPE_SELECTION, readonly=True, required=True)
    hours_qty = fields.Float(readonly=True, required=True)
    days_qty = fields.Float(readonly=True, required=True)
    employee_id = fields.Many2one("hr.employee", readonly=True, required=True)
    analytic_group_id = fields.Many2one("account.analytic.group", readonly=True)
    manager_id = fields.Many2one(
        "hr.employee", related="employee_id.parent_id", store=True
    )
    user_id = fields.Many2one("res.users", related="employee_id.user_id", store=True)
    company_id = fields.Many2one(
        "res.company", related="employee_id.company_id", store=True
    )
    project_id = fields.Many2one("project.project", readonly=True)
    task_id = fields.Many2one("project.task", readonly=True)
    model_id = fields.Many2one("ir.model", "Model", readonly=True, ondelete="set null")
    res_id = fields.Integer("Ressource ID", readonly=True, required=True)

    _sql_constraints = [
        (
            "uniqueness",
            f"UNIQUE({get_valid_search_fields(',')})",
            _("You can't have two hour lines with same fields: %s")
            % get_valid_search_fields(","),
        )
    ]

    @api.model
    def _reference_models(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    @api.model
    def toggle_active_for_records(self, records, apply_to_name_id=False):
        """Toggle active state of line hours depending of records' active field
        By default applied on the lines thats matches model_id and res_id,
        except if apply_to_name_id option is set.

        :param records: a list of any model records
        :param apply_to_name_id: Process only records that match the name_id
        """
        sudo_self = self.sudo()
        for active, records in groupby(records, lambda r: r.active):
            # First, limit the liens that is not in the same active state
            domain = [("active", "=", not active)]
            if apply_to_name_id:
                # Our generate the list of unique name_id
                # Using the reference pattern : "model_name,model_id"
                generated_name_ids = {f"{r._name},{r.id}" for r in records}
                domain.extend([("name_id", "in", list(generated_name_ids))])
            else:
                models = sudo_self.env["ir.model"].search(
                    [("model", "in", records.mapped("_name"))]
                )
                domain.extend(
                    [("model_id", "in", models.ids), ("res_id", "in", records.ids)]
                )
            sudo_self.search(domain).write({"active": active})

    @api.model
    def create_or_update(self, vals_list):
        """This method aims to allow proper creation or update of lines"""
        records = self.browse()
        if not vals_list:
            return records
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        sudo_self = self.sudo().with_context(active_test=False)
        to_create = []
        for values in vals_list:
            # Avoid testing all calls to _prepare...() in case of missing data
            if not values:
                continue
            heh_domain = [
                (field, "=", values.get(field, False))
                # Use of constraint fields to get at most 1 record
                for field in get_valid_search_fields()
            ]
            found_record = sudo_self.search(heh_domain)
            # Due to constraint usage, only one record is retrieved
            if found_record:
                found_record.write(values)
                records |= found_record
            else:
                to_create.append(values)
        if to_create:
            records |= sudo_self.create(to_create)
        return records

    @api.model
    def action_generate_data(self, employee_ids=None, date_from=None, date_to=None):
        """Launch update process

        :param employee_ids: a list of employee ids
        :param date_from: a datetime.date object
        (default first contract date, included)
        :param date_to: a datetime.date object (default today, included)
        """
        if date_to is None:
            date_to = datetime.datetime.now()
        if not employee_ids:
            employees = self.env["hr.employee"].search([])
        else:
            employees = self.env["hr.employee"].browse(employee_ids)
        if not date_from:
            contracts = self.env["hr.contract"].search(
                [("employee_id", "in", employees.ids)]
            )
            date_from = min(contracts.mapped("date_start"), default=None)
            if not date_from:
                return
        wizard = self.env["wizard.hr.employee.hour.updater"].create(
            {
                "employee_ids": employees.ids,
                "date_from": date_from,
                "date_to": date_to,
            }
        )
        wizard.action_submit()

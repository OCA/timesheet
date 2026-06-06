# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrTimesheetCosting(models.Model):
    _name = "hr.timesheet.costing"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Timesheet Costing"
    _order = "name desc"

    name = fields.Char(
        copy=False,
        default="/",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
    )
    date_from = fields.Date(
        required=True,
    )
    date_to = fields.Date(
        required=True,
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        default=lambda self: self.env.company.timesheet_cost_journal_id,
    )
    auto_post = fields.Boolean(
        string="Auto Post Journal Entry",
        default=True,
    )
    accounting_date = fields.Date(
        default=fields.Date.today,
    )
    project_ids = fields.Many2many(
        comodel_name="project.project",
        relation="hr_timesheet_costing_project_rel",
        column1="costing_id",
        column2="project_id",
        string="Projects",
        help="Leave empty to include all projects.",
    )
    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        relation="hr_timesheet_costing_employee_rel",
        column1="costing_id",
        column2="employee_id",
        string="Employees",
        help="Leave empty to include all employees.",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        readonly=True,
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Journal Entry",
        readonly=True,
    )
    domain_timesheet_ids = fields.Many2many(
        comodel_name="account.analytic.line",
        compute="_compute_timesheet_domain",
    )
    timesheet_ids = fields.Many2many(
        comodel_name="account.analytic.line",
        relation="hr_timesheet_costing_analytic_line_rel",
        column1="costing_id",
        column2="analytic_line_id",
        string="Timesheets",
        copy=False,
    )
    group_by_project = fields.Boolean(
        string="Group by Project",
        default=False,
        help="When enabled, debit lines on the Journal Entry will be "
        "summarised per project instead of one line per timesheet.",
    )
    group_by_employee = fields.Boolean(
        string="Group by Employee",
        default=False,
        help="When enabled, debit lines on the Journal Entry will be "
        "summarised per employee instead of one line per timesheet.",
    )
    amount_total = fields.Monetary(
        string="Total Cost",
        compute="_compute_amount_total",
        currency_field="currency_id",
    )
    can_reset_to_draft = fields.Boolean(
        compute="_compute_can_reset_to_draft",
    )

    @api.depends("state", "move_id", "move_id.state")
    def _compute_can_reset_to_draft(self):
        for rec in self:
            if rec.state in ("confirmed", "cancelled"):
                rec.can_reset_to_draft = True
            elif rec.state == "done":
                rec.can_reset_to_draft = not rec.move_id
            else:
                rec.can_reset_to_draft = False

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(
                    self.env._("Date From must be earlier than or equal to Date To.")
                )

    @api.depends(
        "timesheet_ids",
        "timesheet_ids.unit_amount",
        "timesheet_ids.employee_id.hourly_cost",
    )
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = abs(sum(rec.timesheet_ids.mapped("amount")))

    @api.depends("company_id", "date_from", "date_to", "project_ids", "employee_ids")
    def _compute_timesheet_domain(self):
        for rec in self:
            domain = self._get_timesheet_domain()
            timesheets = self.env["account.analytic.line"].search(domain)
            rec.domain_timesheet_ids = timesheets.ids

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "hr.timesheet.costing"
                )
        return super().create(vals_list)

    def unlink(self):
        blocked = self.filtered(lambda r: r.state in ("confirmed", "done"))
        if blocked:
            raise UserError(
                self.env._(
                    "Cannot delete Timesheet Costing in Confirmed or Done state."
                )
            )
        return super().unlink()

    def _prepare_timesheet_debit_line_vals(self, group, cost_account):
        """One debit line for a group of timesheets (or individual if not grouped)."""
        return {
            "name": group.get("label"),
            "account_id": cost_account.id,
            "debit": group.get("amount"),
            "analytic_distribution": group.get("analytic_distribution") or {},
            "credit": 0.0,
        }

    def _prepare_timesheet_counterpart_line_vals(self, total_credit, suspense_account):
        return {
            "name": self.env._("Suspense - Timesheet Cost"),
            "account_id": suspense_account.id,
            "debit": 0.0,
            "credit": total_credit,
        }

    def _get_timesheet_cost_items(self, ts):
        """Return cost breakdown items for a timesheet line.
        Override in extensions to split cost by type. Each item is a dict::

            {
                "amount": float,        # cost amount for this item
                "label_suffix": str,    # appended to group label
                "type_code": str,       # used in grouping key
            }

        Default returns a single item with the total timesheet amount.
        """
        return [{"amount": abs(ts.amount), "label_suffix": "", "type_code": ""}]

    def _get_grouping_key(self, ts, cost_item=None):
        """Return the dict key used to group timesheets."""
        if self.group_by_project and self.group_by_employee:
            key = (ts.project_id.id, ts.employee_id.id)
        elif self.group_by_project:
            key = ts.project_id.id
        elif self.group_by_employee:
            key = ts.employee_id.id
        else:
            key = ts.id  # no grouping, each ts is its own group
        if cost_item and cost_item.get("type_code"):
            return (key, cost_item["type_code"])
        return key

    def _get_group_label(self, ts, cost_item=None):
        """Return a human-readable label for the group that `ts` belongs to."""
        if self.group_by_project and self.group_by_employee:
            label = f"{ts.project_id.name} / {ts.employee_id.name}"
        elif self.group_by_project:
            label = ts.project_id.name or self.env._("No Project")
        elif self.group_by_employee:
            label = ts.employee_id.name or self.env._("No Employee")
        else:
            label = f"{ts.employee_id.name} - {ts.date} - {ts.name}"
        if cost_item and cost_item.get("label_suffix"):
            return f"{label}{cost_item['label_suffix']}"
        return label

    def _prepare_account_move_lines(self, cost_account, suspense_account):
        """Prepare movelines for the JV.

        Debit lines are grouped according to *group_by_project* /
        *group_by_employee* and further split by cost items (via
        ``_get_timesheet_cost_items``). A single credit (suspense)
        line is appended.
        """
        self.ensure_one()
        # Group timesheets
        groups = {}  # key -> {label, amount, analytic_amounts}
        for ts in self.timesheet_ids:
            for cost_item in self._get_timesheet_cost_items(ts):
                amount = cost_item["amount"]
                if not amount:
                    continue
                key = self._get_grouping_key(ts, cost_item)
                if key not in groups:
                    groups[key] = {
                        "label": self._get_group_label(ts, cost_item),
                        "amount": 0.0,
                        "analytic_amounts": {},
                    }
                groups[key]["amount"] += amount
                analytic_account = ts.project_id.account_id
                if analytic_account:
                    acc_key = str(analytic_account.id)
                    groups[key]["analytic_amounts"][acc_key] = (
                        groups[key]["analytic_amounts"].get(acc_key, 0.0) + amount
                    )

        if not groups:
            raise UserError(self.env._("No amount found in selected timesheet lines."))

        # Compute analytic_distribution (percentage) per group
        for group in groups.values():
            total = group["amount"]
            analytic_amounts = group["analytic_amounts"]
            if total and analytic_amounts:
                group["analytic_distribution"] = {
                    k: round(v / total * 100, 2) for k, v in analytic_amounts.items()
                }
            else:
                group["analytic_distribution"] = {}

        # Debit side
        line_vals = []
        total_credit = 0.0
        for group in groups.values():
            total_credit += group["amount"]
            vals_debit = self._prepare_timesheet_debit_line_vals(group, cost_account)
            line_vals.append(Command.create(vals_debit))

        # Credit side
        vals_credit = self._prepare_timesheet_counterpart_line_vals(
            total_credit, suspense_account
        )
        line_vals.append(Command.create(vals_credit))
        return line_vals

    def _get_timesheet_domain(self):
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("project_id", "!=", False),
            ("employee_id", "!=", False),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("timesheet_costing_id", "=", False),
        ]
        if self.project_ids:
            domain.append(("project_id", "in", self.project_ids.ids))
        if self.employee_ids:
            domain.append(("employee_id", "in", self.employee_ids.ids))
        return domain

    def _action_auto_post(self, move):
        self.ensure_one()
        if self.auto_post:
            move.action_post()
        return move

    def action_get_timesheets(self):
        self.ensure_one()
        domain = self._get_timesheet_domain()
        timesheets = self.env["account.analytic.line"].search(domain)
        return self.write({"timesheet_ids": [Command.set(timesheets.ids)]})

    def action_confirm(self):
        self.ensure_one()
        if not self.timesheet_ids:
            raise UserError(self.env._("Please fetch timesheets before confirming."))
        return self.write({"state": "confirmed"})

    def action_reset_draft(self):
        self.ensure_one()
        if self.state == "done":
            if self.move_id:
                raise UserError(
                    self.env._(
                        "Cannot reset: a Journal Entry is linked. "
                        "Please delete or reverse it in Accounting first."
                    )
                )
            self.timesheet_ids.write({"timesheet_costing_id": False})
            return self.write({"state": "draft"})
        return self.write({"state": "draft"})

    def action_cancel(self):
        self.ensure_one()
        return self.write({"state": "cancelled"})

    def action_create_jv(self):
        self.ensure_one()
        company = self.company_id
        suspense_account = company.timesheet_suspense_account_id
        cost_account = company.timesheet_cost_account_id

        if not suspense_account or not cost_account:
            raise UserError(
                self.env._(
                    "Please configure Cost Account and Suspense Account "
                    "in Accounting Settings."
                )
            )

        line_vals = self._prepare_account_move_lines(cost_account, suspense_account)

        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": self.journal_id.id,
                "date": self.accounting_date,
                "ref": self.name,
                "timesheet_costing_id": self.id,
                "line_ids": line_vals,
            }
        )
        self._action_auto_post(move)

        self.timesheet_ids.write({"timesheet_costing_id": self.id})
        self.write({"move_id": move.id, "state": "done"})

    def action_view_move(self):
        self.ensure_one()
        return {
            "name": self.env._("Journal Entry"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": self.move_id.id,
            "view_mode": "form",
            "target": "current",
        }

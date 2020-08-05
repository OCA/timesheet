# Copyright (C) 2019 Odoo SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ast import literal_eval

from odoo import _, http
from odoo.http import request

from odoo.addons.sale_timesheet.controllers.main import SaleTimesheetController
from odoo.addons.web.controllers.main import clean_action


class SaleTimesheetControllerNew(SaleTimesheetController):
    def _plan_get_stat_button(self, projects):
        stat_buttons = []
        if len(projects) == 1:
            stat_buttons.append(
                {
                    "name": _("Project"),
                    "res_model": "project.project",
                    "res_id": projects.id,
                    "icon": "fa fa-puzzle-piece",
                }
            )
        stat_buttons.append(
            {
                "name": _("Timesheets"),
                "res_model": "account.analytic.line",
                "domain": [("project_id", "in", projects.ids)],
                "icon": "fa fa-calendar",
            }
        )
        stat_buttons.append(
            {
                "name": _("Tasks"),
                "count": sum(projects.mapped("task_count")),
                "res_model": "project.task",
                "domain": [("project_id", "in", projects.ids)],
                "icon": "fa fa-tasks",
            }
        )
        if request.env.user.has_group("sales_team.group_sale_salesman_all_leads"):
            sale_orders = projects.mapped("sale_line_id.order_id") | projects.mapped(
                "tasks.sale_order_id"
            )
            if sale_orders:
                stat_buttons.append(
                    {
                        "name": _("Sales Orders"),
                        "count": len(sale_orders),
                        "res_model": "sale.order",
                        "domain": [("id", "in", sale_orders.ids)],
                        "icon": "fa fa-dollar",
                    }
                )
                invoices = sale_orders.mapped("invoice_ids").filtered(
                    lambda inv: inv.type == "out_invoice"
                )
                if invoices:
                    stat_buttons.append(
                        {
                            "name": _("Invoices"),
                            "count": len(invoices),
                            "res_model": "account.invoice",
                            "domain": [
                                ("id", "in", invoices.ids),
                                ("type", "=", "out_invoice"),
                            ],
                            "icon": "fa fa-pencil-square-o",
                        }
                    )
        if request.env.user.has_group("purchase.group_purchase_user"):
            accounts = projects.mapped("analytic_account_id.id")
            purchase_order_lines = request.env["purchase.order.line"].search(
                [("account_analytic_id", "in", accounts)]
            )
            purchase_orders = purchase_order_lines.mapped("order_id")
            if purchase_orders:
                stat_buttons.append(
                    {
                        "name": _("Purchase Orders"),
                        "count": len(purchase_orders),
                        "icon": "fa fa-shopping-cart",
                        "res_model": "purchase.order",
                        "domain": [("id", "in", purchase_orders.ids)],
                    }
                )
            account_invoice_lines = request.env["account.invoice.line"].search(
                [
                    ("account_analytic_id", "in", accounts),
                    ("invoice_id.type", "in", ["in_invoice", "in_refund"]),
                ]
            )
            account_invoices = account_invoice_lines.mapped("invoice_id")
            if account_invoices:
                stat_buttons.append(
                    {
                        "name": _("Vendor Bills"),
                        "count": len(account_invoices),
                        "icon": "fa fa-pencil-square-o",
                        "res_model": "account.invoice",
                        "domain": [("id", "in", account_invoices.ids)],
                    }
                )
        return stat_buttons

    @http.route("/timesheet/plan/action", type="json", auth="user")
    def plan_stat_button(
        self, domain=[], res_model="account.analytic.line", res_id=False
    ):
        action = {
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "tree,form",
            "view_type": "list",
            "domain": domain,
        }
        if res_model == "project.project":
            view_form_id = request.env.ref("project.edit_project").id
            action = {
                "name": _("Project"),
                "type": "ir.actions.act_window",
                "res_model": res_model,
                "view_mode": "form",
                "view_type": "form",
                "views": [[view_form_id, "form"]],
                "res_id": res_id,
            }
        elif res_model == "account.analytic.line":
            ts_view_tree_id = request.env.ref(
                "hr_timesheet.hr_timesheet_line_tree").id
            ts_view_form_id = request.env.ref(
                "hr_timesheet.hr_timesheet_line_form").id
            action = {
                "name": _("Timesheets"),
                "type": "ir.actions.act_window",
                "res_model": res_model,
                "view_mode": "tree,form",
                "view_type": "form",
                "views": [[ts_view_tree_id, "list"], [ts_view_form_id, "form"]],
                "domain": domain,
            }
        elif res_model == "project.task":
            action = request.env.ref("project.action_view_task").read()[0]
            action.update(
                {
                    "name": _("Tasks"),
                    "domain": domain,
                    # erase original context to avoid default filter
                    "context": dict(request.env.context),
                }
            )
            # if only one project, add it in the context as default value
            tasks = request.env["project.task"].sudo().search(
                literal_eval(domain))
            if len(tasks.mapped("project_id")) == 1:
                action["context"]["default_project_id"] = tasks.mapped("project_id")[
                    0
                ].id
        elif res_model == "sale.order":
            action = clean_action(request.env.ref(
                "sale.action_orders").read()[0])
            action["domain"] = domain
            # No CRUD operation when coming from overview
            action["context"] = {"create": False,
                                 "edit": False, "delete": False}
        elif res_model == "account.invoice":
            action = clean_action(
                request.env.ref("account.action_invoice_tree1").read()[0]
            )
            action["domain"] = domain
            # only edition of invoice from overview
            action["context"] = {"create": False, "delete": False}
        elif res_model == "purchase.order":
            action = clean_action(
                request.env.ref("purchase.purchase_form_action").read()[0]
            )
            action["domain"] = domain
            action["context"] = {"create": False, "delete": False}
        return action

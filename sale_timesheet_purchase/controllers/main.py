# Copyright (C) 2019 Odoo S.A.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, http

from odoo.addons.sale_timesheet.controllers.main import SaleTimesheetController
from odoo.addons.web.controllers.main import clean_action

from odoo.http import request


class SaleTimesheetControllerNew(SaleTimesheetController):

    def _plan_get_stat_button(self, projects):
        res = super(SaleTimesheetControllerNew,
                    self)._plan_get_stat_button(projects)
        if request.env.user.has_group("purchase.group_purchase_user"):
            accounts = projects.mapped("analytic_account_id.id")
            purchase_order_lines = request.env["purchase.order.line"].search(
                [("account_analytic_id", "in", accounts)]
            )
            purchase_orders = purchase_order_lines.mapped("order_id")
            if purchase_orders:
                res.append(
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
                res.append(
                    {
                        "name": _("Vendor Bills"),
                        "count": len(account_invoices),
                        "icon": "fa fa-pencil-square-o",
                        "res_model": "account.invoice",
                        "domain": [("id", "in", account_invoices.ids)],
                    }
                )
        return res

    @http.route("/timesheet/plan/action", type="json", auth="user")
    def plan_stat_button(
            self, domain=None, res_model="account.analytic.line",
            res_id=False):
        if domain is None:
            domain = []
        res = super(SaleTimesheetControllerNew,
                    self).plan_stat_button(domain=domain,
                                           res_model=res_model,
                                           res_id=res_id)
        if res_model == "purchase.order":
            res = clean_action(
                request.env.ref("purchase.purchase_form_action").read()[0]
            )
            res["domain"] = domain
            res["context"] = {"create": False, "delete": False}
        return res

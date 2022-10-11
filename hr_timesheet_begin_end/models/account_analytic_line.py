# Copyright 2015 Camptocamp SA - Guewen Baconnier
# Copyright 2017 Tecnativa, S.L. - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import timedelta

from odoo import _, api, exceptions, fields, models
from odoo.tools.float_utils import float_compare


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    _order = "date desc, time_start desc, id desc"

    time_start = fields.Float(string="Begin Hour")
    time_stop = fields.Float(string="End Hour")

    @api.constrains("time_start", "time_stop", "unit_amount")
    def _check_time_start_stop(self):
        for line in self:
            value_to_html = self.env["ir.qweb.field.float_time"].value_to_html
            start = timedelta(hours=line.time_start)
            stop = timedelta(hours=line.time_stop)
            if stop < start:
                raise exceptions.ValidationError(
                    _("The beginning hour (%s) must " "precede the ending hour (%s).")
                    % (
                        value_to_html(line.time_start, None),
                        value_to_html(line.time_stop, None),
                    )
                )
            hours = (stop - start).seconds / 3600
            rounding = self.env.ref("uom.product_uom_hour").rounding
            if hours and float_compare(
                hours, line.unit_amount, precision_rounding=rounding
            ):
                raise exceptions.ValidationError(
                    _(
                        "The duration (%s) must be equal to the difference "
                        "between the hours (%s)."
                    )
                    % (
                        value_to_html(line.unit_amount, None),
                        value_to_html(hours, None),
                    )
                )
            # check if lines overlap
            others = self.search(
                [
                    ("id", "!=", line.id),
                    ("user_id", "=", line.user_id.id),
                    ("date", "=", line.date),
                    ("time_start", "<", line.time_stop),
                    ("time_stop", ">", line.time_start),
                ]
            )
            if others:
                message = _("Lines can't overlap:\n")
                message += "\n".join(
                    [
                        "%s - %s"
                        % (
                            value_to_html(other.time_start, None),
                            value_to_html(other.time_stop, None),
                        )
                        for other in (line + others).sorted(lambda l: l.time_start)
                    ]
                )
                raise exceptions.ValidationError(message)

    @api.onchange("time_start", "time_stop")
    def onchange_hours_start_stop(self):
        start = timedelta(hours=self.time_start)
        stop = timedelta(hours=self.time_stop)
        if stop < start:
            return
        self.unit_amount = (stop - start).seconds / 3600

    def merge_timesheets(self):  # pragma: no cover
        """This method is needed in case hr_timesheet_sheet is installed"""
        lines = self.filtered(lambda l: not l.time_start and not l.time_stop)
        if lines:
            return super(AccountAnalyticLine, lines).merge_timesheets()
        return self[0]

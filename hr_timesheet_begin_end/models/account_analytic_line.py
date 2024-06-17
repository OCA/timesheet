# Copyright 2015 Camptocamp SA - Guewen Baconnier
# Copyright 2017 Tecnativa, S.L. - Luis M. Ontalba
# Copyright 2024 Coop IT Easy SC - Carmen Bianca BAKKER
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import timedelta

from odoo import _, api, exceptions, fields, models
from odoo.tools.float_utils import float_compare


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    _order = "date desc, time_start desc, id desc"

    time_start = fields.Float(string="Begin Hour")
    time_stop = fields.Float(string="End Hour")

    # Override to be a computed field.
    unit_amount = fields.Float(
        compute="_compute_unit_amount",
        store=True,
        readonly=False,
        # This default is a workaround for a bizarre situation: if a line is
        # created with a time range but WITHOUT defining unit_amount, then you
        # would expect unit_amount to be computed from the range. But this never
        # happens, and it is instead set to default value 0. Subsequently the
        # constraint _validate_unit_amount_equal_to_time_diff kicks in and
        # raises an exception.
        #
        # By setting the default to None, the computation is correctly
        # triggered. If nothing is computed, None falls back to 0.
        default=None,
    )

    @api.depends("time_start", "time_stop", "project_id")
    def _compute_unit_amount(self):
        # Do not compute/adjust the unit_amount of non-timesheets.
        lines = self.filtered(lambda line: line.project_id)
        for line in lines:
            line.unit_amount = line.unit_amount_from_start_stop()

    def _validate_start_before_stop(self):
        value_to_html = self.env["ir.qweb.field.float_time"].value_to_html
        for line in self:
            if line.time_stop < line.time_start:
                raise exceptions.ValidationError(
                    _(
                        "The beginning hour (%(html_start)s) must "
                        "precede the ending hour (%(html_stop)s)."
                    )
                    % {
                        "html_start": value_to_html(line.time_start, None),
                        "html_stop": value_to_html(line.time_stop, None),
                    }
                )

    def _validate_unit_amount_equal_to_time_diff(self):
        value_to_html = self.env["ir.qweb.field.float_time"].value_to_html
        for line in self:
            hours = line.unit_amount_from_start_stop()
            rounding = self.env.ref("uom.product_uom_hour").rounding
            if hours and float_compare(
                hours, line.unit_amount, precision_rounding=rounding
            ):
                raise exceptions.ValidationError(
                    _(
                        "The duration (%(html_unit_amount)s) must be equal to the difference "
                        "between the hours (%(html_hours)s)."
                    )
                    % {
                        "html_unit_amount": value_to_html(line.unit_amount, None),
                        "html_hours": value_to_html(hours, None),
                    }
                )

    def _overlap_domain(self):
        self.ensure_one()
        return [
            ("id", "!=", self.id),
            ("employee_id", "=", self.employee_id.id),
            ("date", "=", self.date),
            ("time_start", "<", self.time_stop),
            ("time_stop", ">", self.time_start),
        ]

    def _validate_no_overlap(self):
        value_to_html = self.env["ir.qweb.field.float_time"].value_to_html
        for line in self:
            others = self.search(line._overlap_domain())
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

    @api.constrains("time_start", "time_stop", "unit_amount")
    def _check_time_start_stop(self):
        lines = self.filtered(lambda line: line.project_id)
        lines._validate_start_before_stop()
        lines._validate_unit_amount_equal_to_time_diff()
        lines._validate_no_overlap()

    @api.model
    def _hours_from_start_stop(self, time_start, time_stop):
        start = timedelta(hours=time_start)
        stop = timedelta(hours=time_stop)
        if stop < start:
            # Invalid case, but return something sensible.
            return 0
        return (stop - start).seconds / 3600

    def unit_amount_from_start_stop(self):
        self.ensure_one()
        # Don't handle non-timesheet lines.
        if not self.project_id:
            return 0
        return self._hours_from_start_stop(self.time_start, self.time_stop)

    def merge_timesheets(self):  # pragma: no cover
        """This method is needed in case hr_timesheet_sheet is installed"""
        lines = self.filtered(lambda l: not l.time_start and not l.time_stop)
        if lines:
            return super(AccountAnalyticLine, lines).merge_timesheets()
        return self[0]

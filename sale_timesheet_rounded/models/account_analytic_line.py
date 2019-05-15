# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import api, fields, models
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    unit_amount_rounded = fields.Float(
        string="Quantity rounded",
        # Important: do NOT pass a default here.
        # Passing a default will break computation at create
        # since we want to allow to pass specific values
        # we must check if the value is there or not.
        # If you set a default, you are going to get it as value at create
        # and the computation won't happen.
        # default=0.0,
        copy=False,
    )

    @api.model_cr_context
    def _init_column(self, column_name):
        """ Initialize the value of the given column for existing rows.
            Overridden here because we need to have different default values
            for unit_amount_rounded for every analytic line.
        """
        if column_name != 'unit_amount_rounded':
            super()._init_column(column_name)
        else:
            _logger.info('Initializing column `unit_amount_rounded` with the '
                         'value of `unit_amount`')
            query = 'UPDATE "%s" SET unit_amount_rounded = unit_amount;' % \
                    self._table
            self.env.cr.execute(query)

    @api.onchange('unit_amount')
    def _onchange_unit_amount(self):
        self.unit_amount_rounded = self.with_context(
            force_compute=1)._calc_unit_amount_rounded()

    def _calc_unit_amount_rounded(self):
        self.ensure_one()
        force_compute = self.env.context.get('force_compute')
        # TODO: do we still need this?
        self = self.with_context(timesheet_rounding=True)
        project_rounding = (
            self.project_id and
            self.project_id.timesheet_rounding_method != 'NO'
        )
        already_set = self.unit_amount_rounded and not force_compute

        if project_rounding and not already_set:
            return self._calc_rounded_amount(
                self.project_id.timesheet_rounding_unit,
                self.project_id.timesheet_rounding_method,
                self.project_id.timesheet_rounding_factor,
                self.unit_amount,
            )
        else:
            return self.unit_amount

    @staticmethod
    def _calc_rounded_amount(rounding_unit, rounding_method, factor, amount):
        factor = factor / 100.0
        if rounding_unit:
            unit_amount_rounded = float_round(
                amount * factor,
                precision_rounding=rounding_unit,
                rounding_method=rounding_method
            )
        else:
            unit_amount_rounded = amount * factor
        return unit_amount_rounded

    def _timesheet_postprocess(self, values):
        # Add no rounding key to avoid triggering
        # _update_unit_amount_rounded on the write from
        # _timesheet_postprocess to update the amount
        self = self.with_context(_no_rounding=True)
        return super()._timesheet_postprocess(values)

    ####################################################
    # ORM Overrides
    ####################################################

    @api.model
    def create(self, values):
        res = super().create(values)
        # TODO improve me
        if values.get('unit_amount_rounded') is None:
            res.write({'unit_amount_rounded': res._calc_unit_amount_rounded()})
        return res

    @api.multi
    def write(self, values):
        res = super().write(values)
        no_rounding = self.env.context.get('_no_rounding')
        # TODO improve me
        if (
            not no_rounding and values.get('unit_amount_rounded') is None
            and 'unit_amount' in values
        ):
            for line in self:
                super(AccountAnalyticLine, line).write({
                    'unit_amount_rounded': line._calc_unit_amount_rounded()
                })
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0,
                   limit=None, orderby=False, lazy=True):
        """Replace the value of unit_amount by unit_amount_rounded.

        When context key `timesheet_rounding` is True
        we change the value of unit_amount with the rounded one.
        This affects `sale_order_line._compute_delivered_quantity`
        which in turns compute the delivered qty on SO line.
        """
        ctx_ts_rounded = self.env.context.get('timesheet_rounding')
        fields_local = fields.copy() if fields else []
        if ctx_ts_rounded and 'unit_amount_rounded' not in fields_local:
            # To add the unit_amount_rounded value on read_group
            fields_local.append('unit_amount_rounded')
        res = super().read_group(
            domain, fields_local, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy
        )
        if ctx_ts_rounded:
            # To set the unit_amount_rounded value instead of unit_amount
            for rec in res:
                rec['unit_amount'] = rec['unit_amount_rounded']
        return res

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        """Replace the value of unit_amount by unit_amount_rounded.

        When context key `timesheet_rounding` is True
        we change the value of unit_amount with the rounded one.
        This affects `account_anaytic_line._sale_determine_order_line`.
        """
        ctx_ts_rounded = self.env.context.get('timesheet_rounding')
        fields_local = fields.copy() if fields else []
        read_unit_amount = 'unit_amount' in fields_local or not fields_local
        if ctx_ts_rounded and read_unit_amount and fields_local:
            if 'unit_amount_rounded' not in fields_local:
                # To add the unit_amount_rounded value on read
                fields_local.append('unit_amount_rounded')
        res = super().read(fields_local, load=load)
        if ctx_ts_rounded and read_unit_amount:
            # To set the unit_amount_rounded value instead of unit_amount
            for rec in res:
                rec['unit_amount'] = rec['unit_amount_rounded']
        return res

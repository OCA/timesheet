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
        default=0.0,
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
        self.with_context(force_compute=1)._update_unit_amount_rounded()

    def _update_unit_amount_rounded(self):
        force_compute = self.env.context.get('force_compute')
        if self.env.context.get('grid_adjust'):
            # TODO: do we need this?
            # support timesheet_grid from EE version
            # force_compute if the timesheet is change in the grid view
            force_compute = True
        for rec in self.with_context(
            timesheet_rounding=True,
            # avoid recursion when writing from this method
            update_unit_amount_rounded=True,
        ):
            if not rec.project_id:
                # no project: do nothing
                continue
            if rec.product_id and rec.product_id.expense_policy != 'no':
                # expense line: do nothing
                continue
            if rec.unit_amount_rounded and not force_compute:
                # already set, no forcing: do nothing
                continue
            if rec.project_id.timesheet_rounding_method == 'NO':
                # No rounding to apply: copy the value
                rec.unit_amount_rounded = rec.unit_amount
            else:
                rec.unit_amount_rounded = self._calc_rounded_amount(
                    rec.project_id.timesheet_rounding_unit,
                    rec.project_id.timesheet_rounding_method,
                    rec.project_id.timesheet_rounding_factor,
                    rec.unit_amount,
                )

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
        # TODO: replace this w/ an override of `_timesheet_postprocess_values`
        # where we update the values passed then to write.
        # This way we could get rid of `_update_unit_amount_rounded`
        # and the consequent call to write,
        # event though it might be still useful for the onchange.
        # NOTE: we don't have to replace `amount` value.
        if (
            not self.env.context.get('update_unit_amount_rounded')
            and not self.env.context.get('_no_rounding')
        ):
            if values.get('unit_amount_rounded') is None:
                self._update_unit_amount_rounded()
        # Add no rounding key to avoid triggering
        # _update_unit_amount_rounded on the write from
        # _timesheet_postprocess to update the amount
        return super(
            AccountAnalyticLine, self.with_context(_no_rounding=True)
        )._timesheet_postprocess(values)

    ####################################################
    # ORM Overrides
    ####################################################
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
        if ctx_ts_rounded:
            # To add the unit_amount_rounded value on read_group
            fields_local.append('unit_amount_rounded')
        res = super().read_group(
            domain, fields_local, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy
        )
        if ctx_ts_rounded:
            # To set the unit_amount_rounded value insted of unit_amount
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
            if 'project_id' not in fields_local:
                fields_local.append('project_id')
            if 'product_id' not in fields_local:
                fields_local.append('product_id')
        res = super().read(fields_local, load=load)
        if ctx_ts_rounded and read_unit_amount:
            # To set the unit_amount_rounded value insted of unit_amount
            for rec in res:
                product_model = self.env['product.product']
                is_expense = False
                product_rec = rec.get('product_id')
                if product_rec:
                    product_id = product_rec
                    if load == '_classic_read':
                        # the classic_read return one tuple like : (id, name)
                        product_id = product_rec[0]
                    # TODO: would be better to browse them all at once
                    product = product_model.browse(product_id)
                    is_expense = product.product_tmpl_id.expense_policy != 'no'
                rounded = 'unit_amount_rounded' in rec
                # Check if the product is a not a expenses
                # and corresponding to one project and unit_amount_rounded is
                # present
                if rec.get('project_id') and not is_expense and rounded:
                    rec['unit_amount'] = rec['unit_amount_rounded']
        return res

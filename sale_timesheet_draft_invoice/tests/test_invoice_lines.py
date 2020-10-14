# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCommonMixin


class TestInvoice(TestCommonMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.context = {
            "active_model": 'sale.order',
            "active_ids": [cls.sale_order.id],
            "active_id": cls.sale_order.id,
            'open_invoices': True,
        }

    def get_invoice(self):
        wizard = self.env['sale.advance.payment.inv'].create(
            {'advance_payment_method': 'delivered'}
        )
        action_invoice = wizard.with_context(self.context).create_invoices()
        invoice_id = action_invoice['res_id']
        invoice = self.env['account.invoice'].browse(invoice_id)
        return invoice

    def test_invoice_timesheet_lines(self):
        invoice = self.get_invoice()
        self.assertEqual(invoice.state, 'draft')
        self.assertEqual(len(invoice.timesheet_ids), 3)
        self.assertEqual(invoice.timesheet_count, 3)
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertEqual(sum(invoice.invoice_line_ids.mapped('quantity')), 3)
        invoice.action_invoice_cancel()
        self.assertEqual(len(invoice.timesheet_ids), 0)
        self.assertEqual(invoice.timesheet_count, 0)
        self.assertEqual(invoice.state, 'cancel')
        invoice.action_invoice_draft()

        # lines relinked to invoice
        self.assertEqual(len(invoice.timesheet_ids), 3)
        self.assertEqual(invoice.timesheet_count, 3)
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertEqual(sum(invoice.invoice_line_ids.mapped('quantity')), 3)
        invoice.action_invoice_cancel()
        self.create_analytic_line(unit_amount=1, date='2019-05-11')
        invoice.action_invoice_draft()
        self.assertEqual(len(invoice.timesheet_ids), 4)
        self.assertEqual(invoice.timesheet_count, 4)
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertEqual(sum(invoice.invoice_line_ids.mapped('quantity')), 4)

        # new ts line linked to new invoice
        self.create_analytic_line(unit_amount=1, date='2019-05-12')
        self.get_invoice()
        new_invoice = self.sale_order.invoice_ids[0]
        self.assertEqual(len(new_invoice.timesheet_ids), 1)
        self.assertEqual(new_invoice.timesheet_count, 1)
        self.assertEqual(len(new_invoice.invoice_line_ids), 1)
        self.assertEqual(
            sum(new_invoice.invoice_line_ids.mapped('quantity')), 1
        )

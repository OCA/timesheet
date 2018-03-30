# -*- coding: utf-8 -*-
# © 2011 Domsense srl (<http://www.domsense.com>)
# © 2011-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2016 OpenSynergy Indonesia (<https://opensynergy-indonesia.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta


class TestHrContract(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestHrContract, self).setUp(*args, **kwargs)
        self.obj_contract = self.env["hr.contract"]
        self.employee = self.env.ref("hr.employee")
        self.working_hours = self.env.ref("resource.timesheet_group1")
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=365)

        self.contract_data = {
            "name": "Contract for administrator",
            "employee_id": self.employee.id,
            "working_hours": self.working_hours.id,
            "date_start": self.start_date.strftime("%Y-%m-%d"),
            "wage": 1500.00,
            "date_end": self.end_date.strftime("%Y-%m-%d"),
        }
        self.contract = self.obj_contract.create(self.contract_data)

        return result

    def test_copy_contract_with_end_date(self):
        # new_contract_start_date = self.end_date + timedelta(days=1)
        self.contract.copy(default=None)

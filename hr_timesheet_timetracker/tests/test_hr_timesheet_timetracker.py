# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2 import IntegrityError
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tools.misc import mute_logger


class TestHrTimesheetTimetracker(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.now = fields.Datetime.now()
        self.uom_hour = self.env.ref('uom.product_uom_hour')
        self.Project = self.env['project.project']
        self.Task = self.env['project.task']
        self.HrEmployee = self.env['hr.employee']
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.User = self.env['res.users']

    def test_editing_while_running_restricted(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
        })

        entry._onchange_employee_id()
        self.assertEqual(entry.can_use_timetracker, True)

        entry._compute_can_use_timetracker()
        self.assertEqual(entry.can_use_timetracker, True)

        entry.timetracker_started_at = self.now - relativedelta(hours=1)

        self.assertEqual(entry.is_timetracker_running, True)
        with self.assertRaises(ValidationError):
            entry.timetracker_started_at = self.now
        with self.assertRaises(ValidationError):
            entry.unit_amount = 1

    def test_running_timer_detection(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
        })

        entry.timetracker_started_at = self.now - relativedelta(hours=1)
        self.assertEqual(entry.is_timetracker_running, True)
        entry.timetracker_stopped_at = self.now
        self.assertEqual(entry.is_timetracker_running, False)

    def test_no_stop_before_start_on_write(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
        })

        entry.timetracker_started_at = self.now

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            entry.timetracker_stopped_at = self.now - relativedelta(hours=1)

    def test_no_stop_without_start_on_write(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            entry.timetracker_stopped_at = self.now - relativedelta(hours=1)

    def test_stopped_at_adjustment_by_unit_amount(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        t = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': t - relativedelta(hours=2),
            'timetracker_stopped_at': t,
        })

        entry.unit_amount = 1.0
        self.assertEqual(
            entry.timetracker_stopped_at,
            t - relativedelta(hours=1)
        )

    def test_editing_started_at(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        self.assertEqual(entry.unit_amount, 2.0)
        entry.timetracker_started_at = self.now - relativedelta(hours=1)
        self.assertEqual(entry.unit_amount, 1.0)

    def test_editing_stopped_at(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        self.assertEqual(entry.unit_amount, 2.0)
        entry.timetracker_stopped_at = self.now - relativedelta(hours=1)
        self.assertEqual(entry.unit_amount, 1.0)

    def test_no_stop_without_start_on_create(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.AccountAnalyticLine.create({
                'project_id': project.id,
                'name': 'Time Entry',
                'employee_id': employee.id,
                'timetracker_stopped_at': self.now,
            })

    def test_no_stop_before_start_on_create(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.AccountAnalyticLine.create({
                'project_id': project.id,
                'name': 'Time Entry',
                'employee_id': employee.id,
                'timetracker_started_at': self.now,
                'timetracker_stopped_at': self.now - relativedelta(hours=1),
            })

    def test_no_stop_before_start_with_amount_on_create(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.AccountAnalyticLine.create({
                'project_id': project.id,
                'name': 'Time Entry',
                'employee_id': employee.id,
                'timetracker_started_at': self.now,
                'timetracker_stopped_at': self.now - relativedelta(hours=1),
                'unit_amount': 1.0,
            })

    def test_single_running_timetracker_per_employee_on_create(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        self.AccountAnalyticLine.create([{
            'project_id': project.id,
            'name': 'Time Entry 1',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=1),
            'timetracker_stopped_at': self.now,
        }, {
            'project_id': project.id,
            'name': 'Time Entry 2',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        }])

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.AccountAnalyticLine.create([{
                'project_id': project.id,
                'name': 'Time Entry 3',
                'employee_id': employee.id,
                'timetracker_started_at': self.now - relativedelta(hours=1),
            }, {
                'project_id': project.id,
                'name': 'Time Entry 4',
                'employee_id': employee.id,
                'timetracker_started_at': self.now - relativedelta(hours=2),
            }])

    def test_single_running_timetracker_per_employee_on_create_2(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        self.AccountAnalyticLine.create([{
            'project_id': project.id,
            'name': 'Time Entry 1',
            'employee_id': employee.id,
            'unit_amount': 1,
        }, {
            'project_id': project.id,
            'name': 'Time Entry 2',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        }])

    def test_get_currently_timetracked(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry_1 = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry 1',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
        })

        entry_2 = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry 2',
            'employee_id': employee.id,
        })

        currently_timetracked_default = (
            self.AccountAnalyticLine.get_currently_timetracked()
        )
        self.assertIn(entry_1, currently_timetracked_default)
        self.assertNotIn(entry_2, currently_timetracked_default)

        currently_timetracked_by_user = (
            self.AccountAnalyticLine.get_currently_timetracked(
                self.env.user
            )
        )
        self.assertIn(entry_1, currently_timetracked_by_user)
        self.assertNotIn(entry_2, currently_timetracked_by_user)

        currently_timetracked_by_users = (
            self.AccountAnalyticLine.get_currently_timetracked(
                self.User.browse()
            )
        )
        self.assertIn(entry_1, currently_timetracked_by_users)
        self.assertNotIn(entry_2, currently_timetracked_by_users)

        entry_2.action_timetracker()

        self.assertEqual(entry_1.is_timetracker_running, False)
        self.assertEqual(entry_2.is_timetracker_running, True)

        currently_timetracked = (
            self.AccountAnalyticLine.get_currently_timetracked()
        )
        self.assertEquals(len(currently_timetracked), 1)
        self.assertEquals(currently_timetracked.project_id, entry_2.project_id)
        self.assertEquals(currently_timetracked.name, entry_2.name)
        self.assertEquals(currently_timetracked.timetracker_stopped_at, False)

        entry_2.toggle_timetracker()
        self.assertEqual(entry_1.is_timetracker_running, False)
        self.assertEqual(entry_2.is_timetracker_running, False)

    def test_no_date_modifition_on_timetracked(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
        })

        with self.assertRaises(ValidationError):
            entry.date = None

        entry.timetracker_stopped_at = self.now

        with self.assertRaises(ValidationError):
            entry.date = None

    def test_rounding_exact_time(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': (
                self.now - relativedelta(hours=2)
            ).replace(
                minute=0,
                second=0,
                microsecond=0,
            ),
        })
        entry.timetracker_stopped_at = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )

        self.assertEqual(entry.unit_amount, 2.0)

    def test_rounding_inexact_time(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': self.now.replace(
                minute=0,
                second=0,
                microsecond=0,
            ),
        })
        entry.timetracker_stopped_at = self.now.replace(
            minute=0,
            second=1,
            microsecond=0,
        )

        self.assertEqual(entry.unit_amount, 0.01)

    def test_rounding_inexact_time_2(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': (
                self.now - relativedelta(hours=2)
            ).replace(
                minute=0,
                second=1,
                microsecond=0,
            ),
        })
        entry.timetracker_stopped_at = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        ) - relativedelta(seconds=1)

        self.assertEqual(entry.unit_amount, 2.0)

    def test_rounding_inexact_time_3(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': (
                self.now - relativedelta(hours=2)
            ).replace(
                minute=0,
                second=0,
                microsecond=0,
            ) - relativedelta(seconds=1),
        })
        entry.timetracker_stopped_at = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        ) + relativedelta(seconds=1)

        self.assertEqual(entry.unit_amount, 2.02)

    def test_rounding_reset_duration(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': (
                self.now - relativedelta(hours=2)
            ).replace(
                minute=0,
                second=0,
                microsecond=0,
            ) - relativedelta(seconds=1),
        })
        entry.timetracker_stopped_at = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        ) + relativedelta(seconds=1)

        entry.reset_timetracked_duration()
        self.assertEqual(entry.unit_amount, 2.02)

    def test_transform_timetracked_to_regular(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        self.assertTrue(entry.is_timetracked)
        entry.write({
            'timetracker_started_at': None,
            'timetracker_stopped_at': None,
            'unit_amount': 1.0,
        })
        self.assertFalse(entry.is_timetracked)
        self.assertEqual(entry.unit_amount, 1.0)

    def test_transform_timetracked_to_regular_date_editable(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        entry.write({
            'timetracker_started_at': None,
            'timetracker_stopped_at': None,
            'date': self.now.date(),
        })

    def test_stopped_at_and_unit_amount_same_editable(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        entry.write({
            'unit_amount': 1,
            'timetracker_stopped_at': self.now - relativedelta(hours=1),
        })

    def test_stopped_at_and_unit_amount_different_editable(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        t = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': t - relativedelta(hours=4),
            'timetracker_stopped_at': t,
        })
        entry.write({
            'unit_amount': 2,
            'timetracker_stopped_at': t,
        })

        self.assertEqual(entry.unit_amount, 4.0)

    def test_rounding_halfup_halfup(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
            'timetracker_started_at_rounding': 'HALF-UP',
            'timetracker_stopped_at_rounding': 'HALF-UP',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': self.now.replace(minute=2, second=30),
            'timetracker_stopped_at': self.now.replace(minute=2, second=30),
        })

        self.assertEqual(entry.unit_amount, 0.0)

    def test_rounding_up_down(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
            'timetracker_started_at_rounding': 'UP',
            'timetracker_stopped_at_rounding': 'DOWN',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': self.now.replace(
                minute=0,
                second=0,
                microsecond=1000,
            ),
            'timetracker_stopped_at': self.now.replace(
                minute=0,
                second=0,
                microsecond=2000,
            ),
        })

        self.assertEqual(entry.unit_amount, 0.0)

    def test_rounding_down_up(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
            'timetracker_started_at_rounding': 'DOWN',
            'timetracker_stopped_at_rounding': 'UP',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        t = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': t - relativedelta(hours=4),
            'timetracker_stopped_at': t,
        })
        entry.write({
            'unit_amount': 1,
            'timetracker_stopped_at': t - relativedelta(hours=2),
        })

        self.assertEqual(entry.unit_amount, 2.0)

    def test_rounding_precision(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        t = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': t,
            'timetracker_stopped_at': t + relativedelta(hours=4),
        })

        base_unit_amount = entry.unit_amount
        half_of_atom = entry.product_uom_id.rounding / 2
        entry.write({
            'unit_amount': base_unit_amount + half_of_atom,
        })
        self.assertEqual(
            entry.unit_amount,
            base_unit_amount + entry.product_uom_id.rounding
        )

    def test_rounding_precision_2(self):
        project = self.Project.create({
            'name': 'Project',
            'timetracker_rounding_enabled': True,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'timetracker_started_at': self.now.replace(
                hour=19,
                minute=53,
                second=22,
                microsecond=0,
            ),
        })
        entry.product_uom_id = self.uom_hour.copy({
            'name': 'Hour',
            'rounding': 0.1,
        })

        entry.timetracker_stopped_at = self.now.replace(
            hour=20,
            minute=11,
            second=22,
            microsecond=0,
        )
        self.assertEqual(entry.unit_amount, 0.4)

        entry.write({
            'unit_amount': 0.283,
        })
        self.assertEqual(entry.unit_amount, 0.3)

    def test_tracking_via_task(self):
        project = self.Project.create({
            'name': 'Project',
        })
        task = self.Task.create({
            'name': 'Task',
            'project_id': project.id,
            'user_id': self.env.user.id,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'task_id': task.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
        })
        task._compute_is_timetracker_running()
        self.assertEqual(task.is_timetracker_running, False)

        entry.action_timetracker()
        task._compute_is_timetracker_running()
        self.assertEqual(task.is_timetracker_running, True)

        task.action_stop_timetracker()
        task._compute_is_timetracker_running()
        self.assertEqual(task.is_timetracker_running, False)
        self.assertEqual(entry.is_timetracker_running, False)

    def test_tracking_via_task_2(self):
        project = self.Project.create({
            'name': 'Project',
        })
        task_1 = self.Task.create({
            'name': 'Task 1',
            'project_id': project.id,
            'user_id': self.env.user.id,
        })
        task_2 = self.Task.create({
            'name': 'Task 2',
            'project_id': project.id,
            'user_id': self.env.user.id,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })

        entry = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'task_id': task_1.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
        })

        task_1._compute_can_use_timetracker()
        self.assertEqual(task_1.can_use_timetracker, True)

        task_1._compute_is_timetracker_running()
        self.assertEqual(task_1.is_timetracker_running, False)

        entry.action_timetracker()
        task_1._compute_is_timetracker_running()
        self.assertEqual(task_1.is_timetracker_running, True)

        task_2.action_start_timetracker()
        task_1._compute_is_timetracker_running()
        self.assertEqual(task_1.is_timetracker_running, False)
        self.assertEqual(entry.is_timetracker_running, False)

    def test_check_project_move(self):
        project_a = self.Project.create({
            'name': 'Project A',
        })
        project_b = self.Project.create({
            'name': 'Project B',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.env.user.id,
        })
        entry_1 = self.AccountAnalyticLine.create({
            'project_id': project_a.id,
            'name': 'Time Entry 1',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })
        entry_2 = self.AccountAnalyticLine.create({
            'project_id': project_a.id,
            'name': 'Time Entry 2',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=1),
            'timetracker_stopped_at': self.now,
        })
        entry_3 = self.AccountAnalyticLine.create({
            'project_id': project_a.id,
            'name': 'Time Entry 3',
            'employee_id': employee.id,
            'unit_amount': 30.0,
        })

        self.assertAlmostEqual(entry_1.unit_amount, 2.0, places=1)
        self.assertAlmostEqual(entry_2.unit_amount, 1.0, places=1)
        (entry_1 | entry_2 | entry_3).write({
            'project_id': project_b.id,
        })
        self.assertAlmostEqual(entry_1.unit_amount, 2.0, places=1)
        self.assertAlmostEqual(entry_2.unit_amount, 1.0, places=1)
        self.assertEqual(entry_3.unit_amount, 30.0)

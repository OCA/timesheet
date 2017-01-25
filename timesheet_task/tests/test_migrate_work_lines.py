# -*- coding: utf-8 -*-
# Copyright 2017 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import TransactionCase


class TestMigrateWorkLines(TransactionCase):

    def setUp(self):
        super(TestMigrateWorkLines, self).setUp()
        # Models to use
        self.TaskWork = self.env['project.task.work']
        self.TSLine = self.env['hr.analytic.timesheet']
        # Test data
        self.task = self.env.ref('project.project_task_13')
        self.task_work = self.TaskWork.create({
            'user_id': self.env.ref('base.user_root').id,
            'date': '2017-01-16 08:30:00',
            'hours': 1.5,
            'name': 'Work to migrate to timesheet',
            'task_id': self.task.id
            })

    def test_10_timesheet_line_created(self):
        """
        When I create a Task Work line,
        a corresponding Timesheet line should also be created,
        and the time should be preserved.
        The purpose is to be able to keep date and time information
        on Timesheet Lines,
        """
        self.assertEqual(
            self.task_work.hr_analytic_timesheet_id.work_date,
            '2017-01-16 08:30:00',
            "Original work line time is preserved in the work_date field")

    def test_20_timesheet_line_migrated(self):
        """
        When I run the Task Work to Timesheet migration,
        Task Work lines that don't have the corresponding Timesheet line
        will see that line created.
        The purpose is to migrate work data in the discontinued Work Lines
        to the Timesheet lines.
        """
        # Delete the timesheet line to make our work line orphan
        task_work_id = self.task_work.id
        self.task_work.hr_analytic_timesheet_id.unlink()
        # Run migration
        self.TaskWork.migrate_to_timesheet()
        # Test if timesheet line was created and work date kept
        task_work_updated = self.TaskWork.browse(task_work_id)
        self.assertEqual(
            task_work_updated.hr_analytic_timesheet_id.work_date,
            '2017-01-16 08:30:00',
            "Timesheet line is created and keeps the original work start time")

    def test_30_create_naive_timehseet_line(self):
        """
        Creating a work line directly from Tasks, providing only
        the minimum data, should correctly compute the remaining data and
        successfully create the timesheet line.
        This is to keep support to create work lines from RPC calls or
        data imports, without having to provide the additional data
        computed on the webclient from through onchange events.
        """
        task = self.env['project.task'].create(
            {'name': 'Test create naive work line',
             'project_id': self.task.project_id.id})
        task.write({
            'work_ids': [(
                0,
                False,
                {'name': 'Naive timesheet line',
                 'user_id': self.env.ref('base.user_root').id,
                 'work_date': '2017-01-16 10:30:00',
                 'unit_amount': 0.5}
            )],
        })
        self.assertEqual(
            task.work_ids[0].work_date,
            '2017-01-16 10:30:00',
            "Create Timesheet line preserving date and time information")

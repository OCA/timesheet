# -*- coding: utf-8 -*-
# Copyright 2017 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, models
from openerp.exceptions import except_orm


_logger = logging.getLogger(__name__)


class TaskWork(models.Model):
    _inherit = 'project.task.work'

    @api.model
    def create(self, vals):
        # If used, work_date overrides date
        if 'work_date' in vals:
            vals['date'] = vals['work_date'][:10]
        work_line = super(TaskWork, self).create(vals)
        work_line.hr_analytic_timesheet_id.work_date = work_line.date
        return work_line

    @api.multi
    def write(self, vals):
        if 'work_date' in vals:
            vals['date'] = vals['work_date'][:10]
            self.filtered('hr_analytic_timesheet_id')\
                .write({'work_date': vals['date']})
        return super(TaskWork, self).write(vals)

    @api.model
    def migrate_to_timesheet(self):
        """Create timesheet lines for the orphan task work lines"""
        TSLine = self.env['hr.analytic.timesheet']
        work_lines_domain = [
            ('hr_analytic_timesheet_id', '=', False),
            ('date', '!=', False),
            ('user_id', '!=', False)]
        _logger.info(
            'Converting %d Task Work lines into Timesheet lines...',
            self.search_count(work_lines_domain))
        count_work, count_created, count_error = 0, 0, 0
        for work in self.search(work_lines_domain, order='date desc'):
            count_work += 1
            try:
                tsline_id = self._create_analytic_entries({
                    'task_id': work.task_id.id,
                    'name': work.name,
                    'user_id': work.user_id.id,
                    'date': work.date[:10],
                    'hours': work.hours})
                # Extra values must be written outside _create_analytic_entries
                TSLine.browse(tsline_id).write({
                    'task_id': work.task_id.id,
                    'work_date': work.date})
                work.hr_analytic_timesheet_id = tsline_id
                count_created += 1
            except except_orm, e:
                # Failed due to insufficient setup
                _logger.debug(e)
                count_error += 1

            if count_work % 100 == 0:
                self.env.cr.commit()
                _logger.info(
                    '...migrated %d work lines, skipped %d lines',
                    count_created,
                    count_error)

        _logger.info(
            '%d Work lines processed, '
            '%d were copied to new Timesheet Lines. '
            '%d were not created due to setup errors.',
            count_work, count_created, count_error)

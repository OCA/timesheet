# -*- coding: utf-8 -*-
# © 2017 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter
import requests
import itertools
from datetime import date, datetime, timedelta
import dateutil.parser

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from openerp.addons.connector.exception \
    import MappingError, InvalidDataError, IDMissingInBackend

from .. import toggl


_logger = logging.getLogger(__name__)


@toggl
class HrAnalyticTimesheetAdapter(CRUDAdapter):
    _model_name = 'toggl.hr.analytic.timesheet'

    def search_read(self, filters=None):
        """ Search records """

        date_from = filters.get('date_from', None)
        date_to = filters.get('date_to', None)
        employee_name = filters.get('name', None)
        if not (date_from and date_to and employee_name):
            raise UserError('No date and/or employee selected')
        num_days = (date_to - date_from).days + 1
        days = [(date_from + timedelta(days=k)).isoformat()
            for k in range(0, num_days)]

        # connect with products/parts database
        self.api_key = self.backend_record.api_key
        self.api_url = self.backend_record.api_url
        self.workspace_id = self.backend_record.workspace_id

        # get detailed toggl info for the selected week
        status = None
        retries = 0
        page = 1
        finished = False
        resultlines = []
        while not finished:
            r = requests.get(
                self.api_url,
                auth=(self.api_key, 'api_token'),
                data={
                    'user_agent': self.env.user.email or \
                                  self.env.user.company_id.email,
                    'workspace_id': self.workspace_id,
                    'since': days[0],
                    'until': days[6],
                    'page': page
                }
            )
            status = r.status_code
            if status == 429:
                sleep(1000)
                retries += 1
                if retries < 5:
                    continue
                else:
                    raise requests.exceptions.ConnectionError(r.reason)
            if status != 200:
                raise requests.exceptions.ConnectionError(r.reason)
            result = r.json()
            resultlines += result['data']
            per_page = result['per_page']
            total_count = result['total_count']
            if total_count < per_page:
                finished = True

        # Error if no results
        if not resultlines:
            raise UserError(_('No timesheet entries found for this date range'))

        # Error if no results for this employee
        real_resultlines = []
        for resultline in resultlines:
            if resultline['user'] == employee_name:
                real_resultlines.append(resultline)
        if not real_resultlines:
            raise UserError(_("No timesheet entries found for employee '%s' "
                "for this date range" % (employee_name,)))

        return real_resultlines

    def aggregate(self, resultlines):
        # aggregate
        agglines = {}
        for line in resultlines:
            start = dateutil.parser.parse(line['start'])
            date = start.date()
            _id = line['id']
            client = line['client']
            user = line['user']
            project = line['project']
            desc = line['description']
            duration = line['dur']
            _hash = '%s_%s_%s_%s_%s' % (user, date, client, project, desc)
            if _hash not in agglines:
                agglines[_hash] = {
                    'id': _id,
                    'date': date,
                    'user': user,
                    'client': client,
                    'project': project,
                    'description': desc,
                    'duration': duration
                }
            else:
                agglines[_hash]['duration'] += duration

        # return results
        return [line for _hash, line in sorted(agglines.iteritems())]

# Copyright 2023 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo import fields

from odoo.addons.resource.models.resource import HOURS_PER_DAY

DEFAULT_TIME_QTY = {"hours_qty": HOURS_PER_DAY, "days_qty": 1.0, "type": "default"}


def get_end_of_day(date, attendances):
    """Returns the datetime corresponding to the end of the day"""
    hour_to = max(attendances.mapped("hour_to"), default=0.0)
    assert 0 <= hour_to < 24
    time_part = datetime.utcfromtimestamp(hour_to * 60 * 60).time()
    return datetime.combine(date, time_part)


def generate_dates_from_range(start_date, end_date=None):
    """Prepare a list of dates to be processed"""
    if not end_date:
        end_date = fields.Date.today()
    deltas = range((end_date - start_date).days + 1)
    return [start_date + timedelta(days=dt) for dt in deltas]


def get_attendances_values_by_date(employees, date_from=None, date_to=None):
    """Retrieve attendances (from resource module) values mapped by date

    These attendances are the matrix product of contractual hours by day
    and week days (NOT the `hr.attendance` model).

    Warning: it is intended to be injected in context to reduce calls

    :param employees: a list of employee records
    :param date_from: a datetime.date object (default first contract date, included)
    :param date_to: a datetime.date object (default today, included)
    """
    values_by_date = {}
    for employee in employees:
        # Always set a value even empty to avoid mistreatment later on.
        values_by_date[employee.id] = {}
        contracts = employee.contract_ids
        if not contracts:
            continue
        for contract in contracts:
            custom_date_from = contract.date_start
            custom_date_to = contract.date_end
            if date_from:
                custom_date_from = max(date_from, custom_date_from)
            if date_to:
                if custom_date_to:
                    custom_date_to = min(date_to, custom_date_to)
                else:
                    custom_date_to = date_to
            if custom_date_to and custom_date_to < custom_date_from:
                continue
            # Manage dates outside contract validity
            if contract.date_end and custom_date_to > contract.date_end:
                continue
            if custom_date_from < contract.date_start:
                continue

            values = contract.prepare_hr_employee_hour_values(
                date_start=custom_date_from, date_end=custom_date_to
            )
            values_by_date[employee.id].update(
                [(hvals["date"], hvals) for hvals in values]
            )
    return values_by_date

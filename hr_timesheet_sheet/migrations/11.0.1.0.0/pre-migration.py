# -*- coding: utf-8 -*-
# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'res_company': [
        ('timesheet_range', None, None),
    ],
}

_field_renames = [
    ('hr_timesheet.sheet', 'hr_timesheet_sheet', 'date_from', 'date_start'),
    ('hr_timesheet.sheet', 'hr_timesheet_sheet', 'date_to', 'date_end'),
]

_xmlid_renames = [
    ('hr_timesheet_sheet.view_config_settings_form_inherit_hr_timesheet_sheet',
     'hr_timesheet_sheet.res_config_settings_view_form'),
    ('hr_timesheet_sheet.act_hr_timesheet_sheet_my_timesheets',
     'hr_timesheet_sheet.hr_timesheet_sheet_action'),
    ('hr_timesheet_sheet.access_hr_timesheet_sheet_sheet_user',
     'hr_timesheet_sheet.access_hr_timesheet_sheet_user'),
]


def rename_hr_timesheet_sheet(cr):
    openupgrade.rename_tables(
        cr, [('hr_timesheet_sheet_sheet', 'hr_timesheet_sheet')]
    )
    openupgrade.rename_models(
        cr, [('hr_timesheet_sheet.sheet', 'hr_timesheet.sheet')]
    )


@openupgrade.migrate()
def migrate(env, version):
    rename_hr_timesheet_sheet(env.cr)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)

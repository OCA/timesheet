# © 2017 bloopark systems (<http://bloopark.de>)
# © 2018 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_company_sheet_range(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('timesheet_range'), 'sheet_range',
        [('month', '1'),
         ('week', '2')],
        table='res_company', write='sql')


@openupgrade.migrate()
def migrate(env, version):
    map_company_sheet_range(env.cr)
    openupgrade.load_data(
        env.cr, 'hr_timesheet_sheet',
        'migrations/11.0.1.0.0/noupdate_changes.xml',
    )

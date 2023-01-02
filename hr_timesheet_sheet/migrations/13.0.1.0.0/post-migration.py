# Copyright 2020 ForgeFlow
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.rrule import DAILY, MONTHLY, WEEKLY
from openupgradelib import openupgrade  # pylint: disable=W7936


def res_company_sheet_range_map_values(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("sheet_range"),
        "sheet_range",
        [(MONTHLY, "MONTHLY"), (WEEKLY, "WEEKLY"), (DAILY, "DAILY")],
        table="res_company",
    )


@openupgrade.migrate()
def migrate(env, version):
    res_company_sheet_range_map_values(env)
    openupgrade.load_data(
        env.cr, "hr_timesheet_sheet", "migrations/13.0.1.0.0/noupdate_changes.xml"
    )

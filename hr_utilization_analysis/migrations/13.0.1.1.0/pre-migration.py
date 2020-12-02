# Copyright 2020 Sunflower IT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute(
        "alter table if exists hr_utilization_analysis_entry "
        "drop constraint if exists hr_utilization_analysis_entry_entry_uniq"
    )

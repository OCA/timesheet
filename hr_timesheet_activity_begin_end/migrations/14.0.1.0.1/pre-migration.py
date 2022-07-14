from openupgradelib import openupgrade

namespec = [("hr_timesheet_activity_begin_end", "hr_timesheet_sheet_begin_end")]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_names(env.cr, namespec, False)

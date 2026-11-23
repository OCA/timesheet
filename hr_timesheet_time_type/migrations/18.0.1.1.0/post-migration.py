# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """Keep the existing time types shared by all companies.

    Before this version a time type had no company: every company could use
    any of them. Initializing the new column with the default assigns them
    all to the company that runs the update, which would hide them from the
    rest of the companies while their timesheet lines keep using them.
    """
    cr.execute("UPDATE project_time_type SET company_id = NULL")

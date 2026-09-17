# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)
_OLD_KEY = "project_timesheet_time_control.timesheet_alignment"
_NEW_KEY = "hr_timesheet_time_control.timesheet_alignment"


@openupgrade.migrate()
def migrate(env, version):
    """Rename the timesheet alignment system parameter.

    The ``config_parameter`` of ``res.config.settings.timesheet_alignment``
    was renamed from ``project_timesheet_time_control.timesheet_alignment``
    to ``hr_timesheet_time_control.timesheet_alignment``. Carry the stored
    value over so the configured alignment survives the upgrade.
    """
    _logger.info(f"Starting pre-migration script for version {version}")
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_config_parameter
        SET key = %(new_key)s
        WHERE key = %(old_key)s
          AND NOT EXISTS (
              SELECT 1 FROM ir_config_parameter WHERE key = %(new_key)s
          )
        """,
        {"old_key": _OLD_KEY, "new_key": _NEW_KEY},
    )
    openupgrade.logged_query(
        env.cr,
        "DELETE FROM ir_config_parameter WHERE key = %(old_key)s",
        {"old_key": _OLD_KEY},
    )

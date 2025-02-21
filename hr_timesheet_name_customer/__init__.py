from . import models


def post_init_hook(cr, registry):
    """Initialize name_customer field with name field value for existing records."""
    cr.execute(
        """
        UPDATE account_analytic_line
        SET name_customer = name
        WHERE name_customer IS NULL
        AND project_id IS NOT NULL
    """
    )

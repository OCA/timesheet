from openupgradelib import openupgrade


def pre_init_hook(cr):
    if not openupgrade.column_exists(
        cr, "account_analytic_line", "exclude_from_sale_order"
    ):
        openupgrade.copy_columns(
            cr,
            {
                "account_analytic_line": [
                    ("non_allow_billable", "exclude_from_sale_order", None),
                ],
            },
        )

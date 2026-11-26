def post_init_hook(env):
    env["account.analytic.plan"].search([])._sync_plan_column("project.task")

def _progress_rate(self, cr, uid, ids, names, arg, context=None):
    """As OpenERP SA made a query for this function field (perf.
    reason obviously), I must overide it all."""
    result = {}.fromkeys(ids, 0.0)
    progress = {}
    if not ids:
        return res
    cr.execute('''SELECT project_id,
                         sum(planned_hours) as sum_planned_hours,
                         sum(total_hours) as sum_total_hours,
                         sum(effective_hours) as sum_effective_hours,
                         sum(remaining_hours) as remaining_hours,
                         sum(deduced_hours) as deduced_hours
                  FROM project_task
                  WHERE  project_id in %s
                   AND state<>'cancelled'
                  GROUP BY project_id''', (tuple(ids),))

    res = cr.dictfetchall()
    for stat in res:
        project = self.browse(cr, uid, res['project_id'], context=context)
        progr = (stat['sum_planned_hours'] and
                 round(100.0 * stat['sum_total_hours'] / stat[
                     'sum_planned_hours'], 2) or 0.0),
        result[project.id] = {'planned_hours': stat['sum_planned_hours'],
                              'effective_hours': stat['sum_effective_hours'],
                              'total_hours': stat['sum_total_hours'],
                              'progress_rate': progr,
                              'deduced_hours': stat['sum_deduced_hours']}
    return res

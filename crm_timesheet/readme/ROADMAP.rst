* Window actions `crm.crm_lead_all_leads` and
  `crm.crm_lead_opportunities_tree_view` contexts are overwritten for
  hiding the lead field in timesheet embedded view. As this is not
  accumulative, this change might be lost by other module overwritting the
  same action, or this masks another module overwritting.

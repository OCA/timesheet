# Copyright 2015 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "CRM Timesheet",
    'category': 'Customer Relationship Management',
    'version': '12.0.2.1.0',
    'depends': [
        'crm',
        'project_timesheet_time_control'
    ],
    'data': [
        'views/crm_lead_view.xml',
        'views/hr_timesheet_view.xml'
    ],
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr-timesheet',
    'license': 'AGPL-3',
    'installable': True,
}

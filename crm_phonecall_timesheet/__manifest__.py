# Copyright 2015 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "CRM Phonecalls Timesheet",
    'category': 'Customer Relationship Management',
    'version': '12.0.1.0.0',
    'depends': [
        'hr_timesheet',
        'crm_phonecall',
    ],
    'data': [
        'views/crm_phonecall_view.xml',
        'views/hr_timesheet_view.xml'
    ],
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/timesheet',
    'license': 'AGPL-3',
    'auto_install': True,
    'installable': True,
}

# -*- coding: utf-8 -*-
# © 2011 Domsense srl (<http://www.domsense.com>)
# © 2011-15 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HR - Attendance Analysis",
    "version": "8.0.1.0.0",
    "category": "Generic Modules/Human Resources",
    "summary": "Dynamic reports based on employee's attendances and "
               "contract's calendar",
    "author": "Agile Business Group,Odoo Community Association (OCA)",
    "website": "http://www.agilebg.com",
    "license": "AGPL-3",
    "depends": [
        "hr_attendance",
        "hr_contract",
        "hr_holidays",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/hr_attendance_views.xml",
        "views/resource_resource_views.xml",
    ],
    "demo": [
        "demo/hr_attendance_demo.xml",
    ],
    "installable": True
}

# -*- coding: utf-8 -*-
# Copyright 2018 Willem Hulshof Magnus (www.magnus.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "magnus_invoicing",

    'summary': """
        This module introduces an advanced professional services invoicing process,
        offering fixed price, time and material, licensing and several combinations
         thereof """,

    'description': """
        This module introduces an advanced professional services invoicing process,
        offering fixed price, time and material, licensing and several combinations
         thereof. 
    """,

    'author': "Magnus",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'module_category_specific_industry_applications',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['magnus_timesheet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/magnus_security.xml',
        'data/data.xml',
        'wizard/analytic_line_invoice_view.xml',
        'wizard/change_chargecode_view.xml',
        'views/hr_view.xml',
        'views/task_view.xml',
        'views/account_analytic_view.xml',
        'views/templates.xml',
        'views/analytic_invoice.xml',
        'views/product_view.xml',
        'views/menuitem.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#        'demo/demo.xml',
    ],
}
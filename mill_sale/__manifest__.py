# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mill Sale',
    'version': '1.8',
    'category': 'mill',
    'sequence': 1,
    'summary': 'Mill Sale Orders',
    'website': 'https://www.singlasteel.in',
    'depends': [
        'base_setup',
        'sale','mill_purchase','stock','mill_core',
    ],
    'data': [
        # Data
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/sale_order_view.xml",
        # Reports
        'report/ir_actions_report.xml',
        'report/report_orders_list.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}

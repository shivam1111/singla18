# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mill Purchase',
    'version': '1.8',
    'category': 'mill',
    'sequence': 1,
    'summary': 'Mill Purchase Orders',
    'website': 'https://www.singlasteel.in',
    'depends': [
        'base_setup',
        'sale','purchase','stock','mill_core',
    ],
    'data': [
        # Data
        # Security
        # Views
        'views/purchase_order_view.xml',
        # Reports
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}

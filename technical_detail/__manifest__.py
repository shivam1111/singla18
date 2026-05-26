# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Technical Details',
    'version': '1.8',
    'category': 'mill',
    'sequence': 1,
    'summary': 'Technical Details',
    'website': 'https://www.singlasteel.in',
    'depends': [
        'base_setup','mill_core',
    ],
    'data': [
        # Data
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/technical_detail_view.xml",
        # Reports
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}

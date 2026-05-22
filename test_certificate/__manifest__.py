# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Test Certificate',
    'version': '1.8',
    'category': 'mill',
    'sequence': 1,
    'summary': 'Prepares Test Certificate',
    'website': 'https://www.singlasteel.in',
    'depends': [
        'base_setup','mill_core'
    ],
    'data': [
        # Data
        'data/ir_sequence_data.xml',
        # Security
        "security/ir.model.access.csv",
        # Views
        'views/chemical_composition.xml',
        # Reports
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}

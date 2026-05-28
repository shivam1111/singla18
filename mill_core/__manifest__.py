# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mill Core',
    'version': '1.8',
    'category': 'mill',
    'sequence': 1,
    'summary': 'Defines mills core requirements',
    'website': 'https://www.singlasteel.in',
    'depends': [
        'base_setup',
        'sale','purchase','stock','report_xlsx',
    ],
    'data': [
        # Data
        "data/ir_sequence_data.xml",
        "data/data.xml",
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/menuitem.xml",
        "views/size_size_view.xml",
        "views/material_grade_views.xml",
        "views/material_grade_spec_view.xml",
        "views/mill_heat_view.xml",
        "views/product_template.xml",
        "views/stock_picking_view.xml",
        "views/mill_production_view.xml",
        "views/production_order_view.xml",
        "views/mill_google_drive_views.xml",
        "views/res_config_settings_views.xml",
        # Reports
        "report/ir_actions_report.xml",
        "report/production_order_report.xml",
        "report/heat_report.xml",
        "report/grade_report.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}

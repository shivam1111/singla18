from odoo import models, fields, api

class ProductionOrder(models.Model):
    _inherit = "production.order"
    _description = "technical.detail.production.order"

    def action_select_technical_detail(self):
        return {
            'name': 'Select Technical Detail',
            'type': 'ir.actions.act_window',
            'res_model': 'technical.detail',
            'view_mode': 'list',
            'view_id': self.env.ref('technical_detail.view_mill_technical_detail_tree').id,
            'target': 'new',  # This opens it in a pop-up modal
            'context': {'is_selection_mode': True},
        }
from odoo import models, fields,api

class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_view_move(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Heats',
            'res_model': 'heat.heat',
            'view_mode': 'list,form',
            'domain': [('move_id', '=', self.id)],
            'target': 'current',
            'context':{'default_move_id':self.id,
                       'default_partner_id':self.picking_id and self.picking_id.partner_id.id or False,
                       'default_grade_spec_id':self.product_id.grade_id.id}
        }
    heat_ids =  fields.One2many('heat.heat','move_id',"Heats")

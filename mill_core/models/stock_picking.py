from odoo import models, fields,api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_no = fields.Char('Invoice No.')

    state_heat = fields.Selection([
        ('pending', 'Heat Pending'),
        ('done', 'Heat Updated'),
    ], default='pending',name="Heat Status")

    order_id = fields.Many2one('mill.production',string='Production Order')
from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # Rolling Mill Specific Fields
    heats = fields.Float(string='Heats', digits=(16, 2), default=0.0)

    # Pricing Matrix Structure
    basic_rate = fields.Monetary(string='Basic Rate (Mandi)', help="Mandi Gobindgarh MS Ingot Price")
    extra_rate = fields.Monetary(string='Extra Rate', help="Grade Difference Premium/Discount")
    net_rate = fields.Monetary(string='Net Rate', compute='_compute_rolling_mill_pricing', store=True)

    # 1. Automate Quantity: Heats * 7.5 MT
    @api.onchange('heats')
    def _onchange_heats(self):
        for line in self:
            if line.heats:
                line.product_qty = line.heats * 7.5

    # 2. Compute Net Rate & Map to Odoo's Native Unit Price
    @api.depends('basic_rate', 'extra_rate')
    def _compute_rolling_mill_pricing(self):
        for line in self:
            net = line.basic_rate + line.extra_rate
            line.net_rate = net
            # Ties our custom steel calculation back to Odoo's native purchasing engine
            line.price_unit = net

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    po_net_rate = fields.Monetary(related='purchase_id.order_line.net_rate', string='PO Net Rate/MT')
    # Required field by Odoo to handle currency symbols cleanly
    currency_id = fields.Many2one(
        related='purchase_id.currency_id',
        string='Currency',
        readonly=True
    )
from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _order = "date_order asc"

    # Field to select the Broker on the contract
    broker_id = fields.Many2one(
        'res.partner',
        string='Broker',
        help="Broker responsible for coordinating this raw material supply run."
    )
    x_line_rate = fields.Float(
        string="Rate",
        related="order_line.price_unit",
        readonly=True,
        store=True
    )
    x_line_product_qty = fields.Float(
        string="Qty",
        related="order_line.product_qty",
        readonly=True,
        store=True
    )
    x_line_qty_received = fields.Float(
        string="Received",
        related="order_line.qty_received",
        readonly=True,
        store=True
    )

    x_qty_balance = fields.Float(
        string="Balance",
        compute="_compute_qty_balance",
        store=True
    )

    @api.depends('x_line_product_qty', 'x_line_qty_received')
    def _compute_qty_balance(self):
        for line in self:
            # Simple math: Ordered minus what has arrived
            line.x_qty_balance = line.x_line_product_qty - line.x_line_qty_received

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

    # Automatically pull the Broker name onto the incoming warehouse gate receipts
    broker_id = fields.Many2one(
        'res.partner',
        related='purchase_id.broker_id',
        string='Broker',
        store=True,
        readonly=True
    )


class StockPicking(models.Model):
    _inherit = "stock.picking"

    product_id = fields.Many2one('product.product', string = "Product",
                                 related="move_ids_without_package.product_id")

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # Create a native, searchable related field pointing to the broker
    broker_id = fields.Many2one(
        'res.partner',
        related='picking_id.broker_id',
        string='Broker',
        store=True,     # Storing it ensures fast grouping and clean pivot reports
        readonly=True
    )

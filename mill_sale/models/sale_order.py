from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # A simple custom ledger table to log dispatches manually
    dispatch_ledger_ids = fields.One2many(
        'sale.order.dispatch.line',
        'order_id',
        string='Dispatch Details Log'
    )
    x_line_price_unit = fields.Float("Rate",related = "order_line.price_unit")
    x_total_qty = fields.Float(
        string="Qty",
        compute="_compute_total_qty",
        store=True
    )
    x_dispatch_qty = fields.Float(
        string="Completed",
        compute="_compute_total_qty",
        store=True
    )
    x_balance_qty = fields.Float(
        string="Balance",
        compute="_compute_total_qty",
        store=True
    )
    @api.depends('order_line.product_uom_qty','order_line.qty_delivered_mill','order_line.qty_pending_mill')
    def _compute_total_qty(self):
        for order in self:
            # Sum up the quantities of all lines
            total_qty = sum(order.order_line.mapped('product_uom_qty'))
            order.x_total_qty = total_qty
            order.x_dispatch_qty = sum(order.order_line.mapped('qty_delivered_mill'))
            order.x_balance_qty = sum(order.order_line.mapped('qty_pending_mill'))


class SaleOrderDispatchLine(models.Model):
    _name = 'sale.order.dispatch.line'
    _description = 'Rolling Mill Manual Dispatch Log'

    # Automatically extract the size attribute when a line item is selected
    @api.onchange('sale_line_id', 'sale_line_id.size_id')
    def _compute_size_from_line(self):
        for rec in self:
            if rec.sale_line_id and rec.sale_line_id.size_id:
                rec.size_id = rec.sale_line_id.size_id
            else:
                rec.size_id = False

    order_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade')
    date = fields.Date(string='Dispatch Date', default=fields.Date.context_today)

    # Let the user choose which line item, size, and weight are leaving the mill gate
    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Order Line',
        domain="[('order_id', '=', order_id),('product_id','!=',False)]",
        required=True)

    size_id = fields.Many2one('size.size', string='Size', required=True)
    qty_dispatched = fields.Float(string='Dispatched', required=True)
    invoice_no = fields.Char("Invoice No.")
    remarks = fields.Char("Remarks")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    size_id = fields.Many2one('size.size', string='Material Size')
    qty_delivered_mill = fields.Float(string='Delivered (MT)', compute='_compute_manual_dispatches', store=True)
    qty_pending_mill = fields.Float(string='Pending (MT)', compute='_compute_manual_dispatches', store=True)

    # The 3 Pricing Components
    basic_mandi_rate = fields.Monetary(
        string='Basic Rate',
        help="Base raw material price from the Mandi."
    )
    extra_misc_charges = fields.Monetary(
        string='Extra Charges',
        help="Grade-specific premiums or specialized testing fees."
    )
    rolling_conversion_rate = fields.Monetary(
        string='Rolling',
        help="Internal cost/rate to convert raw ingot into finished profiles."
    )

    # Final Computed Metric
    net_rate = fields.Monetary(
        string='Net Rate',
        compute='_compute_rolling_mill_pricing',
        store=True,
        help="Final calculated price per MT (Mandi + Extra + Conversion)."
    )

    # Dynamic Pricing Engine
    @api.depends('basic_mandi_rate', 'extra_misc_charges', 'rolling_conversion_rate')
    def _compute_rolling_mill_pricing(self):
        for line in self:
            # Sum up all three pricing pillars
            computed_net = (
                    line.basic_mandi_rate +
                    line.extra_misc_charges +
                    line.rolling_conversion_rate
            )
            line.net_rate = computed_net

            # Map directly to Odoo's native unit price variable
            # to drive standard accounting subtotal metrics
            line.price_unit = computed_net

    # 1. TRICK: Change how the Sale Order Line looks in dropdown menus
    @api.depends('product_id', 'size_id')
    def _compute_display_name(self):
        for line in self:
            if line.product_id and line.size_id:
                # Displays: "SUP9 (50x8mm)"
                line.display_name = f"{line.product_id.name} ({line.size_id.name})"
            else:
                super(SaleOrderLine, line)._compute_display_name()

    # Compute totals directly from our manual dispatch log sub-table
    @api.depends('product_uom_qty', 'order_id.dispatch_ledger_ids.qty_dispatched')
    def _compute_manual_dispatches(self):
        for line in self:
            # Sum up all manual weight entries for this specific line item
            total_sent = sum(line.order_id.dispatch_ledger_ids.filtered(
                lambda d: d.sale_line_id == line
            ).mapped('qty_dispatched'))

            line.qty_delivered_mill = total_sent
            line.qty_pending_mill = max(0.0, line.product_uom_qty - total_sent)

    def _action_launch_stock_rule(self, tracking_ids=None):
        """
        Intercepts Odoo's delivery generation engine.
        Bypasses stock move creation entirely for your rolling mill sales lines.
        """
        return True
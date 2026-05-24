from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # A simple custom ledger table to log dispatches manually
    dispatch_ledger_ids = fields.One2many(
        'sale.order.dispatch.line',
        'order_id',
        string='Dispatch Details Log'
    )


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

    size_id = fields.Many2one('size.size', string='Size Delivered', required=True)
    qty_dispatched = fields.Float(string='Weight Dispatched (MT)', required=True)
    invoice_no = fields.Char("Invoice No.")
    remarks = fields.Char("Remarks")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    size_id = fields.Many2one('size.size', string='Material Size')
    qty_delivered_mill = fields.Float(string='Delivered (MT)', compute='_compute_manual_dispatches', store=True)
    qty_pending_mill = fields.Float(string='Pending (MT)', compute='_compute_manual_dispatches', store=True)

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
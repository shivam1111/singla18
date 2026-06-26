from odoo import fields, models, tools


class SaleReportSizeBalance(models.Model):
    _name = "sale.report.size.balance"
    _description = "Rolling Mill Size Dispatch and Balance Analysis"
    _auto = False

    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    product_id = fields.Many2one('product.product', string='Grade (Product)', readonly=True)
    size_id = fields.Many2one('size.size', string='Size', readonly=True)

    qty_ordered = fields.Float(string='Ordered Qty', readonly=True)
    qty_dispatched = fields.Float(string='Total Dispatched', readonly=True)
    qty_balance = fields.Float(string='Balance Qty', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT 
                    sol.id AS id,
                    so.partner_id AS partner_id,
                    sol.product_id AS product_id,
                    sol.size_id AS size_id,
                    sol.product_uom_qty AS qty_ordered,
                    COALESCE(dl.total_dispatched, 0) AS qty_dispatched,
                    (sol.product_uom_qty - COALESCE(dl.total_dispatched, 0)) AS qty_balance
                FROM sale_order_line sol
                JOIN sale_order so ON sol.order_id = so.id

                -- Group & aggregate your Rolling Mill dispatch log table
                LEFT JOIN (
                    SELECT 
                        sale_line_id, 
                        SUM(qty_dispatched) AS total_dispatched
                    FROM sale_order_dispatch_line
                    GROUP BY sale_line_id
                ) dl ON dl.sale_line_id = sol.id

                -- Only report on confirmed sales orders
                WHERE so.state IN ('sale', 'done') and so.locked = false
            )
        """)
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('product_id', 'linked_line_id', 'linked_line_ids')
    def _compute_name(self):
        print("This is a trial--------------")
        for line in self:
            if not line.product_id and not line.is_downpayment:
                continue

            lang = line.order_id._get_lang()
            if lang != self.env.lang:
                line = line.with_context(lang=lang)

            if line.product_id:
                line.name = line._get_sale_order_line_multiline_description_sale()
                continue

            if line.is_downpayment:
                line.name = line._get_downpayment_description()
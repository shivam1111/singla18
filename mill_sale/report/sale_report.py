from odoo import fields, models

class SaleReport(models.Model):
    _inherit = "sale.report"

    # Define the custom field (assuming size_id links to a 'product.size' model)
    size_id = fields.Many2one('size.size', string='Size', readonly=True)

    def _select_sale(self):
        # Inject your field into the SELECT clause of the SQL query
        select_str = super()._select_sale()
        select_str += ", l.size_id AS size_id"
        return select_str

    def _group_by_sale(self):
        # Inject your field into the GROUP BY clause of the SQL query
        group_by_str = super()._group_by_sale()
        group_by_str += ", l.size_id"
        return group_by_str
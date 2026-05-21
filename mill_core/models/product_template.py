from odoo import models, fields,api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends( 'product_role', 'grade_id')
    def _compute_name(self):
        for rec in self:
            if rec.product_role == 'raw' and rec.grade_id:
                rec.name = f"Ingot {rec.grade_id.display_name}"

    grade_id = fields.Many2one('material.grade.spec', string="Grade")
    name = fields.Char(compute="_compute_name",store=True,readonly=False)
    product_role = fields.Selection([
        ('raw', 'Raw Material'),
        ('finished', 'Finished Good'),
    ], required=True)






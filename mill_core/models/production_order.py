from odoo import models, fields,api
from odoo.exceptions import UserError,AccessError
from odoo.tools.translate import _

class ProductionOrderLine(models.Model):
    _name = "production.order.line"
    _description = "Production Order Line"
    _order = "sequence"

    @api.depends('size_id', 'kg_per_pc')
    def _compute_flat_length(self):
        for i in self:
            if i.size_id and i.size_id.section_weight_kg_m:
                i.flat_length = i.kg_per_pc / i.size_id.section_weight_kg_m
            else:
                i.flat_length = 0.0

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('production.order.line') or _('New')
        result = super(ProductionOrderLine, self).create(vals)
        return result

    @api.onchange('pcs', 'kg_per_pc')
    def _compute_qty(self):
        self.qty = (self.kg_per_pc * self.pcs) / 1000

    # def view_production_order(self):
    #     # Find production line that has the bundle number
    #     line_ids = self.env['stock.line'].search([('production_line_id', '=', self.id)])
    #     if line_ids:
    #         return {
    #             'name': _('Production Details'),
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'mill.production',
    #             'view_type': 'form',
    #             'view_mode': 'tree',
    #             'view_id': self.env.ref('mill_production.view_mill_production_tree').id,
    #             'context': {},
    #             'domain': [('id', 'in', [i.production_id.id for i in line_ids])],
    #             'target': 'current'
    #         }
    #     else:
    #         raise exceptions.Warning('There are no production orders attached to this bundle')

    name = fields.Char('Name', help="This is also a bundle No.", default='/')
    size_id = fields.Many2one('size.size', string="Size", required=True)
    tolerance = fields.Char('Tolerance')
    corner_id = fields.Many2one('corner.type', string="Corner Type", related="size_id.corner_id", store=True)
    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=10)
    pcs = fields.Float('Pcs')
    kg_per_pc = fields.Float('Kg/pc')
    qty = fields.Float('Qty')
    flat_length = fields.Float("Bar Length", compute="_compute_flat_length")
    grade_id = fields.Many2one('material.grade.spec', 'Grade')
    partner_id = fields.Many2one('res.partner', help="Mostly furnce, but depends on usage", string="Furnace")
    customer_id = fields.Many2one('res.partner', 'Customer')
    cc = fields.Char('Clear Cut (CC)')
    production_id = fields.Many2one('production.order', 'Production Order')
    heat_no = fields.Char('Heat No.')
    remarks = fields.Char('Remarks')
    is_inspection = fields.Boolean('Insp',help = "Inspection")


class ProductionOrder(models.Model):
    _name = "production.order"
    _description = "Production Order"
    _order = "date"

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('production.order') or _('New')
        result = super(ProductionOrder, self).create(vals)
        return result

    name = fields.Char('Name',default = '/')
    date = fields.Date('Date',required=True,default = fields.Date.today)
    line_ids = fields.One2many('production.order.line', 'production_id', 'Order Lines')
    remarks = fields.Text('Remarks')
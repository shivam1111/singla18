from odoo import models, fields, api

class ProductionPlan(models.Model):
    _name = "production.plan"
    _description = "Production Planning"

    size_id = fields.Many2one("size.size",string = 'Size')
    partner_id = fields.Many2one('res.partner',string = 'Partner')
    grade_id = fields.Many2one('material.grade.spec','Grade')
    qty = fields.Float("Qty")
    remarks = fields.Char("Remarks")


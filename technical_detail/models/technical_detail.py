from odoo import models, fields, api

class TechnicalDetail(models.Model):
    _name = "technical.detail"
    _description = "Technical Details"


    partner_id = fields.Many2one('res.partner','Customer')
    size_id = fields.Many2one('size.size','Size')
    length_primary = fields.Float("Primary Length")
    secondary_length = fields.Float("Secondary Length")
    remarks = fields.Char("Remarks")
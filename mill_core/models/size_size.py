from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CornerType(models.Model):
    _name = "corner.type"
    _description = "Corner Type for Flat Bars"

    name = fields.Char("Name")

class Size(models.Model):
    _name = 'size.size'
    _description = 'Rolling Section Size'
    _order = 'width_mm, thickness_mm'

    _sql_constraints = [
        ('size_unique',
         'unique(name, corner_id)',
         'This size already exists for this shape.')
    ]

    name = fields.Char(
        compute='_compute_name',
        store=True,index=True
    )

    corner_id = fields.Many2one('corner.type',name = "Corner Type")
    width_mm = fields.Float("Width (mm)", digits=(10, 2))
    thickness_mm = fields.Float("Thickness (mm)", digits=(10, 2))
    diameter_mm = fields.Float("Diameter (mm)", digits=(10, 2))
    active = fields.Boolean(default=True)

    shape = fields.Selection([
        ('flat', 'Flat'),
        ('round', 'Round'),
        ], required=True)

    section_weight_kg_m = fields.Float(
        "Section Weight (kg/ft)",
        compute='_compute_section_weight',
        store=True
    )
    remarks = fields.Text()

    # ---------- DISPLAY NAME ----------
    @api.depends('corner_id', 'width_mm', 'thickness_mm', 'diameter_mm')
    def _compute_name(self):
        for rec in self:
            if rec.shape == 'round' and rec.diameter_mm:
                rec.name = f"Ø {rec.diameter_mm:g}"
            elif rec.shape == 'flat' and rec.width_mm and rec.thickness_mm:
                rec.name = f"{rec.width_mm:g}x{rec.thickness_mm:g}"
            else:
                rec.name = "Undefined Size"

    # ---------- WEIGHT CALCULATION ----------
    @api.depends('corner_id', 'width_mm', 'thickness_mm', 'diameter_mm')
    def _compute_section_weight(self):
        for rec in self:
            if rec.shape == 'round' and rec.diameter_mm:
                rec.section_weight_kg_m = (rec.diameter_mm * rec.diameter_mm) * 0.0019
            elif rec.shape == 'flat' and rec.width_mm and rec.thickness_mm:
                rec.section_weight_kg_m = rec.width_mm * rec.thickness_mm * 0.002389
            else:
                rec.section_weight_kg_m = 0.0
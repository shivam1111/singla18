from odoo import api, fields, models


class MaterialGrade(models.Model):
    _name = "material.grade"
    _description = "Material Grade"
    _order = "name"

    name = fields.Char(
        string="Grade",
        required=True,
        index=True
    )
    standard = fields.Char(
        string="Standard"
    )
    description = fields.Text(
        string="Description"
    )
    active = fields.Boolean(
        default=True
    )
    _sql_constraints = [
        (
            "material_grade_unique",
            "unique(name)",
            "This material grade already exists."
        )
    ]

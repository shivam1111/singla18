from odoo import api, fields, models


class MaterialElement(models.Model):
    _name = "material.element"
    _description = "Elements"
    _order = "code"

    name = fields.Char(
        string="Element Name",
        required=True
    )
    code = fields.Char(
        string="Symbol",
        required=True
    )
    active = fields.Boolean(default=True)
    _sql_constraints = [
        (
            "element_symbol_unique",
            "unique(code)",
            "Element symbol must be unique."
        )
    ]

class MaterialGradeSpecChem(models.Model):
    _name = "material.grade.spec.chem"
    _description = "Spec Limtis"

    spec_id = fields.Many2one(
        "material.grade.spec",
        string="Grade Specification",
        required=True,
        ondelete="cascade"
    )
    element_id = fields.Many2one(
        "material.element",
        string="Element",
        required=True,
        ondelete="restrict"
    )
    min_value = fields.Float(string="Min %",digits=(10, 3))
    max_value = fields.Float(string="Max %",digits=(10, 3))
    sequence = fields.Integer(
        default=10,
        help="Display order in chemistry tables"
    )
    _sql_constraints = [
        (
            "spec_element_unique",
            "unique(spec_id, element_id)",
            "This element is already defined for this specification."
        )
    ]

class MaterialGradeSpec(models.Model):
    _name = "material.grade.spec"
    _description = "Material Grade Specification"
    _order = "grade_id, name"
    _rec_name = "display_name"

    grade_id = fields.Many2one(
        "material.grade",
        string="Grade",
        required=True,
        ondelete="restrict",
        index=True
    )
    name = fields.Char(
        string="Spec Code",
        required=True,
        index=True
    )
    description = fields.Text(
        string="Description"
    )
    active = fields.Boolean(
        default=True
    )
    display_name = fields.Char(
        compute="_compute_display_name",
        store=True
    )
    chemistry_ids = fields.One2many(
        "material.grade.spec.chem",
        "spec_id",
        string="Chemistry Limits"
    )


    @api.depends("grade_id.name", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.grade_id.name} / {rec.name}"

    _sql_constraints = [
        (
            "grade_spec_unique",
            "unique(grade_id, name)",
            "This specification already exists for this grade."
        )
    ]

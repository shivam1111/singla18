from odoo import models, fields, api


class InclusionRatingLine(models.Model):
    _name = "inclusion.rating.line"
    _description = "Inclusion Rating Line"

    type = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')], string="Inclusion Type")
    thin = fields.Char('Thin')
    thick = fields.Char('Thick')
    composition_id = fields.Many2one('chemical.composition', 'Composition')

class CompositionLine(models.Model):
    _name = "composition.line"
    _description = "Composition Line"

    element_id = fields.Many2one('material.element', 'Element', required=True)
    min_val = fields.Char('Min')
    max_val = fields.Char('Max')
    actual_val = fields.Char('Actual')
    furnace_val = fields.Char('Furnace Report')
    sequence = fields.Integer('Sequence')
    heat_id = fields.Many2one('heat.heat',string = 'Heat',ondelete='cascade', index=True, copy=False, readonly=True)
    grade_id = fields.Many2one('material.grade.spec',"Grade")
    composition_id = fields.Many2one('chemical.composition', 'Test Certificate')



class ChemicalComposition(models.Model):
    _name = "chemical.composition"
    _description = "Chemical Compositions"

    def update_composition_lines(self):
        for c in self:
            c.line_ids.unlink() # Once executed change is grade_id is resetted. Hence we are saving the grade in previous line
            lines = [(5, 0, 0)]
            for i in self.grade_id.chemistry_ids:
                line_values = {'element_id':i.element_id.id,'min_val':i.min_value,'max_val':i.max_value}
                lines.append((0, 0, line_values))
            c.line_ids = lines
        return

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('chemical.composition') or _('New')
        result = super(ChemicalComposition, self).create(vals)
        return result

    @api.onchange('heat_id')
    def _onchange_heat_id(self):
        for c in self:
            lines = [(5, 0, 0)]
            heat_id = c.heat_id
            for i in heat_id.line_ids:
                line_values = {'element_id':i.element_id.id,'min_val':i.min_val,'max_val':i.max_val,
                               'furnace_val':i.furnace_val,'actual_val':i.actual_val}
                lines.append((0, 0, line_values))
            c.line_ids = lines
            c.heat_no = heat_id.name

    @api.depends('line_ids','line_ids.element_id','line_ids.actual_val')
    def _compute_carbon_equivalence(self):
        for tc in self:
            ce = 0.00
            nicrmo = 0.00
            for l in tc.line_ids:
                if l.element_id.code == 'C':
                    ce += float(l.actual_val)
                if l.element_id.code == 'Mn':
                    ce += float(l.actual_val)/6.00
                if l.element_id.code == 'Ni':
                    nicrmo += float(l.actual_val)
                if l.element_id.code == 'Mo':
                    nicrmo += float(l.actual_val)
                if l.element_id.code == 'Cr':
                    nicrmo += float(l.actual_val)
            tc.carbon_equivalence = round (ce + 1.00/20.00,2)
            tc.nicrmo = round(nicrmo,2)

    name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner','Partner')
    no_of_pieces = fields.Float('Number of Pieces')
    date = fields.Date('Date',default = fields.Date.today)
    truck_no = fields.Char('Vehicle No.')
    heat_no = fields.Char('Heat No.')
    grade_id = fields.Many2one('material.grade.spec','Grade')
    route_id = fields.Many2one('process.route','Process Route')
    heat_id = fields.Many2one('heat.heat', 'Select Heat No.')
    size = fields.Char('Size')
    color_code = fields.Char('Color Code')
    invoice_no = fields.Char('Invoice No.')
    line_ids = fields.One2many('composition.line','composition_id','Composition Line')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('sale.order'))
    inclusion_rating_ids = fields.One2many('inclusion.rating.line','composition_id','Inclusion Rating')
    min_hardness = fields.Char("Min. Hardness")
    max_hardness = fields.Char("Max. Hardness")
    complete_decarb = fields.Float('Complete Decarb')
    partial_decarb = fields.Float('Partial Decarb')
    grain_size = fields.Float('Grain Size')
    qty = fields.Char('Qty')
    ultimate_tensile_strength = fields.Float('Ultimate Tensile Strength (N/mm2)')
    yield_strength = fields.Float('Yield Strength (N/mm2)')
    elongation = fields.Float('Elongation %')
    reduction_ratio = fields.Char('Reduction Ratio')
    spark_test = fields.Boolean('Spark Test',default=False)
    is_xrf = fields.Boolean ('XRF Test',default=True)
    is_ut = fields.Boolean('UT Test')
    is_mpi = fields.Boolean('MPI')
    carbon_equivalence = fields.Float('Carbon Equivalence',default = 0.00,help = "%C + (%Mn/6) + 1/20",compute = '_compute_carbon_equivalence')
    nicrmo = fields.Float('Ni+Cr+Mo',compute = '_compute_carbon_equivalence')
    surface_inspection = fields.Selection([('ok','Ok'),('dentfree','Free from Dent')],default = 'dentfree')
    remarks = fields.Text("Remarks")
    lateral_bend = fields.Float("Lateral Bend")
    length = fields.Char("Length")


from odoo import models, fields, api
from odoo.tools.translate import _

class ProcessRoute(models.Model):
    _name = "process.route"
    _description = "Process Route"

    name = fields.Char('Route')

class IngotSize(models.Model):
    _name = "ingot.size"
    _description = "Ingot Size"

    name = fields.Char('Ingot Size')

class MillHeatChem(models.Model):
    _name = "mill.heat.chem"
    _description = "Heat Chemistry"

    heat_id = fields.Many2one( "heat.heat",
        required=True,
        ondelete="cascade"
    )
    element_id = fields.Many2one(
        "material.element",
        required=True
    )

    min_val = fields.Float("Min Value",digits=(10, 3))
    max_val = fields.Float("Max Value",digits=(10, 3))
    furnace_val  = fields.Float("Furnace Value %",digits=(10, 3))
    actual_val = fields.Float(
        string="Actual %",digits=(10, 3)
    )

    _sql_constraints = [
        (
            "heat_element_unique",
            "unique(heat_id, element_id)",
            "Element already exists for this heat."
        )
    ]


class Heat(models.Model):
    _name = 'heat.heat'
    _description = "Heats"

    def action_view_production_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Production Lines',
            'res_model': 'mill.production.line',
            'view_mode': 'list,form',
            'domain': [('heat_ids', 'in', self.id)],
            'context': {
                'default_heat_ids': [(4, self.id)],
                'create': False,
                'edit': False,
                'delete': False,
            },
        }

    @api.onchange('grade_spec_id')
    def _onchange_grade_id(self):
        data = []
        # First check if the record is being created or grade_id value if being changed
        # if self._context.get('onchange', False):
        # This means the grade_id field value is being changed
        for i in self.grade_spec_id.chemistry_ids:
            data.append((0, 0, {'element_id': i.element_id, 'min_val': i.min_value, 'max_val': i.max_value}))
        self.line_ids = data

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args+=['|',('furnace_heat_no', operator, name),('name',operator,name)]
        return  super(Heat, self).name_search(name, args, operator, limit)

    # 1. This controls WHAT the user sees inside the dropdown list rows
    @api.depends('name', 'furnace_heat_no')
    def _compute_display_name(self):
        for record in self:
            record.display_name = '[' + str(record.furnace_heat_no or "") + ']' + ' ' + record.name

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('heat.heat') or _('New')
        result = super(Heat, self).create(vals)
        return result

    def action_validate_chemistry(self):
        for heat in self:
            res = heat._validate_chemistry()
            heat.chemistry_result = res['result']
            heat.chemistry_fail_reason = res['message']

    def _validate_chemistry(self):
        self.ensure_one()
        result_lines = []
        failed = False

        # Build lookup of actual chemistry
        actual_map = {
            line.element_id.id: line.actual_val
            for line in self.line_ids
            if line.element_id
        }

        for limit in self.grade_spec_id.chemistry_ids:
            actual = actual_map.get(limit.element_id.id)

            if actual is None:
                failed = True
                result_lines.append(
                    f"{limit.element_id.code}: Missing value"
                )
                continue

            if limit.min_value and actual < limit.min_value:
                failed = True
                result_lines.append(
                    f"{limit.element_id.code}: {actual} < Min {limit.min_value}"
                )

            if limit.max_value and actual > limit.max_value:
                failed = True
                result_lines.append(
                    f"{limit.element_id.code}: {actual} > Max {limit.max_value}"
                )
        if failed:
            self.write({"state":'rejected'})
        else:
            self.write({"state": 'pass'})

        return {
            'result': 'fail' if failed else 'pass',
            'message': "\n".join(result_lines)
        }

    def _get_default_route(self):
        try:
            return self.env.ref('mill_core.data_process_route_1').id
        except ValueError:
            return False

    name = fields.Char('SSAI Heat No.', default='/', required=True)
    display_name = fields.Char(compute='_compute_display_name',store=True)
    route_id = fields.Many2one('process.route',"Process Route",
                               required=True,default=lambda self:self._get_default_route())
    furnace_heat_no = fields.Char('Supplier Heat No.', required=True)
    grinding = fields.Boolean('Grinding')
    date = fields.Char('Date Rcvd', required=True, default=fields.Date.today)
    partner_id = fields.Many2one('res.partner',string=" Supplier",required=True)
    grade_spec_id = fields.Many2one('material.grade.spec',string="Grade",)
    print_supplier = fields.Boolean('Print Supplier',help="Print Supplier in Report")
    line_ids = fields.One2many(
        "mill.heat.chem",
        "heat_id",
        string="Chemistry"
    )
    surface_inspection = fields.Boolean('Surface Inspection')
    xrf_tested = fields.Boolean('XRF Tested')
    state = fields.Selection(
        [('draft', 'Draft'), ('pass', 'Pass'), ('rejected', 'Rejected')],
        default='draft', string="State")
    remarks = fields.Text('Remarks')
    size = fields.Many2one('ingot.size', 'Ingot Size')
    supervisor_id = fields.Many2one('res.users', 'Supervisor', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'))
    chemistry_result = fields.Selection(
        [('pass', 'PASS'), ('fail', 'FAIL')],
        readonly=True
    )
    chemistry_fail_reason = fields.Text(readonly=True)
    move_id = fields.Many2one('stock.move','Receipt')
    size_id = fields.Many2one('size.size','Size',help="Used in case of trading if we want to add sizes manually")
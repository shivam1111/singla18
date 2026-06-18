from odoo import models, fields,api
from odoo.exceptions import UserError,AccessError
from odoo.tools.translate import _

SELECTION = [('draft','Draft'),('done','Done')]

class MillProductionLine(models.Model):
    _name = "mill.production.line"
    _description = "Mill Production Line"

    def action_return_picking(self):
        self.ensure_one()
        if self.picking_id and not self.return_picking_id:
            picking = self.env['stock.picking'].create({
                'partner_id': self.picking_id.partner_id.id,
                'location_dest_id': self.env.ref(
                    'stock.stock_location_stock'
                ).id,
                'picking_type_id': self.env.ref('stock.picking_type_internal').id,
                'location_id': self.product_id.property_stock_production.id,
                'origin': "Return of " + self.picking_id.name + " / " + self.name,
                'order_id':self.production_id.id,
                'move_ids_without_package': [
                    (0, 0, {
                        'name': '/',
                        'product_id': self.product_id.id,
                        'product_uom_qty': self.qty,
                        'quantity': self.qty
                    }),
                ]
            })
            picking.button_validate()
            self.return_picking_id = picking
            self.qty = 0.0

    def action_view_production_order_line(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('View'),
            'res_model': 'mill.production.line',
            'view_mode': 'form',
            'res_id': self.id,
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
        }

    @api.model_create_multi
    def create(self, vals):
        if self.env.user.has_group('stock.group_stock_manager'):
            for val in vals:
                val['name'] = self.env['ir.sequence'].next_by_code('mill.production.line') or _('New')
            result = super(MillProductionLine, self).create(vals)
            return result
        else:
            raise UserError(_('You are not allowed to create this record'))

    @api.onchange('pcs', 'kg_per_pc')
    def _compute_qty(self):
        for line in self:
            line.qty = (line.kg_per_pc * line.pcs) / 1000

    @api.depends('scrap', 'qty')
    def _compute_scrap(self):
        for line in self:
            try:
                line.scrap_percentage = (line.scrap * 100) / (1000 * line.qty)
            except ZeroDivisionError:
                line.scrap_percentage = 0.00

    name = fields.Char('Name')
    sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
    qty = fields.Float('Qty',default=0.0)
    pcs = fields.Integer('Pcs')
    partner_id = fields.Many2one('res.partner', help="Mostly furnce, but depends on usage", string="Furnace")
    heat_ids = fields.Many2many('heat.heat',string ='Heats')
    size_id = fields.Many2one('size.size',string = "Size",required=True)
    batch = fields.Float('No. of Batch',help = "Dhakku")
    kg_per_pc = fields.Float('Kg/pc')
    production_id = fields.Many2one('mill.production','Production',ondelete='cascade')
    scrap = fields.Float('Scrap')
    scrap_percentage = fields.Float('Scrap%',compute = "_compute_scrap")
    product_id = fields.Many2one('product.product','Grade',domain=[('product_role','=','raw')],required=True)
    remarks = fields.Char("Remarks")
    picking_id = fields.Many2one('stock.picking','Stock Picking',help="internal transfer")
    return_picking_id = fields.Many2one('stock.picking','Return Stock Picking',help="internal transfer")
    state = fields.Selection(SELECTION,string="State",related='production_id.state',store=True)
    production_line_id = fields.Many2one('production.order.line',string = "Bundle No.")


class MillProduction(models.Model):
    _name = 'mill.production'
    _description = "Mill Production Register"
    _order = 'date asc'

    @api.depends('solar_units_opening_kwh','solar_units_closing_kwh',
                 'solar_units_opening_kwh_2',
                 'solar_units_closing_kwh_2')
    def _compute_solar_production(self):
        for po in self:
            po.solar_net = (po.solar_units_closing_kwh-po.solar_units_opening_kwh)+\
                           (po.solar_units_closing_kwh_2 - po.solar_units_opening_kwh_2) * 80

    @api.depends('kwh_closing','kwh_opening','total_production')
    def _compute_units(self):
        for po in self:
            po.total_units = (po.kwh_closing - po.kwh_opening)*15

    @api.depends('kwh_closing','kwh_opening','total_production')
    def _compute_units_mt(self):
        for po in self:
            try:
                po.units_per_mt = po.total_units / po.total_production
            except ZeroDivisionError:
                po.units_per_mt = 0.00

    @api.depends('total_production', 'production_line_ids.scrap')
    def _compute_scrap(self):
        for po in self:
            total = 0.00
            for i in po.production_line_ids:
                total = total + i.scrap
            po.total_scrap = total

    @api.depends('total_production', 'production_line_ids.scrap')
    def _compute_scrap_percentage(self):
        for po in self:
            try:
                po.scrap_percentage = (po.total_scrap * 100) / (1000 * po.total_production)
            except ZeroDivisionError:
                po.scrap_percentage = 0.00

    @api.depends('png_units_opening', 'png_units_closing')
    def _compute_png_units(self):
        for po in self:
            po.png_net = po.png_units_closing - po.png_units_opening

    @api.depends('png_units_opening', 'png_units_closing')
    def _compute_png_mt(self):
        for po in self:
            try:
                po.png_net_mt = po.png_net/po.total_production
            except ZeroDivisionError:
                po.png_net_mt = 0.00

    @api.depends('production_line_ids', 'production_line_ids.qty','hours')
    def _compute_total_production(self):
        for po in self:
            total = 0.00
            for i in po.production_line_ids:
                total = total + i.qty
            po.total_production = total
            try:
                po.production_mt = total/po.hours
            except ZeroDivisionError:
                po.production_mt = 0.0

    @api.depends('production_line_ids', 'production_line_ids.qty', 'coal')
    def _compute_coal_mt(self):
        for po in self:
            self.coal_pmt = self.coal/po.total_production

    @api.model_create_multi
    def create(self, vals):
        if self.env.user.has_group('stock.group_stock_manager'):
            for val in vals:
                val['name'] = self.env['ir.sequence'].next_by_code('mill.production') or _('New')
            result = super(MillProduction, self).create(vals)
            return result
        else:
            raise UserError(_('You are not allowed to create this record'))

    @api.depends('production_line_ids.size_id')
    def _compute_size_ids(self):
        for rec in self:
            rec.size_ids = rec.production_line_ids.mapped('size_id')

    def action_draft(self):
        if not self.env.user.has_group('base.group_system'):
            raise AccessError("Access Denied: Only administrators can execute this action.")
        else:
            self.state = "draft"

    def action_confirm(self):
        for order in self:
            if order.state != 'draft':
                continue
            for line in order.production_line_ids:
                if line.picking_id:
                    continue
                picking = self.env['stock.picking'].create({
                    'partner_id':line.partner_id.id,
                    'location_id':self.env.ref(
                        'stock.stock_location_stock'
                    ).id,
                    'picking_type_id':self.env.ref('stock.picking_type_internal').id,
                    'location_dest_id':line.product_id.property_stock_production.id,
                    'origin':order.name+" / "+line.name,
                    'order_id':order.id,
                    'move_ids_without_package':[
                        (0, 0, {
                            'name':'/',
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.qty,
                            'quantity':line.qty
                        }),
                    ]
                })
                picking.button_validate()
                line.picking_id = picking
            order.state = 'done'
        return True

    @api.depends('production_line_ids','production_line_ids.picking_id', 'production_line_ids.return_picking_id')
    def _compute_all_picking_ids(self):
        for production in self:
            # pickings = self.env['stock.picking']
            # # Loop through the lines to gather both types of pickings
            # for line in production.production_line_ids:
            #     if line.picking_id:
            #         pickings |= line.picking_id
            #     if line.return_picking_id:
            #         pickings |= line.return_picking_id
            # Remove any duplicate IDs (just in case) and assign to the field
            # In computed One2many fields, you write the recordset or IDs directly
            production.all_picking_ids = self.env['stock.picking'].search([('order_id', '=', production.id)])

    name = fields.Char('Name', default='/', required=True)
    state = fields.Selection(SELECTION,string='State',default='draft')
    date = fields.Date('Date', required=True, default=fields.Date.today)
    total_production = fields.Float('Total Production', compute="_compute_total_production", store=True)
    production_mt = fields.Float('Production Rate', compute="_compute_total_production", store=True, digits=(16, 2))
    total_scrap = fields.Float('Total Scrap', compute="_compute_scrap", store=True)
    scrap_percentage = fields.Float('Scrap%', compute="_compute_scrap_percentage")
    remarks = fields.Text('Remarks')
    md_mt = fields.Float('MD/MT')
    hours = fields.Float('Total Hours')
    furnace_kara = fields.Float('Furnace Kara')
    mill_kara = fields.Float('Mill Kara')
    miss_roll = fields.Text('Miss Roll')
    production_line_ids = fields.One2many('mill.production.line', 'production_id', 'Production Order')
    total_units = fields.Float("Total Units Consumed", compute="_compute_units", store=True)
    units_per_mt = fields.Float('Units/MT', compute='_compute_units_mt', digits=(16, 2))
    kwh_mt = fields.Float('KWH/MT', compute='_compute_kwh_mt')
    water_units_opening = fields.Float('Water Units Opening')
    water_units_closing = fields.Float('Water Units Closing')
    solar_units_opening_kwh = fields.Float('Solar Units Opening (KWH)')
    solar_units_closing_kwh = fields.Float('Solar Units Closing (KWH)')
    solar_net = fields.Float('Solar Production', compute='_compute_solar_production',store=True)
    solar_units_opening_kvah = fields.Float('Solar Units Opening (KVaH)')
    solar_units_closing_kvah = fields.Float('Solar Units Closing (KVaH)')
    solar_units_opening_kwh_2 = fields.Float('Solar Units Opening (KWH)')
    solar_units_closing_kwh_2 = fields.Float('Solar Units Closing (KWH)')
    solar_units_opening_kvah_2 = fields.Float('Solar Units Opening (KVaH)')
    solar_units_closing_kvah_2 = fields.Float('Solar Units Closing (KVaH)')
    png_units_opening = fields.Float('PNG Opening')
    png_units_closing = fields.Float('PNG Closing')
    kwh_opening = fields.Float('KWH Op.')
    kwh_closing = fields.Float('KWH Cl.')
    kva_opening = fields.Float('KVA Op.')
    kva_closing = fields.Float('KVA Cl.')
    png_net = fields.Float("Total PNG", compute='_compute_png_units', store=True)
    png_net_mt = fields.Float('PNG (SCM/MT)',compute="_compute_png_mt",digits=(16, 2))
    size_ids = fields.Many2many(
        'size.size',
        compute='_compute_size_ids',
        store=True,
        string='Sizes'
    )
    order_id = fields.Many2one('production.order','Production Order')
    all_picking_ids = fields.Many2many(
        'stock.picking',
        compute='_compute_all_picking_ids',
        string='All Stock Moves (Delivery & Returns)',
        compute_sudo=True
    )
    coal = fields.Float(string="Coal")
    coal_pmt = fields.Float('Coal/MT', compute='_compute_coal_mt', digits=(16, 2))
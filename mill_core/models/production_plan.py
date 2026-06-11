from odoo import models, fields, api


class SaleLineSelectionWizard(models.TransientModel):
    _name = 'sale.line.selection.wizard'
    _description = 'Wizard to select Sale Order Lines'

    # Field containing the lines you will pick from
    sale_order_line_ids = fields.Many2many(
        'sale.order.line',
        string="Sale Order Lines",
        domain=[('state', 'in', ['sale'])]  # Optional: Only active lines
    )

    def action_confirm_selection(self):
        """ Transports chosen lines back to the active record """
        active_id = self.env.context.get('active_main_id')
        print("Active-------",active_id)
        if not active_id:
            return

        main_record = self.env['sale.order.line'].browse(active_id)

        # Populate data into the main record's Many2many link field
        # main_record.write({
        #     'sale_line_ids': [(6, 0, self.sale_order_line_ids.ids)]
        # })

        return {'type': 'ir.actions.client', 'tag': 'reload'}


class ProductionPlan(models.Model):
    _name = "production.plan"
    _description = "Production Planning"

    def action_open_sale_lines_wizard(self):
        """ Opens the custom wizard with preset grouped criteria """
        return {
            'name': 'Select Sale Order Lines',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.line.selection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                # Passes group_by to the Many2many list view inside the wizard form
                'search_default_group_by_partner': 1,
                'search_default_group_by_order': 1,
                'active_main_id': self.id,  # Keep track of where the action started
            }
        }

    size_id = fields.Many2one("size.size",string = 'Size')
    partner_id = fields.Many2one('res.partner',string = 'Partner')
    grade_id = fields.Many2one('material.grade.spec','Grade')
    qty = fields.Float("Qty")
    remarks = fields.Char("Remarks")


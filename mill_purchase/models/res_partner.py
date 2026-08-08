from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"
    _desc = "Mill Purchase Partner"


    # Field to select the Broker on the contract
    broker_id = fields.Many2one(
        'res.partner',
        string='Broker',
        help="Broker responsible for coordinating this raw material supply run."
    )
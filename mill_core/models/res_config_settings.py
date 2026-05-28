from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings' # Use a dot, not an underscore

    mill_google_drive_json_path = fields.Char(
        string="Google JSON Path",
        config_parameter='mill_google_drive.json_path'
    )
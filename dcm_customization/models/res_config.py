from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    privacy_policy_url = fields.Char("Privacy Policy URL",related="company_id.privacy_policy_url")

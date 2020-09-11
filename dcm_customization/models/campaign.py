from odoo import api, fields, models


class Campaign(models.Model):
    _name = 'utm.campaign'
    _inherit = ['utm.campaign', 'image.mixin']

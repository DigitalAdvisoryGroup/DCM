# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MailThemes(models.Model):
    _name = 'mail.themes'
    _description = 'Mail Theme Custom'

    name = fields.Char("Name")
    image = fields.Binary("Image")
    body_arch = fields.Html("Content")
    body_html = fields.Html("Content")
    

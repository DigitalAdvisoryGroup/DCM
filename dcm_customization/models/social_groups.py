# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class SocialPartnerGroups(models.Model):
    _name = 'social.partner.group'
    _description = "Social Groups"
    _rec_name = "name"

    name = fields.Char("Name",required=True)
    partner_ids = fields.Many2many('res.partner','social_groups_partners',string="Partner",required=True)

    
# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.modules.module import get_module_resource
import base64

class SocialPartnerGroups(models.Model):
    _name = 'social.partner.group'
    _inherit = ['image.mixin']
    _description = "Social Groups"
    _rec_name = "name"

    @api.model
    def _default_image(self):
        image_path = get_module_resource('dcm_customization', 'static/src/img', 'bit.png')
        return base64.b64encode(open(image_path, 'rb').read())

    image_1920 = fields.Image(default=_default_image)
    name = fields.Char("Name",required=True)
    type = fields.Selection([('normal','Normal'),('functional','Functional')], string="Type", default="normal")
    partner_ids = fields.Many2many('res.partner','social_group_partner_rel','social_group_id','partner_id',string="Partner")
    fun_partner_ids = fields.Many2many('res.partner','social_group_fun_partner_rel','social_group_id','partner_id',string="Partner")
    parent_id = fields.Many2one("social.partner.group",string="Parent")
    child_ids = fields.One2many('social.partner.group','parent_id',string="Child Groups")
    total_count = fields.Integer("Total Subscribers",compute="compute_total_count")
    child_total_count = fields.Integer("Child Subscribers",compute="compute_total_count")


    # oe1_id = fields.Char("OE 1")
    # oe2_id = fields.Char("OE 2")
    # oe3_id = fields.Char("OE 3")
    # oe_key = fields.Char("OE-Key")
    # ou1_id = fields.Char("OU 1")
    # ou2_id = fields.Char("OU 2")
    # ou3_id = fields.Char("OU 3")
    # ou_key = fields.Char("Org Unit Key")

    parent2_id = fields.Char("Parent (new)")
    code = fields.Char("Code")
    
    def action_subscriber_list(self):
        action = self.env.ref('contacts.action_contacts').read()[0]
        partner_ids = self.child_ids.mapped('partner_ids').ids
        action['domain'] = [('id', 'in', partner_ids)]
        return action

    def action_subscriber_list_total(self):
        action = self.env.ref('contacts.action_contacts').read()[0]
        partner_ids = self.child_ids.mapped('partner_ids').ids + self.partner_ids.ids
        action['domain'] = [('id', 'in', partner_ids)]
        return action

    @api.depends('partner_ids','child_ids')
    def compute_total_count(self):
        for record in self:
            partner_ids = record.child_ids.mapped('partner_ids').ids
            record.child_total_count = len(partner_ids)
            record.total_count = len(set(partner_ids+record.partner_ids.ids))



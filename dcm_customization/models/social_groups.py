# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class SocialPartnerGroups(models.Model):
    _name = 'social.partner.group'
    _description = "Social Groups"
    _rec_name = "name"

    name = fields.Char("Name",required=True)
    partner_ids = fields.Many2many('res.partner','social_group_partner_rel','social_group_id','partner_id',string="Partner")
    parent_id = fields.Many2one("social.partner.group",string="Parent")
    child_ids = fields.One2many('social.partner.group','parent_id',string="Child Groups")
    total_count = fields.Integer("Total Subscribers",compute="compute_total_count")
    child_total_count = fields.Integer("Child Subscribers",compute="compute_total_count")
    
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



# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.modules.module import get_module_resource
import base64
import logging
_logger = logging.getLogger(__name__)


class SocialPartnerGroupsType(models.Model):
    _name = 'social.partner.group.type'
    _description = "Social Groups Type"
    _rec_name = "name"

    name = fields.Char("Name", required=True,translate=True)
    # type = fields.Selection([('normal', 'Normal'), ('functional', 'Functional')], string="Type", default="normal")


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
    type_id = fields.Many2one("social.partner.group.type",string="Type")
    # type = fields.Selection(related="type_id.type", string="Type", store=True)
    partner_ids = fields.Many2many('res.partner','social_group_partner_rel','social_group_id','partner_id',string="Partner")
    # fun_partner_ids = fields.Many2many('res.partner','social_group_fun_partner_rel','social_group_id','partner_id',string="Partner")
    parent_id = fields.Many2one("social.partner.group",string="Parent")
    child_ids = fields.One2many('social.partner.group','parent_id',string="Child Groups")
    total_count = fields.Integer("Total Subscribers",compute="compute_total_count")
    child_total_count = fields.Integer("Child Subscribers",compute="compute_total_count")

    group_owner_id = fields.Many2one("res.partner", string="Group Owner")
    is_org_unit = fields.Boolean("Org Unit Flag")
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


    def get_social_group_details(self):
        self.ensure_one()
        data = []
        if self:
            data.append({
                "name": self.name,
                "group_owner_name": self.group_owner_id and self.group_owner_id.name or '',
                "group_owner_id": self.group_owner_id and self.group_owner_id.id or '',
                "total_count": len(self.partner_ids),
                "code": self.code,
                "members": [{"id": x.id,"name": x.name,"function": x.function} for x in self.partner_ids],
                "org_data": self.get_all_heirarchy_data()
            })
        _logger.info("----------social---data-----------%s",data)
        return {"data": data}

    def get_all_heirarchy_data(self):

        results = self.env['social.partner.group'].sudo().read_group([('id','in',self.ids)], ['name'], ['type_id'])
        results = {m['type_id'] and str(m['type_id'][1]) or 'Unknown': self.env['social.partner.group'].sudo().search_read(m['__domain'], ['type_id']) for m in results}
        hierarchy_dict = []
        for s_key, s_group in results.items():
            hierarchy_data = []
            temp_dict = {'name': s_key,'children': []}
            for main_data in s_group:
                hierarchy_parent_data = self.get_heirarchy_data(main_data.get('id'))
                hierarchy_data.append(hierarchy_parent_data)
                temp_dict['children'].append(hierarchy_parent_data)
            hierarchy_dict.append(temp_dict)
        _logger.info("0-------------hierarchy_parents----social--------%s-",hierarchy_dict)
        return hierarchy_dict

    def get_heirarchy_data(self, group_id):
        sc_groups = self.env['social.partner.group'].sudo().browse(group_id)
        group_data = {'id': sc_groups.id, 'name': sc_groups.name, 'children': []}
        hierarchy_parents = self.get_parent_data(group_id, group_data)
        return hierarchy_parents

    def get_parent_data(self,group_id,group_data):
        sc_groups = self.env['social.partner.group'].sudo().browse(group_id)
        if sc_groups:
            parent_sg_id = self.env['social.partner.group'].sudo().search([('code', '=', sc_groups.parent2_id)], limit=1)
            if parent_sg_id.parent2_id:
                if group_data:
                    pr_group_data = {'id' : parent_sg_id.id,'name' :parent_sg_id.name,'children' : [group_data]}
                    return self.get_parent_data(parent_sg_id.id,pr_group_data)
                else:
                    group_data = {'id' : parent_sg_id.id,'name' :parent_sg_id.name,'children' : []}
                    return self.get_parent_data(parent_sg_id.id,group_data)
            else:
                if group_data:
                    return {'id' : parent_sg_id.id,'name' :parent_sg_id.name,'children' : [group_data]}
                else:
                    return {'id' : parent_sg_id.id,'name' :parent_sg_id.name,'children' : []}



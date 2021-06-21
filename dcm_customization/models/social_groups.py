# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource
import base64
from werkzeug.urls import url_join
import time
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class SocialPartnerGroupsType(models.Model):
    _name = 'social.partner.group.type'
    _inherit = ['image.mixin']
    _description = "Social Groups Type"
    _rec_name = "name"

    @api.model
    def _default_image(self):
        image_path = get_module_resource('dcm_customization', 'static/src/img', 'bit.png')
        return base64.b64encode(open(image_path, 'rb').read())

    image_1920 = fields.Image(default=_default_image)
    name = fields.Char("Name", required=True,translate=True)
    is_org_unit = fields.Boolean(string="Org Unit Flag")
    is_user_updatable = fields.Boolean(string="User updatable")
    is_restrict_max_group_assing_user = fields.Boolean(string="Restrict Max Groups Per user")
    max_group_assing_user = fields.Integer(string="Max Groups Per user")
    # type = fields.Selection([('normal', 'Normal'), ('functional', 'Functional')], string="Type", default="normal")


    def get_social_group_data(self,partner_id=False):
        res = {"selected_data": [], "unselected_data": []}
        if partner_id:
            partner_browse = self.env['res.partner'].browse(int(partner_id))
            sel_groups = partner_browse.social_group_id.filtered(lambda x: x.type_id.id == self.id)
            if sel_groups:
                res['selected_data'] = [{
                    "id": x.id,
                    "name": x.name,
                    "code": x.code or ''
                } for x in sel_groups]
            unsel_groups = self.env['social.partner.group'].search([('type_id','=',self.id),('is_org_unit','=',True)])
            if unsel_groups:
                res['unselected_data'] = [{
                    "id": x.id,
                    "name": x.name,
                    "code": x.code or ''
                } for x in unsel_groups]
        _logger.info("-------group-------update----------%s",res)
        return {"data": res}




class SocialPartnerGroups(models.Model):
    _name = 'social.partner.group'
    _inherit = ['image.mixin']
    _description = "Social Groups"
    _rec_name = "name"

    # @api.model
    # def _default_image(self):
    #     image_path = get_module_resource('dcm_customization', 'static/src/img', 'bit.png')
    #     return base64.b64encode(open(image_path, 'rb').read())

    # image_1920 = fields.Image("Image", default=_default_image)
    name = fields.Char("Name",required=True)
    type_id = fields.Many2one("social.partner.group.type",string="Type")
    # type = fields.Selection(related="type_id.type", string="Type", store=True)
    partner_ids = fields.Many2many('res.partner','social_group_partner_rel','social_group_id','partner_id',string="Partner")
    # fun_partner_ids = fields.Many2many('res.partner','social_group_fun_partner_rel','social_group_id','partner_id',string="Partner")
    parent_id = fields.Many2one("social.partner.group",string="Parent")
    child_ids = fields.One2many('social.partner.group','parent_id',string="Child Groups")
    total_count = fields.Integer("Total Subscribers",compute="compute_total_count")
    child_total_count = fields.Integer("Child Subscribers",compute="compute_total_count")
    current_subscribers_count = fields.Integer("Child Subscribers", compute="_compute_subscriber_count")
    current_and_childs_subscribers_count = fields.Integer("Child Subscribers", compute="_compute_subscriber_count")
    group_owner_id = fields.Many2one("res.partner", string="Group Owner")
    is_org_unit = fields.Boolean(string="Org Unit Flag")
    parent2_id = fields.Char("Parent (new)")
    code = fields.Char("Code")
    last_import_flag = fields.Char("Last import flag")

    @api.constrains('partner_ids', 'type_id')
    def _check_group_assing_users(self):
        for group in self:
            if group.type_id.is_restrict_max_group_assing_user and group.partner_ids:
                for part in group.partner_ids:
                    group_check = self.search_count([('id','!=',group.id),('type_id','=',group.type_id.id),('partner_ids','in',part.ids)])
                    if group_check >= group.type_id.max_group_assing_user:
                        raise ValidationError(_('%s can not belongs to more groups!')%(part.name))

    def get_mobile_sunburst_child_data(self, sunburst_data):
        if self.code:
            child_sg_ids = self.search([('is_org_unit', '=', True), ('parent2_id', '=', self.code)])
            if child_sg_ids:
                for child_sg in child_sg_ids:
                    sunburst_data.append({'name': child_sg.name, 'id': child_sg.id, 'parent': self.id, 'value': self.current_subscribers_count})
                    child_sg.get_mobile_sunburst_child_data(sunburst_data)
                return sunburst_data
            else:
                return sunburst_data
        else:
            return sunburst_data

    def get_mobile_sunburst_data(self):
        sunburst_data = [{'name': self.name, 'id': self.id, 'parent': 0, 'value': self.current_subscribers_count}]
        sunburst_data = self.get_mobile_sunburst_child_data(sunburst_data)
        return sunburst_data

    def get_child_count(self):
        if self.code:
            child_sg_ids = self.env['social.partner.group'].sudo().search([('is_org_unit', '=', True), ('parent2_id', '=', self.code)])
            if child_sg_ids:
                count = 0
                for cs in child_sg_ids:
                    count += cs.get_child_count()
                return len(self.partner_ids.ids) + count
            else:
                return len(self.partner_ids.ids)
        else:
            return len(self.partner_ids.ids)

    @api.depends('partner_ids')
    def _compute_subscriber_count(self):
        for record in self:
            record.current_subscribers_count = len(record.partner_ids.ids)
            record.get_child_count()
            record.current_and_childs_subscribers_count = record.get_child_count()

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


    def get_social_group_details(self,partner_id=False):
        self.ensure_one()
        data = []
        if self:
            partner_browse = self.env['res.partner'].browse(int(partner_id))
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            data.append({
                "group_image": url_join(base_url, '/web/myimage/social.partner.group.type/%s/image_512/?%s' % (self.type_id.id, str(int(time.time() * 100000))[-15:])),
                "name": self.name,
                "group_owner_name": self.group_owner_id and self.group_owner_id.name or '',
                "group_owner_id": self.group_owner_id and self.group_owner_id.id or '',
                "group_owner_function": self.group_owner_id and self.group_owner_id.function or '',
                "group_owner_mlevel": self.group_owner_id and self.group_owner_id.mlevel_id and self.group_owner_id.mlevel_id.name or '',
                "group_owner_id": self.group_owner_id and self.group_owner_id.id or '',
                "group_owner_image_url": self.group_owner_id and url_join(base_url,
                                 '/web/myimage/res.partner/%s/image_128/?%s' % (self.group_owner_id.id, self.group_owner_id.file_name_custom)) or '',
                "total_count": len(self.partner_ids),
                "code": self.code,
                "members": [{"image_url": url_join(base_url,
                                 '/web/myimage/res.partner/%s/image_128/?%s' % (x.id, x.file_name_custom)),"id": x.id,"name": x.name,"function": x.function} for x in self.partner_ids],
                "org_data": self.get_all_heirarchy_data(),
                "org_data_latest": self.with_context(lang=partner_browse.lang).get_all_heirarchy_data_latest(),
                'is_display_chart': partner_browse and partner_browse.is_display_chart or False
            })
        _logger.info("----------social---data-----------%s",data)
        return {"data": data}

    def get_all_heirarchy_data_latest(self):
        data = self.get_all_heirarchy_data()
        output = [{'name': data[0]['name'],'id': 0}]
        in_pass = data[0]['children']
        def add_child(in_pass, output):
            output.append({'id': in_pass['id'], 'name': in_pass['name']})
            if in_pass['children']:
                add_child(in_pass['children'][0], output)
            else:
                return output
        add_child(in_pass[0], output)
        return output

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
        if not sc_groups.parent2_id:
            return {'id': sc_groups.id, 'name': sc_groups.name, 'children': []}
        group_data = {'id': sc_groups.id, 'name': sc_groups.name, 'children': []}
        hierarchy_parents = self.get_parent_data(group_id, group_data)
        return hierarchy_parents

    def get_parent_data(self,group_id,group_data):
        sc_groups = self.env['social.partner.group'].sudo().browse(group_id)
        if sc_groups:
            parent_sg_id = self.env['social.partner.group'].sudo().search([('is_org_unit','=',True),('code', '=', sc_groups.parent2_id)], limit=1)
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

class SocialGroupUpdate(models.Model):
    _name = "social.group.update"

    partner_id = fields.Many2one("res.partner", "Partner")
    name = fields.Char(related="partner_id.name", string="Name", store=True)
    old_group_ids = fields.Many2many("social.partner.group", "rel_social_partner_group_old_update", "group_update_old_id","group_old_id", string="Old Groups")
    new_group_ids = fields.Many2many("social.partner.group", "rel_social_partner_group_new_update", "group_update_new_id","group_new_id", string="New Groups")
    social_group_type_id = fields.Many2one("social.partner.group.type",string="Group Type")


    def update_social_group(self, partner_id=False,new_group=False,group_type=False):
        res_id = False
        if partner_id:
            partner_browse = self.env['res.partner'].browse(int(partner_id))
            vals = {
                "social_group_type_id": group_type,
                "partner_id": int(partner_id),
                "old_group_ids": partner_browse.social_group_id.filtered(lambda x: x.type_id.id == int(group_type)).ids,
                "new_group_ids": new_group
            }
            res_id = self.create(vals)
            res_id.assing_parnter_group()
        return res_id.id


    def assing_parnter_group(self):
        if self.old_group_ids:
            self.old_group_ids.write({'partner_ids': [(3, self.partner_id.id)]})
        if self.new_group_ids:
            self.new_group_ids.write({'partner_ids': [(4, self.partner_id.id)]})


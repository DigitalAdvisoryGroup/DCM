from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.addons.mass_mailing.models.mailing import MassMailing

class MassMailings(models.Model):
    _inherit = 'mailing.mailing'

    social_groups_id = fields.Many2many('social.partner.group',string="Social Groups(Recipients)")
    is_social_group = fields.Boolean("Social Group",compute="compute_is_social")
    is_include_all = fields.Boolean("Is Include All Recipients ?")

    @api.onchange('is_include_all')
    def onchange_is_include_all(self):
        if self.social_groups_id:
            if self.is_include_all:
                partner_ids = self.social_groups_id.mapped('partner_ids').ids
                if self.social_groups_id.mapped("child_ids"):
                    partner_ids += self.social_groups_id.mapped(
                        "child_ids").mapped('partner_ids').ids
            else:
                partner_ids = self.social_groups_id.mapped(
                    'partner_ids').filtered(
                    lambda x: not x.is_token_available).ids
                if self.social_groups_id.mapped("child_ids"):
                    partner_ids += self.social_groups_id.mapped(
                        "child_ids").mapped('partner_ids').filtered(
                        lambda x: not x.is_token_available).ids
            self.mailing_domain = repr([('id', 'in', list(set(partner_ids)))])

    @api.onchange('social_groups_id')
    def groups_id_onchange_(self):
        if self.social_groups_id:
            contact = self.env['ir.model'].search([('model','=','res.partner')])
            self.mailing_model_id = contact.id
            if self.is_include_all:
                partner_ids = self.social_groups_id.mapped('partner_ids').ids
                if self.social_groups_id.mapped("child_ids"):
                    partner_ids += self.social_groups_id.mapped("child_ids").mapped('partner_ids').ids
            else:
                partner_ids = self.social_groups_id.mapped('partner_ids').filtered(lambda x: not x.is_token_available).ids
                if self.social_groups_id.mapped("child_ids"):
                    partner_ids += self.social_groups_id.mapped("child_ids").mapped('partner_ids').filtered(lambda x: not x.is_token_available).ids
            self.mailing_domain = repr([('id','in',list(set(partner_ids)))])
        else:
            # mailing = self.env['ir.model'].search([('model','=','mailing.list')])
            self.mailing_model_id = False
            self.mailing_model_real = "mailing.contact"
            self.mailing_domain = False

    @api.depends('social_groups_id')
    def compute_is_social(self):
        for record in self:
            record.is_social_group = False
            if record.social_groups_id:
                record.is_social_group = True

    
    def action_statistics(self):
        action = self.env['ir.actions.act_window'].for_xml_id('mass_mailing', 'mailing_trace_action')
        action['domain'] = [('mass_mailing_id','=',self.id)]
        return action


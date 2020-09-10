from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.addons.mass_mailing.models.mailing import MassMailing

class MassMailings(models.Model):
    _inherit = 'mailing.mailing'

    social_groups_id = fields.Many2many('social.partner.group',string="Social Groups(Recipients)")
    is_social_group = fields.Boolean("Social Group",compute="compute_is_social")


    @api.onchange('social_groups_id')
    def groups_id_onchange_(self):
        if self.social_groups_id:
            contact = self.env['ir.model'].search([('model','=','res.partner')])
            self.mailing_model_id = contact.id
            partner_ids = self.social_groups_id.mapped('partner_ids').ids
            self.mailing_domain = repr([('id','in',partner_ids)])
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


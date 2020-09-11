from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

class MassMailings(models.Model):
    _inherit = 'mailing.mailing'


    def action_view_open_theme(self):
        context = dict(self.env.context or {})
        context.update({
            'default_mass_mailing_id':self.id,
            'mass_mailing_id':self.id
        })
        action = {
                'name': 'Choose Template',
                'view_mode': 'form',
                'res_model': 'theme.wizard',
                'view_id': self.env.ref('mail_theme_custom_cr.theme_wizard_view_form').id,
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new'
            }
        return action

    def set_theme_to_mailing(self):
        if self and self.env.context.get('theme_id'):
            theme_id = self.env['mail.themes'].browse(self.env.context.get('theme_id'))
            self.write({
                'body_arch':theme_id.body_arch,
                'body_html':theme_id.body_html
            })
        
        return {'type': 'ir.actions.act_window_close'}

    
    def save_current_open_theme(self):
        context = dict(self.env.context or {})
        context.update({
            'default_mass_mailing_id':self.id,
            'mass_mailing_id':self.id,
            'default_body_html':self.body_html,
            'default_body_arch':self.body_arch
        })
        action = {
                'name': 'Save Template',
                'view_mode': 'form',
                'res_model': 'theme.wizard',
                'view_id': self.env.ref('mail_theme_custom_cr.theme_wizard_view_forms').id,
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new'
            }
        return action

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

class ThemeWizard(models.TransientModel):
    _name = 'theme.wizard'

    theme_ids = fields.Many2many("mail.themes",string="Theme Ids")
    mass_mailing_id = fields.Many2one('mailing.mailing',string="Mailing")
    image = fields.Binary("Theme View Image")
    body_arch = fields.Html("Content")
    body_html = fields.Html("Content")
    name = fields.Char("Name")

    @api.model
    def default_get(self, fields):
        res = super(ThemeWizard, self).default_get(fields)
        theme_ids = self.env['mail.themes'].search([])
        res.update({
            'theme_ids': [(6,0,theme_ids.ids)],
        })
        return res


    def action_save_template(self):
        self.env['mail.themes'].create({'name':self.name,'image':self.image,'body_arch':self.body_arch,'body_html':self.body_html})
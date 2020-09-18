from odoo import api, fields, models
from werkzeug.urls import url_join

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Campaign(models.Model):
    _name = 'utm.campaign'
    _inherit = ['utm.campaign', 'image.mixin']

    is_mandatory_campaign = fields.Boolean("Is Mandatory Campaign?")
    opt_out_partner_ids = fields.Many2many('res.partner','res_partner_opt_out',string="Opt Out Users")
    rating_ids = fields.One2many("social.bit.comments",'utm_campaign_id',string="Rating",domain=[('record_type','=','rating')])
    avg_rating = fields.Float("Avg Rating",compute="compute_rating",store=True)

    @api.depends('rating_ids')
    def compute_rating(self):
        for record in self:
            if record.rating_ids:
                record.avg_rating = sum(record.rating_ids.mapped('rating'))/len(record.rating_ids)
            else:
                record.avg_rating = 0.0

    def get_unsubscribe_campaign(self, partner_id):
        if partner_id:
            utm_campaign_ids = self.search([('opt_out_partner_ids','in',[int(partner_id)])])
            if utm_campaign_ids:
                data = []
                base_url = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                for campaign in utm_campaign_ids:
                    data.append({
                        'image':url_join(base_url,'/web/myimage/utm.campaign/%s/image_128'%campaign.id),
                        'name': campaign.name,
                        'post_owner': campaign.user_id.name,
                        'date': campaign.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'id': campaign.id
                    })
                return {'data': data}
        else:
            return {'data': []}

    def do_subscribe_campaign(self, partner_id):
        if self:
            self.utm_campaign_id.write({'opt_out_partner_ids': [(3, int(partner_id))]})
        return True

    def action_redirect_to_engagement(self):
        action = self.env.ref('dcm_customization.comments_model_name_action').read()[0]
        action['domain'] = [('utm_campaign_id', 'in', self.ids)]
        action['context'] = {
            "default_utm_campaign_id": self.id
        }
        return action


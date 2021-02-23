from odoo import api, fields, models,_
from werkzeug.urls import url_join
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Campaign(models.Model):
    _name = 'utm.campaign'
    _inherit = ['utm.campaign', 'image.mixin']

    is_mandatory_campaign = fields.Boolean("Is Mandatory Campaign?")
    is_public_campaign = fields.Boolean("Is Public Campaign?", default=True)
    opt_out_partner_ids = fields.Many2many('res.partner','res_partner_opt_out',string="Opt Out Users")
    rating_ids = fields.One2many("social.bit.comments",'utm_campaign_id',string="Rating",domain=[('record_type','=','rating')])
    comments_ids = fields.One2many("social.bit.comments",'utm_campaign_id',string="Comments",domain=[('record_type','=','comment')])
    like_ids = fields.One2many("social.bit.comments",'utm_campaign_id',string="Likes",domain=[('record_type','=','like')])
    dislikes_ids = fields.One2many("social.bit.comments",'utm_campaign_id',string="Dislikes",domain=[('record_type','=','dislike')])
    share_ids = fields.One2many("social.bit.comments",'utm_campaign_id',string="Shares",domain=[('record_type','=','share')])
    avg_rating = fields.Float("Avg Rating",compute="compute_rating",store=False)
    file_name = fields.Char("Filename")

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
                        'image':url_join(base_url,'/web/image/utm.campaign/%s/image_128/%s'% (campaign.id,campaign.file_name)),
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

    def campaign_rating(self,partner_id,rating,comment):
        if self and partner_id:
            partner_rating = self.env['social.bit.comments'].search([('partner_id','=',int(partner_id)),('utm_campaign_id','=',self.id),('record_type','=','rating')],limit=1)
            if partner_rating:
                partner_rating.write({'rating':rating,'comment':comment})
            else:
                self.env['social.bit.comments'].create({'utm_campaign_id':self.id,
                                                        'rating':rating,
                                                        'record_type': 'rating',
                                                        'partner_id': int(partner_id),
                                                        'comment':comment})
            return True
        return False

    def get_campaign_details(self,partner_id):
        if self:
            partner_rating = self.env['social.bit.comments'].search([('partner_id','=',int(partner_id)),('utm_campaign_id','=',self.id),('record_type','=','rating')],limit=1)
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            return {'data':[{
                    'name': self.name,
                    'create_date':self.create_date,
                    'responsible':self.user_id.name,
                    'responsible_partner_id':self.user_id.partner_id.id,
                    'like_count':len(self.like_ids),
                    'dislike_count':len(self.dislikes_ids),
                    'comments_count':len(self.comments_ids),
                    'shares_count':len(self.share_ids),
                    'mailing_count':len(self.mailing_mail_ids),
                    'post_count':len(self.social_post_ids.filtered(lambda post: post.state == 'posted')),
                    'rating_count':len(self.rating_ids),
                    'avg_rating':round(self.avg_rating,1),
                    'my_rating':round(partner_rating.rating,1) if partner_rating else 0.0,
                    'image': url_join(base_url,'/web/image/utm.campaign/%s/image_128/%s' % (self.id,self.file_name)),

                 }]}
        return {'data':[]}

    def unlink(self):
        for record in self:
            if record.stage_id.is_active:
                raise UserError(_('You can not delete campaign which is in active stage!'))
        return super(Campaign, self).unlink()

class UTMStage(models.Model):
    _inherit = 'utm.stage'

    is_active = fields.Boolean("Is Active State?")
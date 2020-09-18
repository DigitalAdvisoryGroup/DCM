from odoo import models, api, fields

class SocialBitComments(models.Model):
    _name = 'social.bit.comments'
    _description = "Social Bit Comments"
    _rec_name = "partner_id"
    _order = "id"

    partner_id = fields.Many2one("res.partner",string="Partner")
    post_id  = fields.Many2one("social.post",string="Social Post")
    utm_campaign_id = fields.Many2one(related="post_id.utm_campaign_id", string="Campaign", store=True)
    comment = fields.Text("Comments", translate=True)
    record_type = fields.Selection([('like','Like'),('dislike','Dislike'),('comment','Comment'),('share','Share'),('rating','Rating')],string="Type", default="comment")
    rating = fields.Integer("Rating")
from odoo import models, api, fields

class SocialShare(models.Model):
    _name = "social.bit.share"
    _description = "Social Bit Share"
    _rec_name = "partner_id"

    partner_id = fields.Many2one("res.partner",string="Partner")
    post_id  = fields.Many2one("social.post",string="Social Post")

class SocialBitComments(models.Model):
    _name = 'social.bit.comments'
    _description = "Social Bit Comments"
    _rec_name = "partner_id"
    _order = "id"

    partner_id = fields.Many2one("res.partner",string="Partner")
    post_id  = fields.Many2one("social.post",string="Social Post")
    comment = fields.Text("Comments")

class SocialPost(models.Model):
    _inherit = 'social.post'

    share_ids = fields.One2many('social.bit.share','post_id',string="Shares")
    comments_ids = fields.One2many('social.bit.comments','post_id',string="Comments")
    
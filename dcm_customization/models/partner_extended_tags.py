# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class PartnerExtendedTags(models.Model):
    _name = 'partner.extended.tag'
    _description = "Partner Extended Tags"

    name = fields.Char("Name", translate=True)
    tag_type_id = fields.Many2one("partner.extended.tag.type", string="Tag Type")


class PartnerExtendedTagsType(models.Model):
    _name = 'partner.extended.tag.type'
    _description = "Partner Extended Tags Type"

    name = fields.Char("Name", translate=True)
    is_display_mobile = fields.Boolean("Is display mobile?")


class ExtendedTagsLevel(models.Model):
    _name = 'extended.tag.level'
    _description = "Extended Tags Level"

    name = fields.Char("Name", translate=True)
    tag_type_id = fields.Many2one("partner.extended.tag.type", string="Tag Type")



class PartnerExtendedTagsLevel(models.Model):
    _name = 'partner.extended.tag.level'
    _description = "Partner Extended Tags Level"

    level_id = fields.Many2one("extended.tag.level", "Level")
    tag_id = fields.Many2one("partner.extended.tag", string="Tag")
    tag_type_id = fields.Many2one(related="tag_id.tag_type_id", string="Tag Type", store=True)
    partner_id = fields.Many2one("res.partner", string="Contact", required=True)

# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_partner_from_email(self,email,token):
        _logger.info("-------------------get partner method email -: %s \n token %s"%(email,token))
        if email:
            partner_id = self.search([('email','=',email)])
            if partner_id:
                website_visitor = self.env['website.visitor'].search([('partner_id','=',partner_id.id)])
                if not website_visitor:
                    self.env['website.visitor'].create({'partner_id': partner_id.id,
                            "push_token":token ,
                            "name": partner_id.name
                            }
                        )
                else:
                    website_visitor.write({'push_token':token})       
                return partner_id.id
            else:
                return False
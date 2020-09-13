# -*- coding: utf-8 -*-
import odoo
from odoo import http
from odoo.http import request
import traceback
from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError

import werkzeug
from odoo import http, _
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.auth_signup.models.res_users import SignupError

import logging
_logger = logging.getLogger(__name__)
import re
from odoo import SUPERUSER_ID
from collections import OrderedDict
from odoo.addons.web.controllers.main import Binary

import uuid
from odoo.addons.mail.controllers.main import MailController
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64

class PortalAccount(CustomerPortal):
    @http.route()
    def account(self, redirect=None, **post):
        if 'image_1920' in post:
            image_1920 = post.get('image_1920')
            if image_1920:
                image_1920 = image_1920.read()
                image_1920 = base64.b64encode(image_1920)
                request.env.user.partner_id.sudo().write({
                    'image_1920': image_1920
                })
            post.pop('image_1920')
        if 'clear_avatar' in post:
            request.env.user.partner_id.sudo().write({
                'image_1920': False
            })
            post.pop('clear_avatar')
        return super(PortalAccount, self).account(redirect=redirect, **post)

class WebController(Binary):

    @http.route(['/web/myimage/<string:model>/<int:id>/<string:field>'], type='http', auth="public")
    def content_image_my(self, xmlid=None, model='ir.attachment', id=None, field='datas',  unique=None, access_token=None):
#         _logger.info("here requrest forr image..")

        if model == "ir.attachment":
            attachment_id = request.env['ir.attachment'].sudo().search([('id','=',id),('access_token','=',access_token)])
            if not attachment_id:
                return request.not_found()
            
        request.uid = SUPERUSER_ID
        return self.content_image(xmlid=xmlid,model=model,id=id,field=field,unique=unique,access_token=access_token)


    @http.route(type='http', auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):
        if kw.get('social_newid') and kw.get('datas'):
            datsss = base64.b64encode(open(kw.get('datas'), 'rb').read())
            content_base64 = base64.b64decode(datsss)
            headers = [('Content-Type',mimetype), ('X-Content-Type-Options', 'nosniff'), ('ETag', '8a20c82cf84a0d0603d7298b28d184e48b235364'), ('Cache-Control', 'max-age=0')]
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
            return response
        else:
            status, headers, content = request.env['ir.http'].binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype, access_token=access_token)
            if status != 200:
                return request.env['ir.http']._response_by_status(status, headers, content)
            else:
                content_base64 = base64.b64decode(content)
                headers.append(('Content-Length', len(content_base64)))
                headers.append(('Accept-Ranges', "bytes"))
                response = request.make_response(content_base64, headers)
            if token:
                response.set_cookie('fileToken', token)
            return response
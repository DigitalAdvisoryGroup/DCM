# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http, _
from odoo.addons.web.controllers.main import ensure_db, Home
import logging
_logger = logging.getLogger(__name__)
from odoo import SUPERUSER_ID
from odoo.addons.web.controllers.main import Binary

from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
from odoo.http import Response


class MidarLogin(Home):

    @http.route()
    def web_login(self, redirect=None, *args, **kw):
        response = super(MidarLogin, self).web_login(redirect=redirect, *args, **kw)
        if 'X-Frame-Options' in response.headers:
            response.headers['X-Frame-Options'] = 'ALLOWALL'
        return response

class MidarVideoAttachment(http.Controller):

    @http.route(['/comment-video'], type='json', auth='public', website=True)
    def comment_video(self, **post):
        res_id = request.env['social.bit.comments'].sudo().create(post)
        return res_id.id

    @http.route('/dcm/get_sg_org_chart', type='json', auth='user')
    def get_org_chart(self, partner_id, **kw):
        if not partner_id:
            return {
                'managers': [],
                'children': [],
            }
        managers_list = []
        partner_browse = request.env['res.partner'].sudo().browse(partner_id)
        if not partner_browse.social_group_id:
            return {
                'managers': [],
                'children': [],
            }
        self_dict = {'id': partner_browse.social_group_id[0].id, 'name': partner_browse.social_group_id[0].name,'code': partner_browse.social_group_id[0].code}
        parent_sg_id = request.env['social.partner.group'].sudo().search([('code','=',partner_browse.social_group_id[0].parent2_id)],limit=1)
        if parent_sg_id:
            managers_list.append({"id": parent_sg_id.id,"name": parent_sg_id.name,"code": parent_sg_id.code})
            if parent_sg_id.parent2_id:
                parent_sg_id1 = request.env['social.partner.group'].sudo().search([('code', '=', parent_sg_id.parent2_id)], limit=1)
                managers_list.append({"id": parent_sg_id1.id, "name": parent_sg_id1.name,"code": parent_sg_id1.code})
        return {
                'self': self_dict,
                'managers': sorted(managers_list, key = lambda i: i['id']),
                'children': [],
            }

    @http.route('/dcm/get_fun_sg_org_chart', type='json', auth='user')
    def get_fun_org_chart(self, partner_id, **kw):
        if not partner_id:
            return {
                'managers': [],
                'children': [],
            }
        managers_list = []
        partner_browse = request.env['res.partner'].sudo().browse(partner_id)
        if not partner_browse.social_group_fun_id:
            return {
                'managers': [],
                'children': [],
            }
        self_dict = {'id': partner_browse.social_group_fun_id[0].id, 'name': partner_browse.social_group_fun_id[0].name, 'code': partner_browse.social_group_fun_id[0].code}
        parent_sg_id = request.env['social.partner.group'].sudo().search([('code', '=', partner_browse.social_group_fun_id[0].parent2_id)], limit=1)
        if parent_sg_id:
            managers_list.append({"id": parent_sg_id.id, "name": parent_sg_id.name, "code": parent_sg_id.code})
            if parent_sg_id.parent2_id:
                parent_sg_id1 = request.env['social.partner.group'].sudo().search([('code', '=', parent_sg_id.parent2_id)], limit=1)
                managers_list.append({"id": parent_sg_id1.id, "name": parent_sg_id1.name, "code": parent_sg_id1.code})
        return {
            'self': self_dict,
            'managers': sorted(managers_list, key=lambda i: i['id']),
            'children': [],
        }

    @http.route('/midardir', type='http', auth='user', website=True, csrf=False)
    def midardir_search(self, **kw):
        data = {}
        if kw and kw.get("search"):
            data = request.env['global.search'].sudo().get_records(kw['search'])
        return request.render("dcm_customization.midardir_search", {'search_models': data.keys(),'records': data,'search': kw.get("search")})

    @http.route('/midardir/contact/<model("res.partner"):partner>', type='http', auth='user', website=True, csrf=False)
    def midardir_contact(self, partner,**kw):
        if partner.social_group_id:
            level_3_dict = {'id': partner.social_group_id[0].id, 'name': partner.social_group_id[0].name, 'code': partner.social_group_id[0].code}
            parent_sg_id = request.env['social.partner.group'].sudo().search([('code', '=', partner.social_group_id[0].parent2_id)], limit=1)
            if parent_sg_id:
                level_2_dict = {"id": parent_sg_id.id, "name": parent_sg_id.name, "code": parent_sg_id.code}
                if parent_sg_id.parent2_id:
                    parent_sg_id1 = request.env['social.partner.group'].sudo().search([('code', '=', parent_sg_id.parent2_id)], limit=1)
                    level_1_dict = {"id": parent_sg_id1.id, "name": parent_sg_id1.name, "code": parent_sg_id1.code}
                else:
                    level_1_dict = level_2_dict
                    level_2_dict = level_3_dict
                    level_3_dict = {}
            else:
                level_1_dict = level_3_dict
                level_2_dict = {}
                level_3_dict = {}
        else:
            level_1_dict = {}
            level_2_dict = {}
            level_3_dict = {}
        return request.render("dcm_customization.midardir_contact", {'record': partner,'level_1': level_1_dict,'search': kw.get("search"),
                                                                     'lang_name': request.env['res.lang']._lang_get(partner.lang).name,
                                                                     'level_2': level_2_dict,'level_3': level_3_dict})

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
        if model == "ir.attachment":
            attachment_id = request.env['ir.attachment'].sudo().search([('id','=',id),('access_token','=',access_token)])
            if not attachment_id:
                return request.not_found()
            
        request.uid = SUPERUSER_ID
        return self.content_image(xmlid=xmlid,model=model,id=id,field=field,unique=unique,access_token=access_token)

    @http.route(type='http', auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None,
                       field='datas',
                       filename=None, filename_field='name', unique=None,
                       mimetype=None,
                       download=None, data=None, token=None, access_token=None,
                       **kw):
        if kw.get('social_newid') and kw.get('datas'):
            datsss = base64.b64encode(open(kw.get('datas'), 'rb').read())
            content_base64 = base64.b64decode(datsss)
            headers = [('Content-Type', mimetype),
                       ('X-Content-Type-Options', 'nosniff'),
                       ('ETag', '8a20c82cf84a0d0603d7298b28d184e48b235364'),
                       ('Cache-Control', 'max-age=0')]
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
            return response
        else:
            status, headers, content = request.env['ir.http'].binary_content(
                xmlid=xmlid, model=model, id=id, field=field, unique=unique,
                filename=filename,
                filename_field=filename_field, download=download,
                mimetype=mimetype, access_token=access_token)
            if status not in (200,206):
                return request.env['ir.http']._response_by_status(status,
                                                                  headers,
                                                                  content)
            # else:
            #     # content_base64 = base64.b64decode(content)
            #     # headers.append(('Content-Length', len(content_base64)))
            #     # buf = BytesIO(content_base64)
            #     # data = wrap_file(http.request.httprequest.environ, buf)
            #     # response = http.Response(
            #     #     data,
            #     #     headers=headers,
            #     #     direct_passthrough=True)
            #     content_base64 = base64.b64decode(content)
            #     mainvideo = content_base64
            #     if request.httprequest.range:
            #         contentrange = request.httprequest.range.make_content_range(
            #             len(content_base64))
            #
            #         if contentrange.stop < len(content_base64):
            #             status = 206
            #             headers.append(('Content-Range', 'bytes %s-%s/%s' % (
            #                 str(contentrange.start), str(1),
            #                 str(len(content_base64)))))
            #         elif contentrange.stop > len(content_base64):
            #             status = 416
            #             mainvideo = ""
            #
            #         if status != 416:
            #             mainvideo = mainvideo[
            #                         contentrange.start:contentrange.stop]
            #             headers.append(('Content-Length', len(mainvideo)))
            #
            #     headers.append(('Accept-Ranges', "bytes"))
            #     headers.append(('access-control-allow-origin', "*"))
            #     response = Response(mainvideo, status=status, headers=headers,
            #                         content_type=mimetype)
            elif status == 206:
                if content:
                    image_base64 = base64.b64decode(content)
                else:
                    image_base64 = self.placeholder(image='placeholder.png')  # could return (contenttype, content) in master
                    dictheaders = dict(headers)
                    dictheaders['Content-Type'] = 'image/png'
                    headers = list(dictheaders.items())

                response = Response(headers=headers, status=status)
                response.automatically_set_content_length = False
                response.set_data(image_base64)
            else:
                content_base64 = base64.b64decode(content)
                headers.append(('Content-Length', len(content_base64)))
                response = request.make_response(content_base64, headers)
            if token:
                response.set_cookie('fileToken', token)
            return response


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


from werkzeug.urls import url_join
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

def string_before(value, a):
    # Find first part and return slice before it.
    pos_a = value.find(a)
    if pos_a == -1: return ""
    return value[0:pos_a]

def string_after(value, a):
    # Find and validate first part.
    pos_a = value.rfind(a)
    if pos_a == -1: return ""
    # Returns chars after the found string.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= len(value): return ""
    return value[adjusted_pos_a:]



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

    @http.route('/midardir', type='http', auth='public', website=True)
    def midardir_search(self, **kw):
        if 'search' not in kw and request.env.company.iframe_acess_token != kw.get("token"):
            return request.render("http_routing.403", {})
        data = {}
        if kw and kw.get("search"):
            data = request.env['global.search.config'].sudo().get_global_search_configuration_data(kw['search'])
        return request.render("dcm_customization.midardir_search_main_menu", {'search_models': data.keys(),'records': data,
                                                                    'search': kw.get("search"),
                                                                    'token': kw.get("token"),
                                                                    })
        
    @http.route('/midardir/result', type='http', auth='public', website=True, csrf=False)
    def midardir_search_result(self, **kw):
        data = {}
        data_result = False
        result_fields = False
        model = False
        if request.env.company.iframe_acess_token != kw.get("token"):
            return request.render("http_routing.403", {})
        if kw and kw.get("search"):
            # data = request.env['global.search'].sudo().get_records(kw['search'])
            data = request.env['global.search.config'].sudo().get_global_search_configuration_data(kw['search'])
            
        if kw and kw.get('config') and kw.get("search"):
            global_search_config_id = request.env['global.search.config'].sudo().browse(int(kw.get('config')))
            if global_search_config_id:
                data_result = global_search_config_id.get_records(kw.get("search"))
                result_fields = global_search_config_id.search_sort_order
                model = global_search_config_id.model_id.model
                page = global_search_config_id.page

        # global_search_config = request.env['global.search.config'].sudo().search([])
        print("----------global_search_config------------\n\n\n\n\--",data_result)
        print ('-------result_fields---------------',result_fields)
        return request.render("dcm_customization.midardir_search_menu_result", {'search_models': data.keys(),'records': data,
                                                                    'search': kw.get("search"),
                                                                    'results' : data_result,
                                                                    'current_config' : int(kw.get('config')),
                                                                    'result_fields' : result_fields,
                                                                    'model' : model,
                                                                    'page': page,
                                                                    'token': kw.get("token"),
                                                                    # 'global_search_config': global_search_config
                                                                    })

    @http.route('/midardir/post/<model("social.post"):post>', type='http', auth='public', website=True)
    def midardir_post(self, post, **kw):
        print("--------post-------------",post)
        if request.env.company.iframe_acess_token != kw.get("token"):
            return request.render("http_routing.403", {})
        data = kw.get("search")
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        image_url = url_join(base_url, '/web/image/utm.campaign/%s/image_128/%s' % (post.utm_campaign_id.id, post.utm_campaign_id.file_name))
        before_msg = string_before(post.message, data)[-40:]
        after_msg = string_after(post.message, data)[-40:]
        prevpath = request.httprequest.referrer
        parent = kw.get('parent')
        print("--------here000000000000000")
        return request.render("dcm_customization.midardir_post", {'record': post,
                                                                     'search': kw.get("search"),
                                                                     'parent': parent,
                                                                     'prevpath': prevpath,
                                                                      'message': before_msg + data + after_msg,
                                                                      'name': post.utm_campaign_id.name or '',
                                                                      'date': post.published_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                                      'total_like_count': len(post.like_ids),
                                                                      'total_dislike_count': len(post.dislike_ids),
                                                                      'total_comment_count': len(post.comments_ids),
                                                                      'total_share_count': len(post.share_ids),
                                                                  'token': kw.get("token"),
                                                                     })

    @http.route('/midardir/contact/<model("res.partner"):partner>', type='http', auth='public', website=True)
    def midardir_contact(self, partner,**kw):
        if request.env.company.iframe_acess_token != kw.get("token"):
            return request.render("http_routing.403", {})
        partner = partner.sudo()
        print("-------partner.display_name---------",partner.display_name)
        if partner.social_group_id:
            level_3_dict = {'id': partner.social_group_id[0].id, 'name': partner.social_group_id[0].name, 'code': partner.social_group_id[0].code}
            if partner.social_group_id[0].parent2_id:
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
                level_1_dict = level_3_dict
                level_2_dict = {}
                level_3_dict = {}
        else:
            level_1_dict = {}
            level_2_dict = {}
            level_3_dict = {}
        prevpath = request.httprequest.referrer
        parent = kw.get('parent')
        org_data_latest = partner.with_context(lang=partner.lang).get_group_data_latest()
        responsbility = partner.get_resp_contact_data()
        return request.render("dcm_customization.midardir_contact", {'record': partner,
                                                                     # 'level_1': level_1_dict,
                                                                     'search': kw.get("search"),
                                                                     'lang_name': request.env['res.lang']._lang_get(partner.lang).name,
                                                                     # 'level_2': level_2_dict,
                                                                     # 'level_3': level_3_dict,
                                                                     'parent': parent,
                                                                     'prevpath': prevpath,
                                                                     'org_data_latest': org_data_latest,
                                                                     'responsbility': responsbility,
                                                                     'token': kw.get("token"),
                                                                     })

    @http.route('/midardir/socialgroup/<model("social.partner.group"):social_group>', type='http', auth='public', website=True, csrf=False)
    def midardir_social_group(self, social_group, **kw):
        prevpath = request.httprequest.referrer
        parent = kw.get('parent')
        parent_sg_id = False
        if request.env.company.iframe_acess_token != kw.get("token"):
            return request.render("http_routing.403", {})
        if social_group:
            if social_group.parent2_id:
                parent_sg_id = request.env['social.partner.group'].sudo().search([('code', '=', social_group.parent2_id)], limit=1)
        return request.render("dcm_customization.midardir_social_group", {'record': social_group,
                                                                          'parent_sg_id': parent_sg_id and parent_sg_id.id or False,
                                                                          'search': kw.get("search"),
                                                                          'parent': parent,
                                                                          'prevpath': prevpath,
                                                                          'token': kw.get("token"),
                                                                     })

    @http.route('/midardir/res/contact/<model("res.partner"):partner>', type='http', auth='public', website=True, csrf=False)
    def midardir_cat_res(self, partner, **kw):
        prevpath = request.httprequest.referrer
        parent = kw.get('parent')
        if request.env.company.iframe_acess_token != kw.get("token"):
            return request.render("http_routing.403", {})
        if partner:
            parnter_ids = request.env['res.partner'].sudo().search([('is_company', '=', False), ('category_res_ids.name', '=', partner.id_code)])
        return request.render("dcm_customization.midardir_cat_res_contacts", {'partners': parnter_ids,
                                                                              'record':partner,
                                                                              'search': kw.get("search"),
                                                                              'parent': parent,
                                                                              'prevpath': prevpath,
                                                                              'token': kw.get("token"),
                                                                          })
        
    @http.route('/social_group_hierarchy', type='http', auth='public', website=True, csrf=False)
    def social_group_hierarchy(self,**kw):
        if request.env.company.iframe_acess_token != kw.get("token"):
            return request.render("http_routing.403", {})
        sc_groups = request.env['social.partner.group'].sudo()
        prevpath = request.httprequest.referrer
        if kw.get('social_group_id'):
            sc_groups = request.env['social.partner.group'].sudo().browse(int(kw.get('social_group_id')))
        parent_sc_group = False
        if sc_groups.parent2_id:
            parent_sc_group = request.env['social.partner.group'].sudo().search(
                    [('is_org_unit', '=', True), ('code', '=', sc_groups.parent2_id)])
        values = {
            'token': kw.get("token"),
            'parent_sc_group': parent_sc_group,
            'social_group_id': kw.get('social_group_id') if kw.get('social_group_id') else False,
            'type': sc_groups.type_id.name if sc_groups else False,
            'search': kw.get('search') if kw.get('search') else False,
            'prevpath': prevpath,
            'record': sc_groups,
            'parent': sc_groups.name
        }
        return request.render('dcm_customization.midardir_social_group_heirarchical_view', values)

    def get_parent_data(self,group_id,group_data,search):
        sc_groups = request.env['social.partner.group'].sudo().browse(group_id)
        print("--------sc_groups.name---------",sc_groups.name)
        if sc_groups:
            parent_sg_id = request.env['social.partner.group'].sudo().search([('is_org_unit','=',True),('code', '=', sc_groups.parent2_id)], limit=1)
            if parent_sg_id.parent2_id:
                if group_data:
                    pr_group_data = {'id' : parent_sg_id.id,'label' :'<a href="/midardir/socialgroup/%d?search=%s">%s</a>' %(parent_sg_id.id,search,parent_sg_id.name),'children' : [group_data]}
                    return self.get_parent_data(parent_sg_id.id,pr_group_data,search)
                else:
                    group_data = {'id' : parent_sg_id.id,'label' :'<a href="/midardir/socialgroup/%d?search=%s">%s</a>' %(parent_sg_id.id,search,parent_sg_id.name),'children' : []}
                    return self.get_parent_data(parent_sg_id.id,group_data,search)
            else:
                if group_data:
                    return {'id' : parent_sg_id.id,'label' :'<a href="/midardir/socialgroup/%d?search=%s">%s</a>' %(parent_sg_id.id,search,parent_sg_id.name),'children' : [group_data]}
                else:
                    return {'id' : parent_sg_id.id,'label' :'<a href="/midardir/socialgroup/%d?search=%s">%s</a>' %(parent_sg_id.id,search,parent_sg_id.name),'children' : []}


    def get_children_data(self,group_id,group_data):
        sc_groups = group_id
        
        if sc_groups:
            if sc_groups.code:
                child_sg_ids = request.env['social.partner.group'].sudo().search([('is_org_unit','=',True),('parent2_id', '=', sc_groups.code)])
                if child_sg_ids:
                    for child_sg in child_sg_ids:
                        child_group_data = self.get_children_data(child_sg,{'name' : child_sg.name,'title' : child_sg.code,'children' : []})
                        if group_data:
                            group_data['children'].append(child_group_data)
                        else:
                            group_data = child_group_data
                    return group_data
                else:
                    return group_data
            else:
                return group_data
        else:
            return {}
    
    def get_heirarchy_data(self,partner_group_id):
        sc_groups = request.env['social.partner.group'].sudo().browse(group_id)
        if not sc_groups.parent2_id:
            return {'id' : sc_groups.id,'label' :'<b><a href="/midardir/socialgroup/%d?search=%s" style="font-size:larger;">%s</a></b>' %(sc_groups.id,search,sc_groups.name),'children' : []}
        group_data = {'id' : sc_groups.id,'label' :'<b><a href="/midardir/socialgroup/%d?search=%s" style="font-size:larger;">%s</a></b>' %(sc_groups.id,search,sc_groups.name),'children' : []}
        
        # hierarchy_children = self.get_children_data(group_id,group_data,search)
        
        hierarchy_parents = self.get_parent_data(group_id,group_data,search)
        
        return hierarchy_parents
        
    
    @http.route('/get_heirarchy_details',auth="public",type="json",website=True)
    def get_hierarchy_details(self,**kw):
        if kw.get('social_group_id'):
            partner_group_id = request.env['social.partner.group'].sudo().browse(int(kw['social_group_id']))
            hierarchy_dict = {}
            if partner_group_id:
                main_level_data = {
                    'name': partner_group_id.name,
                    'title' : partner_group_id.code,
                    'children': [],
                }
                hierarchy_child_data =  self.get_children_data(partner_group_id,main_level_data)
                hierarchy_dict.update(hierarchy_child_data)
            return hierarchy_dict
        
    def get_tree_parent_data(self,group_id,group_data,search,token):
        sc_groups = request.env['social.partner.group'].sudo().browse(group_id)
        if sc_groups:
            parent_sg_id = request.env['social.partner.group'].sudo().search([('is_org_unit','=',True),('code', '=', sc_groups.parent2_id)], limit=1)
            if parent_sg_id.parent2_id:
                if group_data:
                    pr_group_data = {'id' : parent_sg_id.id,'label' :'<a href="/midardir/socialgroup/%d?search=%s&token=%s">%s</a>' %(parent_sg_id.id,search,token,parent_sg_id.name),'children' : [group_data]}
                    return self.get_tree_parent_data(parent_sg_id.id,pr_group_data,search,token)
                else:
                    group_data = {'id' : parent_sg_id.id,'label' :'<a href="/midardir/socialgroup/%d?search=%s&token=%s">%s</a>' %(parent_sg_id.id,search,token,parent_sg_id.name),'children' : []}
                    return self.get_tree_parent_data(parent_sg_id.id,group_data,search,token)
            else:
                if group_data:
                    return {'id' : parent_sg_id.id,'label' :'<a href="/midardir/socialgroup/%d?search=%s&token=%s">%s</a>' %(parent_sg_id.id,search,token,parent_sg_id.name),'children' : [group_data]}
                else:
                    return {'id' : parent_sg_id.id,'label' :'<a href="/midardir/socialgroup/%d?search=%s&token=%s">%s</a>' %(parent_sg_id.id,search,token,parent_sg_id.name),'children' : []}


    def get_tree_children_data(self,group_id,group_data,search):
        sc_groups = request.env['social.partner.group'].sudo().browse(group_id)
        
        if sc_groups:
            if sc_groups.code:
                child_sg_ids = request.env['social.partner.group'].sudo().search([('is_org_unit','=',True),('parent2_id', '=', sc_groups.code)])
                print("CHIld SG IDS===",child_sg_ids)
                if child_sg_ids:
                    for child_sg in child_sg_ids:
                        child_group_data = self.get_tree_children_data(child_sg.id,{'id' : child_sg.id,'label' : '<a href="/midardir/socialgroup/%d?search=%s">%s</a>' %(child_sg.id,search,child_sg.name),'children' : []},search)
                        if group_data:
                            group_data['children'].append(child_group_data)
                        else:
                            group_data = child_group_data
                    return group_data
                else:
                    return group_data
            else:
                return group_data
        else:
            return {}
    
    def get_tree_heirarchy_data(self,group_id,search,token):
        sc_groups = request.env['social.partner.group'].sudo().browse(group_id)
        group_data = {'id' : sc_groups.id,'label' :'<b><a href="/midardir/socialgroup/%d?search=%s&token=%s" style="font-size:larger;">%s</a></b>' %(sc_groups.id,search,token,sc_groups.name),'children' : []}
        # hierarchy_children = self.get_tree_children_data(group_id,group_data,search)
        
        hierarchy_parents = self.get_tree_parent_data(group_id,group_data,search,token)
        
        # return hierarchy_children
        return hierarchy_parents
        
    @http.route('/get_tree_heirarchy_details',auth="public",type="json",website=True)
    def get_tree_hierarchy_details(self,**kw):
        if request.env.company.iframe_acess_token != kw.get("token"):
            return request.render("http_routing.403", {})
        if kw.get('social_group_id'):
            search = kw.get('search')
            token = kw.get('token')
            group_id = request.env['social.partner.group'].sudo().browse(int(kw['social_group_id']))
            hierarchy_dict = {}
            hierarchy_children_data = self.get_tree_heirarchy_data(group_id.id,search,token)
            # hierarchy_data.append(hierarchy_parent_data)
            heirachy_main_data = {'label' :'<b>' + group_id.type_id.name + '</b>','children' : [hierarchy_children_data]}
            hierarchy_dict.update({group_id.name : heirachy_main_data})   
            return hierarchy_dict

    @http.route('/get_sunburst_details', auth="public", type="json", website=True)
    def get_sunburst_details(self, **kw):
        if request.env.company.iframe_acess_token != kw.get("token"):
            return request.render("http_routing.403", {})
        if kw.get('social_group_id'):
            search = kw.get('search')
            sc_groups = request.env['social.partner.group'].sudo().browse(int(kw.get('social_group_id')))
            data = self.get_sunburst_data(sc_groups,search, kw.get("token"))
            return {"data": data, "header": sc_groups.name, "current_group": sc_groups.name}

    def get_sunburst_data(self, main_sc_group, search, token):
        group_data = [{
            'id': str(main_sc_group.id),
            'name': main_sc_group.name,
            'parent': '',
            'value': main_sc_group.current_and_childs_subscribers_count,
            'parent_id': main_sc_group.id,
            'parent_name': main_sc_group.name,
            'parent_group_owner_id': main_sc_group.group_owner_id.id,
            'parent_group_owner_name': main_sc_group.group_owner_id.name,
            'parent_value': main_sc_group.current_and_childs_subscribers_count,
            'parent_current_subscribers_count': main_sc_group.current_subscribers_count,
        }]
        if main_sc_group.code:
            child_sg_ids = request.env['social.partner.group'].sudo().search([('is_org_unit', '=', True), ('parent2_id', '=', main_sc_group.code)])
            if child_sg_ids:
                for child_sg in child_sg_ids:
                    group_data.append({
                        'id': str(child_sg.id),
                        'current_subscribers_count': child_sg.current_subscribers_count,
                        'group_owner_id': child_sg.group_owner_id.id,
                        'group_owner_name': child_sg.group_owner_id.name,
                        'name': child_sg.name,
                        'parent': main_sc_group.id,
                        'value': child_sg.current_and_childs_subscribers_count,
                        'token': token,
                        'parent_id': main_sc_group.id,
                        'parent_name': main_sc_group.name,
                        'parent_group_owner_id': main_sc_group.group_owner_id.id,
                        'parent_group_owner_name': main_sc_group.group_owner_id.name,
                        'parent_value': main_sc_group.current_and_childs_subscribers_count,
                        'parent_current_subscribers_count': main_sc_group.current_subscribers_count,
                    })

                for second_level_sg in child_sg_ids:
                    self.get_sunburst_children_data(second_level_sg, group_data, search, token)
        return group_data

    def get_sunburst_children_data(self, sc_group, group_data, search, token):
        if sc_group and sc_group.code:
            child_sg_ids = request.env['social.partner.group'].sudo().search([('is_org_unit', '=', True), ('parent2_id', '=', sc_group.code)])
            if child_sg_ids:
                group_data.append({
                    'id': str(sc_group.id)+"dummy",
                    'current_subscribers_count': sc_group.current_subscribers_count,
                    'group_owner_id': sc_group.group_owner_id.id,
                    'group_owner_name': sc_group.group_owner_id.name,
                    'name': sc_group.name,
                    'parent': sc_group.id,
                    'value': len(sc_group.partner_ids.ids),
                    'token': token,
                })
                for child_sg in child_sg_ids:
                    group_data.append({
                        'id': str(child_sg.id),
                        'current_subscribers_count': child_sg.current_subscribers_count,
                        'group_owner_id': child_sg.group_owner_id.id,
                        'group_owner_name': child_sg.group_owner_id.name,
                        'name': child_sg.name,
                        'parent': sc_group.id,
                        'value': child_sg.current_and_childs_subscribers_count,
                        'token': token,
                        'parent_id': sc_group.id,
                        'parent_name': sc_group.name,
                        'parent_group_owner_id': sc_group.group_owner_id.id,
                        'parent_group_owner_name': sc_group.group_owner_id.name,
                        'parent_value': sc_group.current_and_childs_subscribers_count,
                        'parent_current_subscribers_count': sc_group.current_subscribers_count,
                    })
                    self.get_sunburst_children_data(child_sg, group_data, search, token)
                return group_data
            else:
                return group_data
        else:
            return group_data

        
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

            if status not in (200, 206):
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


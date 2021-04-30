from odoo import api, models, fields, _
from ast import literal_eval
import logging
_logger = logging.getLogger(__name__)


class GlobalSearchConfig(models.Model):
    _name = 'global.search.config'
    _order = 'sequence asc'
    _description  = 'Global Search Configuration'


    name = fields.Char("Name", translate=True)
    sequence = fields.Integer(help="Used to order the note stages")
    model_id = fields.Many2one("ir.model", string="Model")
    page = fields.Selection([('profile','Profile'),('group','Group'),('post','Post Detail')], string="Page Redirect", required=True)
    active = fields.Boolean("Active", default=True)

    search_fields_lines = fields.Many2many("ir.model.fields", "rel_fields_global_search", "global_search_id","field_search_id", string="Fields to be searched")
    result_fields_lines = fields.Many2many("ir.model.fields", "rel_fields_global_search_result", "global_search_result_id","field_search_result_id", string="Fields to be shown in result")
    global_search_model_real = fields.Char(compute='_compute_model', string='Recipients Real Model', default='mailing.contact', required=True)
    global_search_domain = fields.Char(string='Model clause', default=[])


    @api.depends('model_id')
    def _compute_model(self):
        for record in self:
            record.global_search_model_real = record.model_id.model or 'res.partner'


    def get_global_search_configuration_data(self):
        data = []
        recs = self.search([])
        if recs:
            for rec in recs:
                data.append({
                    "id": rec.id,
                    "name": rec.name,
                    "type": rec.model_id.model,
                    "page": rec.page,
                    "result_fields": ",".join([x.name for x in rec.result_fields_lines])
                })
        _logger.info("----------global-data---config-------%s", data)
        return {"data": data}

    def get_models(self):
        return {self.global_search_model_real: _(self.name)}

    def get_model_domains(self, data):
        domain = []
        for i in range(1,len(self.search_fields_lines)):
            domain.append('|')
        for f in self.search_fields_lines:
            domain.append([f.name,'ilike',data])
        extra_domain = literal_eval(self.global_search_domain) if self.global_search_domain else []
        return {self.global_search_model_real: domain+extra_domain}

    def get_records(self, data):
        global_data = {}
        if data:
            models = self.get_models()
            domains = self.get_model_domains(data)
            _logger.info("-------models--------%s",models)
            _logger.info("-------domains---------%s",domains)
            for model in models.keys():
                results = self.env[model.split('-')[0]].search_read(domains[model], self.result_fields_lines.mapped("name"))
                if results:
                    global_data[model] = {
                        'header': models[model],
                        'count': self.env[model.split('-')[0]].search_count(domains[model]),
                        'data': results
                    }
        _logger.info("----------global-data---new-------%s", global_data)
        return global_data






class GlobalSearch(models.Model):
    _name = 'global.search'
    _description  = 'Global Search'

    @api.model
    def get_app_data(self, res_model):
        datas = {}
        if res_model == 'res.partner':
            datas[res_model] = {}
            menu_id = self.env.ref('contacts.menu_contacts').id
            action_id = self.env.ref('contacts.action_contacts').id
            datas[res_model]['menu_id'] = menu_id
            datas[res_model]['action_id'] = action_id
        if res_model == 'social.partner.group':
            datas[res_model] = {}
            menu_id = self.env.ref('dcm_customization.social_partner_group_menu_act').id
            action_id = self.env.ref('dcm_customization.social_partner_group_action').id
            datas[res_model]['menu_id'] = menu_id
            datas[res_model]['action_id'] = action_id
        # if res_model == 'social.bit.comments':
        #     datas[res_model] = {}
        #     menu_id = self.env.ref('dcm_customization.menu_midar_statistics_eng').id
        #     action_id = self.env.ref('dcm_customization.comments_model_name_action').id
        #     datas[res_model]['menu_id'] = menu_id
        #     datas[res_model]['action_id'] = action_id
        # if res_model == 'social.post':
        #     datas[res_model] = {}
        #     menu_id = self.env.ref('social.menu_social_post').id
        #     action_id = self.env.ref('social.action_social_post').id
        #     datas[res_model]['menu_id'] = menu_id
        #     datas[res_model]['action_id'] = action_id
        return datas
        
    @api.model
    def open_in_dashboard(self, data, model_data):
        domains = self.get_domains(data)
        searched_models = {}
        for model in model_data:
            if domains.get(model):
                searched_models[model] = domains.get(model)
                if model_data[model].get('list_view_id', False):
                    searched_models[model].update({'list_view_id': model_data[model].get('list_view_id', False)})
                if model_data[model].get('form_view_id', False):
                    searched_models[model].update({'form_view_id': model_data[model].get('form_view_id', False)})
        return searched_models

    @api.model
    def get_domains(self, data):
        domains = {
            # 'social.bit.comments': {'domain': ['|','|',('partner_id','ilike',data),('comment','ilike',data),('comment','ilike',data)]},
            # 'social.post': {'domain': ['|', '|', '|', '|',('message','ilike',data),('utm_campaign_id','ilike',data),('social_partner_ids.name','ilike',data),('social_groups_ids.name','ilike',data),('social_groups_ids.partner_ids.name','ilike',data)]},
            'social.partner.group': {'domain': ['|', '|', '|',('name', 'ilike', data), ('parent_id', 'ilike', data), ('partner_ids.name', 'ilike', data),('code','ilike',data)]},
            'res.partner': {
                'domain': ['|', '|', '|', '|', '|', '|', '|', '|', '|', '|',  '|','|','|','|' ,'|',('social_group_id.code','ilike',data),('category_res_ids.name','ilike',data),('category_skill_ids.name','ilike',data),('category_id.name','ilike',data),('name', 'ilike', data), ('email', 'ilike', data), ('phone', 'ilike', data), ('ref', 'ilike', data), ('website', 'ilike', data), ('parent_id', 'ilike', data), ('street', 'ilike', data), ('street2', 'ilike', data), ('city', 'ilike', data), ('zip', 'ilike', data), ('state_id', 'ilike', data), ('country_id', 'ilike', data),('parent_id','!=',False)]},
            'res.partner.category': {'domain': [('name', 'ilike', data)]},
        }

        return domains
        
    @api.model
    def get_models(self):
        models = {
            'res.partner': _('Persons'),
            'social.partner.group': _('Social Groups'),
            'res.partner.category': _('Responsibilities')
                  # 'social.bit.comments': _('Engagements'),
            # 'social.post': _('Posts')
                  }
        return models

    @api.model
    def get_model_domains(self, data):
        domains = {
            # 'social.bit.comments': ['|','|',('partner_id','ilike',data),('comment','ilike',data),('comment','ilike',data)],
            #        'social.post': ['|', '|', '|', '|',('message','ilike',data),('utm_campaign_id','ilike',data),('social_partner_ids.name','ilike',data),('social_groups_ids.name','ilike',data),('social_groups_ids.partner_ids.name','ilike',data)],
                   'social.partner.group':['|','|','|',('name','ilike',data),('parent_id','ilike',data),('partner_ids.name','ilike',data),('code','ilike',data)],
                   'res.partner': ['|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|','|',('social_group_id.code','ilike',data),('category_res_ids.name','ilike',data),('category_skill_ids.name','ilike',data),('social_group_id.name','ilike',data),('category_id.name','ilike',data),('name', 'ilike', data), ('email', 'ilike', data), ('phone', 'ilike', data), ('ref', 'ilike', data), ('website', 'ilike', data), ('parent_id', 'child_of', data), ('street', 'ilike', data), ('street2', 'ilike', data), ('city', 'ilike', data), ('zip', 'ilike', data), ('state_id', 'ilike', data), ('country_id', 'ilike', data),('parent_id','!=',False)],
                   'res.partner.category': [('name','ilike',data)]
        }
        return domains

    @api.model
    def get_global_data(self, model):
        global_data = {}
        return global_data

    @api.model
    def get_field_list(self, model):
        field_list = ['display_name']
        # if model == "social.post":
        #     field_list = ["utm_campaign_id","message"]
        if model == "social.partner.group":
            # field_list.append("type")
            field_list.append("type_id")
        if model == "res.partner":
            field_list.append("category_id_name")
            field_list.append("category_skill_id_name")
            field_list.append("category_res_id_name")
            field_list.append("parent_id")
            field_list.append("name")
            field_list.append("category_social_id_name")
        return field_list

    @api.model
    def get_records(self, data, type=False):
        global_data = {}
        if type == "res.partner":
            models = {
                'res.partner': _('Persons'),
            }
            domains = {
                'res.partner': ['|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', ('social_group_id.code', 'ilike', data), ('category_res_ids.name', 'ilike', data),
                                ('category_skill_ids.name', 'ilike', data), ('social_group_id.name', 'ilike', data), ('category_id.name', 'ilike', data), ('name', 'ilike', data),
                                ('email', 'ilike', data), ('phone', 'ilike', data), ('ref', 'ilike', data), ('website', 'ilike', data), ('parent_id', 'child_of', data), ('street', 'ilike', data),
                                ('street2', 'ilike', data), ('city', 'ilike', data), ('zip', 'ilike', data), ('state_id', 'ilike', data), ('country_id', 'ilike', data), ('parent_id', '!=', False)],
            }
        elif type == "social.post":
            models = {
                'social.post': _('Posts')
            }
            domains = {
                       'social.post': ['|', '|', '|', '|',('message','ilike',data),('utm_campaign_id','ilike',data),('social_partner_ids.name','ilike',data),('social_groups_ids.name','ilike',data),('social_groups_ids.partner_ids.name','ilike',data),('state','=','posted')],
            }
        elif type == "social.partner.group":
            models = {
                'social.partner.group': _('Social Groups'),
            }
            domains = {
                'social.partner.group': ['|', '|', '|', ('name', 'ilike', data), ('parent_id', 'ilike', data), ('partner_ids.name', 'ilike', data), ('code', 'ilike', data)],
            }
        else:
            models = self.get_models()
            domains = self.get_model_domains(data)
        if data:
            new_data = data.split(" ")
            if len(new_data) > 1:
                for data in new_data:
                    domains = self.get_model_domains(data)
                    for model in models.keys():
                        # Get Total Records Count
                        count = self.env[model.split('-')[0]].search_count(domains[model])
                        field_list = self.get_field_list(model)
                        if model.split('-')[0] == 'social.partner.group' and not type:
                            results = self.env['social.partner.group'].sudo().read_group(domains[model], ['name'], ['type_id'])
                            results = {m['type_id'] and str(m['type_id'][1]) or 'Unknown': self.env['social.partner.group'].sudo().search_read(m['__domain'], field_list) for m in results}
                            if results:
                                global_data[model] = {'header': models[model], 'count': count}
                                global_data[model].update(self.get_global_data(model))
                                # Update Search Results
                                global_data[model].update({
                                    'data': [results]
                                })
                        else:
                            results = self.env[model.split('-')[0]].search_read(domains[model], field_list)
                            if model == "res.partner" and results:
                                all_parent_ids = list(set([x['parent_id'][0] for x in results if x.get("parent_id")]))
                                if all_parent_ids:
                                    parent_results = self.env[model.split('-')[0]].search_read([('id','in',all_parent_ids)], field_list)
                                    parent_results += self.env[model.split('-')[0]].search_read([('parent_id','=',False),('name','ilike',data)], field_list)
                                    model = "company"
                                    global_data[model] = {'header': _("Companies"), 'count': len(all_parent_ids)}
                                    global_data[model].update(self.get_global_data(model))
                                    # Update Search Results
                                    global_data[model].update({
                                        'data': parent_results
                                    })
                                    model = "res.partner"
                            if results:
                                global_data[model] = {'header': models[model], 'count': count}
                                global_data[model].update(self.get_global_data(model))
                                # Update Search Results
                                global_data[model].update({
                                    'data': results
                                })
            else:
                for model in models.keys():
                    # Get Total Records Count
                    count = self.env[model.split('-')[0]].search_count(domains[model])
                    field_list = self.get_field_list(model)
                    if model.split('-')[0] == 'social.partner.group' and not type:
                        results = self.env['social.partner.group'].sudo().read_group(domains[model], ['name'], ['type_id'])
                        results = {m['type_id'] and str(m['type_id'][1]) or 'Unknown': self.env['social.partner.group'].sudo().search_read(m['__domain'],field_list) for m in results}
                        if results:
                            global_data[model] = {'header': models[model], 'count': count}
                            global_data[model].update(self.get_global_data(model))
                            # Update Search Results
                            global_data[model].update({
                                'data': [results]
                            })
                    else:
                        results = self.env[model.split('-')[0]].search_read(domains[model], field_list)
                        if model == "res.partner" and results:
                            all_parent_ids = list(set([x['parent_id'][0] for x in results if x.get("parent_id")]))
                            if all_parent_ids:
                                parent_results = self.env[model.split('-')[0]].search_read([('id', 'in', all_parent_ids)], field_list)
                                parent_results += self.env[model.split('-')[0]].search_read([('parent_id', '=', False), ('name', 'ilike', data)], field_list)
                                model = "company"
                                global_data[model] = {'header': _("Companies"), 'count': len(all_parent_ids)}
                                global_data[model].update(self.get_global_data(model))
                                # Update Search Results
                                global_data[model].update({
                                    'data': parent_results
                                })
                                model = "res.partner"
                        if results:
                            global_data[model] = {'header': models[model], 'count': count}
                            global_data[model].update(self.get_global_data(model))
                            # Update Search Results
                            global_data[model].update({
                                'data': results
                            })
        _logger.info("----------global-data----------%s", global_data)
        return global_data

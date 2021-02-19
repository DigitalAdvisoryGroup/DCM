from odoo import api, models, _


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
        if res_model == 'social.bit.comments':
            datas[res_model] = {}
            menu_id = self.env.ref('dcm_customization.menu_midar_statistics_eng').id
            action_id = self.env.ref('dcm_customization.comments_model_name_action').id
            datas[res_model]['menu_id'] = menu_id
            datas[res_model]['action_id'] = action_id
        if res_model == 'social.post':
            datas[res_model] = {}
            menu_id = self.env.ref('social.menu_social_post').id
            action_id = self.env.ref('social.action_social_post').id
            datas[res_model]['menu_id'] = menu_id
            datas[res_model]['action_id'] = action_id
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
            'social.bit.comments': {'domain': ['|','|',('partner_id','ilike',data),('comment','ilike',data),('comment','ilike',data)]},
            'social.post': {'domain': ['|', '|', '|', '|',('message','ilike',data),('utm_campaign_id','ilike',data),('social_partner_ids.name','ilike',data),('social_groups_ids.name','ilike',data),('social_groups_ids.partner_ids.name','ilike',data)]},
            'social.partner.group': {'domain': ['|', '|', ('name', 'ilike', data), ('parent_id', 'ilike', data), ('partner_ids.name', 'ilike', data)]},
            'res.partner': {
                'domain': ['|', '|', '|', '|', '|', '|', '|', '|', '|', '|',  '|','|','|','|' ,('category_res_ids.name','ilike',data),('category_skill_ids.name','ilike',data),('category_id.name','ilike',data),('name', 'ilike', data), ('email', 'ilike', data), ('phone', 'ilike', data), ('ref', 'ilike', data), ('website', 'ilike', data), ('parent_id', 'ilike', data), ('street', 'ilike', data), ('street2', 'ilike', data), ('city', 'ilike', data), ('zip', 'ilike', data), ('state_id', 'ilike', data), ('country_id', 'ilike', data)]}
        }

        return domains
        
    @api.model
    def get_models(self):
        models = {'res.partner': _('Contacts'),'social.partner.group': _('Social Groups'),'social.bit.comments': _('Engagements'),'social.post': _('Posts')}
        return models

    @api.model
    def get_model_domains(self, data):
        domains = {
            'social.bit.comments': ['|','|',('partner_id','ilike',data),('comment','ilike',data),('comment','ilike',data)],
                   'social.post': ['|', '|', '|', '|',('message','ilike',data),('utm_campaign_id','ilike',data),('social_partner_ids.name','ilike',data),('social_groups_ids.name','ilike',data),('social_groups_ids.partner_ids.name','ilike',data)],
                   'social.partner.group':['|','|',('name','ilike',data),('parent_id','ilike',data),('partner_ids.name','ilike',data)],
                   'res.partner': ['|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',('category_res_ids.name','ilike',data),('category_skill_ids.name','ilike',data),('social_group_id.name','ilike',data),('category_id.name','ilike',data),('name', 'ilike', data), ('email', 'ilike', data), ('phone', 'ilike', data), ('ref', 'ilike', data), ('website', 'ilike', data), ('parent_id', 'child_of', data), ('street', 'ilike', data), ('street2', 'ilike', data), ('city', 'ilike', data), ('zip', 'ilike', data), ('state_id', 'ilike', data), ('country_id', 'ilike', data)]}
        return domains

    @api.model
    def get_global_data(self, model):
        global_data = {}
        return global_data

    @api.model
    def get_field_list(self, model):
        field_list = ['display_name']
        if model == "social.post":
            field_list = ["utm_campaign_id"]
        if model == "res.partner":
            field_list.append("category_id_name")
            field_list.append("category_skill_id_name")
            field_list.append("category_res_id_name")
            field_list.append("parent_id")
        return field_list

    @api.model
    def get_records(self, data):
        print("-------data----------",data)
        global_data = {}
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
                        # Search First 5 Records
                        results = self.env[model.split('-')[0]].search_read(domains[model], field_list, limit=5)
                        if model == "res.partner":
                            all_parent_ids = list(set([x['parent_id'][0] for x in results]))
                            if all_parent_ids:

                                parent_results = self.env[model.split('-')[0]].search_read([('id','in',all_parent_ids)], field_list, limit=5)
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
                    # Search First 5 Records

                    results = self.env[model.split('-')[0]].search_read(domains[model], field_list, limit=5)
                    if model == "res.partner":
                        all_parent_ids = list(set([x['parent_id'][0] for x in results]))
                        if all_parent_ids:
                            parent_results = self.env[model.split('-')[0]].search_read([('id', 'in', all_parent_ids)], field_list, limit=5)
                            model = "company"
                            global_data[model] = {'header': "Companies", 'count': len(all_parent_ids)}
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

        return global_data

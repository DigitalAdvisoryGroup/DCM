# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Allure Backend Theme Enterprise Studio',
    'category': "Themes/Backend",
    'version': '1.1',
    'license': 'OPL-1',
    'summary': 'Customized Backend Theme With studio',
    'description': 'Customized Backend Theme With studio',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'depends': ['web_studio','allure_backend_theme_ent'],
    'website': 'www.synconics.com',
    'data': [
        'views/webclient_templates.xml',
    ],
    'qweb': [
    ],
    'images': [
    ],
    'installable': True,
    'auto_install': False,
    'bootstrap': True,
    'application': True,
}
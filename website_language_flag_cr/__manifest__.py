# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Language Flag',
    'summary': 'Shows language flag image in website',
    'description': 'Shows language flag image in website',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://www.candidroot.com/",
    'depends': ['website'],
    'data': [
        'views/res_lang_view.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'license': 'OPL-1',
}

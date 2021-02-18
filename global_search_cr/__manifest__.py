# -*- coding: utf-8 -*-
{
    'name': 'Global Search',
    'version': '13.0.1.0',
    'category': 'Extra Tools',
    'description': "Search Contacts. Open searched results in separate form having Filters and Views per App. Add support for multilingual search.",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': "https://www.candidroot.com/",
    'depends': ['contacts','web_enterprise'],
    "data": [
        'security/global_search_security.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/res_partner_view.xml',
    ],
    'qweb': ['static/src/xml/base.xml'],
    'installable': True,
    'auto_install': False,
}

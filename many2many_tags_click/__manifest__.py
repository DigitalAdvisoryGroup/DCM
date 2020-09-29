# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Many2Many Tag record open",

    'summary': """
        Many2many tags widget open record in readonly""",

    'description': """
        Many2many tags widget open record in readonly.
    """,

    'author': "Candidroot Solutions Pvt Ltd",
    'website': "https://www.candidroot.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        'views/assets.xml',
    ],
}

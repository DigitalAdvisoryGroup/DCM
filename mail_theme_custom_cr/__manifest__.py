# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Mass Mail Template",

    'summary': """
        Save Custom Template from Massmailing also user can select template from saved Template.""",

    'description': """
        Custom Template for Mass Mailing.
    """,

    'author': "Candidroot Solutions Pvt Ltd",
    'website': "https://www.candidroot.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Marketing/Email Marketing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mass_mailing'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/mass_mailing.xml',
        'views/custom_theme.xml',
        "wizard/theme_wizard.xml"
    ],
}

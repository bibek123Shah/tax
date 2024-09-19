# -*- coding: utf-8 -*-
{
    'name': 'TDS Section',
    'author': 'Smarten Technologies',
    'category': 'Account',
    'license': 'GPL-3',
    'website': 'https://www.smarten.com.np',
    'version': '14.0',
    'summary': "This module help to create TDS section",
    'description': '''''',
    'depends': [
        'account',
        'account_reports'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/demo.xml',
        'views/view.xml',
        'views/account.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}

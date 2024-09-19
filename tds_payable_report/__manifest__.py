# -*- coding: utf-8 -*-

{
    'name': 'TDS Payable Report',
    'version': '17.0',
    'category': 'Accounting',
    'summary': 'TDS Payable Report',
    'website': 'https://www.smarten.com.np',
    'author': 'Smarten Technologies Pvt. Ltd.',
    'description': """The aim is to have a tds payable report.""",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/tds_payable_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}

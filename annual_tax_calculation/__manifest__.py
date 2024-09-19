{
    "name": "Annual Tax Invoioce",
    "version": "17.1",
    "category": "POS",
    "summary": "Annual Tax calculation ",
    "author": "Smarten Technologies",
    "website": "https://www.smarten.com.np",
    "license": "AGPL-3",
    "depends": ["hr_payroll","base"],


    'data': [
            'security/ir.model.access.csv',
            'wizard/tax_form.xml',

            'report/tax_report_template.xml',
            'report/tax_report.xml',
            
            # 'view/annual_tax_form.xml',
    ],
        

   
    'installable': True,
    'application': True,
    'auto_install': True,
}

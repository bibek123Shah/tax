from odoo import models, fields

class TaxReport(models.AbstractModel):
    _name = 'report.annual_tax_calculation.tax_report_template'
    _description = 'Tax Report'

    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'hr.payroll.annual.tax.form.wizard',
            'data': data.get('data', []),
            'employee_name': data.get('employee_name', ''),
            'batch': data.get('batch', ''),
        }
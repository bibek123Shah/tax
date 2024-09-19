from odoo import api, fields, models
from odoo.exceptions import UserError

class TaxFormWizard(models.TransientModel):
    _name = 'hr.payroll.annual.tax.form.wizard'
    _description = 'Annual tax form'

    department_id = fields.Many2one('hr.department', string="Department", required=True)
    employee_name = fields.Many2one('hr.employee', string="Employee", required=True)
    payslip_run_id = fields.Many2one('hr.payslip.run', string="Batch")
    payslip_id = fields.Many2one('hr.payslip', string = "Batch", required = True)
    
    def tax_report(self):
        # payslip_lines = self.env['hr.payslip'].search([('employee_id','=',self.employee_name.id),('payslip_run_id','=',self.payslip_run_id.id)])
        if self.payslip_id:
            data=[]
            for index,line in  enumerate(self.payslip_id.line_ids):
                data.append({
                    'name':line.name,
                    'category': line.category_id.name,
                    'quantity':line.quantity,
                    'rate':line.rate,
                    'salary_rule': line.salary_rule_id.name,
                    'amount': line.amount,
                    'total':line.total

                    })
            report_data = {
                    'data': data,
                    'employee_name': self.employee_name.name,
                    'batch': self.payslip_id.payslip_run_id.name
            }
            return self.env.ref('annual_tax_calculation.action_tax_report').report_action(self, data=report_data)
        else:
            raise UserError("No payslip found for the selected employee and batch.")
            
            
            
        

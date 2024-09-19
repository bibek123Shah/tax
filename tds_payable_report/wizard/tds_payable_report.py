# -*- coding: utf-8 -*-
import base64
import logging
import xlwt
from odoo import models, fields, _
from datetime import datetime, timedelta, date
import nepali_datetime

_logger = logging.getLogger(__name__)


class PartnerDetailedReporting(models.TransientModel):
    _name = "tds.payable.report"

    invoice_data = fields.Char('Name', )
    file_name = fields.Binary('TDS Payable Report', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
    date_from = fields.Date('Start Date', required=True, default=date.today())
    date_to = fields.Date('End date', required=True, default=date.today())

    def action_tds_payable_report(self):
        m_date_from = str(self.date_from)
        m_date_to = str(self.date_to)
        workbook = xlwt.Workbook()
        format0 = xlwt.easyxf(
            'font:height 300, bold True; pattern: pattern solid, fore_colour gray25; align: horiz center; borders: left thin, right thin, top thin, bottom thin;')
        format1 = xlwt.easyxf(
            'font:bold True; align: horiz left; borders: left thin, right thin, top thin, bottom thin;')
        format3 = xlwt.easyxf(
            'align: horiz left; borders: left thin, right thin, top thin, bottom thin;')
        format4 = xlwt.easyxf(
            'align: horiz right; borders: left thin, right thin, top thin, bottom thin;')
        format5 = xlwt.easyxf(
            'font:bold True; align: horiz right; borders: left thin, right thin, top thin, bottom thin;')
        format6 = xlwt.easyxf(
            'font:bold True; align: horiz left; borders: left thin, right thin, top thin, bottom thin;')

        sheet = workbook.add_sheet(
            "tds_payable_report", cell_overwrite_ok=True)
        sheet.col(0).width = int(15 * 260)
        sheet.col(1).width = int(60 * 260)
        sheet.col(2).width = int(18 * 260)
        sheet.col(3).width = int(10 * 260)
        sheet.col(4).width = int(16 * 260)
        sheet.col(5).width = int(14 * 260)
        sheet.col(6).width = int(14 * 260)
        sheet.col(7).width = int(12 * 260)
        sheet.col(8).width = int(15 * 260)

        sheet.write_merge(0, 1, 0, 6, 'TDS Payable Report' + " from " + str(
            self.date_from) + " to " + str(self.date_to), format0)
        sheet.write(2, 0, str("Company"), format1)
        sheet.write(2, 1, str(self.env.company.name), format1)

        sheet.write(4, 0, "PAN No.", format1)
        sheet.write(4, 1, "Name", format1)
        sheet.write(4, 2, "Transaction Date", format1)
        sheet.write(4, 3, "Date Type", format1)
        sheet.write(4, 4, "Payment Amount", format5)
        sheet.write(4, 5, "TDS Amount", format5)
        sheet.write(4, 6, "TDS Type", format5)

        self._cr.execute(
            """SELECT rp.vat pan, rp.name partner, aml.date, am.amount_untaxed payment_amount, aml.credit tds_amount, tt.name tds_type 
                FROM account_move_line aml  
                LEFT JOIN account_move am ON aml.move_id = am.id
                LEFT JOIN res_partner rp ON aml.partner_id = rp.id
                LEFT JOIN account_account aa ON aml.account_id = aa.id
                LEFT JOIN tds_section tds on tds.id = am.revenue_heading
                LEFT JOIN tds_type tt on tt.id = tds.tds_type
                WHERE aml.parent_state = 'posted' AND aa.name IN ('TDS Payable') 
                AND aml.debit = 0
                AND aml.date >= %s AND aml.date <= %s ORDER BY aml.date""",
            (m_date_from, m_date_to))
        result = self._cr.dictfetchall()
        row = 5
        for data in result:
            sheet.write(row, 0, data['pan'], format3)
            sheet.write(row, 1, data['partner'], format3)
            sheet.write(row, 2,
                        str(nepali_datetime.date.from_datetime_date(fields.Date.from_string(data['date'])).strftime(
                            '%Y.%m.%d')), format3)
            sheet.write(row, 3, str('BS'), format3)
            sheet.write(row, 4, data['payment_amount'], format4)
            sheet.write(row, 5, data['tds_amount'], format4)
            sheet.write(row, 6, data['tds_type'], format4)
            row = row + 1

        path = ("/home/odoo/reports/tds_payable_report.xls")
        workbook.save(path)
        file = open(path, "rb")
        file_data = file.read()
        out = base64.encodebytes(file_data)
        self.write({'state': 'get', 'file_name': out,
                   'invoice_data': 'Tds_Payable_Report.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tds.payable.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    # Convert the date in Nepali Date Format and Returns in Start Date to End Date(Start Date in BS to End Date in BS)
    def date_converter(self, date_from, date_to):
        start_bs = nepali_datetime.date.from_datetime_date(
            fields.Date.from_string(date_from))
        end_bs = nepali_datetime.date.from_datetime_date(
            fields.Date.from_string(date_to))
        date = str(date_from) + " to " + str(date_to) + \
            " ( " + str(start_bs) + " to " + str(end_bs) + " )"
        return date

import logging
from contextlib import nullcontext

from odoo import models, api, fields, _

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_tds_account = fields.Boolean('Is TDS Account', default=False)


class AccountMove(models.Model):
    _inherit = 'account.move'

    revenue_heading = fields.Many2one('tds.section', string='Revenue Headings')
    tds_rate = fields.Many2one('tds.rate', string="TDS Rate")
    tds_amount = fields.Float("TDS Amount", compute="_calculate_tds", store=True)
    tds_account = fields.Many2one('account.account', string="TDS Account", domain="[('is_tds_account','=',True)]")
    total_amount_after_tds = fields.Float("Total Amount After TDS", compute="_calculate_tds", store=True)
    is_tds_posted = fields.Boolean('Posted TDS', default=False)
    is_tds_bill = fields.Boolean('Is TDS', default=False)
    tds_label = fields.Char("TDS label")

    @api.onchange('tds_label')
    def change_label(self):
        if self.move_type in ('in_invoice', 'out_invoice') and self.is_tds_bill and self.is_tds_posted:
            for line in self.line_ids:
                if line.credit:
                    record = self.env['account.move.line'].browse(line._origin.id)
                    if record:
                        record.name = self.tds_label

    @api.onchange('tds_rate')
    def check_correct_rate(self):
        for rec in self:
            if rec.tds_rate and rec.revenue_heading:
                tds_rates_list = []
                for tds_rate in rec.revenue_heading.tds_rates:
                    tds_rates_list.append(tds_rate.name)

                if rec.tds_rate.name not in tds_rates_list:
                    rec.tds_rate = nullcontext

                    raise UserError(_('The TDS Rate you have selected is not in this Revenue Headings.'
                                      'The rate for this section are %s') % tds_rates_list)

    @api.depends('tds_rate', 'amount_total', 'amount_untaxed')
    def _calculate_tds(self):
        for self_obj in self:
            if self_obj.move_type in ['in_invoice', 'out_invoice'] and self_obj.is_tds_bill and self_obj.tds_rate:
                self_obj.tds_amount = (float(
                    self_obj.tds_rate.name) / 100) * self_obj.amount_untaxed if self_obj.amount_untaxed else 0
                self_obj.total_amount_after_tds = self_obj.amount_total - self_obj.tds_amount
            else:
                self_obj.tds_amount = 0
                self_obj.total_amount_after_tds = 0

    # ====bill==============tds===
    def get_tds_move_line_bill(self, move_id, account):
        return {
            'move_id': move_id,
            'name': self.tds_label,
            'account_id': account,
            'credit': round(self.tds_amount, 2),
            "display_type": "tax"
        }

    # ===========invoice======tds===entry
    def get_tds_move_line(self, move_id, account):
        return {
            'move_id': move_id,
            'name': self.tds_label,
            'account_id': account,
            'debit': round(self.tds_amount, 2),
            "display_type": "tax"
        }

    # ============bill===========payable===entry
    def get_payable_move_line(self, move_id, account):
        for rec in self.line_ids:
            if rec.credit:
                return {
                    'move_id': move_id,
                    'id': rec.id,
                    'partner_id': self.partner_id.commercial_partner_id.id,
                    'name': self.tds_label,
                    'account_id': account,
                    'credit': round(rec.credit - self.tds_amount, 2)
                }

    # ==========invoice=========receivable=====entry
    def get_receievable_move_line_invoice(self, move_id, account):
        for rec in self.line_ids:
            if rec.debit:
                return {
                    'move_id': move_id,
                    'id': rec.id,
                    'partner_id': self.partner_id.commercial_partner_id.id,
                    'name': self.tds_label,
                    'account_id': account,
                    'debit': round(rec.debit - self.tds_amount, 2)
                }

    # =========bill=========as===whole===entry==combine
    def get_move_vals(self, debit_line, credit_line):
        return {
            'id': self.id,
            'line_ids': [
                (1, debit_line['id'], debit_line),
                (0, 0, credit_line),
            ]
        }

    # ===============invoice===as==a===whole===entry==combine
    def get_move_vals_invoice(self, debit_line, credit_line):
        return {
            'id': self.id,
            'line_ids': [
                (1, debit_line['id'], debit_line),
                (0, 0, credit_line),
            ]
        }

    def calculate_tds(self):
        if self.move_type == 'in_invoice' and self.is_tds_bill:
            if not self.revenue_heading:
                raise UserError(_("Please Select the TDS Revenue Heading."
                                  "If you dont want to calculate TDS Please untick the 'Is TDS bill' field"))

            if not self.tds_rate:
                raise UserError(_("Please Select the TDS Rate."
                                  "If you dont want to calculate TDS Please untick the 'Is TDS bill' field"))

            if not self.tds_label:
                raise UserError(_("Please Enter the TDS label."))

            if not self.tds_account:
                raise UserError(_("Please Select the TDS Account."
                                  "If you dont want to calculate TDS Please untick the 'Is TDS bill' field"))

            if not self.partner_id:
                raise UserError(_("Please Select Partner"))

            if not self.is_tds_posted:
                if self.tds_amount:
                    move_line_vals_debit = self.get_payable_move_line(
                        self.id,
                        self.partner_id.property_account_payable_id.id
                    )
                    move_line_vals_credit = self.get_tds_move_line_bill(
                        self.id,
                        self.tds_account.id
                    )
                    move_vals = self.get_move_vals(
                        move_line_vals_debit,
                        move_line_vals_credit
                    )
                    self.with_context(check_move_validity=False).write(move_vals)
                    self.is_tds_posted = True

    def calculate_tds_invoice(self):
        if self.move_type == 'out_invoice' and self.is_tds_bill:
            if not self.revenue_heading:
                raise UserError(_("Please Select the TDS Revenue Heading."
                                  "If you dont want to calculate TDS Please untick the 'Is TDS bill' field"))
            if not self.tds_rate:
                raise UserError(_("Please Select the TDS Rate."
                                  "If you dont want to calculate TDS Please untick the 'Is TDS bill' field"))

            if not self.tds_label:
                raise UserError(_("Please Enter the TDS label."))

            if not self.tds_account:
                raise UserError(_("Please Select the TDS Account."
                                  "If you dont want to calculate TDS Please untick the 'Is TDS bill' field"))

            if not self.partner_id:
                raise UserError(_("Please Select Partner"))

            if not self.is_tds_posted:
                if self.tds_amount:
                    move_line_vals_debit = self.get_receievable_move_line_invoice(
                        self.id,
                        self.partner_id.property_account_receivable_id.id
                    )
                    move_line_vals_credit = self.get_tds_move_line(
                        self.id,
                        self.tds_account.id
                    )
                    move_vals = self.get_move_vals_invoice(
                        move_line_vals_debit,
                        move_line_vals_credit
                    )
                    self.with_context(check_move_validity=False).write(move_vals)
                    self.is_tds_posted = True

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.move_type == 'in_invoice':
                rec.calculate_tds()
            if rec.move_type == 'out_invoice':
                rec.calculate_tds_invoice()

        return res

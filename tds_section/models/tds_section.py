from odoo import models, fields


class TdsSection(models.Model):
    _name = 'tds.section'

    name = fields.Char(string="Revenue Headings", required=True)
    tds_type = fields.Many2one('tds.type', string="TDS Type", required=True)
    revenue_code = fields.Char(string="Revenue code")
    tds_rates = fields.Many2many('tds.rate', string="TDS Rate", required=True)

    def name_get(self):
        tds_rates = []
        for rec in self:
            name_list = []
            if rec.name and rec.tds_rates:
                for rate in rec.tds_rates:
                    name_list.append(rate.name)

                clean_name_list = [name.replace("'", "") for name in name_list]
                tds_rates.append((rec.id, rec.name + str(clean_name_list)))
            else:
                tds_rates.append((rec.id, rec.name))
        return tds_rates


class TdsType(models.Model):
    _name = 'tds.type'

    name = fields.Char("TDS Type", required=True)


class TdsRate(models.Model):
    _name = 'tds.rate'

    name = fields.Char(string="TDS Rate (in %)")

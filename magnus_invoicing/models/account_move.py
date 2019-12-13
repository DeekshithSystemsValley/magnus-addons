# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2018 Magnus Group B.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tools.translate import _
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    user_id = fields.Many2one(
        'res.users',
        string='Timesheet User'
    )


    @api.multi
    @api.constrains('operating_unit_id', 'analytic_account_id','user_id')
    def _check_analytic_operating_unit(self):
        for rec in self.filtered('user_id'):
            if not rec.operating_unit_id == \
                                    rec.user_id._get_operating_unit_id():
                raise UserError(_('The Operating Unit in the'
                                  ' Move Line must be the '
                                  'Operating Unit in the department'
                                  ' of the user/employee'))
        super(AccountMoveLine, self - self.filtered('user_id'))._check_analytic_operating_unit()

    @api.onchange('analytic_account_id', 'user_id')
    @api.multi
    def onchange_operating_unit(self):
        super(AccountMoveLine, self).onchange_operating_unit()
        if self.user_id:
            self.operating_unit_id = \
                self.user_id._get_operating_unit_id()

class AccountMove(models.Model):
    _inherit = "account.move"

    # override post(), when first post, nothing extra. When move.name exists,
    # it cannot be first posting. Then 'OU-balancing' lines are unlinked.
    @api.multi
    def post(self):
        for move in self:
            if not move.company_id.ou_is_self_balanced or not move.name:
                continue
            for line in move.line_ids:
                if line.name == 'OU-Balancing':
                    line.with_context(wip=True).unlink()
        res = super(AccountMove, self).post()
        return res

    @api.multi
    def wip_move_create(self, wip_journal):
        self.ensure_one()
        move_date = datetime.strptime(self.date, "%Y-%m-%d")
        last_day_month_before = (move_date - timedelta(days=move_date.day)).strftime("%Y-%m-%d")
        default = {
            'ref': 'WIP Invoicing Posting',
            'journal_id': wip_journal.id,
            'date': last_day_month_before,
            'narration': 'WIP Invoicing Posting',
         #   'name': "new_name",
            'to_be_reversed': True,
        }
        wip_move = self.copy(default)
        mls = wip_move.line_ids
        ids = []
        ids.append(self.env.ref('account.data_account_type_other_income').id)
        ids.append(self.env.ref('account.account.data_account_type_revenue').id)
        ids.append(self.env.ref('account.account.data_account_type_depreciation').id)
        ids.append(self.env.ref('account.account.data_account_type_expenses').id)
        ids.append(self.env.ref('account.account.data_account_type_direct_costs').id)
        bs_move_lines = mls.filtered(lambda r: r.account_id.type.id not in ids)
        pl_move_lines = mls - bs_move_lines
        amount = 0.0
        for line in pl_move_lines:
            amount += line.debit - line.credit
        bs_move_lines.unlink()
        ml_vals = {
            'type': 'dest',
            'name': name,
            'price': total,
            'account_id': self.env['account.invoice'].get_wip_default_account(),
            'date_maturity': inv.date_due,
            'amount_currency': diff_currency and total_currency,
            'currency_id': diff_currency and inv.currency_id.id,
        }
        (0, 0, {values})




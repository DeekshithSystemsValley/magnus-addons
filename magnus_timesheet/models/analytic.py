# -*- coding: utf-8 -*-
# Copyright 2018 Magnus ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from datetime import datetime, timedelta

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _fetch_emp_plan(self):
        emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        return True if emp and emp.planning_week else False

    @api.onchange('user_id')
    def _onchange_users(self):
        self.planned = self._fetch_emp_plan()

    @api.onchange('date')
    def _onchange_dates(self):
        if self.planned or self.env.context.get('default_planned',False) :
            dt = datetime.strptime(self.date, "%Y-%m-%d") if self.date else datetime.now().date()
            self.date = dt-timedelta(days=dt.weekday())
            self.company_id = self.env.user.company_id
            date = self.find_daterange_week(self.date)
            self.week_id = date.id
            self.select_week_id = date.id

    @api.onchange('select_week_id')
    def _onchange_select_week(self):
        if self.select_week_id and self.select_week_id != self.week_id:
            self.week_id = self.select_week_id.id

    @api.model
    def create(self, vals):
        res = super(AccountAnalyticLine, self).create(vals)
        if self.env.context.get('default_planned', False) and res.week_id != res.select_week_id:
            self.env.cr.execute(
                """UPDATE account_analytic_line SET week_id = %s
                WHERE id = %s""",
                (res.select_week_id.id, res.id),
            )
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountAnalyticLine, self).write(vals)
        for obj in self:
            if vals.get('select_week_id', False) and obj.week_id != obj.select_week_id:
                self.env.cr.execute(
                    """UPDATE account_analytic_line SET week_id = %s
                    WHERE id = %s""",
                    (obj.select_week_id.id, obj.id),
                )
        return res

    def _get_qty(self):
        for line in self:
            if line.planned:
                line.planned_qty = line.unit_amount
                line.actual_qty = 0.0
            else:
                line.actual_qty = line.unit_amount
                line.planned_qty = 0.0

    def _get_day(self):
        for line in self:
            line.day_name = str(datetime.strptime(line.date, '%Y-%m-%d').strftime("%m/%d/%Y"))+' ('+datetime.strptime(line.date, '%Y-%m-%d').strftime('%a')+')'

    task_id = fields.Many2one(ondelete='restrict')
    select_week_id = fields.Many2one('date.range', string='Week')
    planned = fields.Boolean(string='Planned')
    actual_qty = fields.Float(string='Actual Qty', compute='_get_qty', store=True)
    planned_qty = fields.Float(string='Planned Qty', compute='_get_qty', store=True)
    day_name = fields.Char(string="Day", compute='_get_day')
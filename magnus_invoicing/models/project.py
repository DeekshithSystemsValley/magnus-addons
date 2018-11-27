# -*- coding: utf-8 -*-
# Copyright 2018 Magnus ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Project(models.Model):
    _inherit = "project.project"

    invoice_principle = fields.Selection([
            ('ff','Fixed Fee'),
            ('tm','Time and Material'),
            ('ctm', 'Capped Time and Material')
        ],)
    invoice_schedule_ids = fields.One2many(
        'invoice.schedule.lines',
        'project_id',
        string='Invoice Schedule')
    code = fields.Char('Project Code')
    tag_ids = fields.Many2many('project.tags', string='Tags')
    po_number = fields.Char('PO Number')

    @api.multi
    def name_get(self):
        return [(value.id, "%s%s" % (value.code + '-' if value.code else '', value.name)) for value in self]



class Task(models.Model):
    _inherit = "project.task"

    task_user_ids = fields.One2many(
        'task.user',
        'task_id',
        string='Can register time',
        track_visibility='always'
    )
    correction_charge = fields.Boolean('Correction Chargeability')
    chargeable = fields.Boolean('Chargeable')
    invoice_properties = fields.Many2one('project.invoicing.properties', 'Invoice Properties')
    standby = fields.Boolean('Standby')
    outof_office_hours_week = fields.Boolean('Out of office hours week')
    outof_office_hours_weekend = fields.Boolean('Out of office hours weekend')

    @api.onchange('correction_charge', 'chargeable')
    def onchange_correction_charge(self):
        if self.correction_charge and not self.chargeable:
            self.chargeable = True
        if not self.correction_charge:
            self.expenses = False

    @api.model
    def default_get(self, fields):
        res = super(Task, self).default_get(fields)
        active_model = self.env.context.get('active_model', False)
        if active_model and active_model == 'project.project':
            active_id = self.env.context.get('active_id', False)
            if active_id:
                project = self.env['project.project'].browse(active_id)
                res['tag_ids'] = project.tag_ids.ids
        return res

    @api.onchange('project_id')
    def onchange_tags(self):
        if self.project_id and self.project_id.tag_ids:
            self.tag_ids = list(set(self.tag_ids.ids+self.project_id.tag_ids.ids))


class TaskUser(models.Model):
    _name = 'task.user'

    @api.one
    @api.depends('product_id')
    def _default_fee_rate(self):
        if self.product_id:
            self.fee_rate = self.product_id.list_price

    @api.model
    def _default_product(self):
        if self.user_id.employee_ids.product_id:
            return self.user_id.employee_ids.product_id.id

    task_id = fields.Many2one(
        'project.task',
        string='Task'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Consultants'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Fee rate Product',
        default=_default_product
    )
    fee_rate = fields.Float(
        default=_default_fee_rate,
        string='Fee Rate',
    )

class InvoiceScheduleLine(models.Model):
    _name = 'invoice.schedule.lines'

    project_id = fields.Many2one(
        'project.project',
    )

class ProjectInvoicingProperties(models.Model):
    _name="project.invoicing.properties"
    _description = "Project invoicing properties"


    name = fields.Char('Project Invoice Period', required=True)
    expenses = fields.Boolean('Expenses', default=True)
    specs_invoice_report = fields.Boolean('Add specs attachment to invoice')
    actual_time_spent = fields.Boolean('Invoice Actual Time Spent')
    actual_expenses = fields.Boolean('Invoice Expenses')
    actual_costs = fields.Boolean('Invoice Costs')
    fixed_amount = fields.Boolean('Invoice Fixed Amount')
    fixed_fee_capped = fields.Boolean('Invoice Fixed Fee Capped')
    fixed_fee_limit = fields.Monetary('Fixed Fee Limit')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)


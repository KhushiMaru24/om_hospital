from collections import defaultdict
from datetime import timedelta
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from odoo.tools.sql import create_index

from odoo.addons.payment import utils as payment_utils


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ref = fields.Many2one('hospital.appointment', string="Reference")
    appointment = fields.Integer(string="Appointment ID")
    appo = fields.Char(string="Appointment ID")
    service_line_ids = fields.One2many('sale.order.line', 'order_id', string='Service Lines', domain=[('product_id.type', '=', 'service')])
    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', domain=['|',('product_id.type', '=', 'consu'),('product_id.type', '=', 'product')])
    data = fields.One2many('sale.order.line', 'wizard_id', string="Data", copy=True, auto_join=True)


    @api.depends_context('lang')
    @api.depends('order_line.tax_id', 'order_line.price_unit', 'service_line_ids.tax_id', 'service_line_ids.price_unit',
                 'amount_total', 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            service_lines = order.service_line_ids.filtered(lambda x: not x.display_type)

            order_tax_lines = []
            if order_lines:
                order_tax_lines.extend([x._convert_to_tax_base_line_dict() for x in order_lines])
            if service_lines:
                order_tax_lines.extend([x._convert_to_tax_base_line_dict() for x in service_lines])

            tax_totals = self.env['account.tax']._prepare_tax_totals(
                order_tax_lines,
                order.currency_id or order.company_id.currency_id,
            )
            order.tax_totals = tax_totals

    # def _get_invoiceable_lines(self, final):
    #     invoiceable_lines = self.order_line.filtered(lambda line: line.qty_to_invoice > 0)
    #     service_lines = self.service_line_ids.filtered(lambda line: line.qty_to_invoice > 0)
    #     return invoiceable_lines + service_lines

    def _get_invoiceable_lines(self, final=False):
        invoices = super(SaleOrder, self)._get_invoiceable_lines(final)
        for order in self:
            for line in order.service_line_ids:
                if line.qty_to_invoice > 0:
                    invoices+=line
        return invoices






    # def _get_invoiceable_lines(self, final=False):
    #     # Call the super method to get the original functionality
    #     invoiceable_line_ids = super(SaleOrder, self)._get_invoiceable_lines(final)
    #     down_payment_line_ids = super(SaleOrder, self)._get_invoiceable_lines(final)
    #     pending_section = None
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #
    #     # Add service_line_ids to the invoiceable lines
    #     for order in self:
    #         for line in order.service_line_ids:
    #             if line.display_type == 'line_section':
    #                 # Only invoice the section if one of its lines is invoiceable
    #                 pending_section = line
    #                 continue
    #             if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
    #                 continue
    #             if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
    #                 if line.is_downpayment:
    #                     # Keep down payment lines separately, to put them together
    #                     # at the end of the invoice, in a specific dedicated section.
    #                     down_payment_line_ids+=line
    #                     continue
    #                 invoiceable_line_ids+=line
    #     return (invoiceable_line_ids + down_payment_line_ids)

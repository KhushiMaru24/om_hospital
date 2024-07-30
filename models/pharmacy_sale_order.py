from odoo import models,fields,api
from datetime import date
class PharmacySaleOrder(models.Model):
    _name = 'pharmacy.sale.order.data'
    _description = 'Pharmacy Order'
    _inherit = ['sale.order', 'mail.thread', 'mail.activity.mixin']

    appointment_ids = fields.One2many('hospital.appointment', 'data', string="Appointments")
    appointment_id = fields.Many2one('hospital.appointment')
    patient_id = fields.Many2one('hospital.patient', string="Patient")
    # pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines','data', string="Medicines")
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', compute='_compute_pharmacy_ids',
                                        string="Pharmacy Lines")
    transaction_ids = fields.Many2many(
        comodel_name='payment.transaction',
        relation='pharmacy_sale_order_transaction_rel',
        column1='pharmacy_sale_order_id',
        column2='transaction_id',
        string="Transactions")
    tag_ids = fields.Many2many('crm.tag', relation='pharmacy_sale_order_tag_rel', column1='order_id', column2='tag_id', string="Tags")
    # product_id = fields.Many2one(related='appointment_ids.pharmacy_line_ids.product')
    # prices = fields.Float(related='product_id.price')
    # company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    # currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    # price_subtotal = fields.Monetary(string="Subtotal", compute="_compute_price_subtotal")

    # @api.depends('price_unit', 'qty')
    # def _compute_price_subtotal(self):
    #     for rec in self:
    #         rec.price_subtotal = rec.price * rec.qty
    #total_price = fields.Float(string="Total Price", compute='_compute_total_price')

    # @api.depends('pharmacy_line_ids.price_subtotal')
    # def _compute_total_price(self):
    #     for rec in self:
    #         rec.total_price = sum(rec.pharmacy_line_ids.mapped('price_subtotal'))

    @api.depends('appointment_id.pharmacy_line_ids')
    def _compute_pharmacy_ids(self):
        for rec in self:
            rec.pharmacy_line_ids = [(6, 0, rec.appointment_id.mapped('pharmacy_line_ids').ids)]

    def action_order(self):
        return

    @api.model
    def create(self, vals):
        # Create partner if needed
        print("hello")
        partner_id = False
        if vals.get('appointment_id'):
            partner_id = self.env['res.partner'].create({
                'name': vals['appointment_id'],
            }).id

        # Create sale order lines
        order_lines = []
        if 'pharmacy_line_ids' in vals:
            for line in vals['pharmacy_line_ids']:
                product = self.env['product.product'].create({
                    'name': line['product_id']['name'],
                    'list_price': line['price_unit'],
                    'type': 'consu',
                })
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': line['product_uom_qty'],
                    'price_unit': line['price_unit'],
                }))

        # Update vals with partner_id and order_lines
        vals['partner_id'] = partner_id
        vals['order_line'] = order_lines
        print(super(PharmacySaleOrder, self).create(vals))
        # Call super to create sale order
        print(vals)
        return super(PharmacySaleOrder, self).create(vals)


# from odoo import models, fields, api
# import logging
#
# _logger = logging.getLogger(__name__)
# class PharmacySaleOrder(models.Model):
#     _name = 'pharmacy.sale.order.data'
#     _description = 'Pharmacy Order'
#     _inherit = 'sale.order'
#
#     # patient_id = fields.Many2one('om_hospital.hospital.patient', string="Patient")
#     appointment_id = fields.Many2one('hospital.appointment')
#     pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', compute='_compute_pharmacy_ids', string="Pharmacy Lines")
#     transaction_ids = fields.Many2many(
#                               comodel_name='payment.transaction',
#                               relation='pharmacy_sale_order_transaction_rel',
#                               column1='pharmacy_sale_order_id',
#                               column2='transaction_id',
#                               string="Transactions")
#     tag_ids = fields.Many2many('crm.tag', relation='pharmacy_sale_order_tag_rel', column1='order_id', column2='tag_id', string="Tags")
#     print("hello")
#     @api.depends('appointment_id.pharmacy_line_ids')
#     def _compute_pharmacy_ids(self):
#         for rec in self:
#             rec.pharmacy_line_ids = [(6, 0, rec.appointment_id.mapped('pharmacy_line_ids').ids)]
#
#     print("hello")
#     # @api.depends('order_line')
#     # def _compute_pharmacy_ids(self):
#     #     for order in self:
#     #         pharmacy_lines = self.env['appointment.pharmacy.lines'].search([('sale_order_id', '=', order.id)])
#     #         order.pharmacy_line_ids = [(6, 0, pharmacy_lines.ids)]
#     print("hello")
#     @api.model
#     def create(self, vals):
#         # Create partner if needed
#         _logger.info("Starting create method with vals: %s", vals)
#
#         print("hello")
#         partner_id = False
#         if vals.get('appointment_id'):
#             partner_id = self.env['res.partner'].create({
#                 'name': vals['appointment_id'],
#             }).id
#
#         # Create sale order lines
#         order_lines = []
#         if 'pharmacy_line_ids' in vals:
#             for line in vals['pharmacy_line_ids']:
#                 product = self.env['product.product'].create({
#                     'name': line['product_id']['name'],  # Assuming 'product_id' is a Many2one field
#                     'list_price': line['price_unit'],
#                     'type': 'consu',
#                 })
#                 order_lines.append((0, 0, {
#                     'product_id': product.id,
#                     'product_uom_qty': line['product_uom_qty'],
#                     'price_unit': line['price_unit'],
#                 }))
#
#         # Update vals with partner_id and order_lines
#         vals['partner_id'] = partner_id
#         vals['order_line'] = order_lines
#         print(super(PharmacySaleOrder, self).create(vals))
#         # Call super to create sale order
#         return super(PharmacySaleOrder, self).create(vals)
#
#         # return {
#         #     'type': 'ir.actions.act_window',
#         #     'res_model': 'sale.order',
#         #     'view_mode': 'form',
#         #     'res_id': sale_order.id,
#         #     'target': 'current',
#         #     'context': {'default_partner_id': self.patient_id.id},
#         # }

    # @api.model
    # def create_sale_order(self):
    #     customer = self.env['res.partner'].create({
    #         'name': self.patient_id
    #     })
    #
    #     product = self.env['product.product'].create({
    #         'name': self.pharmacy_line_ids.product,
    #         'list_price': self.pharmacy_line_ids.price,
    #         'type': 'consu',
    #     })
    #
    #     sale_order = self.env['sale.order'].create({
    #         'partner_id': customer.id,
    #         'order_line': [(0,0,{
    #             'product_id': product.id,
    #             'product_uom_qty': self.pharmacy_line_ids.qty,
    #             'price_unit': product.list_price,
    #         })]
    #     })
    #
    #     return sale_order

        # Extract patient_id
        # patient_id = vals.get('patient_id')
        #
        # # Call super to invoke original create method
        # new_order = super(PharmacySaleOrder, self).create(vals)
        #
        # # Update patient_id if provided
        # if patient_id:
        #     new_order.partner_id = patient_id
        #
        # if vals.get('transaction_ids'):
        #     transaction_ids = []
        #     for transaction_id in vals.get('transaction_ids'):
        #         transaction_ids.append((4, transaction_id.id))
        #         new_order.write({'transaction_ids': transaction_ids})
        #
        #         if vals.get('tag_ids'):
        #             tags = new_order.tag_ids + vals.get('tag_ids')
        #             new_order.write({'tag_ids': [(6, 0, tags.ids)]})
        #
        # return new_order

from odoo import models, fields,api

class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'
    _description = 'Sale Order Wizard'

    order_id = fields.Many2one('sale.order', string='Order Reference', required=True)
    data = fields.One2many('service.line.data', 'wizard_id', string="Data", copy=True, auto_join=True)
    # data = fields.One2many('sale.order.line', 'reference', string="Data", copy=True, auto_join=True)

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderWizard, self).default_get(fields)
        order_id = self.env.context.get('active_id')
        order = self.env['sale.order'].browse(order_id)
        order.ensure_one()  # Ensure there's exactly one record
        res['order_id'] = order.id
        return res

    def add_product_to_order(self):
        order = self.order_id
        for line in self.data:
            order_line_vals = {
                'order_id': order.id,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'price_unit': line.price_unit,
                'tax_id': [(6, 0, line.tax_id.ids)],
                'discount': line.discount,
                'product_packaging_id': line.product_packaging_id.id,
                'product_packaging_qty': line.product_packaging_qty,
                'name': line.name,
                # 'display_type': line.display_type,
            }
            self.env['sale.order.line'].create(order_line_vals)

        return {
            'type': 'ir.actions.act_window_close',
        }

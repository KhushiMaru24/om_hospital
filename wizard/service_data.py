from odoo import models,fields,api

class SrviceData(models.TransientModel):
    _name = 'service.line.data'

    wizard_id = fields.Many2one('sale.order.wizard', string='Wizard Reference')
    # order_id = fields.Many2one('sale.order', string='Order Reference', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)

    product_uom_qty = fields.Float(string="Quantity", default=1.0, required=True)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', depends=['product_id'])
    product_uom = fields.Many2one('uom.uom', string="Unit of Measure", compute='_compute_product_uom',
        store=True, readonly=False, precompute=True, ondelete='restrict')
    price_unit = fields.Float(string="Unit Price", compute='_compute_price_unit', digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)
    tax_id = fields.Many2many('account.tax', string='Taxes')
    discount = fields.Float(string='Discount (%)')
    product_packaging_id = fields.Many2one('product.packaging', string='Packaging')
    product_packaging_qty = fields.Float(string='Packaging Quantity')
    name = fields.Text(string="Description", compute='_compute_name', store=True)

    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            line.name = line.product_id.display_name or ''

    @api.depends('product_id', 'product_packaging_qty', 'product_uom')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.product_packaging_id:
                packaging_uom = line.product_packaging_id.product_uom_id
                qty_per_packaging = line.product_packaging_id.qty
                line.product_uom_qty = packaging_uom._compute_quantity(
                    line.product_packaging_qty * qty_per_packaging, line.product_uom or line.product_id.uom_id)

    @api.depends('product_id')
    def _compute_price_unit(self):
        for record in self:
            if record.product_id:
                record.price_unit = record.product_id.list_price
            else:
                record.price_unit = 0.0

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
                line.product_uom = line.product_id.uom_id

    @api.depends('product_id')
    def _compute_price_unit(self):
        self.price_unit = self.product_id.list_price
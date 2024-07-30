from odoo import models,fields,api,_

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    wizard_id = fields.Many2one(
        comodel_name='sale.order',
        string="Order Reference",
        required=True, ondelete='cascade', index=True, copy=False)

    reference = fields.Char(string='Transient Reference')

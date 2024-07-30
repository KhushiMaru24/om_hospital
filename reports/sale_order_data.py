from odoo import api, models, _


class PatientCardReport(models.AbstractModel):
    _name = 'report.om_hospital.sale_order_data'
    _description = 'Sale Order'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids[0])
        return {
            'doc_model': 'sale.order',
            'docs': docs
        }
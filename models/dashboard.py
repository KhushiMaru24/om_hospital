from odoo import models, fields, api

class Dashboard(models.Model):
    _name = 'dashboard.data'

    @api.model
    def fetch_data(self):
        user = self.env.user
        patient_count = self.env['hospital.patient'].search_count([])
        appointment_count = self.env['hospital.appointment'].search_count([])
        pharmacy_data = self.env['appointment.pharmacy.lines'].search([])
        product_qty_map = {}

        # Aggregate quantities per product
        for pharmacy_record in pharmacy_data:
            product_name = pharmacy_record.product.product_id
            quantity = pharmacy_record.qty

            if product_name in product_qty_map:
                product_qty_map[product_name] += quantity
            else:
                product_qty_map[product_name] = quantity

        # Prepare data in required format
        product_data = []
        for product_name, quantity_added in product_qty_map.items():
            product_data.append({
                'product_name': product_name,
                'quantity_added': quantity_added,
            })
        print(product_data)

        return {
            'patient_count': patient_count,
            'appointment_count': appointment_count,
            'pharmacy_data': product_data,
        }

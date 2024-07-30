from odoo import http
from odoo.http import request

class AjaxController(http.Controller):

    @http.route('/get_data', auth='public', type='json', csrf=True)  # Ensure csrf is enabled
    def get_total_product(self):
        try:
            # Example: Fetch data from 'om_hospital' related models
            patient_data = request.env['hospital.patient'].sudo().search_read([], ['name', 'age', 'gender'])
            # appointments = request.env['hospital.appointment'].sudo().search_read([], ['patient_id', 'appointment_date'])

            return {
                'result': {
                    'patients': patient_data,
                },
            }
        except Exception as e:
            return {'error': str(e)}

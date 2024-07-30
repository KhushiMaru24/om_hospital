from odoo import http
from odoo.http import request

class PatientController(http.Controller):

    @http.route('/patients', type='http', auth='public', website=True)
    def list_patients(self, **kwargs):
        patients = request.env['hospital.patient'].search([])
        return request.render('om_hospital.patient_list', {'patients': patients})

    @http.route('/patients/add_favorite', type='json', auth='public', methods=['POST'])
    def add_favorite(self, patient_id):
        patient = request.env['hospital.patient'].browse(int(patient_id))
        if patient:
            existing_favorite = request.env['hospital.favorite.patient'].search([
                ('patient_id', '=', patient.id),
                ('user_id', '=', request.env.user.id)
            ])
            if not existing_favorite:
                request.env['hospital.favorite.patient'].create({
                    'patient_id': patient.id,
                    'user_id': request.env.user.id
                })
                return {'success': True}
        return {'success': False}

from odoo import http
from odoo.http import request, Response
import json

class HospitalRpcController(http.Controller):

    @http.route('/rpc/hospital/patients', type='json', auth='public', methods=['POST'], csrf=False)
    def rpc_list_patients(self):
        patients = request.env['hospital.patient'].sudo().search([])
        patient_data = []
        for patient in patients:
            patient_data.append({
                'id': patient.id,
                'name': patient.name,
                'gender': patient.gender,
                # Add more fields as needed
            })
        return patient_data
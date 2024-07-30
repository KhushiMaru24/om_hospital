import logging
from datetime import datetime, date
import fields
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)

class CreateAppointment(http.Controller):


    @http.route('/appointment_webform', type="http", auth='public', website=True)
    def appointment_webform(self, **kw):
        patients = request.env['hospital.patient'].sudo().search([])
        return request.render("om_hospital.create_appointmentss", {})

    patient = ""

    # def action_done(self):
    #     if not self.patient:
    #         action = request.env.ref('om_hospital.create_patient_tg').read([])
    #         print(action)
    #         print(action[0])# Read the action
    #         if action:
    #             return action[0]  # Return the first (and presumably only) action dictionary
    #         else:
    #             return {}

    @http.route('/create/webappointment', type="http", auth='public', website=True)
    def create_webappointment(self, **kw):
        patient_name = kw.get('patient_id')
        appointment_time = kw.get('appointment_time')
        appointment_date = kw.get('appointment_date')
        hide_sales_price = kw.get('hide_sales_price')
        ref = kw.get('ref')
        gender = kw.get('gender')
        if appointment_date:
            try:
                appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
                current_year = date.today().year
                max_future_year = current_year + 2

                if appointment_date.year < current_year or appointment_date.year > max_future_year:
                    return request.render('om_hospital.create_appointmentss', {
                        'warning': {
                            'title': "Invalid Date",
                            'message': f"The appointment date must be between {current_year} and {max_future_year}"
                        }
                    })
            except ValueError:
                appointment_date = False
                return request.render('om_hospital.create_appointmentss', {
                    'warning': {
                        'title': "Invalid Date",
                        'message': "The appointment date is required"
                    }
                })
            if appointment_date < date.today():
                appointment_date = False
                return request.render('om_hospital.create_appointmentss', {
                    'warning': {
                        'title': "Invalid Date",
                        'message': "The appointment date must be today or future date"
                    }
                })

        patients = request.env['hospital.patient'].sudo().search([('name', '=', patient_name)])
        self.patient = patients

        if not patients:
            action = request.ref('om_hospital.create_patient_action')
            menu = request.ref('om_hospital.create_pati-_menu')
            return "/web#action=%s&view_type=form&menu_id=%s" % (action.id, menu.id)
            #return

        else:
            patient = patients[0]
            patient = request.env['hospital.appointment'].sudo().create({
                    'patient_id': patient.id,
                    'appointment_date': appointment_date,
                    'appointment_time': appointment_time,
                    # 'ref': ref,
                    'hide_sales_price': hide_sales_price,
                })
            _logger.info('Received form data: %s', patient)
            return request.render("om_hospital.appointment_thanks", {})




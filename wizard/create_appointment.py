# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
# from odoo.exception import ValidationError

class CreateAppointmentWizard(models.TransientModel):
    _name = "create.appointment.wizard"
    _description = "Create Appointment"

    # @api.model
    # def default_get(self, fields):
    #     print("Default")
    #     return super(CreateAppointmentWizard, self).default_get(fields)

    ref = fields.Char(string='Reference', tracking=True, default='123')
    patient_id = fields.Many2one('hospital.patient', string="Patient", required=True)
    appointment_id = fields.Many2one('hospital.patient', string="Appointment", domain=[('state','=','draft'), ('priority','in',('0','1',False))])

    def action_create_appointment(self):
        self.patient_id.ref = self.ref
        print("Button is clicked")
        # return{
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'create.appointment.wizard',
        #     'target': 'new',
        #     'res_id': self.id
        # }
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # def action_cancle(self):
    #     if self.appointment_id.booking_date == fields.Date.today():
    #         raise ValidationError(_("Sorry, cancellation is not allowed same date of appointment"))
    #     return


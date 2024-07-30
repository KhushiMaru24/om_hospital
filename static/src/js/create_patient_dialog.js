/** @odoo-module **/
import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class CreatePatientDialog extends Component {
    static template = "om_hospital.create_patient_tg";
    setup(env) {
        super.setup(env);
        this.state = useState({
            name: '',
            date_of_birth:'',
            age: '',
            gender: '',
        });
        this.rpc = useService('rpc');
        this.action = useService('action');
        this.save = this.save.bind(this);
        this.cancel = this.cancel.bind(this);
    }

    async save() {
        console.log('Save button clicked.');
        try {
            const { name,date_of_birth, age, gender } = this.state;

            // Check if required fields are filled before saving
            if (!name || !age || !gender) {
                throw new Error('Please fill out all required fields.');
            }
            const selectedDate = new Date(date_of_birth);
            const today = new Date();

            if (selectedDate > today) {
                alert('Invalid Date: Appointment date must be today or a past date.');
            }

            // Perform RPC call to create patient
            const result = await this.rpc("/web/dataset/call_kw/hospital.patient/create_patient",{
                model: 'hospital.patient',
                method: 'create_patient',
                args: [{ name,date_of_birth, age, gender }],
                kwargs: {}
            });
            console.log('RPC result:', result);

            // Trigger dialog close event on successful save
            this.closeDialog({ onClose: () => console.log('Patient created successfully.') });
        } catch (error) {
            console.error('Failed to create patient:', error);
            if (error.data && error.data.message) {
                alert('Error: ' + error.data.message);
            } else {
                alert('Failed to save patient. Please try again later.');
            }
        }
    }

    async cancel() {
        // Trigger dialog close event on cancel
         this.closeDialog({ onClose: () => console.log('Dialog cancelled.') });
     }


     closeDialog(options = {}) {
        try {
            console.log('Closing dialog...');
            const actionResult = this.action.doAction(
                { type: "ir.actions.act_window_close" },
                { onClose: options.onClose }
            );
            console.log('Action result:', actionResult); // Log the result to check for any returned data or errors
            console.log('Dialog closed.');
        } catch (error) {
            console.error('Failed to close dialog:', error);
        }
    }

}
//
//CreatePatientDialog.template = "om_hospital.create_patient_tg";

registry.category("public_components").add("create_patient_tg", CreatePatientDialog);

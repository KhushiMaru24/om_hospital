/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.add-favorite');
    buttons.forEach(function (button) {
        button.addEventListener('click', function () {
            var patientId = button.getAttribute('data-id');
            jsonrpc('/patients/add_favorite', 'call', {
                patient_id: patientId
            }).then(function (result) {
                if (result.success) {
                    alert('Patient added to favorites');
                } else {
                    alert('Failed to add patient to favorites');
                }
            }).guardedCatch(function (error) {
                console.error('Error:', error);
            });
        });
    });
});

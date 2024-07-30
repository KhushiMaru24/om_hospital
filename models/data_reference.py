from odoo import api, SUPERUSER_ID, _

def update_existing_appointments(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    appointments = env['hospital.appointment'].search([])

    for appointment in appointments:
        if appointment.reference is _('New'):
            sequence_code = 'hospital.appointment'
            reference = env['ir.sequence'].next_by_code('hospital.appointment') or '/'
            appointment.write({'reference': reference})

if __name__ == "__main__":
    # Use odoo-bin or odoo script to run this script
    # For example: ./odoo-bin -c odoo.conf -d your_database_name -u your_module_name --stop-after-init --logfile=/path/to/logfile.log --addons-path=/path/to/addons-path
    update_existing_appointments(cr, registry)

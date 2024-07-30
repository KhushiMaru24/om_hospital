/** @odoo-module */

import { ControlPanel } from "@web/search/control_panel/control_panel";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class PatientKanbanController extends KanbanController {

    setup() {
        super.setup();
        // Add any additional setup logic here if needed
    }
}

class PatientControlPanel extends ControlPanel {
    setup() {
        super.setup();
        this.action = useService('action');
    }

    // Add any additional methods or properties needed for the control panel

    get display() {
        return {
            layoutActions: false,
            ...this.props.display,
        };
    }
}
PatientControlPanel.template = 'om_hospital.PatientKanban.ControlPanel';

const PatientKanbanView = {
    ...kanbanView,
    Controller: PatientKanbanController,
    ControlPanel: PatientControlPanel,
    display: {
        controlPanel: {},
    },
};

registry.category('views').add('patient_kanban', PatientKanbanView);

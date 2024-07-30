/** @odoo-module **/

import { Component, useEffect, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { getColor } from "@web/core/colors/colors";
import { cookie } from "@web/core/browser/cookie";
import { loadBundle } from "@web/core/assets";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class CreateDashboard extends Component {
    setup() {
        super.setup(...arguments);
        this.pieChart = null;
        this.barChart = null;
        this.canvasRef = useRef("canvas");
        this.barCanvasRef = useRef("barCanvas");
        this.state = {
            patientCount: 0,
            appointmentCount: 0,
            pharmacyData: [],
            patientData: []
        };
        this.rpc = useService('rpc');
        this.action = useService('action');
        this.fetchData();
    }

    async fetchData() {
        try {
            const result = await this.rpc("/web/dataset/call_kw/hospital.appointment/fetch_data", {
                model: 'hospital.appointment',
                method: 'fetch_data',
                args: [],
                kwargs: {}
            });

            this.state.patientCount = result.patient_count;
            this.state.appointmentCount = result.appointment_count;
            this.state.pharmacyData = result.pharmacy_data;
            this.state.patientData = result.patient_data;

            console.log(result.patient_count);
            console.log(result.patient_data);

            this.render();
            this.renderCharts();
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        }
    }

    get patientCount() {
        return this.state.patientCount;
    }

    get appointmentCount() {
        return this.state.appointmentCount;
    }

    get pharmacyData() {
        return this.state.pharmacyData;
    }

    get patientData() {
        return this.state.patientData;
    }

    onPatientCardClick() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Patients',
            res_model: 'hospital.patient',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
        });
    }

    onAppointmentCardClick() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Appointments',
            res_model: 'hospital.appointment',
            view_mode: 'tree,form',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
        });
    }

    renderCharts() {
        if (this.pieChart) {
            this.pieChart.destroy();
        }

        if (this.barChart) {
            this.barChart.destroy();
        }

        const pieConfig = this.getPieChartConfig();
        this.pieChart = new Chart(this.canvasRef.el, pieConfig);

        const barConfig = this.getBarChartConfig();
        this.barChart = new Chart(this.barCanvasRef.el, barConfig);
    }

    getPieChartConfig() {
        const labels = this.state.pharmacyData.map(data => data.product_name);
        const data = this.state.pharmacyData.map(data => data.quantity_added);
        const backgroundColors = this.state.pharmacyData.map((_, index) => getColor(index, cookie.get("color_scheme")));

        return {
            type: "pie",
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: backgroundColors,
                    hoverOffset: 4,
                }],
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: 'Pharmacy Data',
                        color: 'black',
                        font: {
                            weight: 'bold',
                            size: 20
                        }
                    },
                    datalabels: {
                        display: true,
                        align: 'bottom',
                        backgroundColor: '#ccc',
                        borderRadius: 3,
                        font: {
                          size: 18,
                        },
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 15,
                            padding: 10,
                        },
                    },
                },
                maintainAspectRatio: false,
            },
        };
    }

    getBarChartConfig() {
        const labels = this.state.patientData.map(data => data.patient_name);
        const data = this.state.patientData.map(data => data.appointment_count);
        const backgroundColors = this.state.patientData.map((_, index) => getColor(index, cookie.get("color_scheme")));

        return {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: 'Number of Appointments',
                    data,
                    backgroundColor: backgroundColors,
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        precision: 0,
                    }
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                    title: {
                        display: true,
                        text: 'Patients Appointment',
                        color: 'black',
                        font: {
                            weight: 'bold',
                            size: 20
                        }
                    },
                    datalabels: {
                        anchor: 'end',
                        // Alignment of the labels
                        // (start, end, center, etc.)
                        align: 'end',
                        // Color of the labels
                        color: 'blue',
                        font: {
                            weight: 'bold',
                        },
                        formatter: function (data, context) {
                            // Display the actual data value
                            return data;
                        }
                    }
                },

                maintainAspectRatio: false,
//                onClick: (event, elements) => {
//                    if (elements.length > 0) {
//                        const chart = elements[0].element.$context.chart;
//                        const index = elements[0].index;
//                        console.log(this.state.patientData[index]);
//                        const patientName = chart.data.labels[index];
//                        const patientId = this.state.patientData[index].id;
//                        console.log(patientId)
//
//                        const appointmentURL = 'http://localhost:8068/web#active_id=5&model=hospital.appointment&view_type=list&cids=${patientId}&menu_id=355';
//
//                        window.location.href = appointmentURL;
//                    }
//                },

            },

        };
    }
}

CreateDashboard.template = "om_hospital.create_dashboard_tag";

registry.category("actions").add("create_dashboard_tag", CreateDashboard);

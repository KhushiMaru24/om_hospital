function createPatientComponent() {
    class PatientFormPopup {
        constructor(parent, props) {
            this.parent = parent;
            this.props = props;
            this.state = {
                name: '',
                age: '',
            };
            this.env = null; // Initialize env
            this.rpc = null; // Initialize rpc function
        }

        // Method to set up env and rpc
        async setup() {
        super.setup();

        this.rpc = useService('rpc');
        }

        async  savePatient() {
            const { name, age } = this.state;
            try {
                const response = await this.sendHttpRequest({
                    method: 'POST',
                    url: '/create/webpatient',
                    data: { name, age },
                });

                const responseData = JSON.parse(response);
                if (responseData.status === 'success') {
                    alert('Patient created successfully!');
                    this.closePopup();
                } else {
                    console.error('Failed to create patient:', responseData.error);
                    alert('Failed to create patient. Please try again.');
                }
            } catch (error) {
                console.error('Failed to create patient:', error);
                alert('Failed to create patient. Please try again.');
            }
        }

        closePopup() {
            const existingPopup = document.querySelector('.patient-form-popup');
            if (existingPopup) {
                existingPopup.remove();
            }
        }

        render() {
            return `
                <div class="patient-form-popup">
                    <h2>Create Patient</h2>
                    <input type="text" placeholder="Name" id="nameInput">
                    <input type="text" placeholder="Age" id="ageInput">
                    <button id="saveButton">Save</button>
                </div>
            `;
        }

        handleNameInputChange(event) {
            this.state.name = event.target.value;
        }

        handleAgeInputChange(event) {
            this.state.age = event.target.value;
        }

        handleSaveButtonClick() {
            this.savePatient();
        }
    }

    return PatientFormPopup;
}

function defineOdooModule() {
    const openPopupCondition = document.getElementById('openPatientPopupButton') !== null;

    if (openPopupCondition) {
        const PatientFormPopup = createPatientComponent();

        document.getElementById('openPatientPopupButton').addEventListener('click', function() {
            const existingPopup = document.querySelector('.patient-form-popup');
            if (!existingPopup) {
                const popupInstance = new PatientFormPopup(this, {});
                const popupHTML = popupInstance.render();
                document.body.insertAdjacentHTML('beforeend', popupHTML);

                const nameInput = document.getElementById('nameInput');
                const ageInput = document.getElementById('ageInput');

                nameInput.addEventListener('input', popupInstance.handleNameInputChange.bind(popupInstance));
                ageInput.addEventListener('input', popupInstance.handleAgeInputChange.bind(popupInstance));

                const saveButton = document.getElementById('saveButton');
                saveButton.addEventListener('click', popupInstance.handleSaveButtonClick.bind(popupInstance));
            }
        });
    } else {
        console.warn('Module not defined based on condition.');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    defineOdooModule();
});

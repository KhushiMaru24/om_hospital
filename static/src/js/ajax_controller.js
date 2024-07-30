jQuery(function($) {
    "use strict";

    function fetchData() {
        $.ajax({
            type: 'POST',
            url: '/get_data',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify({jsonrpc: '2.0', method: 'call', params: {}, id: Date.now()}),
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRF-Token', $("input[name='csrf_token']").val());
            },
            success: function(data) {
                //console.log("Server response:", data); // Log the entire server response
                if (data.error) {
                    console.error('Server error:', data.error.message);
                    $('.error-message').text(data.error.message || 'An error occurred');
                    $('.error-message').removeClass('d-none');
                    return;
                }

                if (!data.result) {
                    console.error('Unexpected response format');
                    $('.error-message').text('Unexpected response format');
                    $('.error-message').removeClass('d-none');
                    return;
                }

//                console.log('Reached after successful response'); // Check if this log appears
//                console.log('Data result:', data.result);
//                console.log('Data result:', data.result.result); // Log the structure of data.result

                // Display patients data
                $('.patients-container').html('');
                //console.log("Patients data:", Array.isArray(data.result.result.patients));
                if (Array.isArray(data.result.result.patients)) {
                    //console.log("Patients data:", data.result.result.patients); // Log patients data
                    data.result.result.patients.forEach(function(patient) {
                        $('.patients-container').append(
                            '<div>' + patient.name + ' -  ' + patient.age + ' -  ' + patient.gender + '</div>'
                        );
                    });
                } else {
                    console.error('No patients data found');
                }

                // Display appointments data
//                $('.appointments-container').html('');
//                if (Array.isArray(data.result.result.appointments)) {
//                    console.log("Appointments data:", data.result.result.appointments); // Log appointments data
//                    data.result.result.appointments.forEach(function(appointment) {
//                        $('.appointments-container').append(
//                            '<div>' + appointment.patient_id[1] + ', ' + appointment.appointment_date + '</div>'
//                        );
//                    });
//
//                } else {
//                    console.error('No appointments data found');
//                }
            },
            error: function(jqXHR, status, err) {
                console.error('Error fetching data:', status, err);
                $('.error-message').text('Error fetching data');
                $('.error-message').removeClass('d-none');
            }
        });
    }

    // Call fetchData initially and then set interval for continuous data refresh
    fetchData();
    setInterval(fetchData, 30000); // Refresh data every 30 seconds (adjust as needed)
});

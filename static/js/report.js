// Filter hospitals based on search inputs
function filterHospitals() {
  const name = document.getElementById('hospitalName').value;
  const state = document.getElementById('hospitalRegion').value;

  fetch(`/filter/hospitals?name=${encodeURIComponent(name)}&hospitalRegion=${encodeURIComponent(state)}`)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('hospitalCards');
      container.innerHTML = '';
      if (data.length === 0) {
        container.innerHTML = '<p>No hospitals found.</p>';
      } else {
        data.forEach(hospital => {
          const card = document.createElement('div');
          card.className = 'card';
          card.innerHTML = `
            <h4>${hospital.name}</h4>
            <p><strong>State:</strong> ${hospital.state}</p>
            <p><strong>City:</strong> ${hospital.city}</p>
            <p><strong>Address:</strong> ${hospital.address}</p>
            <p><strong>Pincode:</strong> ${hospital.pincode}</p>
          `;
          container.appendChild(card);
        });
      }
    })
    .catch(error => console.error('Error filtering hospitals:', error));
}

  // Filter doctors based on search inputs
  function filterDoctors() {
    const name = document.getElementById('doctorName').value;
    const speciality = document.getElementById('doctorSpeciality').value;
  
    fetch(`/filter/doctors?name=${encodeURIComponent(name)}&speciality=${encodeURIComponent(speciality)}`)
      .then(response => response.json())
      .then(data => {
        const container = document.getElementById('doctorCards');
        container.innerHTML = '';
        if (data.length === 0) {
          container.innerHTML = '<p>No doctors found.</p>';
        } else {
          data.forEach(doctor => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
              <h4>${doctor.name}</h4>
              <p><strong>Email:</strong> ${doctor.email}</p>
              <p><strong>Gender:</strong> ${doctor.gender}</p>
              <p><strong>Experience:</strong> ${doctor.experience} years</p>
              <p><strong>Specialty:</strong> ${doctor.specialty}</p>
              <p><strong>Contact:</strong> ${doctor.contact}</p>
              <p><strong>Location:</strong> ${doctor.location}</p>
            `;
            container.appendChild(card);
          });
        }
      })
      .catch(error => console.error('Error filtering doctors:', error));
  }
  
  
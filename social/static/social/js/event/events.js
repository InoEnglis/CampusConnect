//  Need to be updated, sad map wont show
//  function initMap() {
//     {% if event.location_type == 'inside' %}
//     const universityLocation = { lat: YOUR_UNIVERSITY_LAT, lng: YOUR_UNIVERSITY_LNG };
//     const universityMap = new google.maps.Map(document.getElementById("universityMap"), {
//       zoom: 16,
//       center: universityLocation,
//       styles: [
//         {
//           "featureType": "poi",
//           "stylers": [
//             { "visibility": "off" }
//           ]
//         }
//       ]
//     });
//     new google.maps.Marker({
//       position: universityLocation,
//       map: universityMap,
//       title: "{{ event.building }}",
//       icon: {
//         url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png"
//       }
//     });
//     {% elif event.location_type == 'outside' %}
//     // External location map
//     const externalLocation = { lat: {{ event.latitude }}, lng: {{ event.longitude }} };
//     const externalMap = new google.maps.Map(document.getElementById("externalMap"), {
//       zoom: 14,
//       center: externalLocation,
//       styles: [
//         {
//           "featureType": "poi",
//           "stylers": [
//             { "visibility": "simplified" }
//           ]
//         }
//       ]
//     });
//     new google.maps.Marker({
//       position: externalLocation,
//       map: externalMap,
//       title: "Event Location",
//       icon: {
//         url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png"
//       }
//     });
//     {% endif %}
//   }
  
  // Initialize Fancybox
  document.addEventListener('DOMContentLoaded', function() {
    Fancybox.bind("[data-fancybox]", {
    });
  });


  let registrationUrl = '';

  function openModal(url) {
    registrationUrl = url; 
    document.getElementById('confirmationModal').classList.remove('hidden'); 
  }

  function closeModal() {
    document.getElementById('confirmationModal').classList.add('hidden'); 
  }

  function redirectToEvent() {
    window.location.href = registrationUrl; 
  }
  


  const setReminderButton = document.getElementById('set-reminder-button');
  const reminderModal = document.getElementById('reminder-modal');
  const closeModalButton = document.getElementById('close-modal');

  // Show the modal when the "Set reminder" button is clicked
  setReminderButton.addEventListener('click', function () {
      reminderModal.classList.remove('hidden');
  });

  // Close the modal when the "Close" button is clicked
  closeModalButton.addEventListener('click', function () {
      reminderModal.classList.add('hidden');
  });

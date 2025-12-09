document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('reportForm');
  const successModal = document.getElementById('successModal');
  const modalContent = document.getElementById('modalContent');
  const modalCloseButton = document.getElementById('modalCloseButton');
  
 
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = `
      <svg class="w-5 h-5 mr-3 -ml-1 text-white animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      Processing...
    `;
    
    fetch(form.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        // Show success modal
        document.getElementById('modalTitle').textContent = 'Report Submitted';
        document.getElementById('modalMessage').textContent = data.message || 'Thank you for your report. Our team will review it promptly.';
        successModal.classList.remove('hidden');
      } else {
        // Handle error case
        document.getElementById('modalTitle').textContent = 'Something Went Wrong';
        document.getElementById('modalMessage').textContent = data.message || 'We encountered an issue processing your report. Please try again.';
        successModal.classList.remove('hidden');
        submitButton.disabled = false;
        submitButton.innerHTML = 'Submit Report';
      }
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('modalTitle').textContent = 'Connection Error';
      document.getElementById('modalMessage').textContent = 'Unable to connect to our servers. Please check your connection and try again.';
      successModal.classList.remove('hidden');
      submitButton.disabled = false;
      submitButton.innerHTML = 'Submit Report';
    });
  });
  
  // Close modal and redirect to post-list(feed)
  modalCloseButton.addEventListener('click', function() {
    successModal.classList.add('hidden');
    window.location.href = "{% url 'post-list' %}";
  });
  
  // Close modal when clicking background
  successModal.addEventListener('click', function(e) {
    if (e.target === successModal) {
      successModal.classList.add('hidden');
      window.location.href = "{% url 'post-list' %}";
    }
  });
});

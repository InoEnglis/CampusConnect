
// Needs documentation.

document.addEventListener('DOMContentLoaded', function() {
    flatpickr("#{{ form.birth_date.id_for_label }}", {
        dateFormat: "m/d/Y",
        maxDate: "today",
        allowInput: true,
        defaultDate: null,
        yearSelector: true,
        position: "auto",
        required: true,
        onOpen: function(selectedDates, dateStr, instance) {
            setTimeout(() => {
                const yearInput = instance.calendarContainer.querySelector('.numInput.cur-year');
                if (yearInput) {
                    yearInput.style.width = '70px';
                    yearInput.readOnly = false;
                }
            }, 10);
        }
    });

    const municipalitySelect = document.getElementById('municipality');
    const barangaySelect = document.getElementById('barangay');
    const municipalityBarangayData = {{ municipality_barangay_data|safe }};

    municipalitySelect.addEventListener('change', function() {
        const selectedMunicipality = this.value;
        barangaySelect.innerHTML = '<option value="">Select Barangay</option>';
        
        if (selectedMunicipality && municipalityBarangayData[selectedMunicipality]) {
            municipalityBarangayData[selectedMunicipality].forEach(barangay => {
                const option = document.createElement('option');
                option.value = barangay;
                option.textContent = barangay;
                barangaySelect.appendChild(option);
            });
        }
    });

    const totalSlides = 5;
    let currentSlide = 1;

    function updateProgress() {
        const progressPercentage = Math.round((currentSlide / totalSlides) * 100);
        document.getElementById('current-step').textContent = currentSlide;
        document.getElementById('total-steps').textContent = totalSlides;
        document.getElementById('progress-percentage').textContent = progressPercentage;
        document.getElementById('form-progress').style.width = `${progressPercentage}%`;
    }

    function validateNameFields() {
        const firstName = document.getElementById('{{ form.first_name.id_for_label }}').value.trim();
        const lastName = document.getElementById('{{ form.last_name.id_for_label }}').value.trim();
        let isValid = true;

        if (!firstName) {
            document.getElementById('first-name-error').classList.remove('hidden');
            document.getElementById('{{ form.first_name.id_for_label }}').classList.add('is-invalid');
            isValid = false;
        } else {
            document.getElementById('first-name-error').classList.add('hidden');
            document.getElementById('{{ form.first_name.id_for_label }}').classList.remove('is-invalid');
        }

        if (!lastName) {
            document.getElementById('last-name-error').classList.remove('hidden');
            document.getElementById('{{ form.last_name.id_for_label }}').classList.add('is-invalid');
            isValid = false;
        } else {
            document.getElementById('last-name-error').classList.add('hidden');
            document.getElementById('{{ form.last_name.id_for_label }}').classList.remove('is-invalid');
        }

        return isValid;
    }

    function validateBirthDate() {
        const birthDateInput = document.getElementById('{{ form.birth_date.id_for_label }}');
        const birthDate = birthDateInput.value.trim();
        let isValid = true;

        if (!birthDate) {
            document.getElementById('birth-date-error').classList.remove('hidden');
            birthDateInput.classList.add('is-invalid');
            return false;
        }
        const today = new Date();
        const birthDateObj = new Date(birthDate);
        let age = today.getFullYear() - birthDateObj.getFullYear();
        const monthDiff = today.getMonth() - birthDateObj.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDateObj.getDate())) {
            age--;
        }
        if (age < 12) {
            document.getElementById('birth-date-error').classList.remove('hidden');
            birthDateInput.classList.add('is-invalid');
            return false;
        }

        document.getElementById('birth-date-error').classList.add('hidden');
        birthDateInput.classList.remove('is-invalid');
        return true;
    }

    function validateAddressFields() {
        const municipality = document.getElementById('municipality').value;
        const barangay = document.getElementById('barangay').value;
        let isValid = true;

        if (!municipality) {
            document.getElementById('municipality-error').classList.remove('hidden');
            document.getElementById('municipality').classList.add('is-invalid');
            isValid = false;
        } else {
            document.getElementById('municipality-error').classList.add('hidden');
            document.getElementById('municipality').classList.remove('is-invalid');
        }

        if (!barangay) {
            document.getElementById('barangay-error').classList.remove('hidden');
            document.getElementById('barangay').classList.add('is-invalid');
            isValid = false;
        } else {
            document.getElementById('barangay-error').classList.add('hidden');
            document.getElementById('barangay').classList.remove('is-invalid');
        }

        return isValid;
    }


    document.querySelectorAll('.next-slide').forEach(button => {
        button.addEventListener('click', function() {
            let canProceed = true;
            
            if (currentSlide === 1) {
                canProceed = validateNameFields();
            } else if (currentSlide === 2) {
                canProceed = validateBirthDate();
            } else if (currentSlide === 3) {
                canProceed = validateAddressFields();
            }

            if (canProceed && currentSlide < totalSlides) {
                document.getElementById(`slide-${currentSlide}`).classList.add('hidden');
                currentSlide++;
                document.getElementById(`slide-${currentSlide}`).classList.remove('hidden');
                updateProgress();
                document.getElementById(`slide-${currentSlide}`).scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
        });
    });


    document.querySelectorAll('.prev-slide').forEach(button => {
        button.addEventListener('click', function() {
            if (currentSlide > 1) {
                document.getElementById(`slide-${currentSlide}`).classList.add('hidden');
                currentSlide--;
                document.getElementById(`slide-${currentSlide}`).classList.remove('hidden');
                updateProgress();
                
                document.getElementById(`slide-${currentSlide}`).scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
        });
    });

    const formInputs = document.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        input.classList.add('block', 'w-full', 'rounded-md', 'border-gray-300', 'shadow-sm', 
                          'focus:border-red-500', 'focus:ring-red-500', 'sm:text-sm');
    });

    updateProgress();
});

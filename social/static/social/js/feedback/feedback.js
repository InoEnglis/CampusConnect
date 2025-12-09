document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.querySelector('textarea');
    const charCounter = document.getElementById('charCounter');
    
    if (textarea && charCounter) {
      textarea.addEventListener('input', function() {
        charCounter.textContent = `${this.value.length}/5000`;
      });
    }
    
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
      fileInput.addEventListener('change', function() {
        const uploadText = document.getElementById('uploadText');
        if (this.files.length > 0) {
          uploadText.innerHTML = `
            <i class="fas fa-file-image text-blue-500 text-2xl mb-2"></i>
            <p class="text-sm text-gray-700 font-medium">${this.files[0].name}</p>
            <p class="text-xs text-gray-500">${(this.files[0].size / 1024 / 1024).toFixed(2)} MB</p>
          `;
        }
      });
    }
  });
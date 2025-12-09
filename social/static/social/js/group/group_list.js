function toggleVisibility(id) {
  const element = document.getElementById(id);
  if (element.classList.contains("hidden")) {
    element.classList.remove("hidden");
  } else {
    element.classList.add("hidden");
  }
}
document
  .getElementById("id_profile_image")
  .addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (event) {
        const preview = document.getElementById("imagePreview");
        preview.innerHTML = `<img src="${event.target.result}" alt="Preview" class="rounded-full w-100 h-100">`;
      };
      reader.readAsDataURL(file);
    }
  });

document.addEventListener("DOMContentLoaded", function () {
  const previews = document.querySelectorAll(".color-preview");
  previews.forEach((preview) => {
    const color = preview.getAttribute("data-banner-color");
    if (color) {
      preview.style.backgroundColor = color;
    }
  });

  const bannerInput = document.getElementById("id_banner_color");
  if (bannerInput) {
    bannerInput.addEventListener("input", function () {
      const colorBox = document.querySelector(".color-picker .color-preview");
      if (colorBox) {
        colorBox.style.backgroundColor = this.value;
      }
    });
  }
});

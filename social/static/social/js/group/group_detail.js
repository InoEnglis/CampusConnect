document.addEventListener("DOMContentLoaded", function () {
  const groupCover = document.querySelector(".group-cover");
  groupCover.style.backgroundColor = groupCover.dataset.bannerColor;
});

document.addEventListener("DOMContentLoaded", function () {
  // Tab switching function
  const postsTab = document.getElementById("posts-tab");
  const aboutTab = document.getElementById("about-tab");
  const membersTab = document.getElementById("members-tab");

  const postsSection = document.getElementById("posts-section");
  const aboutSection = document.getElementById("about-section");
  const membersSection = document.getElementById("members-section");

  //Tab switching handlers
  postsTab.addEventListener("click", function (e) {
    e.preventDefault();
    setActiveTab("posts");
  });

  aboutTab.addEventListener("click", function (e) {
    e.preventDefault();
    setActiveTab("about");
  });

  membersTab.addEventListener("click", function (e) {
    e.preventDefault();
    setActiveTab("members");
  });

  function setActiveTab(tabName) {
    // Update tab appearance
    postsTab.classList.remove("active");
    aboutTab.classList.remove("active");
    membersTab.classList.remove("active");

    // Hide all sections
    postsSection.classList.add("d-none");
    aboutSection.classList.add("d-none");
    membersSection.classList.add("d-none");

    // Show selected section and update tab
    if (tabName === "posts") {
      postsTab.classList.add("active");
      postsSection.classList.remove("d-none");
    } else if (tabName === "about") {
      aboutTab.classList.add("active");
      aboutSection.classList.remove("d-none");
    } else if (tabName === "members") {
      membersTab.classList.add("active");
      membersSection.classList.remove("d-none");
    }
  }

  // PReview image functionality
  const imageInput = document.getElementById("id_images");
  const imagePreviewContainer = document.getElementById(
    "imagePreviewContainer"
  );
  const previewImagesWrapper = document.getElementById("previewImagesWrapper");

  imageInput.addEventListener("change", function () {
    previewImagesWrapper.innerHTML = "";

    if (this.files && this.files.length > 0) {
      imagePreviewContainer.classList.remove("d-none");

      for (let i = 0; i < this.files.length; i++) {
        const reader = new FileReader();
        const file = this.files[i];

        reader.onload = function (e) {
          const col = document.createElement("div");
          col.className = "col-6 col-md-4";

          const imgContainer = document.createElement("div");
          imgContainer.className = "position-relative";

          const img = document.createElement("img");
          img.src = e.target.result;
          img.className = "img-fluid rounded mb-2";
          img.style.maxHeight = "100px";
          img.style.width = "100%";
          img.style.objectFit = "cover";

          const removeBtn = document.createElement("button");
          removeBtn.className =
            "btn btn-danger btn-sm position-absolute top-0 end-0";
          removeBtn.innerHTML = "&times;";
          removeBtn.onclick = function () {
            col.remove();
            if (previewImagesWrapper.children.length === 0) {
              imagePreviewContainer.classList.add("d-none");
            }
          };

          imgContainer.appendChild(img);
          imgContainer.appendChild(removeBtn);
          col.appendChild(imgContainer);
          previewImagesWrapper.appendChild(col);
        };

        reader.readAsDataURL(file);
      }
    } else {
      imagePreviewContainer.classList.add("d-none");
    }
  });
});

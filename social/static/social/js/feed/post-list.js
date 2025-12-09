let currentPage = 1; // Current page
const postContainer = document.getElementById("post-container");
const loadingSpinner = document.getElementById("loading");
const loadedPostIds = new Set(); // Track loaded post IDs

// Flag to track ongoing requests
let isLoading = false;

// Trigger infinite scroll when the user reaches the bottom
window.addEventListener("scroll", () => {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
    loadMorePosts();
  }
});

function loadMorePosts() {
  if (isLoading) return;
  isLoading = true;
  loadingSpinner.classList.remove("d-none");

  fetch(`/social/post/new/?page=${currentPage}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.posts.length > 0) {
        data.posts.forEach((postHtml) => {
          const tempDiv = document.createElement("div");
          tempDiv.innerHTML = postHtml;

          const postElement = tempDiv.querySelector("[data-post-id]");
          const postId = postElement?.dataset.postId;

          if (postId && !loadedPostIds.has(postId)) {
            // Check if post already exists in DOM
            if (!document.querySelector(`[data-post-id="${postId}"]`)) {
              loadedPostIds.add(postId);
              postContainer.appendChild(postElement);

              // Optional: Add smooth fade-in
              postElement.style.opacity = 0;
              setTimeout(() => {
                postElement.style.transition = "opacity 0.5s";
                postElement.style.opacity = 1;
              }, 10);
            }
          }
        });
        currentPage++;
        // Rebind event listeners after appending new posts
        bindPostActions(); // Rebind like, share, gallery, etc.
      } else {
        console.log("No more posts to load.");
        window.removeEventListener("scroll", loadMorePosts);
      }
    })
    .catch((error) => console.error("Error loading more posts:", error))
    .finally(() => {
      isLoading = false;
      loadingSpinner.classList.add("d-none");
    });
}

function bindPostActions() {
  // Rebind like button functionality
  document.querySelectorAll(".like-button").forEach((button) => {
    button.addEventListener("click", function () {
      if (button.disabled) return;
      button.disabled = true;

      const postId = this.dataset.postId;

      fetch(`/social/like/${postId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })
        .then((response) => response.json())
        .then((data) => {
          const likeCount = this.querySelector(".like-count");
          if (data.liked) {
            this.classList.add("liked");
            likeCount.innerText = data.like_count;
          } else {
            this.classList.remove("liked");
            likeCount.innerText = data.like_count;
          }
        })
        .catch((error) => console.error("Error:", error))
        .finally(() => (button.disabled = false));
    });
  });

  // Rebind share button functionality
  document.querySelectorAll(".share-button").forEach((button) => {
    button.addEventListener("click", function () {
      const postId = this.dataset.postId;
      fetch(`/social/share/${postId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Create a modal for sharing
            const modal = document.createElement("div");
            modal.className = "share-modal";
            modal.innerHTML = `
                            <div class="share-modal-content">
                                <div class="share-modal-header">
                                    <h4>Share Post</h4>
                                    <button class="close-modal">&times;</button>
                                </div>
                                <div class="share-modal-body">
                                    <p>Share this link with your friends:</p>
                                    <div class="share-link-container">
                                        <input type="text" value="${data.shared_post_url}" readonly class="share-link">
                                        <button class="copy-link">Copy</button>
                                    </div>
                                    <div class="share-options">
                                        <button class="share-option"><i class="fab fa-twitter"></i> Twitter</button>
                                        <button class="share-option"><i class="fab fa-facebook"></i> Facebook</button>
                                        <button class="share-option"><i class="fab fa-linkedin"></i> LinkedIn</button>
                                    </div>
                                </div>
                            </div>
                        `;
            document.body.appendChild(modal);

            // Copy link functionality
            modal
              .querySelector(".copy-link")
              .addEventListener("click", function () {
                const input = modal.querySelector(".share-link");
                input.select();
                document.execCommand("copy");
                this.innerText = "Copied!";
                setTimeout(() => {
                  this.innerText = "Copy";
                }, 2000);
              });

            // Close modal
            modal
              .querySelector(".close-modal")
              .addEventListener("click", function () {
                document.body.removeChild(modal);
              });

            // Close when clicking outside
            modal.addEventListener("click", function (e) {
              if (e.target === modal) {
                document.body.removeChild(modal);
              }
            });
          } else {
            console.error("Share failed:", data.error);
          }
        })
        .catch((error) => console.error("Error:", error));
    });
  });

  // Rebind gallery trigger
  document.querySelectorAll(".gallery-trigger").forEach((trigger) => {
    trigger.addEventListener("click", function (e) {
      e.stopPropagation(); // Prevent event bubbling
      const postId = this.closest(".post-media").dataset.postId;
      const startIndex = parseInt(this.dataset.index);

      // Get all image URLs for this post
      const imageElements = document.querySelectorAll(
        `#post-${postId} .gallery-data span`
      );
      const images = Array.from(imageElements).map((el) => el.dataset.url);

      // Create gallery modal
      openGallery(images, startIndex);
    });
  });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {
  // Elements
  const modal = document.getElementById("addPostModal");
  const previewContainer = document.getElementById("filePreviewContainer");
  const previewFiles = document.getElementById("previewFiles");
  const floatingProgressContainer = document.getElementById(
    "floatingProgressContainer"
  );
  const progressBar = document.getElementById("uploadProgressBar");
  const uploadPercentage = document.getElementById("uploadPercentage");
  const uploadStatus = document.getElementById("uploadStatus");
  const submitButton = document.getElementById("submitButton");
  const closeProgressBtn = document.getElementById("closeProgressBtn");
  const fileInputs = {
    images: document.getElementById("id_images"),
    video: document.getElementById("id_video"),
    files: document.getElementById("id_files"),
  };

  // Get Bootstrap modal instance
  let modalInstance = null;
  if (typeof bootstrap !== "undefined") {
    modalInstance = bootstrap.Modal.getInstance(modal);
  }

  // Setup file input triggers
  document
    .getElementById("uploadImagesBtn")
    .addEventListener("click", () => fileInputs.images.click());
  document
    .getElementById("uploadVideoBtn")
    .addEventListener("click", () => fileInputs.video.click());
  document
    .getElementById("uploadFilesBtn")
    .addEventListener("click", () => fileInputs.files.click());

  // Close progress button
  closeProgressBtn.addEventListener("click", function () {
    floatingProgressContainer.classList.add("hidden");
  });

  // Handle file selection for all types
  Object.values(fileInputs).forEach((input) => {
    input.addEventListener("change", function (e) {
      previewFiles.innerHTML = "";

      if (this.files && this.files.length > 0) {
        previewContainer.classList.remove("hidden");

        Array.from(this.files).forEach((file) => {
          const previewItem = document.createElement("div");
          previewItem.className =
            "relative bg-[#22303c] rounded-lg p-2 w-24 h-24 flex items-center justify-center";

          if (file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = function (e) {
              const img = document.createElement("img");
              img.src = e.target.result;
              img.className = "max-h-20 max-w-20 object-contain";
              previewItem.appendChild(img);
            };
            reader.readAsDataURL(file);
          } else if (file.type.startsWith("video/")) {
            const videoIcon = document.createElement("i");
            videoIcon.className = "fas fa-video text-3xl text-purple-400";
            previewItem.appendChild(videoIcon);
          } else {
            const fileIcon = document.createElement("i");
            fileIcon.className = "fas fa-file text-3xl text-green-400";
            previewItem.appendChild(fileIcon);
          }

          const fileName = document.createElement("div");
          fileName.className =
            "absolute bottom-0 left-0 right-0 bg-black bg-opacity-70 text-white text-xs p-1 truncate";
          fileName.textContent = file.name;
          previewItem.appendChild(fileName);

          const removeBtn = document.createElement("button");
          removeBtn.className =
            "absolute top-0 right-0 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs";
          removeBtn.innerHTML = "&times;";
          removeBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            previewItem.remove();
            if (previewFiles.children.length === 0) {
              previewContainer.classList.add("hidden");
            }
          });
          previewItem.appendChild(removeBtn);

          previewFiles.appendChild(previewItem);
        });
      } else {
        previewContainer.classList.add("hidden");
      }
    });
  });

  // Form submission with progress tracking
  document.getElementById("postForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const xhr = new XMLHttpRequest();

    // Show floating progress bar
    floatingProgressContainer.classList.remove("hidden");

    // Disable submit button during upload
    submitButton.disabled = true;
    submitButton.classList.add("opacity-50", "cursor-not-allowed");

    // Close the modal
    if (modalInstance) {
      modalInstance.hide();
    } else {
      // Fallback if Bootstrap modal instance is not available
      modal.classList.remove("show");
      modal.style.display = "none";
      modal.setAttribute("aria-hidden", "true");
      document.body.classList.remove("modal-open");

      // Remove modal backdrop if exists
      const backdrop = document.querySelector(".modal-backdrop");
      if (backdrop) {
        backdrop.remove();
      }
    }

    // Track upload progress
    xhr.upload.addEventListener("progress", function (e) {
      if (e.lengthComputable) {
        const percentComplete = Math.round((e.loaded / e.total) * 100);
        progressBar.style.width = percentComplete + "%";
        uploadPercentage.textContent = percentComplete + "%";

        if (percentComplete < 100) {
          uploadStatus.textContent = "Uploading...";
        } else {
          uploadStatus.textContent = "Processing...";
        }

        // Change color when complete
        if (percentComplete === 100) {
          progressBar.classList.remove("bg-blue-500");
          progressBar.classList.add("bg-green-500");
        }
      }
    });

    xhr.addEventListener("load", function () {
      // Handle successful upload
      progressBar.classList.remove("bg-blue-500");
      progressBar.classList.add("bg-green-500");
      uploadStatus.textContent = "Upload Complete!";
      uploadPercentage.textContent = "100%";

      // Hide progress bar after delay
      setTimeout(() => {
        floatingProgressContainer.classList.add("hidden");
        progressBar.style.width = "0%";
        progressBar.classList.remove("bg-green-500");
        progressBar.classList.add("bg-blue-500");
        uploadPercentage.textContent = "0%";
        uploadStatus.textContent = "Processing...";

        // Reset form
        document.getElementById("postForm").reset();
        previewContainer.classList.add("hidden");
        previewFiles.innerHTML = "";

        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.classList.remove("opacity-50", "cursor-not-allowed");
      }, 3000);

      // Handle response
      console.log(xhr.responseText);
      try {
        const response = JSON.parse(xhr.responseText);
        // Handle response data here
      } catch (e) {
        console.error("Error parsing response:", e);
      }
    });

    xhr.addEventListener("error", function () {
      // Handle upload error
      progressBar.classList.remove("bg-blue-500");
      progressBar.classList.add("bg-red-500");
      uploadStatus.textContent = "Upload Failed";
      uploadPercentage.textContent = "Error";

      setTimeout(() => {
        floatingProgressContainer.classList.add("hidden");
        progressBar.style.width = "0%";
        progressBar.classList.remove("bg-red-500");
        progressBar.classList.add("bg-blue-500");
        uploadPercentage.textContent = "0%";
        uploadStatus.textContent = "Processing...";

        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.classList.remove("opacity-50", "cursor-not-allowed");
      }, 5000);
    });

    xhr.open("POST", this.action || window.location.href, true);
    xhr.send(formData);
  });
});

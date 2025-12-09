document.addEventListener("DOMContentLoaded", function () {
  setupLikeButtons();
  setupShareButtons();
  setupGalleryTriggers();
});

/** Like button functionality */
function setupLikeButtons() {
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
          this.classList.toggle("liked", data.liked);
          likeCount.innerText = data.like_count;
        })
        .catch(console.error)
        .finally(() => (button.disabled = false));
    });
  });
}

/** Share button functionality */
function setupShareButtons() {
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
          if (data.success) showShareModal(data.shared_post_url);
          else console.error("Share failed:", data.error);
        })
        .catch(console.error);
    });
  });
}

function showShareModal(url) {
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
                        <input type="text" value="${url}" readonly class="share-link">
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

  modal.querySelector(".copy-link").addEventListener("click", function () {
    const input = modal.querySelector(".share-link");
    input.select();
    document.execCommand("copy");
    this.innerText = "Copied!";
    setTimeout(() => (this.innerText = "Copy"), 2000);
  });

  modal
    .querySelector(".close-modal")
    .addEventListener("click", () => modal.remove());
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.remove();
  });
}

/* Gallery image viewer */
function setupGalleryTriggers() {
  document.querySelectorAll(".gallery-trigger").forEach((trigger) => {
    trigger.addEventListener("click", function (e) {
      e.stopPropagation();
      const postId = this.closest(".post-media").dataset.postId;
      const startIndex = parseInt(this.dataset.index);
      const imageElements = document.querySelectorAll(
        `#post-${postId} .gallery-data span`
      );
      const images = Array.from(imageElements).map((el) => el.dataset.url);
      openGallery(images, startIndex);
    });
  });
}

function openGallery(images, startIndex = 0) {
  document
    .querySelectorAll(".gallery-modal")
    .forEach((modal) => modal.remove());
  document.body.style.overflow = "";

  const modal = document.createElement("div");
  modal.className = "gallery-modal";
  let currentIndex = startIndex;

  modal.innerHTML = `
            <div class="gallery-modal-content">
                <button class="close-gallery">&times;</button>
                <button class="prev-image"><i class="fas fa-chevron-left"></i></button>
                <div class="gallery-image-container">
                    <img src="${
                      images[currentIndex]
                    }" class="gallery-image" alt="Gallery image">
                </div>
                <button class="next-image"><i class="fas fa-chevron-right"></i></button>
                <div class="gallery-counter">${currentIndex + 1}/${
    images.length
  }</div>
            </div>
        `;

  document.body.appendChild(modal);
  document.body.style.overflow = "hidden";

  const close = () => {
    modal.remove();
    document.body.style.overflow = "";
    document.removeEventListener("keydown", onKey);
  };

  const galleryImg = modal.querySelector(".gallery-image");
  const counter = modal.querySelector(".gallery-counter");

  const loadImage = (index) => {
    const img = new Image();
    showLoader();
    img.onload = () => {
      galleryImg.src = images[index];
      counter.textContent = `${index + 1}/${images.length}`;
      hideLoader();
    };
    img.onerror = () => {
      galleryImg.src = "data:image/svg+xml,...";
      hideLoader();
    };
    img.src = images[index];
  };

  const showLoader = () => {
    const loader = document.createElement("div");
    loader.className = "gallery-loader";
    modal.querySelector(".gallery-image-container").appendChild(loader);
  };

  const hideLoader = () => {
    const loader = modal.querySelector(".gallery-loader");
    if (loader) loader.remove();
  };

  const onKey = (e) => {
    if (e.key === "ArrowLeft")
      nav((currentIndex - 1 + images.length) % images.length);
    if (e.key === "ArrowRight") nav((currentIndex + 1) % images.length);
    if (e.key === "Escape") close();
  };

  const nav = (index) => {
    currentIndex = index;
    loadImage(currentIndex);
  };

  modal.querySelector(".close-gallery").addEventListener("click", close);
  modal
    .querySelector(".prev-image")
    .addEventListener("click", () =>
      nav((currentIndex - 1 + images.length) % images.length)
    );
  modal
    .querySelector(".next-image")
    .addEventListener("click", () => nav((currentIndex + 1) % images.length));
  modal.addEventListener("click", (e) => {
    if (e.target === modal) close();
  });
  modal
    .querySelector(".gallery-modal-content")
    .addEventListener("click", (e) => e.stopPropagation());
  document.addEventListener("keydown", onKey);

  // Swipe Support
  let startX = 0,
    endX = 0;
  modal.addEventListener(
    "touchstart",
    (e) => (startX = e.changedTouches[0].screenX)
  );
  modal.addEventListener("touchend", (e) => {
    endX = e.changedTouches[0].screenX;
    if (endX < startX - 50) nav((currentIndex + 1) % images.length);
    if (endX > startX + 50)
      nav((currentIndex - 1 + images.length) % images.length);
  });
}


function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

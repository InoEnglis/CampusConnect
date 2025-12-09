const postId = "{{ post.id|escapejs }}";
const commentsSection = document.getElementById("comments-section");
const commentForm = document.getElementById("comment-form");
const commentInput = commentForm.querySelector(".comment-input");
const commentOptions = commentForm.querySelector(".comment-options");
const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
const wsUrl = `${wsProtocol}://${window.location.host}/ws/social/${postId}/`;

const CommentSocket = new WebSocket(wsUrl);

// Show comment options
commentInput.addEventListener("focus", function () {
  commentOptions.classList.remove("d-none");
});

// Hide comment options
commentInput.addEventListener("blur", function () {
  if (commentInput.value.trim() === "") {
    commentOptions.classList.add("d-none");
  }
});

CommentSocket.onmessage = function (e) {
  const data = JSON.parse(e.data);

  // Format the time display
  const timeDisplay = "Just now";

  if (data.parent_id === null) {
    // Main comment
    const commentHtml = `
                <div class="comment mb-3" id="comment-${data.comment_id}">
                    <div class="d-flex">
                        <img src="{{ request.user.profile.picture.url }}" alt="Profile Picture" 
                             class="rounded-circle me-2" style="width: 32px; height: 32px; object-fit: cover;">
                        <div class="flex-grow-1">
                            <div class="comment-bubble">
                                <div class="d-flex align-items-center mb-1">
                                    <strong class="me-2">${data.author}</strong>
                                    <small class="text-muted">${timeDisplay}</small>
                                </div>
                                <p class="mb-1">${data.comment}</p>
                            </div>
                            <div class="comment-actions mt-1 ms-2">
                                <button class="btn btn-link p-0 me-2 text-muted like-btn">
                                    Like
                                </button>
                                <button class="btn btn-link p-0 me-2 text-muted reply-btn" data-parent-id="${data.comment_id}">
                                    Reply
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
    commentsSection.insertAdjacentHTML("afterbegin", commentHtml);
  } else {
    // Reply to comment
    const parentComment = document.getElementById(`comment-${data.parent_id}`);
    let repliesContainer = parentComment.querySelector(".replies-container");

    if (!repliesContainer) {
      repliesContainer = document.createElement("div");
      repliesContainer.classList.add("replies-container", "ms-3", "mt-2");
      parentComment.querySelector(".flex-grow-1").appendChild(repliesContainer);
    }

    const replyHtml = `
                <div class="reply mb-2" id="comment-${data.comment_id}">
                    <div class="d-flex">
                        <img src="{{ request.user.profile.picture.url }}" alt="Profile Picture" 
                             class="rounded-circle me-2" style="width: 32px; height: 32px; object-fit: cover;">
                        <div class="flex-grow-1">
                            <div class="comment-bubble">
                                <div class="d-flex align-items-center mb-1">
                                    <strong class="me-2">${data.author}</strong>
                                    <small class="text-muted">${timeDisplay}</small>
                                </div>
                                <p class="mb-1">${data.comment}</p>
                            </div>
                            <div class="comment-actions mt-1 ms-2">
                                <button class="btn btn-link p-0 me-2 text-muted like-btn">
                                    Like
                                </button>
                                <button class="btn btn-link p-0 me-2 text-muted reply-btn" data-parent-id="${data.comment_id}">
                                    Reply
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

    repliesContainer.insertAdjacentHTML("beforeend", replyHtml);
  }
};

commentForm.addEventListener("submit", function (e) {
  e.preventDefault();
  const comment = commentInput.value;

  if (comment.trim()) {
    CommentSocket.send(
      JSON.stringify({
        comment: comment,
        author: "{{ request.user.username }}",
        parent_id: null,
      })
    );
    commentInput.value = "";
    commentOptions.classList.add("d-none");
  }
});

// Handle reply button clicks
document.addEventListener("click", function (e) {
  if (e.target.classList.contains("reply-btn")) {
    e.preventDefault();
    const parentId = e.target.dataset.parentId;
    const commentElement = document.getElementById(`comment-${parentId}`);

    // Remove any existing reply forms
    document
      .querySelectorAll(".reply-form-container")
      .forEach((el) => el.remove());

    const replyForm = `
                <div class="reply-form-container mt-2 d-flex">
                    <img src="{{ request.user.profile.picture.url }}" alt="Profile Picture" 
                         class="rounded-circle me-2" style="width: 32px; height: 32px; object-fit: cover;">
                    <form class="reply-form flex-grow-1" data-parent-id="${parentId}">
                        <input type="text" class="form-control reply-input mb-2" placeholder="Write a reply..." 
                               style="border-radius: 20px; background-color: #f0f2f5; border: none; font-size: 0.9375rem;">
                        <div class="d-flex">
                            <button type="submit" class="btn btn-primary btn-sm me-2" style="border-radius: 6px; font-weight: 600;">
                                Reply
                            </button>
                            <button type="button" class="btn btn-light btn-sm cancel-reply" style="border-radius: 6px;">
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            `;

    //insert the reply form
    let targetElement;
    if (commentElement.querySelector(".replies-container")) {
      targetElement = commentElement.querySelector(".replies-container");
    } else {
      // creates replies container if it doesn't exist
      const repliesContainer = document.createElement("div");
      repliesContainer.classList.add("replies-container", "ms-3", "mt-2");
      commentElement
        .querySelector(".flex-grow-1")
        .appendChild(repliesContainer);
      targetElement = repliesContainer;
    }

    targetElement.insertAdjacentHTML("beforeend", replyForm);
    targetElement.querySelector(".reply-input").focus();
  }

  // Handle cancel reply
  if (e.target.classList.contains("cancel-reply")) {
    e.target.closest(".reply-form-container").remove();
  }
});

// Handle reply form submission
document.addEventListener("submit", function (e) {
  if (e.target.classList.contains("reply-form")) {
    e.preventDefault();
    const replyInput = e.target.querySelector(".reply-input");
    const replyText = replyInput.value;
    const parentId = e.target.dataset.parentId;

    if (replyText.trim()) {
      CommentSocket.send(
        JSON.stringify({
          comment: replyText,
          author: "{{ request.user.username }}",
          parent_id: parentId,
        })
      );
      e.target.closest(".reply-form-container").remove();
    }
  }
});

// like functionality
document.addEventListener("click", function (e) {
  if (e.target.classList.contains("like-btn")) {
    e.preventDefault();
    e.target.classList.toggle("text-primary");
    if (e.target.classList.contains("text-primary")) {
      e.target.innerHTML = "Liked";
    } else {
      e.target.innerHTML = "Like";
    }
  }
});

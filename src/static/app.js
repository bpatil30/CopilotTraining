document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Helper to escape HTML so participant strings are safe to insert
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading/message and the select dropdown (keep default option)
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants section
        let participantsHTML = `<div class="participants">`;
        participantsHTML += `<div class="participants-header"><strong>Participants</strong><span class="participant-count">(${details.participants.length})</span></div>`;

        if (details.participants.length > 0) {
            participantsHTML += `<ul class="participants-list">`;
            details.participants.forEach((p) => {
              // include a delete button next to each participant
              participantsHTML += `<li class="participant-item"><span class="participant-email">${escapeHtml(p)}</span><button class="delete-participant" data-activity="${escapeHtml(name)}" data-email="${escapeHtml(p)}" aria-label="Remove participant">✖</button></li>`;
            });
            participantsHTML += `</ul>`;
          } else {
            participantsHTML += `<p class="no-participants">No participants yet</p>`;
          }

        participantsHTML += `</div>`; // end participants

        activityCard.innerHTML = `
          <h4>${escapeHtml(name)}</h4>
          <p>${escapeHtml(details.description)}</p>
          <p><strong>Schedule:</strong> ${escapeHtml(details.schedule)}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Refresh activities so participants list updates immediately
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Delegate delete clicks from participant delete buttons
  activitiesList.addEventListener("click", async (evt) => {
    const btn = evt.target.closest && evt.target.closest(".delete-participant");
    if (!btn) return;

    const activityName = btn.getAttribute("data-activity");
    const email = btn.getAttribute("data-email");

    if (!activityName || !email) return;

    if (!confirm(`Remove ${email} from ${activityName}?`)) return;

    try {
      const response = await fetch(`/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`, {
        method: "POST",
      });

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message || "Participant removed";
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");
        // Refresh activities to update UI
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "Failed to remove participant";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }

      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 4000);
    } catch (error) {
      console.error("Error removing participant:", error);
      messageDiv.textContent = "Failed to remove participant. Try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
    }
  });

  // Initialize app
  fetchActivities();
});

function fillGeolocation(formId) {
  const form = document.getElementById(formId);
  if (!form) return;
  const lat = form.querySelector('input[name="latitude"]');
  const lon = form.querySelector('input[name="longitude"]');
  if (!lat || !lon) return;

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        lat.value = position.coords.latitude;
        lon.value = position.coords.longitude;
      },
      () => {
        console.warn("Geolocation permission denied or unavailable.");
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 },
    );
  }
}

function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.content : "";
}

function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast align-items-center text-bg-${type} border-0`;
  toast.setAttribute("role", "alert");
  toast.setAttribute("aria-live", "assertive");
  toast.setAttribute("aria-atomic", "true");
  toast.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>`;
  container.appendChild(toast);
  new bootstrap.Toast(toast, { delay: 5000 }).show();
}

function insertHtml(selector, html) {
  const target = document.querySelector(selector);
  if (target) {
    target.insertAdjacentHTML("beforeend", html);
  }
}

// ============ Loading Overlay Functions ============
function showLoadingOverlay() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) {
    overlay.classList.add("show");
  }
}

function hideLoadingOverlay() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) {
    overlay.classList.remove("show");
  }
}

// ============ Password Modal Functions ============
function showPasswordModal(password) {
  const modal = document.getElementById("passwordModal");
  const passwordDisplay = document.getElementById("passwordDisplay");
  if (modal && passwordDisplay) {
    passwordDisplay.textContent = password;
    modal.classList.add("show");
  }
}

function hidePasswordModal() {
  const modal = document.getElementById("passwordModal");
  if (modal) {
    modal.classList.remove("show");
  }
}

function copyToClipboard(text) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      const btn = document.getElementById("copyPasswordBtn");
      const originalHtml = btn.innerHTML;
      btn.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
      btn.disabled = true;
      setTimeout(() => {
        btn.innerHTML = originalHtml;
        btn.disabled = false;
      }, 2000);
    })
    .catch(() => {
      showToast("Failed to copy password. Please copy manually.", "warning");
    });
}

// ============ Setup Password Modal Event Listeners ============
function setupPasswordModalListeners() {
  const copyBtn = document.getElementById("copyPasswordBtn");
  const closeBtn = document.getElementById("closePasswordBtn");

  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      const passwordDisplay = document.getElementById("passwordDisplay");
      if (passwordDisplay) {
        copyToClipboard(passwordDisplay.textContent);
      }
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", hidePasswordModal);
  }
}

async function submitAjaxForm(event) {
  event.preventDefault();
  const form = event.target;
  const action = form.action;
  const method = form.method.toUpperCase() || "POST";
  const submitButton = form.querySelector('button[type="submit"]');

  // Show loading overlay and disable button
  showLoadingOverlay();
  if (submitButton) {
    submitButton.disabled = true;
  }

  const formData = new FormData(form);
  const payload = {};
  formData.forEach((value, key) => {
    payload[key] = value;
  });

  try {
    const response = await fetch(action, {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
        "X-Requested-With": "XMLHttpRequest",
      },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    // Hide loading overlay
    hideLoadingOverlay();

    if (!response.ok || result.success === false) {
      showToast(
        result.error || result.message || "Unable to complete the request.",
        "danger",
      );
      if (submitButton) {
        submitButton.disabled = false;
      }
      return;
    }

    // Check if password should be shown in modal
    if (result.temporary_password) {
      showPasswordModal(result.temporary_password);
      // Reset form after showing password modal
      if (typeof form.reset === "function") {
        form.reset();
      }
      return;
    }

    // Show success toast
    showToast(result.message || "Saved successfully.", "success");

    const refreshTarget = form.dataset.refreshTarget || result.refreshTarget;
    if (result.row_html && refreshTarget) {
      insertHtml(refreshTarget, result.row_html);
      if (result.reset !== false && typeof form.reset === "function") {
        form.reset();
      }
      return;
    }

    if (result.redirect) {
      window.location.href = result.redirect;
      return;
    }

    // Reset form and re-enable button
    if (typeof form.reset === "function") {
      form.reset();
    }
    if (submitButton) {
      submitButton.disabled = false;
    }

    if (result.reload !== false && result.temporary_password === undefined) {
      // Only reload if we're not showing password modal
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    }
  } catch (error) {
    console.error(error);
    hideLoadingOverlay();
    showToast("Unable to complete the request. Please try again.", "danger");
    if (submitButton) {
      submitButton.disabled = false;
    }
  }
}

function bindAjaxForms() {
  const ajaxForms = document.querySelectorAll(
    'form[data-ajax="true"], form.ajax-form',
  );
  ajaxForms.forEach((form) => {
    form.addEventListener("submit", submitAjaxForm);
  });

  // Setup password modal listeners
  setupPasswordModalListeners();
}

window.addEventListener("DOMContentLoaded", () => {
  bindAjaxForms();
});

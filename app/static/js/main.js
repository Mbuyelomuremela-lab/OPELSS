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

async function submitAjaxForm(event) {
  event.preventDefault();
  const form = event.target;
  const action = form.action;
  const method = form.method.toUpperCase() || "POST";
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
      },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok || result.success === false) {
      showToast(result.message || "Unable to complete the request.", "danger");
      return;
    }
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

    if (result.reload !== false) {
      window.location.reload();
    }
  } catch (error) {
    console.error(error);
    showToast("Unable to complete the request. Please try again.", "danger");
  }
}

function bindAjaxForms() {
  const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
  ajaxForms.forEach((form) => {
    form.addEventListener("submit", submitAjaxForm);
  });
}

window.addEventListener("DOMContentLoaded", () => {
  bindAjaxForms();
});

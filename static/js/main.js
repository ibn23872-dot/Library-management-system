/* Library Management System - Frontend JS */

// Sidebar toggle
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const wrapper = document.querySelector('.main-wrapper');
  sidebar.classList.toggle('collapsed');
  if (wrapper) wrapper.classList.toggle('expanded');
}

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => alert.remove(), 5000);
  });
});

// Delete confirmation modal
function confirmDelete(formId, itemName) {
  const overlay = document.getElementById('confirm-modal');
  const msgEl   = document.getElementById('confirm-msg');
  if (msgEl) msgEl.textContent = `Are you sure you want to delete "${itemName}"? This action cannot be undone.`;
  overlay.classList.add('active');
  overlay.dataset.formId = formId;
}

function closeModal() {
  document.getElementById('confirm-modal').classList.remove('active');
}

function confirmAction() {
  const overlay = document.getElementById('confirm-modal');
  const form = document.getElementById(overlay.dataset.formId);
  if (form) form.submit();
  closeModal();
}

// AJAX member lookup on borrow/return screens
function lookupMember(input, displayEl) {
  const id = input.value.trim();
  if (!id || isNaN(id)) { displayEl.textContent = ''; return; }
  fetch(`/api/member/${id}`)
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        displayEl.innerHTML = `
          <span class="badge ${data.account_status === 'Active' ? 'badge-success' : 'badge-danger'}">
            ${data.name} — ${data.type} (${data.account_status})
          </span>`;
      } else {
        displayEl.innerHTML = '<span class="badge badge-danger">Member not found</span>';
      }
    })
    .catch(() => { displayEl.textContent = ''; });
}

function lookupBook(input, displayEl) {
  const isbn = input.value.trim();
  if (!isbn) { displayEl.textContent = ''; return; }
  fetch(`/api/book/${isbn}`)
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        displayEl.innerHTML = `
          <span class="badge ${data.available > 0 ? 'badge-success' : 'badge-danger'}">
            ${data.title} — ${data.available} available
          </span>`;
      } else {
        displayEl.innerHTML = '<span class="badge badge-danger">Book not found</span>';
      }
    })
    .catch(() => { displayEl.textContent = ''; });
}

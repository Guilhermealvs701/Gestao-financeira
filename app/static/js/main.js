/* ============================================================
   Finance Control Pro — main.js
   ============================================================ */

// ── Sidebar ───────────────────────────────────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('open');
  document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : '';
}

function closeSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.remove('open');
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}

// Fecha sidebar com ESC
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeSidebar();
});

// ── Dark Mode ─────────────────────────────────────────────────
function toggleDarkMode() {
  fetch('/api/toggle-dark', { method: 'POST',
    headers: { 'X-CSRFToken': getCSRFToken(), 'Content-Type': 'application/json' }
  })
  .then(r => r.json())
  .then(data => {
    document.documentElement.setAttribute('data-theme', data.dark_mode ? 'dark' : 'light');
    const icon = document.getElementById('darkIcon');
    if (icon) {
      icon.className = data.dark_mode ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    }
  })
  .catch(() => {
    // fallback local
    const html  = document.documentElement;
    const theme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', theme);
  });
}

// ── CSRF Token ────────────────────────────────────────────────
function getCSRFToken() {
  const el = document.querySelector('input[name="csrf_token"]') ||
             document.querySelector('meta[name="csrf-token"]');
  return el ? el.value || el.content : '';
}

// ── Toggle senha ──────────────────────────────────────────────
function togglePassword(inputId, btn) {
  const input = document.getElementById(inputId);
  const icon  = btn.querySelector('i');
  if (input.type === 'password') {
    input.type = 'text';
    icon.className = 'fa-solid fa-eye-slash';
  } else {
    input.type = 'password';
    icon.className = 'fa-solid fa-eye';
  }
}

// ── Auto-fechar toasts ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toast').forEach(el => {
    const toast = new bootstrap.Toast(el, { delay: 4500 });
    toast.show();
  });

  // Animação de entrada nos cards
  animateCards();

  // Formatar campos de valor
  formatCurrencyInputs();
});

// ── Animação de entrada ───────────────────────────────────────
function animateCards() {
  const cards = document.querySelectorAll('.kpi-card, .card-pro, .goal-card');
  cards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(16px)';
    card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    setTimeout(() => {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 50 + i * 40);
  });
}

// ── Formatação de moeda ───────────────────────────────────────
function formatCurrencyInputs() {
  document.querySelectorAll('input[type="number"][name="amount"]').forEach(input => {
    input.addEventListener('blur', () => {
      const val = parseFloat(input.value);
      if (!isNaN(val)) {
        input.value = val.toFixed(2);
      }
    });
  });
}

// ── Confirm delete genérico ───────────────────────────────────
function confirmDelete(url, name) {
  const form = document.getElementById('deleteForm');
  const nameEl = document.getElementById('deleteItemName');
  if (form) form.action = url;
  if (nameEl) nameEl.textContent = name;
  const modal = document.getElementById('deleteModal');
  if (modal) new bootstrap.Modal(modal).show();
}

// ── Responsivo: fecha sidebar ao clicar em nav-item (mobile) ──
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    if (window.innerWidth < 992) closeSidebar();
  });
});
const DOC_TYPE_ICONS = {
    'Property': '', 'Insurance': '', 'Passport': '',
    'Identity': '', 'Medical': '', 'Financial': '',
    'Legal': '', 'Vehicle': '', 'Other': '',
};

let isAdmin = false;
let allDocuments = [];
let activeFilter = 'All';

function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    html.setAttribute('data-theme', isDark ? 'light' : 'dark');
    document.getElementById('themeBtn').textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('vaultTheme', isDark ? 'light' : 'dark');
}

(function () {
    const saved = localStorage.getItem('vaultTheme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    window.addEventListener('DOMContentLoaded', () => {
        document.getElementById('themeBtn').textContent = saved === 'dark' ? '🌙' : '☀️';
    });
})();

function showToast(msg, type = 'success') {
    const t = document.getElementById('toast');
    t.textContent = '> ' + msg; t.className = 'toast ' + type; t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

function formatDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function escapeHtml(t) {
    return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function filterDocs(type, btn) {
    activeFilter = type;
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    renderDocuments(allDocuments);
}

function renderDocuments(docs) {
    const grid = document.getElementById('docGrid');
    const filtered = activeFilter === 'All' ? docs : docs.filter(d => d.document_type === activeFilter);

    if (filtered.length === 0) {
        grid.innerHTML = `
      <div class="empty-state">
        <span class="empty-icon">📂</span>
        <h3>No Documents Found</h3>
        <p>// ${activeFilter === 'All' ? 'No documents have been uploaded yet.' : 'No ' + activeFilter + ' documents found.'}</p>
      </div>`;
        return;
    }

    grid.innerHTML = filtered.map((doc, i) => {
        const icon = DOC_TYPE_ICONS[doc.document_type] || '';
        const deleteBtn = isAdmin ? `<button class="btn-doc danger" data-title="${escapeHtml(doc.title)}" onclick="openDeleteModal('${doc.id}', this, this.dataset.title)">DELETE</button>` : '';
        return `
      <div class="doc-card" data-type="${escapeHtml(doc.document_type)}" style="animation-delay:${i * 0.06}s">
        <div class="doc-card-top">
          <span class="doc-type-badge">${escapeHtml(doc.document_type || 'Document')}</span>
          <span class="doc-icon">${icon}</span>
        </div>
        <div class="doc-card-body">
          <div class="doc-title">${escapeHtml(doc.title)}</div>
          <div class="doc-date">// ADDED ${formatDate(doc.uploaded_at)}</div>
          <div class="doc-actions">
            <a class="btn-doc primary" href="/api/get_document/${doc.id}" target="_blank">VIEW</a>
            <a class="btn-doc" href="/api/get_document/${doc.id}" download>SAVE</a>
            ${deleteBtn}
          </div>
        </div>
      </div>`;
    }).join('');
}

async function loadUser() {
    try {
        const r = await fetch('/api/auth/me');
        if (!r.ok) { window.location.href = '/'; return; }
        const u = await r.json();
        document.getElementById('navUsername').textContent = u.username || u.email;
        isAdmin = u.is_admin;
        if (isAdmin) document.getElementById('adminLink').style.display = '';
    } catch { window.location.href = '/'; }
}

async function loadDocuments() {
    try {
        const r = await fetch('/api/documents');
        if (!r.ok) { window.location.href = '/'; return; }
        const data = await r.json();
        document.getElementById('docCount').textContent = `${data.count} / ${data.limit} DOCS`;
        allDocuments = data.documents || [];
        renderDocuments(allDocuments);
    } catch {
        document.getElementById('docGrid').innerHTML =
            `<div class="empty-state"><span class="empty-icon">⚠️</span><h3>Load Failed</h3><p>// Please refresh the page.</p></div>`;
    }
}

let pendingDeleteId = null;
let pendingDeleteBtn = null;

function openDeleteModal(id, btn, title) {
    pendingDeleteId = id;
    pendingDeleteBtn = btn;
    document.getElementById('modalDocTitle').textContent = title || 'this document';
    document.getElementById('deleteModal').classList.add('show');
    document.getElementById('modalConfirmBtn').disabled = false;
    document.getElementById('modalConfirmBtn').textContent = 'Yes';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('show');
    pendingDeleteId = null;
    pendingDeleteBtn = null;
}

// Close modal on overlay click
document.getElementById('deleteModal').addEventListener('click', function (e) {
    if (e.target === this) closeDeleteModal();
});

// Close modal on Escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeDeleteModal();
});

async function confirmDelete() {
    if (!pendingDeleteId) return;
    const btn = document.getElementById('modalConfirmBtn');
    btn.disabled = true;
    btn.textContent = 'Deleting…';
    try {
        const r = await fetch(`/api/documents/${pendingDeleteId}`, { method: 'DELETE' });
        const d = await r.json();
        if (!r.ok) throw new Error(d.detail);
        closeDeleteModal();
        showToast('Document deleted.');
        loadDocuments();
    } catch (e) {
        showToast(e.message, 'error');
        btn.disabled = false;
        btn.textContent = 'Yes';
    }
}

async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/';
}

// Inactivity Timer Protocol (5 minutes = 300000 ms)
let inactivityTimer;

function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    
    inactivityTimer = setTimeout(logout,  3 * 60 * 1000); // 5 mins
}

// Reset timer on any user interaction
window.addEventListener('mousemove', resetInactivityTimer);
window.addEventListener('mousedown', resetInactivityTimer);
window.addEventListener('keypress', resetInactivityTimer);
window.addEventListener('scroll', resetInactivityTimer);
window.addEventListener('touchstart', resetInactivityTimer);

// Initialize timer on load
resetInactivityTimer();

loadUser().then(loadDocuments);
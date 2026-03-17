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

function showMsg(text, type = 'error') {
    const box = document.getElementById('msgBox');
    box.textContent = '> ' + text; box.className = 'msg ' + type;
}

function fileSelected(input) {
    const f = input.files[0]; if (!f) return;
    if (!f.name.toLowerCase().endsWith('.pdf')) { showMsg('Only PDF files are accepted.'); input.value = ''; return; }
    if (f.size > 20 * 1024 * 1024) { showMsg('File too large. Maximum 20 MB.'); input.value = ''; return; }
    document.getElementById('fileName').textContent = f.name;
    document.getElementById('fileSize').textContent = (f.size / 1024 / 1024).toFixed(2) + ' MB';
    document.getElementById('filePreview').classList.add('show');
}

const dz = document.getElementById('dropZone');
dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('dragover'); });
dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
dz.addEventListener('drop', e => { e.preventDefault(); dz.classList.remove('dragover'); });

async function uploadDocument() {
    const title = document.getElementById('titleInput').value.trim();
    const type = document.getElementById('typeInput').value;
    const file = document.getElementById('fileInput').files[0];
    if (!title) return showMsg('Document title required.');
    if (!type) return showMsg('Document type required.');
    if (!file) return showMsg('PDF file required.');

    const btn = document.getElementById('uploadBtn');
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>ENCRYPTING & UPLOADING…';

    const pw = document.getElementById('progressWrap');
    const pf = document.getElementById('progressFill');
    pw.classList.add('show'); pf.style.width = '30%';

    const formData = new FormData();
    formData.append('title', title);
    formData.append('document_type', type);
    formData.append('file', file);

    try {
        pf.style.width = '65%';
        const r = await fetch('/api/upload-document', { method: 'POST', body: formData });
        const d = await r.json();
        if (!r.ok) throw new Error(d.detail || 'Upload failed');
        pf.style.width = '100%';
        showMsg('Upload complete: ' + d.message, 'success');
        document.getElementById('titleInput').value = '';
        document.getElementById('typeInput').value = '';
        document.getElementById('fileInput').value = '';
        document.getElementById('filePreview').classList.remove('show');
        loadDocCount();
    } catch (e) { showMsg(e.message); pf.style.width = '0'; }
    finally {
        btn.disabled = false; btn.innerHTML = 'ENCRYPT & UPLOAD';
        setTimeout(() => pw.classList.remove('show'), 2200);
    }
}

async function loadDocCount() {
    try {
        const r = await fetch('/api/documents'); if (!r.ok) return;
        const d = await r.json();
        const pct = Math.min((d.count / d.limit) * 100, 100);
        document.getElementById('limitText').textContent = `${d.count} / ${d.limit} DOCS USED`;
        document.getElementById('limitFill').style.width = pct + '%';
        if (d.count >= d.limit) {
            document.getElementById('limitText').textContent += ' — LIMIT REACHED';
            document.getElementById('uploadBtn').disabled = true;
        }
    } catch { }
}

async function checkAdmin() {
    try {
        const r = await fetch('/api/auth/me'); if (!r.ok) { window.location.href = '/'; return; }
        const u = await r.json();
        if (!u.is_admin) {
            document.body.innerHTML = `<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:#111;font-family:'Space Mono',monospace">
        <div style="border:3px solid #f5f0e8;background:#FF2D2D;color:white;padding:52px 48px;text-align:center;box-shadow:10px 10px 0 #f5f0e8;max-width:440px;width:90%">
          <div style="font-family:'Bebas Neue',sans-serif;font-size:56px;letter-spacing:0.1em">ACCESS DENIED</div>
          <p style="font-size:12px;margin:14px 0 24px;letter-spacing:0.08em;opacity:0.85">// ADMIN ONLY PAGE</p>
          <a href="/dashboard" style="background:#f5f0e8;color:#0a0a0a;padding:13px 28px;text-decoration:none;font-size:13px;font-weight:700;letter-spacing:0.08em;display:inline-block;border:2px solid #f5f0e8">← BACK TO VAULT</a>
        </div>
      </div>`;
            return;
        }
        const notice = document.getElementById('adminNotice');
        document.getElementById('adminEmail').textContent = u.email;
        notice.style.display = '';
    } catch { window.location.href = '/'; }
}

async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/';
}

// Inactivity Timer Protocol (5 minutes = 300000 ms)
let inactivityTimer;

function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(logout, 5 * 60 * 1000); // 5 mins
}

// Reset timer on any user interaction
window.addEventListener('mousemove', resetInactivityTimer);
window.addEventListener('mousedown', resetInactivityTimer);
window.addEventListener('keypress', resetInactivityTimer);
window.addEventListener('scroll', resetInactivityTimer);
window.addEventListener('touchstart', resetInactivityTimer);

// Initialize timer on load
resetInactivityTimer();

checkAdmin(); loadDocCount();

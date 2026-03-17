let currentEmail = '';

function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    html.setAttribute('data-theme', isDark ? 'light' : 'dark');
    document.getElementById('themeBtn').textContent = isDark ? '☀️ LIGHT' : '🌙 DARK';
    localStorage.setItem('vaultTheme', isDark ? 'light' : 'dark');
}

(function () {
    const saved = localStorage.getItem('vaultTheme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    window.addEventListener('DOMContentLoaded', () => {
        document.getElementById('themeBtn').textContent = saved === 'dark' ? '🌙 DARK' : '☀️ LIGHT';
    });
})();

function showMsg(text, type = 'error') {
    const box = document.getElementById('msgBox');
    box.textContent = '> ' + text;
    box.className = 'msg ' + type;
}
function clearMsg() { document.getElementById('msgBox').className = 'msg'; }

function updateDots(step) {
    [1, 2, 3].forEach(i => {
        const d = document.getElementById('dot' + i);
        d.className = 'step-dot' + (i < step ? ' done' : i === step ? ' active' : '');
    });
}

function showStep(n) {
    ['step1', 'step2', 'step3'].forEach((id, i) => {
        document.getElementById(id).classList.toggle('active', i === n - 1);
    });
    updateDots(n); clearMsg();
}

async function sendOTP() {
    const email = document.getElementById('emailInput').value.trim();
    if (!email) return showMsg('Email address required.');
    const btn = document.getElementById('sendOtpBtn');
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>SENDING…';
    try {
        const r = await fetch('/api/auth/request-otp', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email }) });
        const d = await r.json();
        if (!r.ok) throw new Error(d.detail || 'Failed to send OTP');
        currentEmail = email; showStep(2);
        showMsg('Code sent to ' + email, 'success');
        document.getElementById('otpInput').focus();
    } catch (e) { showMsg(e.message); }
    finally { btn.disabled = false; btn.innerHTML = 'Send Code →'; }
}

async function verifyOTP() {
    const otp = document.getElementById('otpInput').value.trim();
    if (otp.length !== 6) return showMsg('Full 6-digit code required.');
    const btn = document.getElementById('verifyBtn');
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>VERIFYING…';
    try {
        const r = await fetch('/api/auth/verify-otp', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: currentEmail, otp }) });
        const d = await r.json();
        if (!r.ok) throw new Error(d.detail || 'Verification failed');
        if (d.needs_username) { showStep(3); showMsg('Almost there! Choose a name.', 'success'); document.getElementById('usernameInput').focus(); }
        else { showMsg('Access granted. Loading vault…', 'success'); setTimeout(() => window.location.href = '/dashboard', 900); }
    } catch (e) { showMsg(e.message); btn.disabled = false; btn.innerHTML = 'Verify & Enter →'; }
}

async function setUsername() {
    const username = document.getElementById('usernameInput').value.trim();
    if (!username) return showMsg('Name required.');
    try {
        const r = await fetch('/api/auth/set-username', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: currentEmail, username }) });
        const d = await r.json();
        if (!r.ok) throw new Error(d.detail || 'Failed to set username');
        showMsg('Welcome, ' + username + '! Entering vault…', 'success');
        setTimeout(() => window.location.href = '/dashboard', 900);
    } catch (e) { showMsg(e.message); }
}

function goBack() { showStep(1); }

document.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    if (document.getElementById('step1').classList.contains('active')) sendOTP();
    else if (document.getElementById('step2').classList.contains('active')) verifyOTP();
    else if (document.getElementById('step3').classList.contains('active')) setUsername();
});
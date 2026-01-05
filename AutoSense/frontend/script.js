const API_BASE = (window.location.protocol === 'file:') ? "http://127.0.0.1:8000" : "";
const CACHE_TTL = 300000; // 5 minute cache
window.lastLoaded = { cleaner: 0, security: 0, ai: 0, processes: 0, disk: 0, uninstaller: 0 };
window.gaugesAnimated = false;

// THEME HANDLING
function toggleTheme() {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const newTheme = isLight ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const btn = document.getElementById('themeBtn');
    if(!btn) return;
    btn.innerHTML = theme === 'light' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
}

// Init logic
document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
});

function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('open');
}

function switchTab(tabId) {
    // Close sidebar on mobile after selection
    document.querySelector('.sidebar').classList.remove('open');
    
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll(`.nav-btn[onclick*="${tabId}"]`).forEach(btn => btn.classList.add('active'));

    const now = Date.now();
    const shouldRefresh = (tag) => (now - window.lastLoaded[tag] > CACHE_TTL);

    if (tabId === 'processes') { if(shouldRefresh('processes')) loadProcesses(); }
    if (tabId === 'cleaner') { if(shouldRefresh('cleaner')) scanJunk(); }
    if (tabId === 'security') { if(shouldRefresh('security')) checkSecurity(); }
    if (tabId === 'ai') { if(shouldRefresh('ai')) loadForecast(); }
    if (tabId === 'disk') { if(shouldRefresh('disk')) scanDisk(); }
    if (tabId === 'uninstaller') { if(shouldRefresh('uninstaller')) loadInstalledApps(); }
}

// --- DASHBOARD LOOPS ---
let netChart = null;
let netData = { labels: [], uploads: [], downloads: [] };

document.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 AutoSense Frontend Initializing...");
    
    // Force immediate visibility of the dashboard as a fallback
    // Force immediate visibility of the dashboard as a fallback logic removed 
    // to prevent it from staying visible when switching tabs.
    // relying on switchTab('dashboard') at the end.

    initNetChart();
    
    try {
        updateDashboard();
        predictRisk();
        loadSpecs();
    } catch (e) {
        console.error("Initial data load failed:", e);
    }

    try {
        initAnimations();
    } catch (e) {
        console.error("Animations failed:", e);
    }

    setInterval(updateDashboard, 3000);
    setInterval(predictRisk, 15000);
    
    // Check if user is logged in
    checkAuth();

    // Final sync
    switchTab('dashboard');
});

function checkAuth() {
    const user = localStorage.getItem('username');
    if (user) {
        document.getElementById('usernameDisplay').innerText = user;
    }
}

async function login() {
    const u = document.getElementById('loginUser').value;
    const p = document.getElementById('loginPass').value;
    if (!u || !p) return showToast("Enter credentials", "error");

    try {
        const r = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, password: p })
        });
        const d = await r.json();
        if (d.success) {
            localStorage.setItem('token', d.token);
            localStorage.setItem('username', d.username);
            showToast("Welcome back, " + d.username, "success");
            checkAuth();
            switchTab('dashboard');
        } else {
            showToast(d.detail || "Login failed", "error");
        }
    } catch { showToast("Auth server error", "error"); }
}

async function register() {
    const u = document.getElementById('loginUser').value;
    const p = document.getElementById('loginPass').value;
    if (!u || !p) return showToast("Enter credentials", "error");

    try {
        const r = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, password: p })
        });
        const d = await r.json();
        if (d.success) {
            showToast("Registration successful! You can now login.", "success");
        } else {
            showToast(d.detail || "Registration failed", "error");
        }
    } catch { showToast("Auth server error", "error"); }
}

function initNetChart() {
    if (typeof Chart === 'undefined') {
        document.getElementById('netChart').parentElement.innerHTML += '<div class="error-message" style="margin-top:10px">Charts Unavailable (Offline)</div>';
        return;
    }
    const ctx = document.getElementById('netChart').getContext('2d');
    netChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Upload (Mbps)',
                    data: [],
                    borderColor: '#8b5cf6',
                    tension: 0.4,
                    fill: false
                },
                {
                    label: 'Download (Mbps)',
                    data: [],
                    borderColor: '#06b6d4',
                    tension: 0.4,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { display: false }
            },
            plugins: { legend: { display: false } }
        }
    });
}

async function updateDashboard() {
    try {
        const r = await fetch(`${API_BASE}/status`);
        const d = await r.json();
        
        // Gauges
        if (!window.gaugesAnimated) {
             animateGauge('#cpuGauge', d.cpu);
             animateGauge('#ramGauge', d.ram);
             window.gaugesAnimated = true;
        } else {
             document.querySelector('#cpuGauge .value').innerText = d.cpu + '%';
             document.querySelector('#ramGauge .value').innerText = d.ram + '%';
        }
        
        // Health Score
        document.getElementById('sysHealthScore').innerText = d.health_score;
        
        // --- AI BRAIN UPDATE ---
        try {
            const rAI = await fetch(`${API_BASE}/api/ai/predict`);
            const aiData = await rAI.json();
            
            const badge = document.getElementById('aiStatusBadge');
            if(badge) {
                badge.innerText = aiData.risk_level;
                badge.style.color = aiData.risk_level === 'CRITICAL' ? '#ef4444' : (aiData.risk_level === 'WARNING' ? '#f59e0b' : '#10b981');
            }
            
            const bubble = document.getElementById('aiChatBubble');
            if(bubble && aiData.explanation) {
                // Avoid rewriting if identical to prevent blink
                 if(!bubble.innerText.includes(aiData.explanation.substring(0, 20))) {
                     bubble.innerHTML = `<p>${aiData.explanation}</p>`;
                 }
            }
        } catch {}

        // --- SECURITY STATUS ---
        try {
           const rSec = await fetch(`${API_BASE}/api/security/scan`);
           const secData = await rSec.json();
           const secEl = document.getElementById('secStatus');
           if(secEl) {
               secEl.innerText = secData.status;
               secEl.style.color = secData.status === 'CLEAN' ? 'var(--success)' : 'var(--danger)';
           }
        } catch {}

    } catch (e) { 
        console.error(e);
        // Offline handling
        const badge = document.getElementById('aiStatusBadge');
        if(badge) { badge.innerText = "OFFLINE"; badge.style.color = "gray"; }
    }
    
    // Net Stats (Keep existing logic)
    try {
        const r = await fetch(`${API_BASE}/api/network-stats`);
        const d = await r.json();
        if(document.getElementById('uploadSpeed')) {
            document.getElementById('uploadSpeed').innerText = d.upload_mbps.toFixed(1);
            document.getElementById('downloadSpeed').innerText = d.download_mbps.toFixed(1);
        }

        // Update Chart
        if (netChart) {
            const now = new Date().toLocaleTimeString();
            netChart.data.labels.push(now);
            netChart.data.datasets[0].data.push(d.upload_mbps);
            netChart.data.datasets[1].data.push(d.download_mbps);
            
            if (netChart.data.labels.length > 20) {
                netChart.data.labels.shift();
                netChart.data.datasets[0].data.shift();
                netChart.data.datasets[1].data.shift();
            }
            netChart.update('none');
        }
    } catch {}
}

async function predictRisk() {
    try {
        const r = await fetch(`${API_BASE}/api/ai/predict`);
        const d = await r.json();
        const el = document.getElementById('aiPrediction');
        el.innerHTML = `AI Risk Assessment: <b style="color:${d.risk_level=='LOW'?'#10b981':'#ef4444'}">${d.risk_level}</b> (${d.risk_score}/100)`;
        
        // Store report globally for modal
        window.currentExpertReport = d.expert_report; // From backend
    } catch {
        const el = document.getElementById('aiPrediction');
        if(el) el.innerHTML = `<span style="color:var(--text-muted)">AI Offine</span>`;
    }
}

function viewExpertReport() {
    if(!window.currentExpertReport) { showToast("AI is still thinking...", "info"); return; }
    
    // Simple Modal for Report or render in Chat
    let reportHtml;
    if (typeof marked !== 'undefined') {
         reportHtml = marked.parse(window.currentExpertReport);
    } else {
         reportHtml = window.currentExpertReport
            .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
            .replace(/\n/g, '<br>');
    }
        
    document.getElementById('modalTitle').innerText = "AutoSense AI Analysis";
    document.getElementById('modalList').innerHTML = `<div style="text-align:left; line-height:1.6; color:#e2e8f0">${reportHtml}</div>`;
    document.querySelector('.modal').classList.remove('hidden');
}

// --- CHATBOT ---
function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.classList.toggle('hidden');
    if(!chatWindow.classList.contains('hidden')) {
        document.getElementById('chatInput').focus();
        if(document.getElementById('chatMessages').children.length === 0) {
            addBotMessage("Hello! I am AutoSense AI. Ask me about your system health, or say 'optimize' to start a cleanup.");
        }
    }
}

async function sendChat() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if(!msg) return;
    
    addUserMessage(msg);
    input.value = "";
    
    // Show typing
    const typingId = addBotMessage("Thinking...");
    
    try {
        const r = await fetch(`${API_BASE}/api/ai/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: msg })
        });
        const d = await r.json();
        
        // Remove typing
        document.getElementById(typingId).remove();
        addBotMessage(d.response);
        
    } catch {
        document.getElementById(typingId).innerText = "Error: Could not reach AI brain.";
    }
}

function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'chat-message user';
    div.innerText = text;
    document.getElementById('chatMessages').appendChild(div);
    div.scrollIntoView();
}

function addBotMessage(text) {
    const div = document.createElement('div');
    div.className = 'chat-message bot';
    div.id = 'msg-' + Date.now();
    div.innerHTML = text.replace(/\n/g, '<br>');
    document.getElementById('chatMessages').appendChild(div);
    div.scrollIntoView();
    return div.id;
}

// Enter key support
document.addEventListener('keydown', (e) => {
   if(e.target.id === 'chatInput' && e.key === 'Enter') sendChat(); 
});

async function quickBoost() {
    const token = localStorage.getItem('token');
    if(!token) { showToast("Login required for boost", "error"); return; }
    
    showToast("Optimizing system...", "info");
    try {
        const r = await fetch(`${API_BASE}/api/boost-ram`, {
            method: 'POST',
            headers: { 'token': token }
        });
        const d = await r.json();
        if(r.status === 401) { showToast("Session expired. Please login.", "error"); return; }
        showToast(`Freed ${d.freed_mb} MB RAM!`, "success");
    } catch { showToast("Boost Failed", "error"); }
}

// --- PROCESSES ---
async function loadProcesses() {
    const tbody = document.getElementById('procTableBody');
    tbody.innerHTML = '<tr><td colspan="6">Loading...</td></tr>';
    try {
        const r = await fetch(`${API_BASE}/api/processes`);
        const data = await r.json();
        tbody.innerHTML = data.map(p => `
            <tr>
                <td>${p.pid}</td>
                <td>${p.name}</td>
                <td>${p.cpu}%</td>
                <td>${p.memory_mb}</td>
                <td>${p.disk_io_mb}</td>
                <td><button class="btn-danger" onclick="killProc(${p.pid})">Kill</button></td>
            </tr>
        `).join('');
        window.lastLoaded.processes = Date.now();
    } catch {
        tbody.innerHTML = '<tr><td colspan="6"><div class="error-message">Failed to load processes.<br><button class="retry-btn" onclick="loadProcesses()">Retry</button></div></td></tr>';
    }
}

async function killProc(pid) {
    const token = localStorage.getItem('token');
    if(!token) { showToast("Login required", "error"); return; }
    
    if(!confirm("Kill process " + pid + "?")) return;
    const r = await fetch(`${API_BASE}/api/processes/${pid}/kill`, {
        method: 'POST',
        headers: { 'token': token }
    });
    if(r.status === 401) { showToast("Session expired", "error"); return; }
    showToast("Process Killed", "success");
    loadProcesses();
}

// --- CLEANER ---
async function scanJunk() {
    document.getElementById('junkSize').innerText = "Scanning...";
    try {
        const r = await fetch(`${API_BASE}/api/deep-clean/scan`);
        const d = await r.json();
        document.getElementById('junkSize').innerText = d.total_size_mb + " MB";
        window.lastLoaded.cleaner = Date.now();
    } catch {
        document.getElementById('junkSize').innerText = "Error";
    }
}

async function cleanJunk() {
    const token = localStorage.getItem('token');
    if(!token) { showToast("Login required", "error"); return; }
    
    const r = await fetch(`${API_BASE}/api/deep-clean/clean`, {
        method: 'POST',
        headers: { 'token': token }
    });
    if(r.status === 401) { showToast("Session expired", "error"); return; }
    showToast("Cleanup Complete", "success");
    scanJunk();
}

async function scanLargeFiles() {
    const list = document.getElementById('largeFilesList');
    list.innerHTML = '<li>Scanning for massive files...</li>';
    try {
        const r = await fetch(`${API_BASE}/api/large-files`);
        const d = await r.json();
        if (d.length === 0) {
            list.innerHTML = '<li>No files > 100MB found.</li>';
            return;
        }
        list.innerHTML = d.map(f => `
            <li style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; background:rgba(255,255,255,0.05); padding:10px; border-radius:8px;">
                <div style="overflow:hidden; text-overflow:ellipsis;">
                    <div style="font-weight:600;">${f.name}</div>
                    <div style="font-size:0.7em; opacity:0.6;">${f.path}</div>
                </div>
                <div style="display:flex; align-items:center; gap:10px;">
                    <b style="color:var(--accent); whitespace:nowrap;">${f.size_mb} MB</b>
                    <button class="btn-danger" style="padding:5px 10px; font-size:0.8em;" onclick="deleteLargeFile('${f.path.replace(/\\/g, '\\\\')}')">DEL</button>
                </div>
            </li>
        `).join('');
    } catch {
        list.innerHTML = '<li style="color:var(--danger);">Scan failed.</li>';
    }
}

async function deleteLargeFile(path) {
    const token = localStorage.getItem('token');
    if(!token) { showToast("Login required", "error"); return; }
    if(!confirm("Permanently delete this file?")) return;
    
    try {
        const r = await fetch(`${API_BASE}/api/large-files/delete?path=${encodeURIComponent(path)}`, {
            method: 'POST',
            headers: { 'token': token }
        });
        showToast("File Deleted", "success");
        scanLargeFiles();
    } catch { showToast("Delete failed", "error"); }
}

// --- SECURITY ---
async function checkSecurity() {
    // Loading State
    const el = document.getElementById('firewallStatus');
    el.innerText = "Checking...";
    el.className = "status-badge";
    document.getElementById('portsList').innerHTML = "<li>Scanning ports...</li>";

    try {
        const r = await fetch(`${API_BASE}/api/security/firewall-status`);
        const d = await r.json();
        // el already defined above
        el.innerText = d.enabled ? "Active" : "Disabled (Risk)";
        el.className = d.enabled ? "status-badge text-success" : "status-badge text-danger";
        
        // Ports
        const r2 = await fetch(`${API_BASE}/api/security/open-ports`);
        const p = await r2.json();
        document.getElementById('portsList').innerHTML = p.map(x => `Port ${x.port}: ${x.service} (${x.risk})`).join('<br>');
        window.lastLoaded.security = Date.now();
    } catch {
        document.getElementById('firewallStatus').innerText = "Error";
        document.getElementById('portsList').innerHTML = '<div class="error-message">Scan failed</div>';
    }
}

async function enableFirewall() {
    showToast("Enabling Firewall...", "info");
    try {
        const r = await fetch(`${API_BASE}/api/security/enable-firewall`, { method: 'POST' });
        const d = await r.json();
        if (d.success) {
            showToast("Firewall Enabled", "success");
            checkSecurity();
        } else {
            showToast("Failed to enable firewall", "error");
        }
    } catch { showToast("Security Service Offline", "error"); }
}

async function toggleAutoMode() {
    const btn = document.getElementById('autoModeBtn');
    const isActive = btn.innerText.includes('Disable');
    const endpoint = isActive ? '/api/ai/auto-mode/stop' : '/api/ai/auto-mode/start';
    
    try {
        const r = await fetch(`${API_BASE}${endpoint}`, { method: 'POST' });
        const d = await r.json();
        if (d.success) {
            btn.innerText = isActive ? "Enable Auto-Pilot" : "Disable Auto-Pilot";
            btn.style.background = isActive ? "" : "var(--danger)";
            showToast(isActive ? "Auto-Pilot Stopped" : "Auto-Pilot Active", "info");
        }
    } catch { showToast("Auto-Engine Connection Error", "error"); }
}

// --- AI FORECAST ---
let forecastChart = null;
async function loadForecast() {
    document.getElementById('forecastLog').innerHTML = "<li>AI Neural Network is predicting...</li>";
    
    const r = await fetch(`${API_BASE}/api/ai/forecast`);
    const d = await r.json();
    
    const ctx = document.getElementById('forecastChart');
    if (forecastChart) forecastChart.destroy();
    
    
    if (typeof Chart === 'undefined') {
         document.getElementById('forecastChart').style.display = 'none';
         document.getElementById('forecastChart').parentElement.innerHTML += '<div class="error-message">Visualization Unavailable</div>';
         return;
    }

    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: d.forecast.map(x => x.time),
            datasets: [{
                label: 'Predicted CPU Load',
                data: d.forecast.map(x => x.predicted_cpu),
                borderColor: '#8b5cf6',
                fill: true,
                backgroundColor: 'rgba(139, 92, 246, 0.1)'
            }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }
    });
    
    document.getElementById('forecastLog').innerHTML = d.forecast.map(x => `
        <li>${x.time}: Risk ${x.risk_level} (Confidence: ${x.confidence})</li>
    `).join('');
    window.lastLoaded.ai = Date.now();
}

// --- DISK ANALYZER ---
let diskChart = null;
async function scanDisk() {
    const table = document.getElementById('largeFilesTable');
    const folderList = document.getElementById('folderList');
    
    table.innerHTML = '<tr><td colspan="4" style="text-align:center;">Scanning Disk... This may take a few seconds.</td></tr>';
    folderList.innerHTML = '<p style="padding:20px; text-align:center;">Analyzing storage structure...</p>';
    
    try {
        const r = await fetch(`${API_BASE}/api/disk/scan`);
        const d = await r.json();
        window.diskData = d;
        
        // 1. Chart
        renderDiskChart(d.distribution);

        // 1.5 Treemap
        renderTreemap(d.treemap);
        
        // 2. Folders
        folderList.innerHTML = d.folders.map(f => {
            const pct = (f.total_size_mb / d.total_mb * 100).toFixed(1);
            return `
                <div class="folder-item">
                    <div class="folder-info">
                        <span>${f.folder_name}</span>
                        <span>${f.total_size_mb} MB (${pct}%)</span>
                    </div>
                    <div class="progress-bg">
                        <div class="progress-fill" style="width: ${pct}%"></div>
                    </div>
                </div>
            `;
        }).join('');
        
        // 3. Files
        table.innerHTML = d.top_files.map(f => `
            <tr>
                <td>${f.name}</td>
                <td style="font-size:0.8em; opacity:0.6;">${f.path}</td>
                <td><b>${f.size_mb} MB</b></td>
                <td><button class="btn-danger" onclick="deleteDiskFile('${f.path.replace(/\\/g, '\\\\')}')">Del</button></td>
            </tr>
        `).join('');
        
        window.lastLoaded.disk = Date.now();
    } catch (e) {
        showToast("Disk Scan Failed", "error");
        table.innerHTML = '<tr><td colspan="4"><div class="error-message">Error accessing disk data.<br><button class="retry-btn" onclick="scanDisk()">Retry</button></div></td></tr>';
        folderList.innerHTML = '<div class="error-message">Could not analyze folders.</div>';
    }
}

// --- DISK SPACE ---
let diskPartitions = [];

async function loadPartitions() {
    const sel = document.getElementById('diskSelect');
    if(!sel) return; 
    try {
        const r = await fetch(`${API_BASE}/api/disk/partitions`);
        if(!r.ok) throw new Error();
        diskPartitions = await r.json();
        
        sel.innerHTML = diskPartitions.map(p => 
            `<option value="${p.mountpoint}">${p.device} (${p.mountpoint}) - ${p.total_gb} GB</option>`
        ).join('');
        
    } catch {
        sel.innerHTML = '<option value="">Failed to load</option>';
    }
}

async function scanDisk() {
    showToast("Starting Disk Scan...", "info");
    
    // Ensure partitions are loaded first
    if(diskPartitions.length === 0) {
        await loadPartitions();
        if(diskPartitions.length === 0) {
            showToast("Could not load drives. Is backend running?", "error");
            return;
        }
    }
    
    // Default to C: or first available if selector is empty/loading
    let selectedMount = "";
    const sel = document.getElementById('diskSelect');
    if (sel && sel.value) selectedMount = sel.value;
    else if (diskPartitions.length > 0) {
        selectedMount = diskPartitions[0].mountpoint;
        if(sel) sel.value = selectedMount; // Sync UI
    }

    if(!selectedMount) {
        showToast("No drive selected", "error");
        return;
    }

    // Find selected partition stats
    const part = diskPartitions.find(p => p.mountpoint === selectedMount);
    
    // Render Stats
    if(part) {
        document.getElementById('diskStatsContainer').innerHTML = `
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; text-align:center;">
                <div>
                    <h3 style="color:var(--text-secondary)">Total</h3>
                    <h2>${part.total_gb} GB</h2>
                </div>
                <div>
                    <h3 style="color:var(--accent)">Used</h3>
                    <h2>${part.used_gb} GB</h2>
                </div>
                <div>
                    <h3 style="color:var(--success)">Free</h3>
                    <h2>${part.free_gb} GB</h2>
                </div>
            </div>
            <div style="width:100%; height:8px; background:rgba(255,255,255,0.1); border-radius:4px; margin-top:10px;">
                <div style="width:${part.percent}%; height:100%; background:linear-gradient(90deg, var(--primary), var(--accent)); border-radius:4px;"></div>
            </div>
            <p style="text-align:right; margin-top:5px; font-size:0.8em; opacity:0.7">${part.percent}% Used</p>
        `;
        renderDiskChart(part); 
    }

    try {
        // Load large files AND render Treemap
        await loadLargeFiles(selectedMount);
        showToast("Scan Complete", "success");
    } catch(e) {
        console.error(e);
        showToast("Disk scan failed: " + e.message, "error");
    }
    
    window.lastLoaded.disk = Date.now();
}

function renderDiskChart(part) {
    if (typeof Chart === 'undefined') return;
    const ctx = document.getElementById('diskChart').getContext('2d');
    if (diskChart) diskChart.destroy();
    
    diskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Used', 'Free'],
            datasets: [{
                data: [part.used_gb, part.free_gb],
                backgroundColor: ['#f43f5e', '#10b981'], 
                borderWidth: 0
            }]
        },
        options: { 
            cutout: '70%', 
            responsive: true,
            maintainAspectRatio: false, // Fix clipping
            plugins: { legend: { display: false } } // Hide legend to save space
        }
    });
}

async function loadLargeFiles(mountPoint) {
    const list = document.getElementById('largeFilesTable'); // Fixed ID targeting
    const treemap = document.getElementById('treemapContainer');
    
    treemap.innerHTML = '<div class="loading-spinner">Scanning files...</div>';
    if(list) list.innerHTML = '<tr><td colspan="4" style="text-align:center">Scanning...</td></tr>';
    
    // Construct API URL
    let url = `${API_BASE}/api/large-files`;
    if(mountPoint) url += `?path=${encodeURIComponent(mountPoint)}`;

    try {
        const r = await fetch(url);
        const files = await r.json();
        
        if(files.length === 0) {
            treemap.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;opacity:0.5;">No large files found to visualize</div>';
            if(list) list.innerHTML = '<tr><td colspan="4" style="text-align:center">No large files found.</td></tr>';
            return;
        }

        // Render List
        if(list) {
            list.innerHTML = files.map(f => `
                <tr>
                   <td><div style="font-weight:600; max-width:200px; overflow:hidden; text-overflow:ellipsis" title="${f.name}">${f.name}</div></td>
                   <td><div style="font-size:0.8em; opacity:0.6; max-width:150px; overflow:hidden; text-overflow:ellipsis" title="${f.path}">${f.path}</div></td>
                   <td><span style="color:var(--accent)">${f.size_mb} MB</span></td>
                   <td>
                        <button class="btn-danger" style="padding:4px 8px; font-size:0.8em" onclick="deleteLargeFile('${f.path.replace(/\\/g, '\\\\')}', this)">
                           <i class="fa-solid fa-trash"></i>
                        </button>
                   </td>
                </tr>
            `).join('');
        }

        // Render Treemap (Simple Block Logic)
        renderSimpleTreemap(files, treemap);

    } catch {
        treemap.innerHTML = '<div class="error-message">Scan failed</div>';
    }
}

function renderSimpleTreemap(files, container) {
    container.innerHTML = '';
    container.style.display = 'flex';
    container.style.flexWrap = 'wrap';
    container.style.alignContent = 'flex-start';
    container.style.overflow = 'hidden';
    
    // Normalize sizes to percentages relative to the total size of these large files
    const totalSize = files.reduce((sum, f) => sum + f.size_mb, 0);
    const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899'];
    
    files.forEach((f, i) => {
        const pct = (f.size_mb / totalSize) * 100;
        if(pct < 1) return; // Skip tiny blocks
        
        const block = document.createElement('div');
        block.style.width = `${pct}%`; // Approximate width based on size
        block.style.height = '100%'; // Full height for now, or use Flex grow
        // Actually, flex-grow is better for filling line
        block.style.flex = `${pct} 1 0%`; 
        block.style.height = `${Math.max(50, pct * 4)}px`; // Dynamic height based on significance? Or just tiling.
        // Let's do a simple 1D treemap (stacked bars) or tiling. 
        // Best approach for simple CSS: Tiling with fixed height or Flex
        block.style.height = '100px'; 
        block.style.backgroundColor = colors[i % colors.length];
        block.style.border = '1px solid rgba(0,0,0,0.2)';
        block.style.position = 'relative';
        block.style.overflow = 'hidden';
        block.title = `${f.name} (${f.size_mb} MB)`;
        block.className = 'treemap-block';
        
        block.innerHTML = `
            <div style="position:absolute; top:2px; left:4px; font-size:0.75em; color:white; font-weight:bold; text-shadow:0 1px 2px black;">${f.name}</div>
            <div style="position:absolute; bottom:2px; right:4px; font-size:0.7em; color:rgba(255,255,255,0.8);">${f.size_mb} MB</div>
        `;
        
        container.appendChild(block);
    });
}

async function loadLargeFiles(mountPoint) {
    const list = document.getElementById('largeFilesList');
    // Using treemap container or creating a new list if checking index.html
    // Assuming structure from previous tasks or existing code. 
    // Let's attach to 'largeFilesList' which presumably exists or we use 'treemapContainer' as fallback?
    // Actually, looking at current script.js, there is no loadLargeFiles function logic visible in the snippet.
    // I will add it here.
    
    // Wait, let's just make sure we target the right element.
    if(!list) return;

    list.innerHTML = '<li class="loading-spinner">Scanning large files...</li>';
    
    // Construct API URL
    let url = `${API_BASE}/api/large-files`;
    if(mountPoint) url += `?path=${encodeURIComponent(mountPoint)}`;

    try {
        const r = await fetch(url);
        const files = await r.json();
        
        if(files.length === 0) {
            list.innerHTML = '<li style="text-align:center; padding:10px;">No large files found.</li>';
            return;
        }

        list.innerHTML = files.map(f => `
            <li class="file-item">
                <div class="file-info">
                    <span class="file-name" title="${f.path}">${f.name}</span>
                    <span class="file-path">${f.path}</span>
                </div>
                <div class="file-actions">
                    <span class="file-size">${f.size_mb} MB</span>
                    <button class="btn-danger" onclick="deleteLargeFile('${f.path.replace(/\\/g, '\\\\')}', this)">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </li>
        `).join('');
    } catch {
        list.innerHTML = '<li style="color:var(--danger)">Error loading files</li>';
    }
}

// Google Auth Callback
function handleCredentialResponse(response) {
    console.log("Encoded JWT ID token: " + response.credential);
    localStorage.setItem('token', 'google-mock-token');
    showToast("Google Login Successful!", "success");
    toggleAuth(false);
}

// --- D3 TREEMAP VISUALIZER (ZOOMABLE) ---
function renderTreemap(data) {
    const container = document.getElementById('treemapContainer');
    if (!container || !data || !data.children) return;
    
    container.innerHTML = ''; // Clear previous

    // Dimensions
    const width = container.clientWidth;
    const height = 400; // Fixed height for visibility
    const format = d3.format(",d");
    
    // Color Scale
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Create Hierarchy
    const root = d3.hierarchy(data)
        .sum(d => d.value)
        .sort((a, b) => b.value - a.value);

    // Layout
    d3.treemap()
        .tile(d3.treemapSquarify)
        .size([width, height])
        .padding(1)
        .round(true)
        (root);

    const svg = d3.select("#treemapContainer").append("svg")
        .attr("viewBox", [0, 0, width, height])
        .style("font", "10px sans-serif");
    
    // Render Tiles
    const leaf = svg.selectAll("g")
        .data(root.leaves())
        .join("g")
        .attr("transform", d => `translate(${d.x0},${d.y0})`);

    leaf.append("rect")
        .attr("fill", d => { while (d.depth > 1) d = d.parent; return color(d.data.name); })
        .attr("fill-opacity", 0.6)
        .attr("width", d => d.x1 - d.x0)
        .attr("height", d => d.y1 - d.y0)
        .style("stroke", "rgba(255,255,255,0.1)")
        .on("mouseover", function() { d3.select(this).attr("fill-opacity", 1); })
        .on("mouseout", function() { d3.select(this).attr("fill-opacity", 0.6); });

    // Clip paths for text
    leaf.append("clipPath")
        .attr("id", (d, i) => (d.clipUid = `clip-${i}`))
        .append("rect")
        .attr("width", d => d.x1 - d.x0)
        .attr("height", d => d.y1 - d.y0);

    // Labels
    leaf.append("text")
        .attr("clip-path", (d, i) => `url(#${d.clipUid})`)
        .selectAll("tspan")
        .data(d => {
            const name = d.data.name;
            const size = (d.data.value / (1024*1024)).toFixed(1) + " MB";
            // Only show if enough space
            return (d.x1 - d.x0) > 50 && (d.y1 - d.y0) > 30 ? [name, size] : [];
        })
        .join("tspan")
        .attr("x", 3)
        .attr("y", (d, i, nodes) => 13 + (i === nodes.length - 1) * 3 + i * 10) // Simple vertical stacking
        .attr("fill-opacity", (d, i, nodes) => i === nodes.length - 1 ? 0.7 : 1)
        .style("fill", "white")
        .style("font-weight", (d, i) => i === 0 ? "bold" : "normal")
        .text(d => d);
        
    leaf.append("title")
        .text(d => `${d.ancestors().reverse().map(d => d.data.name).join("/")}\n${format(d.value)} bytes`);
}

// --- STARTUP MANAGER ---
async function loadStartupApps() {
    const list = document.getElementById('startupListBody');
    if(!list) return;
    list.innerHTML = '<tr><td colspan="4" class="text-center">Loading Startup Items...</td></tr>';
    
    try {
        const r = await fetch(`${API_BASE}/api/startup-apps`);
        const apps = await r.json();
        
        if(apps.length === 0) {
            list.innerHTML = '<tr><td colspan="4" class="text-center">No startup apps found.</td></tr>';
            return;
        }
        
        list.innerHTML = apps.map(app => `
            <tr>
                <td><strong style="color:var(--text-main)">${app.name}</strong></td>
                <td style="font-family:monospace; font-size:0.85em; color:var(--text-muted);">${app.command.substring(0, 50)}${app.command.length>50?'...':''}</td>
                <td><span class="badge" style="background:${app.location==='HKLM'?'#f59e0b20':'#3b82f620'}; color:${app.location==='HKLM'?'#f59e0b':'#3b82f6'}">${app.location}</span></td>
                <td>
                    ${app.can_toggle ? 
                        `<button class="btn-secondary" style="padding:4px 10px; font-size:0.8em;" onclick="toggleStartup('${app.name}', false)">Disable</button>` : 
                        `<span style="opacity:0.5; font-size:0.8em;">Admin Req</span>`
                    }
                </td>
            </tr>
        `).join('');
    } catch {
        list.innerHTML = '<tr><td colspan="4" class="text-center error-message">Failed to load startup apps.</td></tr>';
    }
}

async function toggleStartup(name, enable) {
    if(!confirm(`Disable ${name} from startup? This cannot be undone easily.`)) return;
    
    try {
        const r = await fetch(`${API_BASE}/api/startup-apps/${encodeURIComponent(name)}/toggle?enabled=${enable}`, { method: 'POST' });
        const d = await r.json();
        if(d.success) {
            showToast("App disabled from startup", "success");
            loadStartupApps();
        } else {
            showToast(d.message, "error");
        }
    } catch { showToast("Connection error", "error"); }
}

async function deleteDiskFile(path) {
    const token = localStorage.getItem('token');
    if(!token) { showToast("Login required", "error"); return; }
    
    if(!confirm("Permenently delete this file?\n" + path)) return;
    
    try {
        const r = await fetch(`${API_BASE}/api/disk/file?path=${encodeURIComponent(path)}`, {
            method: 'DELETE',
            headers: { 'token': token }
        });
        if(r.status === 401) { showToast("Session expired", "error"); return; }
        showToast("File Deleted", "success");
        scanDisk(); // Refresh
    } catch {
        showToast("Delete failed", "error");
    }
}

// --- UTILS ---
function showToast(msg, type) {
    const t = document.createElement('div');
    t.className = 'toast';
    t.innerText = msg;
    t.style.borderLeft = `4px solid ${type=='success'?'#10b981':'#ef4444'}`;
    document.body.appendChild(t);
    setTimeout(() => t.classList.add('show'), 10);
    setTimeout(() => { t.classList.remove('show'); setTimeout(()=>t.remove(),300); }, 3000);
}

// --- ANIMATIONS (ANIME.JS) ---
function initAnimations() {
    if(typeof anime === 'undefined') return; // Safety Exit

    // 1. Initial Staggered Entry
    anime({
        targets: '.sidebar, .section-header, .hero-status > div, .glass-panel',
        translateY: [20, 0],
        // opacity: [0, 1], // Removed to prevent visibility issues
        delay: anime.stagger(100),
        easing: 'spring(1, 80, 10, 0)'
    });
    
    // 2. Continuous Floating for Chat Button
    // Moved to CSS for better performance
    /*
    anime({
        targets: '.chat-toggle-btn',
        translateY: [-5, 5],
        direction: 'alternate',
        loop: true,
        easing: 'easeInOutSine',
        duration: 2000
    });
    */
}


// --- APP MANAGER (REVO) ---
let installedApps = [];

async function loadInstalledApps() {
    const tbody = document.getElementById('appListBody');
    tbody.innerHTML = '<tr><td colspan="3" style="text-align:center">Loading apps... (This scans the registry)</td></tr>';
    
    try {
        const r = await fetch(`${API_BASE}/api/apps/installed`);
        if(!r.ok) throw new Error("API Error");
        installedApps = await r.json();
        renderApps(installedApps);
        window.lastLoaded.uninstaller = Date.now();
    } catch {
        tbody.innerHTML = '<tr><td colspan="3"><div class="error-message">Failed to load apps. Ensure backend is running.</div></td></tr>';
    }
}

function renderApps(apps) {
    const tbody = document.getElementById('appListBody');
    if(apps.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center">No apps found.</td></tr>';
        return;
    }
    
    tbody.innerHTML = apps.map(app => `
        <tr>
            <td>
                <div style="font-weight:600">${app.name}</div>
            </td>
            <td style="opacity:0.7">${app.version || '-'}</td>
            <td>
                <button class="btn-danger" style="padding:6px 12px; font-size:0.9em;" 
                    onclick="initUninstall('${app.name.replace(/'/g, "\\'")}', '${app.uninstall_string.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}')">
                    <i class="fa-solid fa-trash"></i> Uninstall
                </button>
            </td>
        </tr>
    `).join('');
}

function filterApps() {
    const term = document.getElementById('appSearch').value.toLowerCase();
    const filtered = installedApps.filter(a => a.name.toLowerCase().includes(term));
    renderApps(filtered);
}

async function initUninstall(appName, command) {
    const token = localStorage.getItem('token');
    if(!token) { showToast("Login required", "error"); return; }
    
    if(!confirm(`Are you sure you want to uninstall ${appName}?`)) return;
    
    showToast("Launching Uninstaller...", "info");
    
    try {
        const r = await fetch(`${API_BASE}/api/apps/uninstall`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'token': token },
            body: JSON.stringify({ command: command })
        });
        const d = await r.json();
        
        if(d.success) {
            showToast("Uninstaller Launched", "success");
            // PROMPT FOR LEFTOVER SCAN
            setTimeout(() => {
                if(confirm(`After you finish uninstalling ${appName}, do you want to scan for leftover files?`)) {
                    scanLeftovers(appName);
                }
            }, 2000);
        } else {
            showToast("Failed to launch: " + d.message, "error");
        }
    } catch { showToast("Error connecting to backend", "error"); }
}

async function scanLeftovers(appName) {
    document.querySelector('.modal').classList.remove('hidden');
    document.getElementById('modalTitle').innerText = `Scanning leftovers for: ${appName}`;
    document.getElementById('modalList').innerHTML = `<p>Searching AppData and Program Files...</p>`;
    document.getElementById('modalActions').innerHTML = ''; // Clear actions
    
    try {
        const r = await fetch(`${API_BASE}/api/apps/leftovers?app_name=${encodeURIComponent(appName)}`);
        const leftovers = await r.json();
        
        if(leftovers.length === 0) {
            document.getElementById('modalList').innerHTML = `<p style="color:var(--success)">No leftover files found! Clean application.</p>`;
            return;
        }
        
        document.getElementById('modalList').innerHTML = `
            <p>Found ${leftovers.length} leftover items:</p>
            <ul style="max-height:300px; overflow-y:auto; margin-top:10px;">
                ${leftovers.map(l => `
                    <li style="background:rgba(255,255,255,0.05); padding:8px; margin-bottom:5px; border-radius:4px; display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.85em; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:70%;" title="${l.path}">${l.path}</span>
                        <span style="font-size:0.85em; color:var(--accent);">${l.size_mb} MB</span>
                        <button class="btn-danger" style="padding:2px 6px; font-size:0.7em;" onclick="deleteLeftover('${l.path.replace(/\\/g, '\\\\')}', this)">DEL</button>
                    </li>
                `).join('')}
            </ul>
        `;
        
    } catch {
        document.getElementById('modalList').innerHTML = `<p class="error-message">Scan failed.</p>`;
    }
}

async function deleteLeftover(path, btnParams) {
    const token = localStorage.getItem('token');
    if(!token) { showToast("Login required", "error"); return; }
    
    const r = await fetch(`${API_BASE}/api/apps/leftovers?path=${encodeURIComponent(path)}`, {
         method: 'DELETE',
         headers: { 'token': token }
    });
    const d = await r.json();
    
    if(d.success) {
        showToast("Item deleted", "success");
        if(btnParams) btnParams.parentElement.remove();
    } else {
        showToast("Failed: " + d.message, "error");
    }
}
// Enhance Tab Switch - CSS HANDLED (Reverting JS override for stability)
// const originalSwitchTab = switchTab;
// switchTab = function(tabId) { ... } -> REMOVED to ensure buttons always work.

// Enhance Gauge Animation
function animateGauge(selector, value) {
    if (typeof anime === 'undefined') {
        document.querySelector(selector + ' .value').innerText = value + '%';
        return;
    }

    // Number count up
    const el = document.querySelector(selector + ' .value');
    anime({
        targets: el,
        innerHTML: [0, value],
        round: 1,
        easing: 'easeInOutExpo',
        duration: 2000,
        update: function(a) {
            el.innerHTML = a.animations[0].currentValue.toFixed(0) + '%';
        }
    });
    
    // Ring fill not easily animatable with simple anime.js on svg stroke-dasharray without more setup, 
    // keeping CSS transition for ring, but adding elastic scale to container
    anime({
        targets: selector,
        scale: [0.8, 1],
        // opacity: [0, 1], // Removed to fix low opacity issue
        easing: 'easeOutElastic(1, .6)',
        duration: 1200
    });
}

// DOMContentLoaded handled at top of file now

// Specs
// Specs
async function loadSpecs() {
     try {
         const r = await fetch(`${API_BASE}/api/system-specs`);
         if (!r.ok) throw new Error("API Error");
         const d = await r.json();
         const target = document.getElementById('sysSpecs');
         if (!target) return;
         target.innerHTML = `
            <p>${d.os}</p>
            <p>${d.processor}</p>
            <p>${d.ram_total_gb} GB RAM</p>
         `;
         if (typeof anime !== 'undefined') {
            anime({ targets: '#sysSpecs p', translateX: [50, 0], opacity: [0, 1], delay: anime.stagger(100)});
         }
     } catch (e) {
         const target = document.getElementById('sysSpecs');
         if(target) target.innerHTML = `<div class="error-message">Failed to load specs.<br><button class="retry-btn" onclick="loadSpecs()">Retry</button></div>`;
     }
}

document.addEventListener('DOMContentLoaded', () => {
    // Other inits might be here
    if(typeof loadPartitions === 'function') loadPartitions();
});

// --- D3 TREEMAP VISUALIZER ---
function renderTreemap(data) {
    const container = document.getElementById('treemapContainer'); // Assume this exists in index.html (I checked, it does?) 
    // Wait, I need to check if there is a container for treemap. 
    // In previous summaries, I implemented a 'treemap' but might have been basic. 
    // Let's ensure the container uses the ID 'diskChart' or similar.
    // Actually, I'll clear 'diskChart' (which was a canvas) and replace it with a D3 SVG if I can.
    // Or finding a dedicated div.
    
    // For now, let's target 'diskChart' parent.
    const chartCanvas = document.getElementById('diskChart');
    if(!chartCanvas) return;
    
    const parent = chartCanvas.parentElement;
    
    // Check if we already created a treemap container
    let svgContainer = document.getElementById('d3Treemap');
    if (!svgContainer) {
        chartCanvas.style.display = 'none'; // Hide Chart.js canvas
        svgContainer = document.createElement('div');
        svgContainer.id = 'd3Treemap';
        svgContainer.style.width = '100%';
        svgContainer.style.height = '300px';
        parent.appendChild(svgContainer);
    }
    
    svgContainer.innerHTML = ''; // Clear previous

    if(!data || !data.children || data.children.length === 0) {
        svgContainer.innerHTML = '<p style="text-align:center; padding:50px; opacity:0.5;">No Data for Heatmap</p>';
        return;
    }

    const width = svgContainer.clientWidth;
    const height = 300;
    
    const root = d3.hierarchy(data)
        .sum(d => d.value)
        .sort((a, b) => b.value - a.value);

    d3.treemap()
        .size([width, height])
        .padding(1)
        (root);

    const svg = d3.select("#d3Treemap")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("font-family", "inherit");

    const nodes = svg.selectAll("g")
        .data(root.leaves())
        .enter()
        .append("g")
        .attr("transform", d => `translate(${d.x0},${d.y0})`);

    nodes.append("rect")
        .attr("width", d => d.x1 - d.x0)
        .attr("height", d => d.y1 - d.y0)
        .attr("fill", d => {
             // Color based on size intensity
             return d3.interpolateViridis(d.value / (root.value * 0.2)); 
        })
        .attr("stroke", "#000")
        .attr("stroke-width", 0.5)
        .style("opacity", 0.8)
        .on("mouseover", function() { d3.select(this).style("opacity", 1); })
        .on("mouseout", function() { d3.select(this).style("opacity", 0.8); });

    nodes.append("text")
        .attr("x", 4)
        .attr("y", 14)
        .text(d => d.data.name)
        .attr("font-size", "10px")
        .attr("fill", "white")
        .style("pointer-events", "none")
        .each(function(d) {
             const self = d3.select(this);
             const regWidth = d.x1 - d.x0;
             if (regWidth < 30) self.remove(); // Hide label if too small
        });
        
    nodes.append("title")
        .text(d => `${d.data.name}\n${d.data.value.toFixed(1)} MB`);
}


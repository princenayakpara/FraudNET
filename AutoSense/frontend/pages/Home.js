import { api } from '../services/api.js';

export class Home {
    constructor() {
        this.interval = null;
    }

    async render(container) {
        container.innerHTML = `
            <div class="header-section">
                <h1>Dashboard</h1>
                <p>System Overview</p>
            </div>
            
            <div class="grid-3">
                <div class="card stat-card">
                    <h3>CPU Usage</h3>
                    <div class="gauge" id="cpu-gauge">0%</div>
                </div>
                <div class="card stat-card">
                    <h3>RAM Usage</h3>
                    <div class="gauge" id="ram-gauge">0%</div>
                </div>
                <div class="card stat-card">
                    <h3>Disk Usage</h3>
                    <div class="gauge" id="disk-gauge">0%</div>
                </div>
            </div>

            <div class="hero-card">
                <div class="health-score-ring" id="health-ring">
                    <span id="health-score">--</span>
                    <small>Health Score</small>
                </div>
                <div class="hero-actions">
                    <button id="quick-boost-btn" class="btn-primary-lg">🚀 Quick Boost</button>
                    <p id="boost-status"></p>
                </div>
            </div>

            <div class="warning-section hidden" id="warning-box">
                <!-- AI Warnings go here -->
            </div>
        `;

        this.attachEvents(container);
        this.startMonitoring();
    }

    attachEvents(container) {
        const btn = container.querySelector('#quick-boost-btn');
        const status = container.querySelector('#boost-status');
        
        btn.addEventListener('click', async () => {
            btn.disabled = true;
            btn.textContent = "Boosting...";
            try {
                const res = await api.boostRam();
                status.textContent = `Freed ${res.freed_mb} MB!`;
                setTimeout(() => status.textContent = '', 3000);
            } catch (e) {
                status.textContent = "Failed";
            }
            btn.disabled = false;
            btn.textContent = "🚀 Quick Boost";
        });
    }

    startMonitoring() {
        const update = async () => {
             try {
                 const data = await api.getStatus();
                 document.getElementById('cpu-gauge').textContent = `${data.cpu}%`;
                 document.getElementById('ram-gauge').textContent = `${data.ram}%`;
                 document.getElementById('disk-gauge').textContent = `${data.disk}%`;
                 
                 const scoreEl = document.getElementById('health-score');
                 if(scoreEl) scoreEl.textContent = data.health_score;

                 // Simple warning logic
                 const warningBox = document.getElementById('warning-box');
                 if (data.health_score < 70) {
                     warningBox.classList.remove('hidden');
                     warningBox.innerHTML = `⚠️ System Health is Low! Check Optimizer tab.`;
                 } else {
                     warningBox.classList.add('hidden');
                 }
             } catch(e) {}
        };
        update();
        this.interval = setInterval(update, 2000);
    }

    destroy() {
        if (this.interval) clearInterval(this.interval);
    }
}

import { api } from '../services/api.js';

export class Optimizer {
    async render(container) {
        container.innerHTML = `
            <div class="header-section">
                <h1>AI Optimizer</h1>
                <p>Forecast health and automate performance</p>
            </div>
            
            <div class="grid-2">
                <div class="card">
                    <h3>⚡ Auto Performance Mode</h3>
                    <p>Automatically kill heavy apps every 5 mins.</p>
                    <div class="toggle-switch">
                        <label class="switch">
                            <input type="checkbox" id="auto-mode-toggle">
                            <span class="slider round"></span>
                        </label>
                        <span id="auto-mode-status">Disabled</span>
                    </div>
                </div>

                <div class="card">
                    <h3>🧠 AI Health Forecast</h3>
                    <div id="forecast-results">
                        <button id="predict-btn" class="btn-secondary">Run Prediction</button>
                    </div>
                </div>
            </div>

            <div class="card full-width">
                <h3>Smart Optimization</h3>
                <p>Instantly optimize RAM, Disk, and Processes.</p>
                <button id="optimize-now-btn" class="btn-primary-lg">✨ Optimize Now</button>
                <div id="opt-results" class="mt-2"></div>
            </div>
        `;

        this.attachEvents(container);
    }

    attachEvents(container) {
        // Auto Mode
        const toggle = container.querySelector('#auto-mode-toggle');
        const status = container.querySelector('#auto-mode-status');

        // Check initial status (Mocking state or we need an API to get status. 
        // Our backend API currently only has start/stop, but returns status. 
        // We might assume OFF initially or store in localStorage)
        if(localStorage.getItem('autoMode') === 'true') {
            toggle.checked = true;
            status.textContent = "Enabled";
            api.startAutoMode(); // Ensure it's running
        }

        toggle.addEventListener('change', async () => {
             if (toggle.checked) {
                 await api.startAutoMode();
                 status.textContent = "Enabled";
                 localStorage.setItem('autoMode', 'true');
             } else {
                 await api.stopAutoMode();
                 status.textContent = "Disabled";
                 localStorage.setItem('autoMode', 'false');
             }
        });

        // Forecast
        const predictBtn = container.querySelector('#predict-btn');
        const forecastRes = container.querySelector('#forecast-results');
        
        predictBtn.addEventListener('click', async () => {
            forecastRes.innerHTML = "Analyzing...";
            const data = await api.getForecast();
            forecastRes.innerHTML = `
                <ul class="forecast-list">
                    <li>CPU Risk: <span class="${data.cpu_overload_probability > 50 ? 'danger':'safe'}">${data.cpu_overload_probability}%</span></li>
                    <li>RAM Risk: <span class="${data.ram_exhaustion_probability > 50 ? 'danger':'safe'}">${data.ram_exhaustion_probability}%</span></li>
                    <li>Degradation: <strong>${data.estimated_degradation_time}</strong></li>
                </ul>
            `;
        });

        // Optimize Now
        const optBtn = container.querySelector('#optimize-now-btn');
        const optRes = container.querySelector('#opt-results');
        
        optBtn.addEventListener('click', async () => {
            optBtn.disabled = true;
            optBtn.textContent = "Optimizing...";
            try {
                const res = await api.optimizeNow();
                optRes.innerHTML = `
                    <div class="success-box">
                        <p>✅ Killed ${res.killed_apps} apps</p>
                        <p>✅ Freed ${res.freed_ram_mb.toFixed(1)} MB RAM</p>
                        <p>✅ Cleaned ${res.junk_cleaned_mb} MB Junk</p>
                    </div>
                `;
            } catch(e) {
                optRes.textContent = "Failed.";
            }
            optBtn.disabled = false;
            optBtn.textContent = "✨ Optimize Now";
        });
    }

    destroy() {}
}

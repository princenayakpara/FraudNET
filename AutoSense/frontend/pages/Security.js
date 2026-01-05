import { api } from '../services/api.js';

export class Security {
    async render(container) {
        container.innerHTML = `
            <div class="header-section">
                <h1>Security Monitor</h1>
                <p>Protect your PC from threats</p>
            </div>
            
            <div class="grid-2">
                <div class="card">
                    <h3>🔥 Windows Firewall</h3>
                    <div id="firewall-status" class="status-indicator">Checking...</div>
                    <button id="enable-fw-btn" class="btn-primary hidden">Enable Firewall</button>
                </div>
                
                <div class="card">
                    <h3>🔓 Open Ports</h3>
                    <ul id="ports-list" class="list-group">
                        <li>Scanning...</li>
                    </ul>
                </div>
            </div>
        `;

        this.checkSecurity(container);
    }

    async checkSecurity(container) {
        // Firewall
        const fwStatusEl = container.querySelector('#firewall-status');
        const fwBtn = container.querySelector('#enable-fw-btn');
        
        try {
            const fw = await api.getFirewallStatus();
            if (fw.enabled) {
                fwStatusEl.innerHTML = `<span class="badge success">Active</span>`;
                fwBtn.classList.add('hidden');
            } else {
                fwStatusEl.innerHTML = `<span class="badge danger">Disabled</span>`;
                fwBtn.classList.remove('hidden');
                
                fwBtn.onclick = async () => {
                    await api.enableFirewall();
                    this.checkSecurity(container); // Reload
                };
            }
        } catch(e) {
            fwStatusEl.textContent = "Error";
        }

        // Ports
        const portsList = container.querySelector('#ports-list');
        try {
            const ports = await api.getOpenPorts();
            if (ports.length === 0) {
                portsList.innerHTML = `<li class="safe">No dangerous ports found.</li>`;
            } else {
                portsList.innerHTML = ports.map(p => `
                    <li class="danger-item">
                        <strong>${p.service}</strong> (Port ${p.port}) - PID: ${p.pid}
                    </li>
                `).join('');
            }
        } catch(e) {
            portsList.innerHTML = "<li>Failed to scan ports</li>";
        }
    }

    destroy() {}
}

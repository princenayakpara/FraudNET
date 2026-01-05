import { api } from '../services/api.js';

export class Apps {
    async render(container) {
        container.innerHTML = `
            <div class="header-section">
                <h1>Apps Management</h1>
                <p>Manage running processes and startup applications</p>
            </div>

            <div class="tabs">
                <button class="tab active" data-target="processes">Running Processes</button>
                <button class="tab" data-target="startup">Startup Apps</button>
            </div>

            <div id="processes-view">
                <div class="card full-width">
                     <div class="flex-row">
                        <h3>Running Processes</h3>
                        <button id="refresh-proc" class="btn-secondary-sm">🔄 Refresh</button>
                     </div>
                     <div class="table-container">
                        <table id="proc-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Memory</th>
                                    <th>CPU</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="4" class="loading">Loading...</td></tr>
                            </tbody>
                        </table>
                     </div>
                </div>
            </div>

            <div id="startup-view" class="hidden">
                <div class="card full-width">
                     <h3>Startup Apps</h3>
                     <div class="table-container">
                        <table id="startup-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Command</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td colspan="3" class="loading">Loading...</td></tr>
                            </tbody>
                        </table>
                     </div>
                </div>
            </div>
        `;
        
        // Add specific Table CSS
        const style = document.createElement('style');
        style.innerText = `
            .flex-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
            .table-container { max-height: 400px; overflow-y: auto; }
            table { width: 100%; border-collapse: collapse; text-align: left; }
            th { border-bottom: 1px solid #334155; padding: 10px; color: #94a3b8; }
            td { border-bottom: 1px solid rgba(255,255,255,0.05); padding: 10px; font-size: 0.9rem; }
            .btn-sm { padding: 4px 8px; font-size: 0.8rem; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; }
            .loading { text-align: center; color: #aaa; padding: 20px; }
        `;
        container.appendChild(style);

        this.attachEvents(container);
        this.loadProcesses(container);
    }

    attachEvents(container) {
        // Tabs
        const tabs = container.querySelectorAll('.tab');
        const views = {
            'processes': container.querySelector('#processes-view'),
            'startup': container.querySelector('#startup-view')
        };
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                Object.values(views).forEach(v => v.classList.add('hidden'));
                const target = views[tab.dataset.target];
                target.classList.remove('hidden');
                
                if (tab.dataset.target === 'processes') this.loadProcesses(container);
                else this.loadStartup(container);
            });
        });

        // Refresh
        container.querySelector('#refresh-proc').addEventListener('click', () => this.loadProcesses(container));
    }

    async loadProcesses(container) {
        const tbody = container.querySelector('#proc-table tbody');
        tbody.innerHTML = '<tr><td colspan="4" class="loading">Loading...</td></tr>';
        
        try {
            const procs = await api.getProcesses();
            tbody.innerHTML = procs.map(p => `
                <tr>
                    <td>${p.name} <small style="color:#666">(${p.pid})</small></td>
                    <td>${p.memory_mb.toFixed(1)} MB</td>
                    <td>${p.cpu}%</td>
                    <td><button class="btn-sm kill-btn" data-pid="${p.pid}">End Task</button></td>
                </tr>
            `).join('');

            // Bind Kill buttons
            tbody.querySelectorAll('.kill-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    if(!confirm("End this process?")) return;
                    btn.textContent = "...";
                    await api.killProcess(btn.dataset.pid);
                    this.loadProcesses(container);
                });
            });
        } catch(e) {
            tbody.innerHTML = '<tr><td colspan="4">Error loading processes</td></tr>';
        }
    }

    async loadStartup(container) {
        const tbody = container.querySelector('#startup-table tbody');
        tbody.innerHTML = '<tr><td colspan="3" class="loading">Loading...</td></tr>';

        try {
            const apps = await api.getStartup();
            if(apps.length === 0) {
                 tbody.innerHTML = '<tr><td colspan="3">No startup apps found (in HKCU)</td></tr>';
                 return;
            }
            tbody.innerHTML = apps.map(app => `
                <tr>
                    <td>${app.name}</td>
                    <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${app.command}">${app.command}</td>
                    <td><span style="color:#22c55e">Enabled</span></td>
                </tr>
            `).join('');
        } catch(e) {
             tbody.innerHTML = '<tr><td colspan="3">Error loading startup apps</td></tr>';
        }
    }

    destroy() {}
}

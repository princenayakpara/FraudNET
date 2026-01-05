import { api } from '../services/api.js';

export class Cleaner {
    async render(container) {
        container.innerHTML = `
            <div class="header-section">
                <h1>Deep Cleaner</h1>
                <p>Remove junk files to free up space</p>
            </div>
            
            <div class="tabs">
                <button class="tab active" data-target="junk">Junk Scan</button>
                <button class="tab" data-target="large">Large Files</button>
            </div>

            <div id="junk-view">
                <div class="card cleaner-card">
                    <div class="cleaner-actions">
                        <button id="scan-btn" class="btn-primary">🔍 Scan Now</button>
                        <button id="clean-btn" class="btn-danger" disabled>🗑️ Clean All</button>
                    </div>
                    <div id="cleaner-results" class="results-list">
                        <p class="placeholder-text">Click Scan to find junk files...</p>
                    </div>
                    <div class="summary hidden" id="cleaner-summary">
                        <h3>Found: <span id="total-files">0</span> files (<span id="total-size">0</span> MB)</h3>
                    </div>
                </div>
            </div>

            <div id="large-view" class="hidden">
                <div class="card">
                     <p>Find files larger than 100MB in your Documents/Downloads/Videos/Desktop.</p>
                     <button id="scan-large-btn" class="btn-primary full-width mb-2">🦕 Scan Large Files</button>
                     <div id="large-results" class="results-list"></div>
                </div>
            </div>
        `;
        
        // CSS for tabs already in global/login style but we ensure it works here
        const style = document.createElement('style');
        style.innerText = `
            .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
            .tab { background: none; border: none; color: #888; padding: 10px; cursor: pointer; font-size: 1rem; border-bottom: 2px solid transparent; }
            .tab.active { color: #fff; border-bottom-color: #3b82f6; }
            .full-width { width: 100%; }
            .mb-2 { margin-bottom: 1rem; }
            .file-item-lg { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); align-items: center; }
            .btn-sm { padding: 4px 8px; font-size: 0.8rem; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; }
        `;
        container.appendChild(style);

        this.attachEvents(container);
    }

    attachEvents(container) {
        // TABS
        const tabs = container.querySelectorAll('.tab');
        const views = {
            'junk': container.querySelector('#junk-view'),
            'large': container.querySelector('#large-view')
        };
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                Object.values(views).forEach(v => v.classList.add('hidden'));
                views[tab.dataset.target].classList.remove('hidden');
            });
        });

        // JUNK SCAN EVENTS
        const scanBtn = container.querySelector('#scan-btn');
        const cleanBtn = container.querySelector('#clean-btn');
        const results = container.querySelector('#cleaner-results');
        const summary = container.querySelector('#cleaner-summary');
        const totalFiles = container.querySelector('#total-files');
        const totalSize = container.querySelector('#total-size');

        scanBtn.addEventListener('click', async () => {
            scanBtn.disabled = true;
            results.innerHTML = `<div class="loader">Scanning...</div>`;
            try {
                const res = await api.scanDeepClean();
                if (res.details && res.details.length > 0) {
                    results.innerHTML = res.details.map(f => `
                        <div class="file-item">
                            <span>${f.category}</span>
                            <small>${f.path}</small>
                            <span>${(f.size_bytes / 1024).toFixed(1)} KB</span>
                        </div>
                    `).join('');
                    totalFiles.textContent = res.total_files;
                    totalSize.textContent = res.total_size_mb;
                    summary.classList.remove('hidden');
                    cleanBtn.disabled = false;
                } else {
                    results.innerHTML = "<p>No junk files found!</p>";
                    cleanBtn.disabled = true;
                }
            } catch(e) {
                results.innerHTML = `<p class="error">Scan failed: ${e.message}</p>`;
            }
            scanBtn.disabled = false;
        });

        cleanBtn.addEventListener('click', async () => {
            if(!confirm("Delete these files?")) return;
            cleanBtn.disabled = true;
            try {
                const res = await api.cleanDeepClean();
                results.innerHTML = `<div class="success-msg">✅ Cleaned ${res.total_files} files, freed ${res.freed_mb} MB!</div>`;
                summary.classList.add('hidden');
            } catch(e) {
                alert("Clean failed");
            }
        });

        // LARGE FILE EVENTS
        const scanLargeBtn = container.querySelector('#scan-large-btn');
        const largeResults = container.querySelector('#large-results');

        if(scanLargeBtn) {
            scanLargeBtn.addEventListener('click', async () => {
                scanLargeBtn.disabled = true;
                scanLargeBtn.textContent = "Scanning...";
                largeResults.innerHTML = '<div class="loader">Scanning specific folders...</div>';
                
                try {
                    const files = await api.getLargeFiles();
                    if(files.length === 0) {
                        largeResults.innerHTML = "<p>No large files found (>100MB).</p>";
                    } else {
                        largeResults.innerHTML = files.map(f => `
                            <div class="file-item-lg">
                                <div>
                                    <div style="font-weight:bold">${f.name}</div>
                                    <small>${f.path}</small>
                                </div>
                                <div style="text-align:right">
                                    <div style="color:#fbbf24">${f.size_mb} MB</div>
                                    <button class="btn-sm del-lg-btn" data-path="${f.path}">Delete</button>
                                </div>
                            </div>
                        `).join('');

                        // Bind Delete
                        largeResults.querySelectorAll('.del-lg-btn').forEach(btn => {
                            btn.addEventListener('click', async () => {
                                if(!confirm("Permanently delete this large file?")) return;
                                await api.deleteLargeFile(btn.dataset.path);
                                btn.closest('.file-item-lg').remove();
                            });
                        });
                    }
                } catch(e) {
                    largeResults.innerHTML = "<p>Error scanning.</p>";
                }
                scanLargeBtn.disabled = false;
                scanLargeBtn.textContent = "🦕 Scan Large Files";
            });
        }
    }

    destroy() {}
}

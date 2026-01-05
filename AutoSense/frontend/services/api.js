const API_BASE = "http://127.0.0.1:8000";

// Helper for Authenticated Requests
async function fetchAuth(url, method = 'GET', body = null) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json'
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
        method,
        headers
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const res = await fetch(url, options);
    if (res.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('token');
        window.location.reload();
        throw new Error("Unauthorized");
    }
    return res;
}

export const api = {
    // Health & Metrics
    getStatus: async () => (await fetch(`${API_BASE}/status`)).json(), // Public
    getLastRecords: async () => (await fetch(`${API_BASE}/api/last-records`)).json(), // Public
    
    // Apps (Auth Required)
    getProcesses: async () => (await fetchAuth(`${API_BASE}/api/apps/processes`)).json(),
    killProcess: async (pid) => (await fetchAuth(`${API_BASE}/api/apps/kill?pid=${pid}`, 'POST')).json(),
    getStartup: async () => (await fetchAuth(`${API_BASE}/api/apps/startup`)).json(),
    
    // Large Files (Auth Required)
    getLargeFiles: async () => (await fetchAuth(`${API_BASE}/api/large-files`)).json(),
    deleteLargeFile: async (path) => (await fetchAuth(`${API_BASE}/api/large-files/delete?path=${encodeURIComponent(path)}`, 'POST')).json(),
    
    // 1. Deep Cleaner
    scanDeepClean: async () => (await fetch(`${API_BASE}/api/deep-clean/scan`)).json(),
    cleanDeepClean: async () => (await fetch(`${API_BASE}/api/deep-clean/clean`, { method: "POST" })).json(),
    
    // 2. Auto Mode
    startAutoMode: async () => (await fetch(`${API_BASE}/api/ai/auto-mode/start`, { method: "POST" })).json(),
    stopAutoMode: async () => (await fetch(`${API_BASE}/api/ai/auto-mode/stop`, { method: "POST" })).json(),
    
    // 3. Security
    getFirewallStatus: async () => (await fetch(`${API_BASE}/api/security/firewall-status`)).json(),
    enableFirewall: async () => (await fetch(`${API_BASE}/api/security/enable-firewall`, { method: "POST" })).json(),
    getOpenPorts: async () => (await fetch(`${API_BASE}/api/security/open-ports`)).json(),
    
    // 4. Forecast
    getForecast: async () => (await fetch(`${API_BASE}/api/ai/forecast`)).json(),
    
    // 5. Optimizer
    optimizeNow: async () => (await fetch(`${API_BASE}/api/ai/optimize-now`, { method: "POST" })).json(),
    
    // Legacy / One-Click Boost
    boostRam: async () => (await fetch(`${API_BASE}/api/boost-ram`, { method: "POST" })).json()
};

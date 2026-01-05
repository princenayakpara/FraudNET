export class Sidebar {
    constructor(containerId, onNavigate) {
        this.container = document.getElementById(containerId);
        this.onNavigate = onNavigate;
        this.activeTab = 'home';
    }

    render() {
        this.container.innerHTML = `
            <div class="sidebar-header">
                <h2>🧠 AutoSense</h2>
            </div>
            <nav class="sidebar-nav">
                <button class="nav-item active" data-tab="home">🏠 Home</button>
                <button class="nav-item" data-tab="cleaner">🧹 Cleaner</button>
                <button class="nav-item" data-tab="apps">📦 Apps</button>
                <button class="nav-item" data-tab="security">🔐 Security</button>
                <button class="nav-item" data-tab="optimizer">⚡ Optimizer</button>
            </nav>
       <div class="sidebar-footer">
                <button id="logout-btn" style="background:none; border:none; color: #ef4444; cursor: pointer; font-weight: bold; margin-bottom: 10px;">
                    🚪 Logout
                </button>
                <p>v2.5 AI Evolved</p>
            </div>
        `;

        this.container.querySelectorAll('.nav-item').forEach(btn => {
            btn.addEventListener('click', () => {
                this.setActive(btn.dataset.tab);
                this.onNavigate(btn.dataset.tab);
            });
        });

        // Logout Event
        const logout = this.container.querySelector('#logout-btn');
        if(logout) {
            logout.addEventListener('click', () => {
                localStorage.removeItem('token');
                window.location.reload();
            });
        }
    }

    setActive(tabName) {
        this.container.querySelectorAll('.nav-item').forEach(btn => {
            if (btn.dataset.tab === tabName) btn.classList.add('active');
            else btn.classList.remove('active');
        });
        this.activeTab = tabName;
    }
}

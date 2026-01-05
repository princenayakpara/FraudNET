import { Sidebar } from './components/Sidebar.js';
import { Home } from './pages/Home.js';
import { Cleaner } from './pages/Cleaner.js';
import { Apps } from './pages/Apps.js';
import { Security } from './pages/Security.js';
import { Optimizer } from './pages/Optimizer.js';
import { Login } from './pages/Login.js';

class App {
    constructor() {
        this.appContainer = document.getElementById('app');
        this.mainContent = document.getElementById('main-content');
        this.sidebarEl = document.getElementById('sidebar');
        this.currentPage = null;

        // AUTH GUARD
        const token = localStorage.getItem('token');
        if (!token) {
            this.sidebarEl.classList.add('hidden'); // Hide sidebar for login
            this.renderLogin();
            return;
        }

        // Initialize Sidebar
        this.sidebar = new Sidebar('sidebar', (tab) => this.navigate(tab));
        this.sidebar.render();
        this.sidebarEl.classList.remove('hidden');

        // Default Route
        this.navigate('home');
    }

    async renderLogin() {
        if (this.currentPage && this.currentPage.destroy) this.currentPage.destroy();
        this.currentPage = new Login();
        this.mainContent.style.width = "100%"; // Full width for login
        this.mainContent.style.padding = "0";
        await this.currentPage.render(this.mainContent);
    }

    async navigate(tab) {
        // Cleanup old page
        if (this.currentPage && this.currentPage.destroy) {
            this.currentPage.destroy();
        }

        this.mainContent.innerHTML = '<div class="loader">Loading...</div>';

        switch(tab) {
            case 'home':
                this.currentPage = new Home();
                break;
            case 'cleaner':
                this.currentPage = new Cleaner();
                break;
            case 'apps':
                this.currentPage = new Apps();
                break;
            case 'security':
                this.currentPage = new Security();
                break;
            case 'optimizer':
                this.currentPage = new Optimizer();
                break;
            default:
                this.currentPage = new Home();
        }

        await this.currentPage.render(this.mainContent);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new App();
});

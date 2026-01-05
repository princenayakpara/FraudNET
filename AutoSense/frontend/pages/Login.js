import { api } from '../services/api.js';

export class Login {
    async render(container) {
        container.innerHTML = `
            <div class="login-container">
                <div class="card login-card">
                    <h2>👋 Welcome to AutoSense</h2>
                    <p class="mb-2">Please sign in to continue</p>
                    
                    <div class="tabs">
                        <button class="tab active" data-target="email">Email</button>
                        <button class="tab" data-target="otp">OTP Login</button>
                        <button class="tab" data-target="google">Google</button>
                    </div>

                    <!-- EMAIL LOGIN -->
                    <div id="email-form" class="auth-form">
                        <input type="email" id="email" placeholder="Email Address" class="input-field">
                        <input type="password" id="password" placeholder="Password" class="input-field">
                        <button id="email-login-btn" class="btn-primary-lg full-width">Sign In</button>
                        <p class="mt-2 text-center text-muted">Don't have an account? <a href="#" id="go-register">Register</a></p>
                    </div>

                    <!-- OTP LOGIN -->
                    <div id="otp-form" class="auth-form hidden">
                        <input type="text" id="otp-identifier" placeholder="Enter Email or Phone Number" class="input-field">
                        <div id="otp-input-group" class="hidden">
                            <input type="text" id="otp-code" placeholder="Enter 6-digit OTP" class="input-field">
                        </div>
                        <button id="get-otp-btn" class="btn-primary-lg full-width">Get OTP</button>
                        <button id="verify-otp-btn" class="btn-success-lg full-width hidden">Verify & Login</button>
                    </div>

                    <!-- GOOGLE LOGIN -->
                    <div id="google-form" class="auth-form hidden">
                         <div class="google-btn-container">
                            <button id="google-signin-btn" class="btn-google">
                                <span class="icon">G</span> Sign in with Google
                            </button>
                        </div>
                        <p class="mt-2 text-muted small">This is a simulated Google Login for demonstration.</p>
                    </div>

                    <!-- REGISTER FORM -->
                    <div id="register-form" class="auth-form hidden">
                        <input type="text" id="reg-name" placeholder="Full Name" class="input-field">
                        <input type="email" id="reg-email" placeholder="Email Address" class="input-field">
                        <input type="password" id="reg-password" placeholder="Password" class="input-field">
                        <button id="register-btn" class="btn-primary-lg full-width">Create Account</button>
                        <p class="mt-2 text-center text-muted">Already have an account? <a href="#" id="go-login">Login</a></p>
                    </div>

                    <div id="login-error" class="error-msg mt-2 hidden"></div>
                </div>
            </div>
        `;
        
        // Add specific Login CSS dynamically
        const style = document.createElement('style');
        style.textContent = `
            .login-container { display: flex; justify-content: center; align-items: center; height: 100%; }
            .login-card { width: 100%; max-width: 400px; text-align: center; }
            .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
            .tab { background: none; border: none; color: #94a3b8; cursor: pointer; padding: 5px 10px; font-weight: 600; }
            .tab.active { color: #3b82f6; border-bottom: 2px solid #3b82f6; }
            .input-field { width: 100%; padding: 12px; margin-bottom: 10px; background: rgba(0,0,0,0.2); border: 1px solid #334155; color: white; border-radius: 6px; }
            .full-width { width: 100%; }
            .text-center { text-align: center; }
            .btn-google { background: white; color: #333; width: 100%; padding: 12px; border: none; border-radius: 6px; font-weight: 600; display: flex; justify-content: center; align-items: center; gap: 10px; cursor: pointer; transition: transform 0.1s; }
            .btn-google:hover { background: #f1f5f9; transform: translateY(-1px); }
            .error-msg { color: #ef4444; font-size: 0.9rem; }
            .mb-2 { margin-bottom: 1rem; }
        `;
        container.appendChild(style);

        this.attachEvents(container);
    }

    attachEvents(container) {
        // Tab Switching
        const tabs = container.querySelectorAll('.tab');
        const forms = {
            'email': container.querySelector('#email-form'),
            'otp': container.querySelector('#otp-form'),
            'google': container.querySelector('#google-form')
        };
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                Object.values(forms).forEach(f => f.classList.add('hidden'));
                forms[tab.dataset.target].classList.remove('hidden');
                container.querySelector('#login-error').classList.add('hidden');
            });
        });

        // 1. Email Login (Existing/Mock)
        container.querySelector('#email-login-btn').addEventListener('click', async () => {
             const email = container.querySelector('#email').value;
             const password = container.querySelector('#password').value;
             this.handleLogin(async () => {
                 // For now, using direct fetch to auth endpoint usually required
                 // But since we are mocking/using the new auth.py:
                 const f = await fetch('/api/auth/login?email='+encodeURIComponent(email)+'&password='+encodeURIComponent(password), {method: 'POST'});
                 return await f.json();
             });
        });

        // 2. Unified OTP (Email/Phone)
        const getOtpBtn = container.querySelector('#get-otp-btn');
        const verifyOtpBtn = container.querySelector('#verify-otp-btn');
        const otpGroup = container.querySelector('#otp-input-group');
        const identifierInput = container.querySelector('#otp-identifier');

        getOtpBtn.addEventListener('click', async () => {
            const identifier = identifierInput.value;
            if(!identifier) return alert("Enter Email or Phone number");
            getOtpBtn.textContent = "Sending...";
            try {
                // We send 'identifier' parameter now
                const res = await (await fetch(`/api/auth/otp/send?identifier=${encodeURIComponent(identifier)}`, {method: 'POST'})).json();
                if(res.success) {
                    getOtpBtn.classList.add('hidden');
                    otpGroup.classList.remove('hidden');
                    verifyOtpBtn.classList.remove('hidden');
                    if(res.mock_otp) {
                         console.log("OTP:", res.mock_otp);
                         alert((identifier.includes('@') ? "📧 Email" : "🔥 SMS") + " OTP Sent! Check backend console: " + res.mock_otp);
                    }
                }
            } catch(e) {
                alert("Failed to send OTP");
                getOtpBtn.textContent = "Get OTP";
            }
        });

        verifyOtpBtn.addEventListener('click', () => {
            const identifier = identifierInput.value;
            const otp = container.querySelector('#otp-code').value;
             this.handleLogin(async () => {
                 const f = await fetch(`/api/auth/otp/verify?identifier=${encodeURIComponent(identifier)}&otp=${encodeURIComponent(otp)}`, {method: 'POST'});
                 return await f.json();
             });
        });
        
        // 3. Google Login
        container.querySelector('#google-signin-btn').addEventListener('click', () => {
            // Mock token
            const mockToken = "google_id_token_mock_12345";
            this.handleLogin(async () => {
                const f = await fetch(`/api/auth/google?token=${mockToken}`, {method: 'POST'});
                return await f.json();
            });
        });


        // 4. Switch to Register
        const regLink = container.querySelector('#go-register');
        const loginLink = container.querySelector('#go-login');
        const regForm = container.querySelector('#register-form');
        const emailForm = container.querySelector('#email-form');
        const tabsEl = container.querySelector('.tabs');
        const title = container.querySelector('h2');

        if(regLink) {
            regLink.addEventListener('click', (e) => {
                e.preventDefault();
                // Hide all Login related
                container.querySelectorAll('.auth-form').forEach(f => f.classList.add('hidden'));
                tabsEl.classList.add('hidden'); // Hide tabs for register
                regForm.classList.remove('hidden');
                title.textContent = "🚀 Create Account";
            });
        }

        if(loginLink) {
            loginLink.addEventListener('click', (e) => {
                e.preventDefault();
                // Show Email Login
                regForm.classList.add('hidden');
                tabsEl.classList.remove('hidden');
                emailForm.classList.remove('hidden');
                title.textContent = "👋 Welcome to AutoSense";
            });
        }

        // 5. Register Action
        const regBtn = container.querySelector('#register-btn');
        if(regBtn) {
            regBtn.addEventListener('click', async () => {
                const name = container.querySelector('#reg-name').value;
                const email = container.querySelector('#reg-email').value;
                const password = container.querySelector('#reg-password').value;

                if(!name || !email || !password) return alert("Please fill all fields");

                try {
                    const res = await (await fetch(`/api/auth/register?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`, {method: 'POST'})).json();
                    if(res.success) {
                        alert("Account created! Please login.");
                        // Switch to login
                        if(loginLink) loginLink.click();
                    } else {
                        alert(res.detail || "Registration failed");
                    }
                } catch(e) {
                    alert("Error: " + e.message);
                }
            });
        }
    }

    async handleLogin(apiCall) {
        const errEl = document.querySelector('#login-error');
        try {
            const res = await apiCall();
            if (res.access_token) {
                localStorage.setItem('token', res.access_token);
                // Reload to trigger Auth Guard in App.js to switch to Home
                window.location.reload(); 
            } else {
                errEl.textContent = res.detail || "Login failed";
                errEl.classList.remove('hidden');
            }
        } catch(e) {
            errEl.textContent = "Connection error";
            errEl.classList.remove('hidden');
        }
    }

    destroy() {}
}

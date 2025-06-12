/**
 * Convivial API Integration
 * Connects frontend with secure API endpoints
 */

class ConvivialAPI {
    constructor() {
        this.apiBase = window.location.origin.replace(':8890', ':5001');
        this.authBase = window.location.origin.replace(':8890', ':5000');
        this.wsBase = window.location.origin.replace(':8890', ':3000').replace('http', 'ws');
        this.token = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.ws = null;
    }

    // Authentication methods
    async login(username, password) {
        try {
            const response = await fetch(`${this.authBase}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access_token;
                this.refreshToken = data.refresh_token;
                localStorage.setItem('access_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);
                localStorage.setItem('user', JSON.stringify(data.user));
                return data;
            } else {
                throw new Error('Invalid credentials');
            }
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }

    async register(userData) {
        try {
            const response = await fetch(`${this.authBase}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();
            if (response.ok) {
                this.token = data.access_token;
                this.refreshToken = data.refresh_token;
                localStorage.setItem('access_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);
                localStorage.setItem('user', JSON.stringify(data.user));
                return data;
            } else {
                throw new Error(data.message || 'Registration failed');
            }
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }

    async logout() {
        try {
            await this.apiCall('/auth/logout', 'POST');
            this.token = null;
            this.refreshToken = null;
            localStorage.clear();
            if (this.ws) {
                this.ws.close();
            }
            window.location.href = '/login';
        } catch (error) {
            console.error('Logout failed:', error);
        }
    }

    // API call wrapper with auth
    async apiCall(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${this.apiBase}${endpoint}`, options);

        if (response.status === 401) {
            // Try to refresh token
            await this.refreshAccessToken();
            // Retry the request
            options.headers.Authorization = `Bearer ${this.token}`;
            return fetch(`${this.apiBase}${endpoint}`, options);
        }

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return response.json();
    }

    async refreshAccessToken() {
        try {
            const response = await fetch(`${this.authBase}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.refreshToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access_token;
                localStorage.setItem('access_token', this.token);
            } else {
                // Refresh failed, redirect to login
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
            window.location.href = '/login';
        }
    }

    // Discovery methods
    async getDiscoveries() {
        return this.apiCall('/discoveries/');
    }

    async shareDiscovery(discovery) {
        return this.apiCall('/discoveries/', 'POST', discovery);
    }

    // Collection methods
    async getCollections() {
        return this.apiCall('/collections/');
    }

    async createCollection(collection) {
        return this.apiCall('/collections/', 'POST', collection);
    }

    // Morning coffee
    async getMorningCoffee() {
        return this.apiCall('/social/morning-coffee');
    }

    // File upload
    async uploadFile(file, type = 'general') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);

        const response = await fetch(`${this.apiBase}/files/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        return response.json();
    }

    // WebSocket connection
    connectWebSocket() {
        if (!this.token) {
            console.error('No auth token for WebSocket');
            return;
        }

        this.ws = new WebSocket(this.wsBase);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            // Send auth token
            this.ws.send(JSON.stringify({
                type: 'auth',
                token: this.token
            }));
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            // Reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };
    }

    handleWebSocketMessage(data) {
        // Dispatch custom events for different message types
        const event = new CustomEvent(`convivial:${data.type}`, {
            detail: data
        });
        window.dispatchEvent(event);
    }

    // Search integration
    enhanceSearch() {
        const searchForm = document.getElementById('search');
        if (!searchForm) return;

        searchForm.addEventListener('submit', (e) => {
            const query = searchForm.querySelector('input[name="q"]').value;
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'search:start',
                    query: query,
                    mood: this.getCurrentMood()
                }));
            }
        });

        // Intercept result clicks
        document.addEventListener('click', async (e) => {
            const resultLink = e.target.closest('.result a');
            if (resultLink) {
                const result = resultLink.closest('.result');
                const discovery = {
                    url: resultLink.href,
                    title: result.querySelector('h3')?.textContent,
                    snippet: result.querySelector('.content')?.textContent,
                    engine: result.dataset.engine,
                    query: searchForm.querySelector('input[name="q"]').value
                };

                try {
                    await this.shareDiscovery(discovery);
                } catch (error) {
                    console.error('Failed to share discovery:', error);
                }
            }
        });
    }

    getCurrentMood() {
        // Get from UI or default
        return document.querySelector('.mood-selector')?.value || 'exploring';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.convivialAPI = new ConvivialAPI();
    
    // Check if user is authenticated
    if (window.convivialAPI.token) {
        window.convivialAPI.connectWebSocket();
        window.convivialAPI.enhanceSearch();
    } else if (!window.location.pathname.includes('login') && !window.location.pathname.includes('register')) {
        // Redirect to login if not authenticated
        window.location.href = '/login';
    }
});
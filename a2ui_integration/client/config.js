// Frontend configuration system
// Environment-driven configuration for security

class FrontendConfig {
    constructor() {
        // Get configuration from environment or secure storage
        this.config = this.loadConfig();
    }
    
    loadConfig() {
        // In production, this would come from:
        // 1. Environment variables (build time)
        // 2. Secure API endpoint (runtime)
        // 3. Secure storage (runtime)
        
        // For now, we'll use a secure pattern that doesn't hardcode secrets
        return {
            // A2A API Configuration
            a2a: {
                apiKey: this.getSecureValue('A2A_API_KEY'),
                model: 'gemini-2.0-flash-exp',
                endpoint: this.getSecureValue('A2A_ENDPOINT') || 'https://api.a2a.example.com'
            },
            
            // User Configuration
            user: {
                email: this.getSecureValue('USER_EMAIL') || 'user@example.com'
            },
            
            // WebSocket Configuration
            websocket: {
                endpoint: this.getSecureValue('WS_ENDPOINT') || 'ws://localhost:8005/ws'
            },
            
            // API Configuration
            api: {
                baseUrl: this.getSecureValue('API_BASE_URL') || 'http://localhost:8005'
            }
        };
    }
    
    getSecureValue(key) {
        // In production, this would:
        // 1. Check environment variables
        // 2. Check secure storage
        // 3. Make API call to get configuration
        // 4. Return null if not found
        
        // For development, check if we have a secure config endpoint
        if (typeof window !== 'undefined' && window.__SECURE_CONFIG__) {
            return window.__SECURE_CONFIG__[key];
        }
        
        // Check for environment variables (in build process)
        if (typeof process !== 'undefined' && process.env) {
            return process.env[key];
        }
        
        // Return null to force proper configuration
        return null;
    }
    
    getA2AConfig() {
        return this.config.a2a;
    }
    
    getUserConfig() {
        return this.config.user;
    }
    
    getWebSocketConfig() {
        return this.config.websocket;
    }
    
    getApiConfig() {
        return this.config.api;
    }
}

// Create singleton instance
const frontendConfig = new FrontendConfig();

// Export for use in other modules
export { frontendConfig, FrontendConfig };
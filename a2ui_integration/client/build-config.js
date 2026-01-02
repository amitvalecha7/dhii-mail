// Secure configuration loader for build process
// This file should be used during build to inject secure configuration

const fs = require('fs');
const path = require('path');

/**
 * Secure configuration loader
 * Injects environment variables into the frontend build
 */
class SecureConfigBuilder {
    constructor() {
        this.config = {
            // A2A API Configuration
            A2A_API_KEY: process.env.A2A_API_KEY || null,
            A2A_ENDPOINT: process.env.A2A_ENDPOINT || 'https://api.a2a.example.com',
            
            // User Configuration
            USER_EMAIL: process.env.USER_EMAIL || 'user@example.com',
            
            // WebSocket Configuration
            WS_ENDPOINT: process.env.WS_ENDPOINT || 'ws://localhost:8005/ws',
            
            // API Configuration
            API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8005'
        };
    }
    
    /**
     * Generate secure configuration script
     * Creates a script that injects configuration into the window object
     */
    generateConfigScript() {
        const configScript = `
// Secure configuration injected at build time
// This script should be included before main.js
(function() {
    window.__SECURE_CONFIG__ = ${JSON.stringify(this.config, null, 2)};
})();
`;
        return configScript;
    }
    
    /**
     * Write configuration script to file
     */
    writeConfigScript(outputPath = './secure-config.js') {
        const configScript = this.generateConfigScript();
        
        try {
            fs.writeFileSync(outputPath, configScript, 'utf8');
            console.log(`✅ Secure configuration written to ${outputPath}`);
            console.log('📋 Configuration summary:');
            
            Object.keys(this.config).forEach(key => {
                const value = this.config[key];
                const displayValue = value ? 
                    (key.includes('KEY') || key.includes('PASSWORD') ? 
                        `${value.substring(0, 4)}...${value.slice(-4)}` : value) : 
                    'NOT SET';
                console.log(`  ${key}: ${displayValue}`);
            });
            
            if (!this.config.A2A_API_KEY) {
                console.log('\n⚠️  WARNING: A2A_API_KEY not set. A2AClient will not function.');
                console.log('   Set A2A_API_KEY environment variable to enable voice features.');
            }
            
        } catch (error) {
            console.error(`❌ Error writing configuration: ${error.message}`);
            process.exit(1);
        }
    }
    
    /**
     * Validate configuration
     */
    validate() {
        const errors = [];
        
        if (!this.config.A2A_API_KEY) {
            errors.push('A2A_API_KEY is required for voice functionality');
        }
        
        if (!this.config.USER_EMAIL || !this.config.USER_EMAIL.includes('@')) {
            errors.push('USER_EMAIL must be a valid email address');
        }
        
        if (!this.config.API_BASE_URL || !this.config.API_BASE_URL.startsWith('http')) {
            errors.push('API_BASE_URL must be a valid URL');
        }
        
        return errors;
    }
}

// CLI usage
if (require.main === module) {
    const builder = new SecureConfigBuilder();
    
    // Validate configuration
    const errors = builder.validate();
    if (errors.length > 0) {
        console.log('⚠️  Configuration validation warnings:');
        errors.forEach(error => console.log(`  - ${error}`));
        console.log('\n💡 Set the required environment variables to fix these issues.');
    }
    
    // Write configuration
    builder.writeConfigScript();
}

module.exports = { SecureConfigBuilder };
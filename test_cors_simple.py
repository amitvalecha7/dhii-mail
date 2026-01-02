"""
Test CORS configuration for dhii-mail
"""

import os
import sys
sys.path.insert(0, '/root/dhii-mail')

def test_cors_configuration():
    """Test CORS configuration in different environments"""
    
    print("=== Testing CORS Configuration ===\n")
    
    # Test development configuration
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'development'
    
    from config import Settings
    dev_settings = Settings()
    
    print("1. Development Configuration:")
    print(f"   Environment: {dev_settings.environment}")
    print(f"   CORS Enabled: {dev_settings.enable_cors}")
    print(f"   CORS Origins: {dev_settings.cors_origins_list}")
    print(f"   Allow Credentials: {dev_settings.cors_allow_credentials}")
    print(f"   Allow Methods: {dev_settings.cors_methods_list}")
    print()
    
    # Test production configuration (default)
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'production'
    
    prod_settings = Settings()
    
    print("2. Production Configuration (default):")
    print(f"   Environment: {prod_settings.environment}")
    print(f"   CORS Enabled: {prod_settings.enable_cors}")
    print(f"   CORS Origins: {prod_settings.cors_origins_list}")
    print(f"   Allow Credentials: {prod_settings.cors_allow_credentials}")
    print(f"   Allow Methods: {prod_settings.cors_methods_list}")
    print(f"   Allow Headers: {prod_settings.get_cors_config()['allow_headers']}")
    print(f"   get_cors_config allow_credentials: {prod_settings.get_cors_config()['allow_credentials']}")
    print()
    
    # Test production with custom origins
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['CORS_ORIGINS'] = 'https://myapp.com,https://admin.myapp.com'
    os.environ['CORS_ALLOW_CREDENTIALS'] = 'true'
    
    prod_custom_settings = Settings()
    
    print("3. Production Configuration (custom origins):")
    print(f"   Environment: {prod_custom_settings.environment}")
    print(f"   CORS Origins: {prod_custom_settings.cors_origins_list}")
    print(f"   Allow Credentials: {prod_custom_settings.cors_allow_credentials}")
    print(f"   CORS Config: {prod_custom_settings.get_cors_config()}")
    print()
    
    # Security assertions
    print("4. Security Assertions:")
    
    # Development should be permissive
    assert dev_settings.is_development, "Should detect development environment"
    assert len(dev_settings.cors_origins_list) >= 4, "Development should have multiple localhost origins"
    assert dev_settings.cors_allow_credentials == True, "Development should allow credentials"
    print("   ✅ Development configuration is permissive")
    
    # Production should be restrictive by default
    assert prod_settings.is_production, "Should detect production environment"
    assert len(prod_settings.cors_origins_list) == 0, "Production should have no origins by default"
    assert prod_settings.get_cors_config()['allow_credentials'] == False, f"Production should not allow credentials by default, got {prod_settings.get_cors_config()['allow_credentials']}"
    print("   ✅ Production configuration is restrictive by default")
    
    # Production with explicit configuration should work
    assert len(prod_custom_settings.cors_origins_list) == 2, "Production should support custom origins"
    assert prod_custom_settings.cors_allow_credentials == True, "Production should support credentials when explicitly set"
    print("   ✅ Production configuration supports explicit settings")
    
    print("\n=== All CORS Tests Passed! ===")

if __name__ == "__main__":
    test_cors_configuration()
"""
Test CORS configuration for dhii-mail
"""

import os
import sys
sys.path.insert(0, '/root/dhii-mail')

from config import settings

def test_cors_configuration():
    """Test CORS configuration in different environments"""
    
    print("=== Testing CORS Configuration ===\n")
    
    # Test development configuration
    print("1. Development Configuration:")
    print(f"   Environment: {settings.environment}")
    print(f"   CORS Enabled: {settings.enable_cors}")
    print(f"   CORS Origins: {settings.cors_origins_list}")
    print(f"   Allow Credentials: {settings.cors_allow_credentials}")
    print(f"   Allow Methods: {settings.cors_methods_list}")
    print()
    
    # Test production configuration
    os.environ['ENVIRONMENT'] = 'production'
    # Clear other env vars to test defaults
    for key in ['CORS_ALLOW_CREDENTIALS', 'CORS_ALLOW_METHODS', 'CORS_ORIGINS']:
        if key in os.environ:
            del os.environ[key]
    # Import fresh to avoid cached settings
    import importlib
    import config
    importlib.reload(config)
    prod_settings = config.Settings()  # Create fresh instance
    
    print("2. Production Configuration (default):")
    print(f"   Environment: {prod_settings.environment}")
    print(f"   CORS Enabled: {prod_settings.enable_cors}")
    print(f"   CORS Origins: {prod_settings.cors_origins_list}")
    print(f"   Allow Credentials: {prod_settings.cors_allow_credentials}")
    print(f"   Allow Methods: {prod_settings.cors_methods_list}")
    print(f"   Allow Headers: {prod_settings.get_cors_config()['allow_headers']}")
    print()
    
    # Test production with custom origins
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['CORS_ORIGINS'] = 'https://myapp.com,https://admin.myapp.com'
    os.environ['CORS_ALLOW_CREDENTIALS'] = 'true'
    
    prod_custom_settings = settings.__class__()  # Create new instance
    
    print("3. Production Configuration (custom origins):")
    print(f"   Environment: {prod_custom_settings.environment}")
    print(f"   CORS Origins: {prod_custom_settings.cors_origins_list}")
    print(f"   Allow Credentials: {prod_custom_settings.cors_allow_credentials}")
    print(f"   CORS Config: {prod_custom_settings.get_cors_config()}")
    print()
    
    # Security assertions
    print("4. Security Assertions:")
    
    # Development should be permissive
    assert settings.is_development, "Should detect development environment"
    assert len(settings.cors_origins_list) >= 4, "Development should have multiple localhost origins"
    assert settings.cors_allow_credentials == True, "Development should allow credentials"
    print("   ✅ Development configuration is permissive")
    
    # Production should be restrictive by default
    assert prod_settings.is_production, "Should detect production environment"
    assert len(prod_settings.cors_origins_list) == 0, "Production should have no origins by default"
    assert prod_settings.get_cors_config()['allow_credentials'] == False, "Production should not allow credentials by default"
    print("   ✅ Production configuration is restrictive by default")
    
    # Production with explicit configuration should work
    assert len(prod_custom_settings.cors_origins_list) == 2, "Production should support custom origins"
    assert prod_custom_settings.cors_allow_credentials == True, "Production should support credentials when explicitly set"
    print("   ✅ Production configuration supports explicit settings")
    
    print("\n=== All CORS Tests Passed! ===")

if __name__ == "__main__":
    test_cors_configuration()
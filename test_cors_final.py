"""
Simple test for CORS configuration
"""

import os
import sys
sys.path.insert(0, '/root/dhii-mail')

def test_cors():
    print("=== Testing CORS Configuration ===\n")
    
    # Test 1: Development configuration
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'development'
    
    # Import fresh config module
    if 'config' in sys.modules:
        del sys.modules['config']
    from config import Settings
    
    dev_settings = Settings()
    print("1. Development Configuration:")
    print(f"   Environment: {dev_settings.environment}")
    print(f"   CORS Origins: {dev_settings.cors_origins_list}")
    print(f"   Allow Credentials: {dev_settings.cors_allow_credentials}")
    print(f"   Methods: {dev_settings.cors_methods_list}")
    print()
    
    # Test 2: Production configuration (default)
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'production'
    
    # Import fresh config module
    if 'config' in sys.modules:
        del sys.modules['config']
    from config import Settings
    
    prod_settings = Settings()
    prod_config = prod_settings.get_cors_config()
    
    print("2. Production Configuration (default):")
    print(f"   Environment: {prod_settings.environment}")
    print(f"   CORS Origins: {prod_settings.cors_origins_list}")
    print(f"   Allow Credentials (raw): {prod_settings.cors_allow_credentials}")
    print(f"   Allow Credentials (config): {prod_config['allow_credentials']}")
    print(f"   Methods: {prod_config['allow_methods']}")
    print(f"   Headers: {prod_config['allow_headers']}")
    print()
    
    # Test 3: Production with custom configuration
    os.environ.clear()
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['CORS_ORIGINS'] = 'https://myapp.com,https://admin.myapp.com'
    os.environ['CORS_ALLOW_CREDENTIALS'] = 'true'
    
    # Import fresh config module
    if 'config' in sys.modules:
        del sys.modules['config']
    from config import Settings
    
    prod_custom_settings = Settings()
    prod_custom_config = prod_custom_settings.get_cors_config()
    
    print("3. Production Configuration (custom):")
    print(f"   Environment: {prod_custom_settings.environment}")
    print(f"   CORS Origins: {prod_custom_settings.cors_origins_list}")
    print(f"   Allow Credentials: {prod_custom_settings.cors_allow_credentials}")
    print(f"   Config: {prod_custom_config}")
    print()
    
    # Assertions
    print("4. Security Assertions:")
    
    # Development should be permissive
    assert dev_settings.is_development, "Should be development"
    assert len(dev_settings.cors_origins_list) >= 4, "Development should have localhost origins"
    assert dev_settings.cors_allow_credentials == True, "Development should allow credentials"
    print("   ✅ Development is permissive")
    
    # Production should be restrictive by default
    assert prod_settings.is_production, "Should be production"
    assert len(prod_settings.cors_origins_list) == 0, "Production should have no origins by default"
    assert prod_config['allow_credentials'] == False, "Production should not allow credentials by default"
    assert prod_config['allow_methods'] == ['GET', 'POST', 'PUT', 'DELETE'], "Production should have restrictive methods"
    print("   ✅ Production is restrictive by default")
    
    # Production should support explicit configuration
    assert len(prod_custom_settings.cors_origins_list) == 2, "Should support custom origins"
    assert prod_custom_settings.cors_allow_credentials == True, "Should support explicit credentials"
    print("   ✅ Production supports explicit configuration")
    
    print("\n=== All CORS Tests Passed! ===")

if __name__ == "__main__":
    test_cors()
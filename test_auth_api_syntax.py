#!/usr/bin/env python3
"""
Test script to verify auth_api.py syntax and unified AuthManager integration
"""

import ast
import sys
import os

def test_auth_api_syntax():
    """Test that auth_api.py has valid syntax and unified AuthManager"""
    
    try:
        # Read and parse the auth_api.py file
        with open('/root/dhii-mail/auth_api.py', 'r') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        tree = ast.parse(content)
        print("✅ auth_api.py has valid Python syntax")
        
        # Check for unified AuthManager import
        has_auth_import = False
        has_auth_manager_var = False
        has_create_access_token = False
        
        for node in ast.walk(tree):
            # Check for 'from auth import get_auth' import
            if isinstance(node, ast.ImportFrom):
                if node.module == 'auth' and any(alias.name == 'get_auth' for alias in node.names):
                    has_auth_import = True
                    print("✅ Found 'from auth import get_auth' import")
            
            # Check for auth_manager variable assignment
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'auth_manager':
                        has_auth_manager_var = True
                        print("✅ Found auth_manager variable assignment")
            
            # Check for create_access_token function
            if isinstance(node, ast.FunctionDef) and node.name == 'create_access_token':
                has_create_access_token = True
                print("✅ Found create_access_token function")
        
        # Check if all required components are present
        if has_auth_import and has_auth_manager_var and has_create_access_token:
            print("✅ SUCCESS: auth_api.py has unified AuthManager integration")
            return True
        else:
            print("❌ Missing components:")
            if not has_auth_import:
                print("  - Missing 'from auth import get_auth' import")
            if not has_auth_manager_var:
                print("  - Missing auth_manager variable")
            if not has_create_access_token:
                print("  - Missing create_access_token function")
            return False
            
    except SyntaxError as e:
        print(f"❌ Syntax error in auth_api.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error parsing auth_api.py: {e}")
        return False

def test_no_legacy_jwt_config():
    """Test that auth_api.py doesn't have legacy JWT configuration"""
    
    try:
        with open('/root/dhii-mail/auth_api.py', 'r') as f:
            content = f.read()
        
        # Check for legacy JWT configuration
        legacy_patterns = [
            'SECRET_KEY =',
            'ALGORITHM =',
            'ACCESS_TOKEN_EXPIRE_MINUTES =',
            'jwt.encode',
            'jwt.decode'
        ]
        
        found_legacy = []
        for pattern in legacy_patterns:
            if pattern in content:
                found_legacy.append(pattern)
        
        if found_legacy:
            print(f"❌ Found legacy JWT configuration: {', '.join(found_legacy)}")
            return False
        else:
            print("✅ No legacy JWT configuration found")
            return True
            
    except Exception as e:
        print(f"❌ Error checking for legacy JWT config: {e}")
        return False

if __name__ == "__main__":
    print("Testing auth_api.py unified AuthManager integration...")
    
    syntax_ok = test_auth_api_syntax()
    no_legacy_ok = test_no_legacy_jwt_config()
    
    if syntax_ok and no_legacy_ok:
        print("\n✅ SUCCESS: auth_api.py unified AuthManager integration is correct")
        sys.exit(0)
    else:
        print("\n❌ FAIL: auth_api.py needs fixes")
        sys.exit(1)
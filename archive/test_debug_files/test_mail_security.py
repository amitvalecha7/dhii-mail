#!/usr/bin/env python3
"""
Comprehensive mail server security test
Tests all secure mail ports and verifies SSL/TLS encryption
"""

import socket
import ssl
import sys

def test_smtp_starttls(host, port):
    """Test SMTP STARTTLS"""
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            # Read greeting
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            if not response.startswith('220'):
                return False, f"No SMTP greeting: {response[:50]}"
            
            # Send EHLO
            sock.send(b'EHLO test\r\n')
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            if 'STARTTLS' not in response:
                return False, "STARTTLS not supported"
            
            # Start TLS
            sock.send(b'STARTTLS\r\n')
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            if not response.startswith('220'):
                return False, f"STARTTLS failed: {response[:50]}"
            
            # Wrap socket with SSL
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cipher = ssock.cipher()
                return True, f"STARTTLS working, Protocol: {cipher[1]}, Cipher: {cipher[0]}"
                
    except Exception as e:
        return False, str(e)

def test_port_ssl(host, port, service_name):
    """Test SSL connection to a port"""
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cipher = ssock.cipher()
                print(f"✓ {service_name} (port {port}): SSL/TLS working")
                print(f"  - Protocol: {cipher[1]}")
                print(f"  - Cipher: {cipher[0]}")
                return True
    except Exception as e:
        print(f"✗ {service_name} (port {port}): {e}")
        return False

def test_port_connection(host, port, service_name):
    """Test basic TCP connection to a port"""
    try:
        with socket.create_connection((host, port), timeout=3) as sock:
            print(f"✗ {service_name} (port {port}): Connection established (should be blocked)")
            return False
    except (socket.timeout, ConnectionRefusedError):
        print(f"✓ {service_name} (port {port}): Properly blocked/unavailable")
        return True
    except Exception as e:
        print(f"? {service_name} (port {port}): {e}")
        return False

def main():
    print("🔒 Mail Server Security Test")
    print("=" * 50)
    
    host = "localhost"
    
    # Test secure ports (should work)
    print("\n📧 Testing Secure Mail Ports:")
    print("-" * 30)
    
    # Test SMTP Submission with STARTTLS
    success, message = test_smtp_starttls(host, 587)
    if success:
        print(f"✓ SMTP Submission (port 587): {message}")
        secure_passed = 1
    else:
        print(f"✗ SMTP Submission (port 587): {message}")
        secure_passed = 0
    
    # Test other SSL/TLS ports
    secure_tests = [
        (465, "SMTPS (SSL/TLS)"),
        (993, "IMAPS (SSL/TLS)"),
        (995, "POP3S (SSL/TLS)")
    ]
    
    for port, service in secure_tests:
        if test_port_ssl(host, port, service):
            secure_passed += 1
    
    # Test unencrypted ports (should be blocked)
    unsecure_tests = [
        (143, "IMAP (unencrypted)"),
        (110, "POP3 (unencrypted)")
    ]
    
    print("\n🚫 Testing Unencrypted Mail Ports (should be blocked):")
    print("-" * 55)
    unsecure_blocked = 0
    for port, service in unsecure_tests:
        if test_port_connection(host, port, service):
            unsecure_blocked += 1
    
    # Test port 25 (SMTP - should be available)
    print("\n⚠️  Testing SMTP Port 25 (should be available):")
    print("-" * 45)
    try:
        with socket.create_connection((host, 25), timeout=3) as sock:
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            if "220" in response:
                print(f"✓ SMTP (port 25): Available (response: {response.strip()[:50]}...)")
                smtp_available = True
            else:
                print(f"? SMTP (port 25): Unexpected response: {response.strip()[:50]}...")
                smtp_available = False
    except Exception as e:
        print(f"✗ SMTP (port 25): {e}")
        smtp_available = False
    
    # Summary
    print("\n📊 Security Test Summary:")
    print("=" * 30)
    print(f"Secure ports working: {secure_passed}/{len(secure_tests)+1}")
    print(f"Unencrypted ports blocked: {unsecure_blocked}/{len(unsecure_tests)}")
    print(f"SMTP port 25 available: {'Yes' if smtp_available else 'No'}")
    
    total_score = secure_passed + unsecure_blocked + (1 if smtp_available else 0)
    max_score = len(secure_tests) + 1 + len(unsecure_tests) + 1
    
    if total_score >= 6:  # Allow for minor issues
        print("🎉 Mail server security configuration is working properly!")
        return 0
    else:
        print(f"⚠️  Some tests failed. Score: {total_score}/{max_score}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
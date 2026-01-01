#!/usr/bin/env python3
"""
Security Audit Script for dhii-mail
Comprehensive security analysis of all API endpoints
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

class SecurityAuditor:
    def __init__(self):
        self.vulnerabilities = []
        self.recommendations = []
        self.endpoints = []
    
    def scan_file(self, filepath: Path) -> Dict[str, Any]:
        """Scan a Python file for security issues"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'GOOGLE_API_KEY\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if not any(x in match for x in ['os.getenv', 'getenv', 'environ']):
                    issues.append({
                        'type': 'hardcoded_secret',
                        'line': self.get_line_number(content, match),
                        'description': f'Potential hardcoded secret: {match}'
                    })
        
        # Check for SQL injection vulnerabilities
        sql_patterns = [
            r'f["\'].*SELECT.*{.*}.*["\']',
            r'f["\'].*INSERT.*{.*}.*["\']',
            r'f["\'].*UPDATE.*{.*}.*["\']',
            r'f["\'].*DELETE.*{.*}.*["\']',
            r'\.format\(.*SELECT.*\)',
            r'\.format\(.*INSERT.*\)',
            r'\.format\(.*UPDATE.*\)',
            r'\.format\(.*DELETE.*\)'
        ]
        
        for pattern in sql_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'type': 'sql_injection',
                    'line': self.get_line_number(content, match),
                    'description': f'Potential SQL injection vulnerability: {match[:100]}...'
                })
        
        # Check for XSS vulnerabilities
        xss_patterns = [
            r'render_template.*{{.*}}',
            r'response.*{{.*}}',
            r'f["\'].*<.*{.*}.*>.*["\']'
        ]
        
        for pattern in xss_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'type': 'xss_vulnerability',
                    'line': self.get_line_number(content, match),
                    'description': f'Potential XSS vulnerability: {match[:100]}...'
                })
        
        return {
            'file': str(filepath),
            'issues': issues,
            'endpoint_count': len(re.findall(r'@(app|router)\.(get|post|put|delete|patch)', content))
        }
    
    def get_line_number(self, content: str, match: str) -> int:
        """Get line number for a match"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if match in line:
                return i
        return 0
    
    def extract_endpoints(self, content: str) -> List[Dict[str, Any]]:
        """Extract API endpoints from content"""
        endpoints = []
        
        # Find FastAPI endpoints
        endpoint_pattern = r'@(app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\'].*?\)'
        matches = re.findall(endpoint_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for decorator_type, method, path in matches:
            # Check if endpoint has authentication
            has_auth = 'Depends(get_current_user)' in content or 'Depends(auth' in content
            
            # Check if endpoint has proper error handling
            has_error_handling = 'try:' in content and 'except' in content
            
            # Check if endpoint has rate limiting
            has_rate_limiting = 'limiter' in content or 'rate_limit' in content
            
            endpoints.append({
                'path': path,
                'method': method.upper(),
                'decorator': decorator_type,
                'has_auth': has_auth,
                'has_error_handling': has_error_handling,
                'has_rate_limiting': has_rate_limiting,
                'security_score': self.calculate_security_score(has_auth, has_error_handling, has_rate_limiting)
            })
        
        return endpoints
    
    def calculate_security_score(self, has_auth: bool, has_error_handling: bool, has_rate_limiting: bool) -> int:
        """Calculate security score for an endpoint"""
        score = 0
        if has_auth:
            score += 40
        if has_error_handling:
            score += 30
        if has_rate_limiting:
            score += 30
        return score
    
    def audit_main_application(self):
        """Audit the main application file"""
        main_file = Path('/root/dhii-mail/main.py')
        if not main_file.exists():
            return
        
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Extract all endpoints
        self.endpoints = self.extract_endpoints(content)
        
        # Perform file scan
        scan_result = self.scan_file(main_file)
        
        return {
            'file': 'main.py',
            'endpoints': self.endpoints,
            'total_endpoints': len(self.endpoints),
            'secure_endpoints': len([e for e in self.endpoints if e['security_score'] >= 70]),
            'vulnerabilities': scan_result['issues']
        }
    
    def generate_security_report(self) -> str:
        """Generate a comprehensive security report"""
        audit_result = self.audit_main_application()
        
        report = []
        report.append("# 🔒 Security Audit Report for dhii-mail")
        report.append("=" * 50)
        report.append("")
        
        if audit_result:
            report.append(f"📊 **Endpoint Analysis:**")
            report.append(f"- Total endpoints: {audit_result['total_endpoints']}")
            report.append(f"- Secure endpoints (score ≥ 70): {audit_result['secure_endpoints']}")
            report.append(f"- Vulnerabilities found: {len(audit_result['vulnerabilities'])}")
            report.append("")
            
            # Endpoint security breakdown
            report.append("📋 **Endpoint Security Breakdown:**")
            for endpoint in audit_result['endpoints']:
                status = "🔒" if endpoint['security_score'] >= 70 else "⚠️" if endpoint['security_score'] >= 40 else "❌"
                report.append(f"{status} {endpoint['method']} {endpoint['path']} - Score: {endpoint['security_score']}/100")
                
                if endpoint['security_score'] < 70:
                    missing = []
                    if not endpoint['has_auth']:
                        missing.append("authentication")
                    if not endpoint['has_error_handling']:
                        missing.append("error handling")
                    if not endpoint['has_rate_limiting']:
                        missing.append("rate limiting")
                    
                    if missing:
                        report.append(f"   Missing: {', '.join(missing)}")
            report.append("")
            
            # Vulnerabilities
            if audit_result['vulnerabilities']:
                report.append("🚨 **Vulnerabilities Found:**")
                for vuln in audit_result['vulnerabilities']:
                    report.append(f"- {vuln['type']}: {vuln['description']} (line {vuln['line']})")
                report.append("")
        
        # General security recommendations
        report.append("🔧 **Security Recommendations:**")
        report.append("1. **Authentication**: Ensure all sensitive endpoints use proper authentication")
        report.append("2. **Rate Limiting**: Implement rate limiting to prevent abuse")
        report.append("3. **Input Validation**: Validate and sanitize all user inputs")
        report.append("4. **Error Handling**: Implement proper error handling with appropriate HTTP status codes")
        report.append("5. **HTTPS**: Use HTTPS in production with proper SSL certificates")
        report.append("6. **CORS**: Configure CORS properly for your domain")
        report.append("7. **Secrets Management**: Use environment variables for sensitive data")
        report.append("8. **Logging**: Implement secure logging without exposing sensitive data")
        report.append("9. **SQL Injection**: Use parameterized queries to prevent SQL injection")
        report.append("10. **XSS Protection**: Sanitize output to prevent XSS attacks")
        report.append("")
        
        report.append("✅ **Next Steps:**")
        report.append("1. Review and fix identified vulnerabilities")
        report.append("2. Implement missing security features")
        report.append("3. Run security tests in staging environment")
        report.append("4. Consider using a Web Application Firewall (WAF)")
        report.append("5. Set up security monitoring and alerting")
        
        return "\n".join(report)

def main():
    """Main function to run the security audit"""
    print("🔒 Starting security audit for dhii-mail...")
    
    auditor = SecurityAuditor()
    
    # Run the audit
    audit_result = auditor.audit_main_application()
    
    # Generate and save report
    report = auditor.generate_security_report()
    
    # Save report to file
    report_file = Path('/root/dhii-mail/security_audit_report.md')
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Security audit completed!")
    print(f"📄 Report saved to: {report_file}")
    
    # Print summary
    if audit_result:
        print(f"\n📊 Summary:")
        print(f"- Total endpoints: {audit_result['total_endpoints']}")
        print(f"- Secure endpoints: {audit_result['secure_endpoints']}")
        print(f"- Vulnerabilities: {len(audit_result['vulnerabilities'])}")
    
    return audit_result

if __name__ == "__main__":
    main()
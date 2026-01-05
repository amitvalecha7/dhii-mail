"""
@dhii.ai Email Integration System
Provides seamless @dhii.ai email account creation and management for new users
"""

import secrets
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from auth import AuthManager
from email_manager import EmailManager, EmailAccount
from security_manager import security_manager

logger = logging.getLogger(__name__)


class DhiiEmailIntegration:
    """
    Manages @dhii.ai email integration for user registration and email client functionality
    """
    
    def __init__(self, email_domain: str = "dhii.ai"):
        self.email_domain = email_domain
        self.smtp_server = "smtp.dhii.ai"
        self.imap_server = "imap.dhii.ai"
        self.smtp_port = 587
        self.imap_port = 993
        self.auth_manager = AuthManager()
        self.email_manager = EmailManager()
    
    async def register_user_with_dhii_email(self, 
                                          username: str, 
                                          password: str,
                                          first_name: str = "",
                                          last_name: str = "",
                                          tenant_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Complete user registration with @dhii.ai email creation
        """
        try:
            # Generate @dhii.ai email address
            dhii_email = f"{username}@{self.email_domain}"
            
            # Create user account
            user_data = self.auth_manager.create_user(
                email=dhii_email,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                tenant_id=tenant_id
            )
            
            if not user_data:
                raise Exception("Failed to create user account")
            
            # Create @dhii.ai email account
            email_account_data = await self._create_dhii_email_account(
                user_id=user_data['id'],
                username=username
            )
            
            # Return complete user information
            return {
                'user': user_data,
                'email_account': email_account_data,
                'dhii_email': dhii_email,
                'login_instructions': self._generate_login_instructions(username, dhii_email)
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            # Clean up if user was created but email failed
            if 'user_data' in locals() and user_data:
                self._cleanup_failed_registration(user_data['id'])
            raise
    
    async def _create_dhii_email_account(self, user_id: int, username: str) -> Dict[str, Any]:
        """Create @dhii.ai email account in database"""
        dhii_email = f"{username}@{self.email_domain}"
        email_password = secrets.token_urlsafe(16)  # Generate secure password
        
        # Create EmailAccount object
        email_account = EmailAccount(
            user_id=user_id,
            email_address=dhii_email,
            display_name=username,
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            smtp_username=dhii_email,
            smtp_password=security_manager.encrypt_sensitive_data(email_password),
            smtp_use_tls=True,
            imap_server=self.imap_server,
            imap_port=self.imap_port,
            imap_username=dhii_email,
            imap_password=security_manager.encrypt_sensitive_data(email_password),
            imap_use_ssl=True,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        # Store in database
        account_id = self.email_manager.add_email_account(email_account)
        
        # Prepare response data
        account_data = {
            'id': account_id,
            'user_id': user_id,
            'email_address': dhii_email,
            'display_name': username,
            'provider': 'dhii',
            'imap_server': self.imap_server,
            'imap_port': self.imap_port,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'is_primary': True,
            'is_active': True,
            'password_plaintext': email_password  # For initial setup only
        }
        
        logger.info(f"Created @dhii.ai email account: {dhii_email}")
        return account_data
    
    def _generate_login_instructions(self, username: str, email: str) -> Dict[str, str]:
        """Generate user-friendly login instructions"""
        return {
            'email': email,
            'login_url': 'https://app.dhii.ai',
            'instructions': f'''
Welcome to dhii Mail! Your @dhii.ai email account has been created:

📧 Email Address: {email}
🔐 Password: Use the password you created during registration

You can:
1. Login at https://app.dhii.ai using your email and password
2. Access your email through any email client using:
   - IMAP: {self.imap_server}:{self.imap_port} (SSL)
   - SMTP: {self.smtp_server}:{self.smtp_port} (TLS)

You can also add other email accounts (Gmail, Outlook, etc.) to manage all your emails in one place!
'''
        }
    
    def _cleanup_failed_registration(self, user_id: int):
        """Clean up resources if registration fails"""
        try:
            # Delete user account
            self.auth_manager.db.execute_update(
                "DELETE FROM users WHERE id = ?", (user_id,)
            )
            # Delete any created email accounts
            self.auth_manager.db.execute_update(
                "DELETE FROM email_accounts WHERE user_id = ?", (user_id,)
            )
            logger.info(f"Cleaned up failed registration for user ID: {user_id}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    async def add_external_email_account(self, user_id: int, 
                                       provider: str, 
                                       email_address: str,
                                       password: str,
                                       account_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Add external email account (Gmail, Outlook, etc.) for synchronization
        """
        provider_configs = {
            'gmail': {
                'imap_server': 'imap.gmail.com',
                'imap_port': 993,
                'imap_ssl': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'smtp_tls': True
            },
            'outlook': {
                'imap_server': 'outlook.office365.com',
                'imap_port': 993,
                'imap_ssl': True,
                'smtp_server': 'smtp.office365.com',
                'smtp_port': 587,
                'smtp_tls': True
            },
            'yahoo': {
                'imap_server': 'imap.mail.yahoo.com',
                'imap_port': 993,
                'imap_ssl': True,
                'smtp_server': 'smtp.mail.yahoo.com',
                'smtp_port': 587,
                'smtp_tls': True
            }
        }
        
        if provider not in provider_configs:
            raise ValueError(f"Unsupported email provider: {provider}")
        
        config = provider_configs[provider]
        account_name = account_name or f"{email_address} ({provider})"
        
        account_data = {
            'user_id': user_id,
            'account_name': account_name,
            'email_address': email_address,
            'display_name': email_address.split('@')[0],
            'provider': provider,
            'imap_server': config['imap_server'],
            'imap_port': config['imap_port'],
            'imap_username': email_address,
            'imap_password': encrypt_password(password),
            'imap_use_ssl': config['imap_ssl'],
            'smtp_server': config['smtp_server'],
            'smtp_port': config['smtp_port'],
            'smtp_username': email_address,
            'smtp_password': encrypt_password(password),
            'smtp_use_tls': config['smtp_tls'],
            'is_primary': False,
            'is_active': True,
            'created_at': datetime.now(timezone.utc)
        }
        
        account_id = self.email_manager.create_email_account(account_data)
        account_data['id'] = account_id
        
        logger.info(f"Added external email account: {email_address} ({provider})")
        return account_data
    
    def get_user_email_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all email accounts for a user"""
        return self.email_manager.get_email_accounts_by_user(user_id)
    
    def set_primary_account(self, user_id: int, account_id: int) -> bool:
        """Set primary email account for a user"""
        try:
            # Reset all accounts to non-primary
            self.auth_manager.db.execute_update(
                "UPDATE email_accounts SET is_primary = FALSE WHERE user_id = ?",
                (user_id,)
            )
            
            # Set the specified account as primary
            self.auth_manager.db.execute_update(
                "UPDATE email_accounts SET is_primary = TRUE WHERE id = ? AND user_id = ?",
                (account_id, user_id)
            )
            
            logger.info(f"Set primary email account: {account_id} for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set primary account: {e}")
            return False


# Global instance for easy access
_dhii_email_integration: Optional[DhiiEmailIntegration] = None


def get_dhii_email_integration() -> DhiiEmailIntegration:
    """Get or create the dhii email integration singleton"""
    global _dhii_email_integration
    if _dhii_email_integration is None:
        _dhii_email_integration = DhiiEmailIntegration()
    return _dhii_email_integration


# Example usage
async def example_registration():
    """Example of user registration with @dhii.ai email"""
    integration = get_dhii_email_integration()
    
    try:
        result = await integration.register_user_with_dhii_email(
            username="johndoe",
            password="securepassword123",
            first_name="John",
            last_name="Doe"
        )
        
        print(f"User registered successfully!")
        print(f"Email: {result['dhii_email']}")
        print(f"Login instructions: {result['login_instructions']['instructions']}")
        
        # Later, user can add external accounts
        gmail_result = await integration.add_external_email_account(
            user_id=result['user']['id'],
            provider='gmail',
            email_address='johndoe@gmail.com',
            password='gmailpassword'
        )
        
        print(f"Added Gmail account: {gmail_result['email_address']}")
        
    except Exception as e:
        print(f"Registration failed: {e}")


if __name__ == "__main__":
    asyncio.run(example_registration())
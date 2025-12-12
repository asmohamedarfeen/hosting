#!/usr/bin/env python3
"""
Test script to demonstrate user classification system
"""

def classify_user_by_email(email):
    """Classify user based on email domain"""
    if '@' not in email:
        return "invalid_email"
    
    domain = email.split('@')[1].lower()
    
    # List of common free email providers
    free_domains = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
        'icloud.com', 'protonmail.com', 'mail.com', 'yandex.com', 'zoho.com',
        'gmx.com', 'live.com', 'msn.com', 'rocketmail.com', 'ymail.com'
    }
    
    if domain in free_domains:
        return "normal"
    else:
        return "domain"

def test_user_classification():
    """Test various email addresses"""
    
    test_emails = [
        "john.doe@gmail.com",
        "jane.smith@yahoo.com",
        "hr@microsoft.com",
        "recruiter@google.com",
        "admin@startup.io",
        "careers@techcorp.com",
        "info@smallbusiness.local",
        "contact@freelancer.net",
        "user@outlook.com",
        "developer@amazon.com"
    ]
    
    print("User Classification System Test")
    print("=" * 50)
    print()
    
    for email in test_emails:
        user_type = classify_user_by_email(email)
        domain = email.split('@')[1] if '@' in email else "N/A"
        
        if user_type == "normal":
            print(f"📧 {email}")
            print(f"   Type: {user_type.upper()} USER")
            print(f"   Domain: {domain}")
            print(f"   Can post jobs: ❌")
            print(f"   Features: Basic networking, content posting")
        elif user_type == "domain":
            print(f"🏢 {email}")
            print(f"   Type: {user_type.upper()} USER (HR/Company)")
            print(f"   Domain: {domain}")
            print(f"   Can post jobs: ✅")
            print(f"   Features: Job posting, event hosting, company features")
        else:
            print(f"❌ {email}")
            print(f"   Type: INVALID")
            print(f"   Domain: {domain}")
            print(f"   Can post jobs: ❌")
            print(f"   Features: None")
        
        print()

if __name__ == "__main__":
    test_user_classification()

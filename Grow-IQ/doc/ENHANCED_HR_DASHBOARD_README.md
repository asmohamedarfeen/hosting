# Enhanced HR Dashboard for Domain ID and HR ID Users

## Overview

This enhancement adds comprehensive HR dashboard access for users with **Domain ID** or **HR ID**, providing company-wide access to job postings and applications beyond the standard domain email requirements.

## New Features

### 🔐 Enhanced Access Control

- **Domain ID Users**: Users assigned a company domain identifier
- **HR ID Users**: Users assigned an HR department identifier  
- **Combined Access**: Users can have both domain ID and HR ID for maximum privileges
- **Backward Compatibility**: Existing domain email users continue to work as before

### 🚀 Enhanced HR Dashboard

- **Company-Wide Access**: View all job postings across the entire company
- **Cross-Department Management**: Manage applications from different teams
- **Advanced Analytics**: Comprehensive company-wide hiring metrics
- **Bulk Operations**: Perform actions on multiple applications simultaneously

## Database Changes

### New Fields Added to User Table

```sql
-- New fields for enhanced HR access
domain_id TEXT,  -- Company domain identifier
hr_id TEXT,      -- HR department identifier
```

### New User Methods

```python
# Check user access type
user.get_access_type()  # Returns: 'hr_id', 'domain_id', 'domain_email', or 'normal'

# Check if user has domain-level access
user.has_domain_access()  # Returns True for any enhanced access

# Enhanced HR user check
user.is_hr_user()  # Now includes domain_id and hr_id users
```

## Installation & Setup

### 1. Run Database Migration

```bash
cd "Glow-IQ 3 (3)1122.5.0/Glow-IQ 3/Glow-IQ"
python migrate_domain_hr_fields.py
```

### 2. Verify Installation

The migration script will:
- Add new database fields
- Create sample test users
- Verify schema compatibility
- Run post-migration tests

### 3. Test Access

```bash
# Test with sample users created by migration
Username: domain_user, Password: (check database)
Username: hr_user, Password: (check database)
Username: senior_hr, Password: (check database)
```

## Usage

### Accessing Enhanced HR Dashboard

1. **Standard HR Dashboard**: `/hr/dashboard` (existing functionality)
2. **Enhanced HR Dashboard**: `/hr/enhanced-dashboard` (new features)

### Navigation

- **Home Page**: Enhanced HR button appears for domain ID/HR ID users
- **HR Dashboard**: Link to enhanced dashboard for qualified users
- **Access Control**: Automatic redirection based on user privileges

## User Types & Access Levels

### 🔵 Standard Users
- Access: Basic platform features
- HR Dashboard: ❌ No access

### 🟢 Domain Email Users  
- Access: Standard HR dashboard (own jobs only)
- HR Dashboard: ✅ `/hr/dashboard`
- Enhanced Dashboard: ❌ No access

### 🟡 Domain ID Users
- Access: Enhanced HR dashboard (company-wide)
- HR Dashboard: ✅ `/hr/dashboard` 
- Enhanced Dashboard: ✅ `/hr/enhanced-dashboard`

### 🟠 HR ID Users
- Access: Enhanced HR dashboard (company-wide)
- HR Dashboard: ✅ `/hr/dashboard`
- Enhanced Dashboard: ✅ `/hr/enhanced-dashboard`

### 🔴 Combined Access Users
- Access: Maximum privileges (both domain and HR)
- HR Dashboard: ✅ `/hr/dashboard`
- Enhanced Dashboard: ✅ `/hr/enhanced-dashboard`

## Enhanced Dashboard Features

### 📊 Company Overview
- Total job postings across company
- Company-wide application statistics
- Hiring success rates and metrics
- Response time analytics

### 👥 All Applications
- View applications from all departments
- Cross-team application management
- Enhanced filtering and search
- Bulk status updates

### 💼 Company Jobs
- Monitor all active job postings
- Track performance metrics
- Application and view statistics
- Department-wise job analysis

### 📈 Advanced Analytics
- Interactive charts and graphs
- Application status distribution
- Job performance trends
- Company-wide hiring insights

## API Endpoints

### New Routes

```python
# Enhanced HR Dashboard
GET /hr/enhanced-dashboard

# Enhanced HR Statistics  
GET /hr/stats/enhanced

# Company-wide Applications
GET /hr/applications/company-wide

# Cross-department Jobs
GET /hr/jobs/company-wide
```

### Access Control

All enhanced routes use the existing `get_hr_user()` dependency, which now includes:
- Domain email verification
- Domain ID verification  
- HR ID verification
- User verification status

## Configuration

### Environment Variables

```bash
# Optional: Custom domain ID patterns
DOMAIN_ID_PATTERN="COMPANY_*"

# Optional: Custom HR ID patterns  
HR_ID_PATTERN="HR_*"
```

### Development Mode

```bash
# Enable HR development mode (bypasses some restrictions)
touch .hr_dev_mode
```

## Security Features

### Access Validation
- User verification required for all enhanced access
- Domain ID and HR ID validation
- Company email verification maintained
- Session-based authentication

### Data Isolation
- Company-wide access for qualified users
- Department-level filtering available
- Audit logging for all HR actions
- Secure API endpoints

## Testing

### Manual Testing

1. **Create Test Users**:
   ```python
   # Domain ID user
   user.domain_id = "COMPANY_DOMAIN_001"
   user.is_verified = True
   
   # HR ID user  
   user.hr_id = "HR_DEPT_001"
   user.is_verified = True
   ```

2. **Test Access Control**:
   - Verify enhanced dashboard access
   - Check company-wide data visibility
   - Test navigation between dashboards

3. **Verify Functionality**:
   - Company statistics display
   - All applications visibility
   - Cross-department job access

### Automated Testing

```bash
# Run existing HR tests
python -m pytest test_hr_system.py

# Test new access methods
python test_enhanced_access.py
```

## Troubleshooting

### Common Issues

1. **Migration Errors**:
   - Ensure database is not locked
   - Check file permissions
   - Verify SQLite version compatibility

2. **Access Denied**:
   - Verify user verification status
   - Check domain_id/hr_id values
   - Ensure proper user_type setting

3. **Template Errors**:
   - Verify template file exists
   - Check Jinja2 syntax
   - Validate context data

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check user access details
print(f"Access Type: {user.get_access_type()}")
print(f"Domain Access: {user.has_domain_access()}")
print(f"HR User: {user.is_hr_user()}")
```

## Migration Guide

### From Existing System

1. **Backup Database**: Always backup before migration
2. **Run Migration**: Execute migration script
3. **Update Users**: Assign domain_id/hr_id as needed
4. **Test Access**: Verify enhanced features work
5. **Train Users**: Educate HR team on new capabilities

### User Assignment

```sql
-- Assign domain ID to existing user
UPDATE users 
SET domain_id = 'COMPANY_DOMAIN_001' 
WHERE email = 'user@company.com';

-- Assign HR ID to existing user  
UPDATE users 
SET hr_id = 'HR_DEPT_001' 
WHERE email = 'hr@company.com';
```

## Future Enhancements

### Planned Features
- **Role-Based Access Control**: Fine-grained permissions
- **Department Hierarchies**: Organizational structure support
- **Advanced Analytics**: Machine learning insights
- **Integration APIs**: Third-party HR system connections

### Customization Options
- **Company Branding**: Custom themes and logos
- **Workflow Automation**: Automated application processing
- **Reporting Tools**: Custom report generation
- **Mobile Support**: Responsive mobile dashboard

## Support & Documentation

### Resources
- **API Documentation**: `/docs` endpoint (Swagger UI)
- **Code Examples**: See `test_enhanced_access.py`
- **Troubleshooting**: Check logs in `logs/` directory

### Contact
- **Technical Issues**: Check application logs
- **Feature Requests**: Submit via issue tracker
- **Documentation**: Update this README as needed

---

## Quick Start Checklist

- [ ] Run database migration script
- [ ] Verify new fields added to database
- [ ] Create test users with domain_id/hr_id
- [ ] Test enhanced dashboard access
- [ ] Verify company-wide data visibility
- [ ] Test navigation between dashboards
- [ ] Update existing users as needed
- [ ] Train HR team on new features

**🎉 Congratulations! You now have enhanced HR dashboard access for domain ID and HR ID users.**

# HR Dashboard - Qrow IQ

## 🎯 Overview

The HR Dashboard is a comprehensive job management system for HR professionals and hiring managers. It provides complete control over job postings, application management, and candidate evaluation within the Qrow IQ platform.

## ✨ Features

### 🔐 **HR-Only Access Control**
- Automatic detection of HR users based on company email domains
- Secure authentication with role-based permissions
- Development mode for testing with any user type

### 📊 **Dashboard Overview**
- Real-time statistics and metrics
- Recent application notifications
- Quick action buttons for common tasks
- Interactive charts showing application trends

### 💼 **Job Management**
- View all posted jobs with application counts
- Job performance metrics and analytics
- Quick access to job-specific applications
- Job editing and management tools

### 📋 **Application Management**
- Comprehensive application tracking system
- Status management (Pending, Reviewed, Interview, Rejected, Hired)
- Bulk actions for efficient processing
- Application filtering and search capabilities

### 👥 **Candidate Profiles**
- Detailed candidate information with skills and experience
- Application history across all job postings
- Contact information and professional profiles
- Advanced candidate search and filtering

### 📈 **Analytics & Reporting**
- Application status breakdown
- Hiring funnel metrics
- Time-to-hire analytics
- Performance insights

## 🏗️ Architecture

### **Backend Components**

#### **Models (`models.py`)**
```python
class JobApplication(Base):
    # Complete application tracking with status, notes, ratings
    # Relationships to User and Job models
    # Status workflow management
```

#### **HR Routes (`hr_routes.py`)**
- `GET /hr/dashboard` - Main HR dashboard
- `GET /hr/applications` - Application management API
- `PUT /hr/applications/{id}/status` - Update application status
- `GET /hr/candidates` - Candidate search and management
- `POST /hr/applications/bulk-action` - Bulk operations

#### **Authentication & Permissions**
- `is_hr_user()` - Check HR privileges
- `can_manage_applications()` - Application management permissions
- `get_hr_user()` - Dependency injection for HR routes

### **Frontend Components**

#### **Templates**
- `hr_dashboard.html` - Main HR interface with sections:
  - Overview with statistics
  - Applications table with filtering
  - Candidate search grid
  - Job management interface

#### **Styling**
- `hr_dashboard.css` - Complete styling for HR interface
- `hr_navigation.css` - HR-specific navigation elements
- LinkedIn-inspired design with professional aesthetics

#### **JavaScript**
- `hr_dashboard.js` - Interactive functionality:
  - Application status updates
  - Bulk actions
  - Real-time filtering
  - Modal management
  - AJAX API calls

## 🚀 Quick Start

### **1. Access HR Dashboard**

**For HR Users:**
- HR Dashboard link appears automatically in navigation
- Access via: `http://localhost:8000/hr/dashboard`
- Quick action button in home sidebar

**User Requirements:**
- Domain email (e.g., `hr@company.com`)
- Verified status
- OR development mode enabled

### **2. Test with Sample Data**

Run the test script to create sample data:
```bash
python test_hr_system.py
```

This creates:
- ✅ HR user with proper permissions
- ✅ 3 test candidates with diverse profiles
- ✅ 3 job postings from HR user
- ✅ Multiple job applications for testing
- ✅ Active HR session for immediate access

### **3. Navigation**

**From Home Page:**
- Click "HR Dashboard" in left navigation (if HR user)
- Use "HR Dashboard" quick action button
- Direct URL access

**HR Dashboard Sections:**
- **Overview** - Statistics and recent activity
- **Applications** - Manage job applications
- **Candidates** - Search and view candidate profiles
- **My Jobs** - Manage posted jobs

## 📋 User Guide

### **Application Management**

#### **Viewing Applications**
1. Go to Applications section
2. Filter by job or status
3. Click "View" to see detailed application
4. Review candidate profile and cover letter

#### **Updating Application Status**
1. Click "Update" button on application
2. Select new status:
   - **Pending** - Awaiting review
   - **Reviewed** - Application reviewed
   - **Interview** - Scheduled for interview
   - **Rejected** - Application declined
   - **Hired** - Candidate hired
3. Add HR notes and rating (1-5 stars)
4. Save changes

#### **Bulk Actions**
1. Select multiple applications using checkboxes
2. Click "Update Status" in bulk actions bar
3. Choose new status and add notes
4. Apply to all selected applications

### **Candidate Search**

#### **Basic Search**
- Use search bar for names, skills, or titles
- Results update in real-time

#### **Advanced Filtering**
- **Skills Filter** - Required technical skills
- **Experience Filter** - Minimum years of experience
- **Location Filter** - Geographic location
- Apply filters to narrow results

#### **Candidate Profiles**
- Click "View Profile" to see complete information
- Access contact details, portfolio links
- View application history across all jobs

### **Job Management**

#### **Job Statistics**
- View application count per job
- Monitor job performance metrics
- Track views and engagement

#### **Managing Applications by Job**
1. Click "View Applications" on job card
2. Filter applications section by specific job
3. Process applications for that position

## 🔧 Configuration

### **HR User Setup**

#### **Automatic Classification**
Users are automatically classified as HR if:
- Email domain is not in free providers list
- Domain verification completed
- Account status is active

#### **Manual HR Setup**
```python
# In database or through admin interface
user.user_type = 'domain'
user.domain = 'company.com'
user.is_verified = True
```

#### **Development Mode**
Enable for testing with any user:
```bash
# Create development mode file
touch .dev_mode

# Or via admin endpoint
POST /jobs/admin/enable-dev-mode
```

### **Permissions Matrix**

| User Type | Can Post Jobs | Is HR User | Can Manage Applications |
|-----------|---------------|------------|------------------------|
| Normal    | ❌ (⚠️ Dev Mode) | ❌ (⚠️ Dev Mode) | ❌ (⚠️ Dev Mode) |
| Domain (Unverified) | ❌ | ❌ | ❌ |
| Domain (Verified) | ✅ | ✅ | ✅ |
| Development Mode | ✅ | ✅ | ✅ |

## 🎨 Customization

### **Styling**
- Modify `hr_dashboard.css` for visual changes
- Update `hr_navigation.css` for navigation styling
- LinkedIn-inspired design with blue accent colors

### **Functionality**
- Extend `hr_routes.py` for new API endpoints
- Add features to `hr_dashboard.js` for client-side logic
- Customize `hr_dashboard.html` template for layout changes

### **Status Workflow**
Modify application statuses in `models.py`:
```python
# Current statuses
'pending', 'reviewed', 'interview', 'rejected', 'hired'

# Add custom statuses as needed
```

## 🔍 API Reference

### **Get Applications**
```http
GET /hr/applications?status=pending&job_id=1&limit=20&offset=0
```

**Response:**
```json
{
  "applications": [
    {
      "id": 1,
      "job": {"id": 1, "title": "Software Engineer"},
      "applicant": {
        "id": 2,
        "name": "John Doe",
        "email": "john@email.com",
        "skills": ["Python", "JavaScript"]
      },
      "status": "pending",
      "applied_at": "2024-01-20T10:30:00",
      "cover_letter": "Dear Hiring Manager..."
    }
  ],
  "total_count": 50
}
```

### **Update Application Status**
```http
PUT /hr/applications/1/status
Content-Type: application/json

{
  "status": "interview",
  "notes": "Strong technical background",
  "hr_rating": 4,
  "interview_date": "2024-01-25T14:00:00"
}
```

### **Search Candidates**
```http
GET /hr/candidates?search=python&experience_min=3&location=NYC
```

### **Bulk Update**
```http
POST /hr/applications/bulk-action
Content-Type: application/json

{
  "application_ids": [1, 2, 3],
  "action": "update_status",
  "status": "reviewed",
  "notes": "Initial review completed"
}
```

## 🚨 Troubleshooting

### **Access Issues**

**Problem**: HR Dashboard not visible
**Solutions:**
1. Verify user has domain email
2. Check verification status
3. Enable development mode for testing
4. Confirm session is active

**Problem**: 403 Forbidden errors
**Solutions:**
1. Check user permissions with `user.can_manage_applications()`
2. Verify HR status with `user.is_hr_user()`
3. Enable development mode if needed

### **Data Issues**

**Problem**: No applications showing
**Solutions:**
1. Run test script: `python test_hr_system.py`
2. Check job ownership (only shows HR user's jobs)
3. Verify job applications exist in database

**Problem**: Database errors
**Solutions:**
1. Ensure JobApplication table exists
2. Run database migration if needed
3. Check table schema matches model

### **Performance Issues**

**Problem**: Slow loading
**Solutions:**
1. Add database indexes on frequently queried fields
2. Implement pagination for large datasets
3. Cache common queries

## 🛡️ Security Considerations

### **Access Control**
- HR routes protected by role-based permissions
- Session-based authentication required
- Automatic verification of HR privileges

### **Data Privacy**
- Candidate information protected by access controls
- Application data only visible to authorized HR users
- Audit trails for sensitive operations

### **Input Validation**
- All inputs sanitized and validated
- SQL injection protection via SQLAlchemy ORM
- XSS prevention in templates

## 📈 Future Enhancements

### **Planned Features**
- **Interview Scheduling** - Calendar integration
- **Email Integration** - Automated candidate communication
- **Advanced Analytics** - Hiring metrics and insights
- **PDF Generation** - Application export functionality
- **Integration APIs** - Connect with external HR systems

### **Technical Improvements**
- Real-time notifications via WebSockets
- Advanced search with Elasticsearch
- Caching layer for improved performance
- Mobile-responsive design improvements

## 💡 Support

For technical support or feature requests:
1. Check this documentation first
2. Review API errors in browser console
3. Check server logs for detailed error information
4. Run test script to verify system functionality

## 🎉 Success! 

Your HR Dashboard is now fully operational with:
- ✅ Complete application management system
- ✅ Professional candidate evaluation tools  
- ✅ Secure role-based access control
- ✅ Modern, intuitive user interface
- ✅ Comprehensive API and documentation

Start managing your hiring process more efficiently with the Qrow IQ HR Dashboard!

# User Classification & Job Posting System

## Overview

Qrow IQ now implements a sophisticated user classification system that automatically distinguishes between regular users and HR/company officers based on their email domain. This system enables company representatives to post job opportunities while maintaining security and authenticity.

## User Types

### 1. Normal Users (Personal Email)
- **Email Domains**: gmail.com, yahoo.com, hotmail.com, outlook.com, etc.
- **Features**:
  - Basic networking and content posting
  - Connection management
  - Profile customization
  - Job searching and application
  - **Cannot post jobs**

### 2. Domain Users (Company Email)
- **Email Domains**: Any non-free email provider (microsoft.com, google.com, startup.io, etc.)
- **Features**:
  - All normal user features
  - **Job posting capabilities**
  - Event hosting
  - Company verification badge
  - Enhanced profile features

## Automatic Classification

The system automatically classifies users during signup based on their email domain:

```python
def classify_user_by_email(email):
    domain = email.split('@')[1].lower()
    
    free_domains = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'icloud.com', 'protonmail.com', 'mail.com', 'zoho.com'
    }
    
    if domain in free_domains:
        return "normal"
    else:
        return "domain"
```

## Job Posting System

### For Domain Users Only

Domain users can create comprehensive job postings with the following fields:

- **Job Title** (required)
- **Company Name** (required)
- **Location** (required)
- **Job Type** (full-time, part-time, contract, internship, freelance)
- **Salary Range**
- **Job Description** (required)
- **Requirements & Qualifications**
- **Benefits & Perks**
- **Application Deadline**

### Job Management

- **Create**: Domain users can post new jobs
- **View**: All users can browse and search jobs
- **Apply**: All users can apply to jobs
- **Delete**: Only job posters can delete their own postings

## Database Schema

### User Model Updates

```python
class User(Base):
    # ... existing fields ...
    user_type = Column(String(20), default='normal')  # normal, domain, premium
    domain = Column(String(100), nullable=True)  # Company domain
    is_verified = Column(Boolean, default=False)  # Auto-verified for domain users
```

### Job Model

```python
class Job(Base):
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    location = Column(String(100))
    job_type = Column(String(50))
    salary_range = Column(String(50))
    description = Column(Text)
    requirements = Column(Text)
    benefits = Column(Text)
    application_deadline = Column(DateTime)
    posted_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    posted_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
```

## API Endpoints

### Job Management

- `GET /jobs/post` - Job posting form (domain users only)
- `POST /jobs/create` - Create new job (domain users only)
- `GET /jobs` - List all active jobs
- `GET /jobs/search` - Search jobs with filters
- `GET /jobs/{job_id}` - View job details
- `POST /jobs/{job_id}/apply` - Apply for a job
- `DELETE /jobs/{job_id}` - Delete job (poster only)

### User Classification

- `POST /auth/signup` - Automatic user classification during signup
- `GET /dashboard` - Shows domain-specific features for company users

## Frontend Features

### Dashboard Integration

Domain users see a special "Company Features" section on their dashboard:

- **Post a New Job** button
- **Manage Job Postings** link
- **Host Events** capability
- Company domain and verification status

### Job Posting Interface

- Professional form design
- Real-time validation
- Responsive layout
- Success/error notifications

### Job Listing Pages

- **Jobs Overview**: Grid layout with search and filters
- **Job Details**: Comprehensive job information with application form
- **Search & Filter**: By title, company, location, and job type

## Security Features

### Access Control

- Job posting restricted to verified domain users
- Users cannot apply to their own job postings
- Soft delete for job management
- Session-based authentication

### Domain Verification

- Automatic detection of company vs. personal email domains
- Immediate verification for domain users
- Visual indicators of company status

## Usage Examples

### Testing User Classification

Run the test script to see how different email addresses are classified:

```bash
python test_user_classification.py
```

Example output:
```
🏢 hr@microsoft.com
   Type: DOMAIN USER (HR/Company)
   Domain: microsoft.com
   Can post jobs: ✅
   Features: Job posting, event hosting, company features

📧 john.doe@gmail.com
   Type: NORMAL USER
   Domain: gmail.com
   Can post jobs: ❌
   Features: Basic networking, content posting
```

### Creating a Job Posting

1. **Sign up** with a company email (e.g., hr@yourcompany.com)
2. **Login** to your dashboard
3. **Click** "Post a New Job" in the Company Features section
4. **Fill out** the comprehensive job form
5. **Submit** to create the job listing

### Applying for Jobs

1. **Browse** available jobs on the jobs page
2. **Click** on a job to view details
3. **Fill out** the application form with your cover letter
4. **Submit** your application

## Configuration

### Free Email Domains

The system maintains a list of free email providers. To modify this list, update the `free_domains` set in:

- `auth_routes.py` (signup classification)
- `social_routes.py` (domain verification)
- `test_user_classification.py` (testing)

### Auto-Verification

Domain users are automatically verified upon signup. To change this behavior, modify the `is_verified` field assignment in the signup route.

## Future Enhancements

### Planned Features

1. **Email Verification**: Send verification emails to domain users
2. **Company Profiles**: Dedicated company profile pages
3. **Job Analytics**: Track job views and applications
4. **Advanced Filtering**: More sophisticated job search options
5. **Application Management**: Track and manage job applications

### Integration Opportunities

1. **ATS Integration**: Connect with Applicant Tracking Systems
2. **Email Notifications**: Automated job alerts and updates
3. **Social Sharing**: Share job postings on social media
4. **Mobile App**: Native mobile application for job seekers

## Troubleshooting

### Common Issues

1. **User not classified as domain**: Check if email domain is in the free domains list
2. **Cannot post jobs**: Verify user type is 'domain' and is_verified is True
3. **Job not appearing**: Check if job is_active is True

### Debug Information

- Check user classification in database: `SELECT user_type, domain, is_verified FROM users WHERE email = 'user@example.com'`
- Verify job status: `SELECT * FROM jobs WHERE posted_by = [user_id]`

## Support

For technical support or feature requests related to the user classification and job posting system, please refer to the main project documentation or contact the development team.

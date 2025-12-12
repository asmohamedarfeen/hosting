from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import os
import re
import json

class Base(DeclarativeBase):
    pass

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship
    user = relationship("User", backref="sessions")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    title = Column(String(100), nullable=True)
    company = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    profile_image = Column(String(200), default='default-avatar.svg')
    profile_pic = Column(String(500), nullable=True)  # New field for profile picture URL/path
    password_hash = Column(String(256), nullable=True)
    user_type = Column(String(20), default='normal', nullable=False)  # normal, domain, premium
    domain = Column(String(100), nullable=True)  # Company domain for domain users
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Additional user profile fields
    phone = Column(String(20), nullable=True)
    website = Column(String(200), nullable=True)
    linkedin_url = Column(String(200), nullable=True)
    twitter_url = Column(String(200), nullable=True)
    github_url = Column(String(200), nullable=True)
    
    # OAuth provider IDs
    google_id = Column(String(100), nullable=True, unique=True)
    
    # HR and Domain Management
    domain_id = Column(String(100), nullable=True)  # Company domain identifier
    hr_id = Column(String(100), nullable=True)      # HR department identifier
    
    # Professional information
    industry = Column(String(100), nullable=True)
    skills = Column(Text, nullable=True)  # JSON string of skills
    experience_years = Column(Integer, nullable=True)
    experience = Column(String(20), nullable=True)  # Experience range (e.g., "0-1", "1-3", "3-5")
    education = Column(Text, nullable=True)  # JSON string of education
    certifications = Column(Text, nullable=True)  # JSON string of certifications
    interests = Column(Text, nullable=True)  # Professional interests
    portfolio_url = Column(String(200), nullable=True)  # Portfolio website URL
    
    # Privacy settings
    profile_visibility = Column(String(20), default='public', nullable=False)  # public, connections, private
    show_email = Column(Boolean, default=False, nullable=False)
    show_phone = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    posts = relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    sent_connections = relationship('Connection', foreign_keys='Connection.user_id', lazy='dynamic', overlaps="sender,receiver")
    received_connections = relationship('Connection', foreign_keys='Connection.connected_user_id', lazy='dynamic', overlaps="sender,receiver")
    sent_friend_requests = relationship('FriendRequest', foreign_keys='FriendRequest.sender_id', lazy='dynamic', overlaps="sender,receiver")
    received_friend_requests = relationship('FriendRequest', foreign_keys='FriendRequest.receiver_id', lazy='dynamic', overlaps="sender,receiver")
    hosted_events = relationship('Event', backref='organizer', lazy='dynamic', cascade='all, delete-orphan')
    posted_jobs = relationship('Job', backref='job_poster', lazy='dynamic', cascade='all, delete-orphan')
    
    # Constraints
    __table_args__ = (
        CheckConstraint("user_type IN ('normal', 'domain', 'premium')", name='valid_user_type'),
        CheckConstraint("profile_visibility IN ('public', 'connections', 'private')", name='valid_profile_visibility'),
        CheckConstraint("experience_years >= 0", name='valid_experience_years'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', full_name='{self.full_name}')>"
    
    def to_dict(self):
        """Convert user object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'bio': self.bio,
            'profile_image': self.profile_image,
            'profile_pic': self.profile_pic,
            'user_type': self.user_type,
            'domain': self.domain,
            'domain_id': self.domain_id,
            'hr_id': self.hr_id,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'phone': self.phone,
            'website': self.website,
            'linkedin_url': self.linkedin_url,
            'twitter_url': self.twitter_url,
            'github_url': self.github_url,
            'industry': self.industry,
            'skills': self.skills,
            'experience_years': self.experience_years,
            'education': self.education,
            'certifications': self.certifications,
            'profile_visibility': self.profile_visibility,
            'show_email': self.show_email,
            'show_phone': self.show_phone
        }
    
    def is_domain_email(self):
        """Check if email is from a company domain (not free email provider)"""
        if not self.email or '@' not in self.email:
            return False
        
        try:
            email_domain = self.email.split('@')[1].lower()
        except IndexError:
            return False
        
        # List of free email providers - users with these emails are NOT HR users
        free_email_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'icloud.com', 'protonmail.com', 'mail.com', 'zoho.com',
            'aol.com', 'yandex.com', 'tutanota.com', 'gmx.com',
            'live.com', 'msn.com', 'yahoo.co.uk', 'yahoo.co.in',
            'rediffmail.com', 'fastmail.com', 'hushmail.com'
        }
        
        # If email domain is in free providers list, it's NOT a domain email
        return email_domain not in free_email_domains
    
    def is_domain_user(self):
        """Check if user has a verified domain email"""
        return self.user_type == 'domain' and self.is_verified
    
    def can_post_jobs(self):
        """Check if user can post job listings"""
        import os
        
        # Check for development mode
        if os.path.exists('.dev_mode'):
            return True
        
        return self.is_domain_user()
    
    def can_host_events(self):
        """Check if user can host events"""
        return self.is_domain_user()
    
    def can_post_content(self):
        """All users can post content"""
        return True
    
    def is_hr_user(self):
        """Check if user can access HR features - for domain email users, domain ID users, or HR ID users"""
        # HR access for verified domain users, domain ID users, or HR ID users
        # No development mode override for HR features
        return (
            (self.user_type == 'domain' and self.is_verified and self.is_domain_email()) or
            (self.domain_id is not None and self.is_verified) or
            (self.hr_id is not None and self.is_verified)
        )
    
    def can_manage_applications(self):
        """Check if user can manage job applications"""
        return self.is_hr_user()
    
    def has_domain_access(self):
        """Check if user has domain-level access (domain email, domain ID, or HR ID)"""
        return (
            self.is_domain_email() or
            (self.domain_id is not None and self.is_verified) or
            (self.hr_id is not None and self.is_verified)
        )
    
    def get_access_type(self):
        """Get the type of access the user has"""
        if self.hr_id is not None and self.is_verified:
            return "hr_id"
        elif self.domain_id is not None and self.is_verified:
            return "domain_id"
        elif self.is_domain_email() and self.is_verified:
            return "domain_email"
        else:
            return "normal"
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now()
    
    def get_public_profile(self):
        """Get public profile information"""
        profile = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'bio': self.bio,
            'profile_image': self.profile_image,
            'profile_pic': self.profile_pic,
            'industry': self.industry,
            'experience_years': self.experience_years,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Add email if user allows it
        if self.show_email:
            profile['email'] = self.email
            
        # Add phone if user allows it
        if self.show_phone:
            profile['phone'] = self.phone
            
        return profile
    
    def get_profile_image_url(self):
        """Get the proper profile image URL"""
        if not self.profile_image or self.profile_image == 'default-avatar.svg':
            return '/static/uploads/default-avatar.svg'
        
        # Check if it's an external URL (starts with http:// or https://)
        if self.profile_image.startswith(('http://', 'https://')):
            return self.profile_image
        
        # Otherwise, it's a local file
        return f'/static/uploads/{self.profile_image}'
    
    def get_profile_pic_url(self):
        """Get the current profile picture URL with fallback"""
        # Priority: profile_pic > profile_image > default
        if self.profile_pic:
            return self.profile_pic
        
        if self.profile_image and self.profile_image != 'default-avatar.svg':
            if self.profile_image.startswith(('http://', 'https://')):
                return self.profile_image
            return f'/static/uploads/{self.profile_image}'
        
        return '/static/uploads/default-avatar.svg'
    
    def update_profile_pic(self, new_pic_url: str):
        """Update the profile picture URL"""
        self.profile_pic = new_pic_url
        self.updated_at = datetime.now()
    
    def get_current_profile_picture(self):
        """Get the current profile picture (alias for get_profile_pic_url)"""
        return self.get_profile_pic_url()
    
    def is_external_profile_image(self):
        """Check if profile image is an external URL"""
        return self.profile_image and self.profile_image.startswith(('http://', 'https://'))
    
    def get_profile_image_filename(self):
        """Get just the filename for local profile images"""
        if not self.profile_image or self.profile_image == 'default-avatar.svg':
            return 'default-avatar.svg'
        
        # If it's an external URL, return default
        if self.profile_image.startswith(('http://', 'https://')):
            return 'default-avatar.svg'
        
        # Return the filename
        return self.profile_image
    
    @property
    def first_name(self):
        """Get first name from full_name"""
        if self.full_name:
            return self.full_name.split()[0] if ' ' in self.full_name else self.full_name
        return ''
    
    @property
    def last_name(self):
        """Get last name from full_name"""
        if self.full_name and ' ' in self.full_name:
            return ' '.join(self.full_name.split()[1:])
        return ''
    
    def set_names(self, first_name: str, last_name: str):
        """Set first and last names, updating full_name"""
        self.full_name = f"{first_name} {last_name}".strip()

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    image_path = Column(String(200))
    video_path = Column(String(200))  # Path to uploaded video file
    certificate_path = Column(String(200))  # Path to uploaded certificate file
    post_type = Column(String(20), default='general')  # general, job, event, announcement, certificate
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    comments = relationship('Comment', backref='post', lazy='selectin', cascade='all, delete-orphan')


class PostLike(Base):
    __tablename__ = 'post_likes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Ensure one like per user per post
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='uq_post_like_post_user'),
    )

    # Lightweight relationships
    post = relationship('Post', backref='post_likes')
    user = relationship('User')

class Connection(Base):
    __tablename__ = 'connections'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    connected_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='pending')  # pending, accepted, declined, removed
    connection_type = Column(String(20), default='professional')  # professional, personal
    message = Column(Text)  # Optional message with connection request
    created_at = Column(DateTime, default=datetime.now)
    accepted_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Ensure unique connections between two users
    __table_args__ = (
        # This ensures we don't have duplicate connections
        # between the same two users
        None,
    )
    
    # Relationships
    sender = relationship('User', foreign_keys=[user_id], overlaps="sent_connections")
    receiver = relationship('User', foreign_keys=[connected_user_id], overlaps="received_connections")

class FriendRequest(Base):
    __tablename__ = 'friend_requests'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='pending')  # pending, accepted, declined, withdrawn, cancelled
    message = Column(Text)  # Optional message with request
    created_at = Column(DateTime, default=datetime.now)
    responded_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    sender = relationship('User', foreign_keys=[sender_id], overlaps="sent_friend_requests,received_friend_requests")
    receiver = relationship('User', foreign_keys=[receiver_id], overlaps="sent_friend_requests,received_friend_requests")
    
    # Ensure unique requests between two users
    __table_args__ = (
        # This ensures we don't have duplicate requests
        # between the same two users
        None,
    )

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    location = Column(String(100))
    job_type = Column(String(50))  # full-time, part-time, contract, internship
    salary_range = Column(String(50))
    description = Column(Text)
    requirements = Column(Text)
    benefits = Column(Text)
    application_deadline = Column(DateTime)
    is_active = Column(Boolean, default=True)
    posted_at = Column(DateTime, default=datetime.now)
    posted_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    views_count = Column(Integer, default=0)
    applications_count = Column(Integer, default=0)
    
    # Relationships
    applications = relationship('JobApplication', backref='job', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'job_type': self.job_type,
            'salary_range': self.salary_range,
            'description': self.description,
            'requirements': self.requirements,
            'benefits': self.benefits,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'is_active': self.is_active,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'posted_by': self.posted_by,
            'views_count': self.views_count,
            'applications_count': self.applications_count,
            'status': 'active' if self.is_active else 'inactive',
            'created_at': self.posted_at.isoformat() if self.posted_at else None
        }

class JobApplication(Base):
    __tablename__ = 'job_applications'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    applicant_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    cover_letter = Column(Text)
    resume_path = Column(String(500))  # Path to uploaded resume file
    status = Column(String(50), default='pending')  # pending, reviewed, interview, rejected, hired
    applied_at = Column(DateTime, default=datetime.now)
    reviewed_at = Column(DateTime)
    notes = Column(Text)  # HR notes about the application
    hr_rating = Column(Integer)  # 1-5 rating from HR
    interview_scheduled = Column(DateTime)
    interview_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    applicant = relationship('User', backref='job_applications')
    # Note: 'job' relationship is created via backref from Job.applications
    
    # Ensure unique applications per user per job
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'reviewed', 'interview', 'rejected', 'hired')", name='valid_application_status'),
        CheckConstraint("hr_rating >= 1 AND hr_rating <= 5", name='valid_hr_rating'),
    )

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_type = Column(String(50))  # webinar, conference, meetup, workshop
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String(200))  # Physical or virtual location
    is_virtual = Column(Boolean, default=False)
    meeting_link = Column(String(500))  # For virtual events
    max_participants = Column(Integer)
    current_participants = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    organizer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    registration_required = Column(Boolean, default=False)

class EventRegistration(Base):
    __tablename__ = 'event_registrations'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    registration_date = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='registered')  # registered, attended, cancelled
    notes = Column(Text)

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50))  # connection, job, post, event, friend_request
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    related_id = Column(Integer)  # ID of related object (post, job, event, etc.)
    related_type = Column(String(50))  # Type of related object

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey('comments.id'))  # For nested comments
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)




class Inbox(Base):
    __tablename__ = 'inbox'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_type = Column(String(50), nullable=False)  # connection_request, message, notification
    item_id = Column(Integer, nullable=False)  # ID of the related item
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    read_at = Column(DateTime)
    
    # Relationships
    user = relationship('User', backref='inbox_items')


class MockInterviewSession(Base):
    __tablename__ = 'mock_interview_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_uuid = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_role = Column(String(200), nullable=False)
    job_desc = Column(Text, nullable=False)
    total_questions = Column(Integer, default=10, nullable=False)
    started_at = Column(DateTime, default=datetime.now, nullable=False)
    ended_at = Column(DateTime)
    
    # Detailed scoring breakdown
    score_overall = Column(Integer)  # Overall score out of 100
    score_accuracy = Column(Integer)  # Accuracy score out of 25
    score_clarity = Column(Integer)   # Clarity score out of 25
    score_relevance = Column(Integer) # Relevance score out of 25
    score_confidence = Column(Integer) # Confidence score out of 25
    
    # Performance grades
    overall_grade = Column(String(10), nullable=True)  # A+, A, B+, B, C+, C, D, F
    accuracy_grade = Column(String(10), nullable=True)
    clarity_grade = Column(String(10), nullable=True)
    relevance_grade = Column(String(10), nullable=True)
    confidence_grade = Column(String(10), nullable=True)
    
    # AI outputs
    feedback_summary = Column(Text)  # concise feedback paragraph
    detailed_feedback = Column(Text) # detailed feedback for each category
    suggestions_json = Column(Text)  # JSON array of suggestions
    transcript_json = Column(Text)   # JSON array of {q, a}
    
    # Enhanced AI report fields
    strengths_json = Column(Text)  # JSON array of strengths
    areas_for_improvement_json = Column(Text)  # JSON array of areas for improvement
    detailed_analysis_json = Column(Text)  # JSON object with category-wise analysis
    keywords_json = Column(Text)  # JSON array of keywords
    
    # Interview metadata
    interview_duration_minutes = Column(Integer, nullable=True)  # Duration in minutes
    questions_answered = Column(Integer, default=0)  # Number of questions actually answered
    confidence_level = Column(String(20), nullable=True)  # High, Medium, Low
    
    # Relationships
    user = relationship('User')
    turns = relationship('MockInterviewTurn', backref='session', lazy='selectin', cascade='all, delete-orphan')
    
    def set_suggestions(self, suggestions):
        try:
            self.suggestions_json = json.dumps(suggestions)
        except Exception:
            self.suggestions_json = None
    
    def set_transcript(self, transcript):
        try:
            self.transcript_json = json.dumps(transcript)
        except Exception:
            self.transcript_json = None
    
    def set_detailed_feedback(self, feedback_dict):
        try:
            self.detailed_feedback = json.dumps(feedback_dict)
        except Exception:
            self.detailed_feedback = None
    
    def set_strengths(self, strengths):
        try:
            self.strengths_json = json.dumps(strengths)
        except Exception:
            self.strengths_json = None
    
    def set_areas_for_improvement(self, areas):
        try:
            self.areas_for_improvement_json = json.dumps(areas)
        except Exception:
            self.areas_for_improvement_json = None
    
    def set_detailed_analysis(self, analysis):
        try:
            self.detailed_analysis_json = json.dumps(analysis)
        except Exception:
            self.detailed_analysis_json = None
    
    def set_keywords(self, keywords):
        try:
            self.keywords_json = json.dumps(keywords)
        except Exception:
            self.keywords_json = None
    
    def get_suggestions(self):
        try:
            return json.loads(self.suggestions_json) if self.suggestions_json else []
        except Exception:
            return []
    
    def get_transcript(self):
        try:
            return json.loads(self.transcript_json) if self.transcript_json else []
        except Exception:
            return []
    
    def get_detailed_feedback(self):
        try:
            return json.loads(self.detailed_feedback) if self.detailed_feedback else {}
        except Exception:
            return {}
    
    def get_strengths(self):
        try:
            return json.loads(self.strengths_json) if self.strengths_json else []
        except Exception:
            return []
    
    def get_areas_for_improvement(self):
        try:
            return json.loads(self.areas_for_improvement_json) if self.areas_for_improvement_json else []
        except Exception:
            return []
    
    def get_detailed_analysis(self):
        try:
            return json.loads(self.detailed_analysis_json) if self.detailed_analysis_json else {}
        except Exception:
            return {}
    
    def get_keywords(self):
        try:
            return json.loads(self.keywords_json) if self.keywords_json else []
        except Exception:
            return []
    
    def calculate_overall_score(self):
        """Calculate overall score based on individual scores"""
        scores = [self.score_accuracy, self.score_clarity, self.score_relevance, self.score_confidence]
        valid_scores = [s for s in scores if s is not None]
        if valid_scores:
            self.score_overall = sum(valid_scores)
        return self.score_overall
    
    def assign_grades(self):
        """Assign letter grades based on scores"""
        def score_to_grade(score):
            if score is None:
                return None
            if score >= 23: return 'A+'
            elif score >= 20: return 'A'
            elif score >= 18: return 'B+'
            elif score >= 15: return 'B'
            elif score >= 13: return 'C+'
            elif score >= 10: return 'C'
            elif score >= 8: return 'D'
            else: return 'F'
        
        self.accuracy_grade = score_to_grade(self.score_accuracy)
        self.clarity_grade = score_to_grade(self.score_clarity)
        self.relevance_grade = score_to_grade(self.score_relevance)
        self.confidence_grade = score_to_grade(self.score_confidence)
        
        # Overall grade based on total score
        if self.score_overall:
            if self.score_overall >= 90: self.overall_grade = 'A+'
            elif self.score_overall >= 80: self.overall_grade = 'A'
            elif self.score_overall >= 70: self.overall_grade = 'B+'
            elif self.score_overall >= 60: self.overall_grade = 'B'
            elif self.score_overall >= 50: self.overall_grade = 'C+'
            elif self.score_overall >= 40: self.score_overall = 'C'
            elif self.score_overall >= 30: self.score_overall = 'D'
            else: self.overall_grade = 'F'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'session_uuid': self.session_uuid,
            'user_id': self.user_id,
            'job_role': self.job_role,
            'job_desc': self.job_desc,
            'total_questions': self.total_questions,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'score_overall': self.score_overall,
            'score_accuracy': self.score_accuracy,
            'score_clarity': self.score_clarity,
            'score_relevance': self.score_relevance,
            'score_confidence': self.score_confidence,
            'overall_grade': self.overall_grade,
            'accuracy_grade': self.accuracy_grade,
            'clarity_grade': self.clarity_grade,
            'relevance_grade': self.relevance_grade,
            'confidence_grade': self.confidence_grade,
            'feedback_summary': self.feedback_summary,
            'detailed_feedback': self.get_detailed_feedback(),
            'suggestions': self.get_suggestions(),
            'transcript': self.get_transcript(),
            'interview_duration_minutes': self.interview_duration_minutes,
            'questions_answered': self.questions_answered,
            'confidence_level': self.confidence_level
        }


class MockInterviewTurn(Base):
    __tablename__ = 'mock_interview_turns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('mock_interview_sessions.id'), nullable=False, index=True)
    turn_number = Column(Integer, nullable=False)  # 1..10
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)


class ResumeTestResult(Base):
    __tablename__ = 'resume_test_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    filepath = Column(String(1000), nullable=False)
    job_title = Column(String(500), nullable=True)
    company = Column(String(500), nullable=True)
    
    # Detailed scores for each category
    content_quality_score = Column(Integer, nullable=False)
    content_quality_explanation = Column(Text, nullable=False)
    skills_match_score = Column(Integer, nullable=False)
    skills_match_explanation = Column(Text, nullable=False)
    experience_achievements_score = Column(Integer, nullable=False)
    experience_achievements_explanation = Column(Text, nullable=False)
    format_structure_score = Column(Integer, nullable=False)
    format_structure_explanation = Column(Text, nullable=False)
    education_certifications_score = Column(Integer, nullable=False)
    education_certifications_explanation = Column(Text, nullable=False)
    
    # Overall score and metadata
    total_score = Column(Integer, nullable=False)
    overall_grade = Column(String(10), nullable=True)  # A+, A, B+, B, C+, C, D, F
    strengths = Column(Text, nullable=True)  # JSON string of strengths
    areas_for_improvement = Column(Text, nullable=True)  # JSON string of improvements
    recommendations = Column(Text, nullable=True)  # JSON string of recommendations
    
    # Analysis metadata
    analysis_timestamp = Column(DateTime, default=datetime.now, nullable=False)
    api_version = Column(String(20), default='1.0', nullable=True)
    model_used = Column(String(100), default='gemini-2.0-flash-exp', nullable=True)
    analysis_duration_ms = Column(Integer, nullable=True)
    
    # File metadata
    file_size = Column(Integer, nullable=True)  # File size in bytes
    file_type = Column(String(50), nullable=True)  # PDF, DOCX, etc.
    
    # Relationships
    user = relationship('User', backref='resume_test_results')


class ResumeathonParticipant(Base):
    __tablename__ = 'resumeathon_participants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    resume_test_result_id = Column(Integer, ForeignKey('resume_test_results.id'), nullable=False, index=True)
    joined_at = Column(DateTime, default=datetime.now, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship('User', backref='resumeathon_participations')
    resume_test_result = relationship('ResumeTestResult', backref='resumeathon_participations')
    
    def __repr__(self):
        return f"<ResumeathonParticipant(id={self.id}, user_id={self.user_id}, score={self.resume_test_result.total_score if self.resume_test_result else 'N/A'})>"
    
    def set_strengths(self, strengths_list):
        """Set strengths as JSON string"""
        try:
            self.strengths = json.dumps(strengths_list)
        except Exception:
            self.strengths = None
    
    def set_areas_for_improvement(self, improvements_list):
        """Set areas for improvement as JSON string"""
        try:
            self.areas_for_improvement = json.dumps(improvements_list)
        except Exception:
            self.areas_for_improvement = None
    
    def set_recommendations(self, recommendations_list):
        """Set recommendations as JSON string"""
        try:
            self.recommendations = json.dumps(recommendations_list)
        except Exception:
            self.recommendations = None
    
    def get_strengths(self):
        """Get strengths as list"""
        try:
            return json.loads(self.strengths) if self.strengths else []
        except Exception:
            return []
    
    def get_areas_for_improvement(self):
        """Get areas for improvement as list"""
        try:
            return json.loads(self.areas_for_improvement) if self.areas_for_improvement else []
        except Exception:
            return []
    
    def get_recommendations(self):
        """Get recommendations as list"""
        try:
            return json.loads(self.recommendations) if self.recommendations else []
        except Exception:
            return []
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'filepath': self.filepath,
            'job_title': self.job_title,
            'company': self.company,
            'content_quality_score': self.content_quality_score,
            'content_quality_explanation': self.content_quality_explanation,
            'skills_match_score': self.skills_match_score,
            'skills_match_explanation': self.skills_match_explanation,
            'experience_achievements_score': self.experience_achievements_score,
            'experience_achievements_explanation': self.experience_achievements_explanation,
            'format_structure_score': self.format_structure_score,
            'format_structure_explanation': self.format_structure_explanation,
            'education_certifications_score': self.education_certifications_score,
            'education_certifications_explanation': self.education_certifications_explanation,
            'total_score': self.total_score,
            'overall_grade': self.overall_grade,
            'strengths': self.get_strengths(),
            'areas_for_improvement': self.get_areas_for_improvement(),
            'recommendations': self.get_recommendations(),
            'analysis_timestamp': self.analysis_timestamp.isoformat() if self.analysis_timestamp else None,
            'api_version': self.api_version,
            'model_used': self.model_used,
            'analysis_duration_ms': self.analysis_duration_ms,
            'file_size': self.file_size,
            'file_type': self.file_type
        }

class Streak(Base):
    __tablename__ = 'streaks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False, default='general')  # general, coding, networking, etc.
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    user = relationship('User', backref='streaks')
    
    def __repr__(self):
        return f"<Streak(user_id={self.user_id}, activity_type='{self.activity_type}', current_streak={self.current_streak})>"
    
    def to_dict(self):
        """Convert streak object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class StreakLog(Base):
    __tablename__ = 'streak_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)
    activity_date = Column(DateTime, default=datetime.now, nullable=False)
    description = Column(String(200), nullable=True)
    
    # Relationships
    user = relationship('User', backref='streak_logs')
    
    def __repr__(self):
        return f"<StreakLog(user_id={self.user_id}, activity_type='{self.activity_type}', date='{self.activity_date}')>"
    
    def to_dict(self):
        """Convert streak log object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'activity_date': self.activity_date.isoformat(),
            'description': self.description
        }

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    sender = relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    
    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id}, content='{self.content[:50]}...')>"
    
    def to_dict(self):
        """Convert message object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'sender': self.sender.to_dict() if self.sender else None,
            'receiver': self.receiver.to_dict() if self.receiver else None
        }

class Workshop(Base):
    __tablename__ = 'workshops'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    instructor = Column(String(100), nullable=False)
    instructor_email = Column(String(120), nullable=True)
    instructor_bio = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # technical, soft-skills, career, etc.
    level = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    duration_hours = Column(Integer, nullable=False)  # Duration in hours
    max_participants = Column(Integer, nullable=True)  # NULL means unlimited
    price = Column(Integer, nullable=False, default=0)  # Price in cents (0 = free)
    currency = Column(String(3), nullable=False, default='USD')
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String(200), nullable=True)  # Physical location or "Online"
    is_online = Column(Boolean, default=False, nullable=False)
    meeting_link = Column(String(500), nullable=True)  # For online workshops
    materials = Column(Text, nullable=True)  # JSON string of required materials
    prerequisites = Column(Text, nullable=True)  # JSON string of prerequisites
    learning_objectives = Column(Text, nullable=True)  # JSON string of objectives
    status = Column(String(20), default='draft', nullable=False)  # draft, published, cancelled, completed
    approval_status = Column(String(20), default='pending', nullable=False)  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_workshops")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_workshops")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'instructor': self.instructor,
            'instructor_email': self.instructor_email,
            'instructor_bio': self.instructor_bio,
            'category': self.category,
            'level': self.level,
            'duration_hours': self.duration_hours,
            'max_participants': self.max_participants,
            'price': self.price,
            'currency': self.currency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location': self.location,
            'is_online': self.is_online,
            'meeting_link': self.meeting_link,
            'materials': json.loads(self.materials) if self.materials else [],
            'prerequisites': json.loads(self.prerequisites) if self.prerequisites else [],
            'learning_objectives': json.loads(self.learning_objectives) if self.learning_objectives else [],
            'status': self.status,
            'approval_status': self.approval_status,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejection_reason': self.rejection_reason,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'creator': self.creator.to_dict() if self.creator else None,
            'approver': self.approver.to_dict() if self.approver else None
        }

class WorkshopRegistration(Base):
    __tablename__ = 'workshop_registrations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workshop_id = Column(Integer, ForeignKey('workshops.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    registration_date = Column(DateTime, default=datetime.now, nullable=False)
    status = Column(String(20), default='registered', nullable=False)  # registered, cancelled, completed
    payment_status = Column(String(20), default='pending', nullable=False)  # pending, paid, refunded
    payment_amount = Column(Integer, nullable=True)  # Amount paid in cents
    notes = Column(Text, nullable=True)
    
    # Relationships
    workshop = relationship("Workshop", backref="registrations")
    user = relationship("User", backref="workshop_registrations")
    
    def to_dict(self):
        return {
            'id': self.id,
            'workshop_id': self.workshop_id,
            'user_id': self.user_id,
            'registration_date': self.registration_date.isoformat(),
            'status': self.status,
            'payment_status': self.payment_status,
            'payment_amount': self.payment_amount,
            'notes': self.notes,
            'workshop': self.workshop.to_dict() if self.workshop else None,
            'user': self.user.to_dict() if self.user else None
        }

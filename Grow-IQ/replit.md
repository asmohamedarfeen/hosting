# Professional Dashboard Application

## Overview

This is a professional networking dashboard application built with Flask that provides social media-like functionality for professional connections. The application features user profiles, post sharing, job listings, connection management, and messaging capabilities. It serves as a LinkedIn-inspired platform where users can build professional networks, share updates, discover job opportunities, and manage their professional presence.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM for database operations
- **Database**: SQLite for development with configurable PostgreSQL support via environment variables
- **Authentication**: Session-based authentication with werkzeug password hashing
- **File Handling**: Local file upload system for profile images and post attachments with configurable upload limits (16MB max)

### Frontend Architecture
- **Template Engine**: Jinja2 templating with modular template inheritance
- **Styling**: Custom CSS with CSS variables for theming and responsive design
- **JavaScript**: Vanilla JavaScript for interactive features like sidebar navigation, theme switching, and dynamic content loading
- **Icons**: Font Awesome integration for consistent iconography

### Data Model Design
The application uses a relational database structure with four main entities:
- **User Model**: Stores user profiles with professional information (title, company, bio, location)
- **Post Model**: Handles content sharing with support for text and images, including engagement metrics
- **Connection Model**: Manages professional relationships with status tracking (pending, accepted, declined)
- **Job Model**: Job listings with detailed information and active status management

### Configuration Management
- Environment-based configuration for database URLs and session secrets
- Configurable upload directories with automatic creation
- Database connection pooling with health checks and recycling
- WSGI proxy fix for deployment behind reverse proxies

### Security Features
- Secure filename handling for file uploads
- Password hashing using werkzeug security utilities
- Session management with configurable secret keys
- File type validation for uploaded content

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and core application structure
- **SQLAlchemy**: Database ORM and connection management
- **Werkzeug**: Security utilities and WSGI middleware
- **Flask-Login**: User session management (imported but not fully implemented)

### Frontend Dependencies
- **Font Awesome**: Icon library for UI elements
- **Custom CSS Framework**: Built-in responsive design system with dark/light theme support

### Database Support
- **SQLite**: Default development database
- **PostgreSQL**: Production database option via DATABASE_URL environment variable

### Development Tools
- **Flask Debug Mode**: Development server with hot reloading
- **Logging**: Built-in Python logging for debugging and monitoring

The application is designed to be easily deployable with minimal external dependencies while maintaining professional-grade features and scalability options.
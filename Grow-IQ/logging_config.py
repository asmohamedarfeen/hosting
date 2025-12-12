import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from config import settings

class CustomFormatter(logging.Formatter):
    """Custom log formatter with colors and structured output"""
    
    # Color codes for terminal output
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add timestamp
        record.timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Add color for terminal output
        if hasattr(record, 'color') and record.color:
            level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        return super().format(record)

def setup_logging():
    """Setup comprehensive logging configuration"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    console_formatter = CustomFormatter(
        fmt='%(timestamp)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter.color = True
    console_handler.setFormatter(console_formatter)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        filename=logs_dir / "qrowiq.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    file_formatter = CustomFormatter(
        fmt='%(timestamp)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_formatter.color = False
    file_handler.setFormatter(file_formatter)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        filename=logs_dir / "errors.log",
        maxBytes=5*1024*1024,   # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # Security events handler
    security_handler = logging.handlers.RotatingFileHandler(
        filename=logs_dir / "security.log",
        maxBytes=5*1024*1024,   # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    security_handler.setLevel(logging.WARNING)
    security_formatter = CustomFormatter(
        fmt='%(timestamp)s - SECURITY - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    security_formatter.color = False
    security_handler.setFormatter(security_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(security_handler)
    
                    # Set specific logger levels
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('watchfiles').setLevel(logging.ERROR)  # Suppress file watching debug messages
    
    # Create application logger
    app_logger = logging.getLogger('qrowiq')
    app_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    return app_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(f'qrowiq.{name}')

class SecurityLogger:
    """Specialized logger for security events"""
    
    def __init__(self):
        self.logger = logging.getLogger('qrowiq.security')
    
    def log_login_attempt(self, username: str, ip_address: str, success: bool, details: str = ""):
        """Log login attempts"""
        level = logging.INFO if success else logging.WARNING
        message = f"Login {'SUCCESS' if success else 'FAILED'} - User: {username}, IP: {ip_address}"
        if details:
            message += f" - Details: {details}"
        self.logger.log(level, message)
    
    def log_suspicious_activity(self, activity_type: str, ip_address: str, details: str):
        """Log suspicious activities"""
        message = f"SUSPICIOUS ACTIVITY - Type: {activity_type}, IP: {ip_address}, Details: {details}"
        self.logger.warning(message)
    
    def log_rate_limit_exceeded(self, ip_address: str, endpoint: str):
        """Log rate limit violations"""
        message = f"RATE LIMIT EXCEEDED - IP: {ip_address}, Endpoint: {endpoint}"
        self.logger.warning(message)
    
    def log_file_upload(self, filename: str, user_id: int, file_size: int, success: bool):
        """Log file uploads"""
        level = logging.INFO if success else logging.ERROR
        message = f"File Upload {'SUCCESS' if success else 'FAILED'} - File: {filename}, User: {user_id}, Size: {file_size} bytes"
        self.logger.log(level, message)

class PerformanceLogger:
    """Specialized logger for performance monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger('qrowiq.performance')
    
    def log_request_time(self, endpoint: str, method: str, duration: float, status_code: int):
        """Log request performance"""
        level = logging.WARNING if duration > 1.0 else logging.DEBUG
        message = f"Request: {method} {endpoint} - Duration: {duration:.3f}s - Status: {status_code}"
        self.logger.log(level, message)
    
    def log_database_query(self, query: str, duration: float):
        """Log database query performance"""
        level = logging.WARNING if duration > 0.5 else logging.DEBUG
        message = f"Database Query - Duration: {duration:.3f}s - Query: {query[:100]}..."
        self.logger.log(level, message)
    
    def log_memory_usage(self, memory_mb: float):
        """Log memory usage"""
        level = logging.WARNING if memory_mb > 500 else logging.DEBUG
        message = f"Memory Usage: {memory_mb:.1f} MB"
        self.logger.log(level, message)

# Initialize logging
app_logger = setup_logging()
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()

# Convenience function for backward compatibility
def get_logger(name: str = None) -> logging.Logger:
    """Get logger instance (backward compatibility)"""
    if name:
        return logging.getLogger(f'qrowiq.{name}')
    return app_logger

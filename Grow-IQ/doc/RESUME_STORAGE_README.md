# Resume Storage System Documentation

## Overview

The Resume Storage System has been enhanced to store both resume test results in the database and actual resume files in a organized folder structure. This system ensures that total marks are properly stored and resumes are securely saved for future reference.

## Features

### 🔐 **Database Storage**
- **Total Score Storage**: All resume test scores are stored in the `resume_test_results` table
- **Detailed Scoring**: Individual category scores with explanations
- **Performance Metrics**: Overall grade, strengths, improvements, and recommendations
- **User Association**: Each result is linked to the user who uploaded the resume
- **Metadata Tracking**: Analysis timestamp, API version, model used, and analysis duration

### 📁 **File Storage**
- **Organized Structure**: Resumes stored in `resume_data/` folder
- **User Separation**: Each user gets their own subfolder (`user_{user_id}/`)
- **Unique Naming**: Files are renamed with timestamps to prevent conflicts
- **Original Format**: PDF files are preserved in their original format

## Database Schema

### ResumeTestResult Table
```sql
CREATE TABLE resume_test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename VARCHAR(500) NOT NULL,
    filepath VARCHAR(1000) NOT NULL,
    job_title VARCHAR(500),
    company VARCHAR(500),
    
    -- Category Scores
    content_quality_score INTEGER NOT NULL,
    content_quality_explanation TEXT NOT NULL,
    skills_match_score INTEGER NOT NULL,
    skills_match_explanation TEXT NOT NULL,
    experience_achievements_score INTEGER NOT NULL,
    experience_achievements_explanation TEXT NOT NULL,
    format_structure_score INTEGER NOT NULL,
    format_structure_explanation TEXT NOT NULL,
    education_certifications_score INTEGER NOT NULL,
    education_certifications_explanation TEXT NOT NULL,
    
    -- Overall Results
    total_score INTEGER NOT NULL,
    overall_grade VARCHAR(10),
    strengths TEXT,
    areas_for_improvement TEXT,
    recommendations TEXT,
    
    -- Metadata
    analysis_timestamp DATETIME NOT NULL,
    api_version VARCHAR(20),
    model_used VARCHAR(100),
    analysis_duration_ms INTEGER,
    file_size INTEGER,
    file_type VARCHAR(50)
);
```

## API Endpoints

### 1. **Score Resume** - `POST /resume-tester/score-resume`
Uploads and scores a resume, storing both the file and results.

**Request:**
```http
POST /resume-tester/score-resume
Content-Type: multipart/form-data

file: [PDF file]
```

**Response:**
```json
{
    "labels": ["Content Quality", "Skills Match", "Experience & Achievements", "Format & Structure", "Education & Certifications"],
    "scores": [23, 21, 19, 14, 8],
    "explanations": ["...", "...", "...", "...", "..."],
    "total_score": 85,
    "metadata": {
        "analysis_duration": 1250,
        "user_id": 123,
        "user_name": "John Doe"
    },
    "db_result_id": 456,
    "json_file_path": "/path/to/scores.json"
}
```

### 2. **List User Resumes** - `GET /resume-tester/resumes`
Retrieves all resume test results for the current user.

**Response:**
```json
{
    "resumes": [
        {
            "id": 456,
            "filename": "resume.pdf",
            "total_score": 85,
            "overall_grade": "A",
            "analysis_timestamp": "2024-01-15T10:30:00",
            "category_scores": {
                "content_quality": 23,
                "skills_match": 21,
                "experience_achievements": 19,
                "format_structure": 14,
                "education_certifications": 8
            },
            "resume_filepath": "/path/to/resume_data/user_123/resume_20240115_103000.pdf"
        }
    ],
    "total_resumes": 1,
    "user_id": 123
}
```

### 3. **Get Resume Detail** - `GET /resume-tester/resume/{result_id}`
Retrieves detailed information about a specific resume test result.

### 4. **Download Resume** - `GET /resume-tester/download-resume/{result_id}`
Downloads the actual resume file.

### 5. **Get Statistics** - `GET /resume-tester/stats`
Retrieves statistics about resume testing for the current user.

**Response:**
```json
{
    "total_resumes": 5,
    "average_score": 78.4,
    "best_score": 92,
    "worst_score": 65,
    "grade_distribution": {
        "A": 2,
        "B": 2,
        "C": 1
    },
    "total_files_size": 2048576,
    "recent_activity": {
        "last_test": "2024-01-15T10:30:00",
        "first_test": "2024-01-10T14:20:00"
    }
}
```

## File Structure

```
resume_data/
├── user_123/
│   ├── resume_20240115_103000.pdf
│   ├── resume_20240112_091500.pdf
│   └── resume_20240110_142000.pdf
├── user_456/
│   ├── resume_20240114_160000.pdf
│   └── resume_20240113_110000.pdf
└── ...
```

## Implementation Details

### File Storage Process
1. **Upload**: Resume file is uploaded via the API
2. **Analysis**: File is temporarily saved for ATS scoring
3. **Storage**: Original file is saved to `resume_data/user_{id}/` folder
4. **Database**: Test results and file path are stored in database
5. **Cleanup**: Temporary analysis file is removed

### Score Calculation
- **Content Quality**: 25 points
- **Skills Match**: 25 points  
- **Experience & Achievements**: 25 points
- **Format & Structure**: 15 points
- **Education & Certifications**: 10 points
- **Total**: 100 points

### Grade Assignment
- **A+**: 90-100 points
- **A**: 85-89 points
- **A-**: 80-84 points
- **B+**: 75-79 points
- **B**: 70-74 points
- **B-**: 65-69 points
- **C+**: 60-64 points
- **C**: 55-59 points
- **C-**: 50-54 points
- **D**: Below 50 points

## Security Features

- **User Isolation**: Each user can only access their own resumes
- **File Validation**: Only PDF files are accepted
- **Path Sanitization**: File paths are validated to prevent directory traversal
- **Authentication Required**: All endpoints require user authentication

## Error Handling

- **File Upload Errors**: Proper error messages for unsupported file types
- **Storage Errors**: Graceful handling of disk space issues
- **Database Errors**: Transaction rollback on database failures
- **File Not Found**: 404 errors for missing files

## Testing

Run the test script to verify the system:
```bash
python test_resume_storage.py
```

This will test:
- Database connection and table structure
- Resume data folder creation
- Sample data handling

## Usage Examples

### Python Client Example
```python
import requests

# Upload and score resume
with open('resume.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/resume-tester/score-resume', 
                           files=files, 
                           headers={'Authorization': 'Bearer your_token'})
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total Score: {result['total_score']}")
        print(f"Grade: {result.get('overall_grade', 'N/A')}")

# Get user's resume list
response = requests.get('http://localhost:8000/resume-tester/resumes',
                       headers={'Authorization': 'Bearer your_token'})
resumes = response.json()['resumes']
```

### JavaScript Client Example
```javascript
// Upload resume
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/resume-tester/score-resume', {
    method: 'POST',
    body: formData,
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
.then(response => response.json())
.then(data => {
    console.log(`Total Score: ${data.total_score}`);
    console.log(`Grade: ${data.overall_grade}`);
});
```

## Troubleshooting

### Common Issues

1. **File Not Saved**: Check if `resume_data` folder has write permissions
2. **Database Errors**: Verify database connection and table structure
3. **Score Not Stored**: Check if `total_score` calculation is working
4. **File Download Fails**: Verify file path exists and is accessible

### Debug Logging

Enable debug logging to see detailed information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **File Compression**: Compress old resumes to save disk space
- **Backup System**: Automated backup of resume files
- **Search Indexing**: Full-text search within resume content
- **Version Control**: Track multiple versions of the same resume
- **Analytics Dashboard**: Visual representation of testing trends

## Support

For issues or questions about the Resume Storage System, check the logs in the `logs/` directory or contact the development team.

# 🎯 Job Recommendation System

A sophisticated, AI-powered job recommendation engine that analyzes user profiles and suggests relevant job opportunities based on multiple intelligent factors.

## ✨ Features

### 🧠 **Intelligent Matching Algorithm**
- **Title Similarity**: Uses TF-IDF vectorization and cosine similarity to match job titles
- **Skills Analysis**: Analyzes user skills against job requirements for optimal matching
- **Location Compatibility**: Smart location matching including remote work support
- **Experience Level**: Maps user experience to appropriate job levels

### 📊 **Multi-Factor Scoring System**
- **Title Match**: 35% weight - Core job function alignment
- **Skills Match**: 25% weight - Technical and soft skills compatibility
- **Location Match**: 20% weight - Geographic and remote work preferences
- **Experience Match**: 20% weight - Career level appropriateness

### 🎨 **Beautiful UI Components**
- **Gradient Design**: Modern, eye-catching recommendation cards
- **Profile Analysis**: Visual metrics showing profile completeness and recommendation potential
- **Smart Notifications**: Contextual reasons for each recommendation
- **Responsive Design**: Mobile-friendly interface

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_ml.txt
```

### 2. Test the System
```bash
python test_recommendations.py
```

### 3. Start the Application
```bash
python app.py
```

## 📁 File Structure

```
├── job_recommendations.py          # Core recommendation engine
├── job_recommendation_routes.py    # API endpoints
├── templates/home.html             # Frontend integration
├── requirements_ml.txt             # ML dependencies
├── test_recommendations.py         # Test script
└── JOB_RECOMMENDATION_README.md   # This documentation
```

## 🔧 API Endpoints

### Get Job Recommendations
```http
GET /api/recommendations/jobs?limit=10
```
**Response:**
```json
{
  "success": true,
  "message": "Generated 10 job recommendations",
  "recommendations": [
    {
      "id": 1,
      "title": "Senior Software Engineer",
      "company": "TechCorp",
      "location": "San Francisco, CA",
      "recommendation_score": 0.85,
      "why_recommended": "Your job title closely matches this position. Your skills align well with the job requirements.",
      "score_breakdown": {
        "title_similarity": 0.9,
        "skills_match": 0.8,
        "location_match": 0.7,
        "experience_match": 0.9
      }
    }
  ]
}
```

### Analyze User Profile
```http
GET /api/recommendations/jobs/analyze-profile
```
**Response:**
```json
{
  "success": true,
  "profile_analysis": {
    "job_title": "Software Engineer",
    "job_categories": ["software_engineering"],
    "experience_level": "mid",
    "profile_completeness": {
      "completeness_percentage": 75.0,
      "missing_fields": ["industry", "bio"]
    },
    "recommendation_potential": {
      "score": 80,
      "recommendation": "Good profile! You'll receive relevant recommendations, but consider adding more details."
    }
  }
}
```

### Get Similar Jobs
```http
GET /api/recommendations/jobs/similar?job_title=Software Engineer&limit=5
```

### Get Trending Jobs
```http
GET /api/recommendations/jobs/trending?limit=10
```

## 🧮 How It Works

### 1. **Profile Analysis**
The system analyzes user profiles using:
- **Job Title Categorization**: Maps titles to predefined categories (software_engineering, data_science, design, etc.)
- **Experience Level Extraction**: Identifies entry, mid, senior, or executive levels
- **Skills Parsing**: Extracts and normalizes user skills from various formats

### 2. **Job Matching**
For each available job, the system calculates:
- **Title Similarity**: TF-IDF vectorization with cosine similarity
- **Skills Match**: Percentage of user skills found in job requirements
- **Location Match**: Geographic compatibility and remote work support
- **Experience Match**: Level appropriateness based on years of experience

### 3. **Scoring & Ranking**
Jobs are scored using weighted factors and ranked by overall recommendation score.

### 4. **Reason Generation**
Human-readable explanations are generated for each recommendation based on score breakdowns.

## 🎨 Frontend Integration

### CSS Classes
- `.job-recommendations-section` - Main container with gradient background
- `.recommendation-card` - Individual job recommendation cards
- `.recommendation-score` - Match percentage display
- `.profile-analysis-summary` - Profile completeness metrics

### JavaScript Functions
- `loadJobRecommendations()` - Fetches and displays recommendations
- `displayJobRecommendations(recommendations)` - Renders recommendation cards
- `loadProfileAnalysis()` - Shows profile analysis and metrics
- `refreshJobRecommendations()` - Reloads recommendations

## 🔍 Job Categories

The system recognizes these job categories:

| Category | Keywords |
|----------|----------|
| **Software Engineering** | software engineer, developer, programmer, full stack, frontend, backend |
| **Data Science** | data scientist, data analyst, machine learning, AI, statistician |
| **Design** | designer, UI/UX, graphic designer, product designer, creative director |
| **Product Management** | product manager, product owner, program manager, scrum master |
| **Marketing** | marketing, digital marketing, social media, SEO, brand manager |
| **Sales** | sales, account executive, business development, sales manager |
| **Finance** | financial analyst, accountant, controller, CFO, investment analyst |
| **HR** | HR, human resources, recruiter, talent acquisition, people operations |
| **Operations** | operations, supply chain, logistics, project manager, business analyst |

## 📊 Experience Levels

| Level | Keywords | Years Experience |
|-------|----------|------------------|
| **Entry** | junior, entry, associate, assistant, trainee, intern | 0-2 years |
| **Mid** | mid, intermediate, experienced | 2-5 years |
| **Senior** | senior, lead, principal, staff, architect | 5-10 years |
| **Executive** | manager, director, VP, head, chief, executive | 10+ years |

## 🛠️ Customization

### Adding New Job Categories
```python
# In job_recommendations.py
self.job_categories['new_category'] = [
    'keyword1', 'keyword2', 'keyword3'
]
```

### Adjusting Scoring Weights
```python
# In calculate_overall_score method
weights = {
    'title': 0.40,      # Increase title importance
    'skills': 0.30,     # Adjust skills weight
    'location': 0.15,   # Reduce location importance
    'experience': 0.15  # Reduce experience importance
}
```

### Custom Similarity Functions
```python
def custom_similarity_function(self, user_data, job_data):
    # Implement your custom logic
    return custom_score
```

## 🧪 Testing

### Run All Tests
```bash
python test_recommendations.py
```

### Test Individual Components
```python
from job_recommendations import JobRecommendationEngine

engine = JobRecommendationEngine()

# Test title categorization
categories = engine.categorize_job_title("Senior Software Engineer")
print(categories)  # ['software_engineering']

# Test similarity calculation
similarity = engine.calculate_title_similarity("Developer", "Software Engineer")
print(similarity)  # 0.0 to 1.0
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements_ml.txt
   ```

2. **Memory Issues with Large Datasets**
   - Reduce `max_features` in TF-IDF vectorizer
   - Implement pagination for recommendations

3. **Slow Performance**
   - Cache recommendation results
   - Use background tasks for heavy computations

4. **No Recommendations**
   - Check user profile completeness
   - Verify job data exists in database
   - Check API endpoint accessibility

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 Future Enhancements

### Planned Features
- **Machine Learning Models**: Train on historical application data
- **Collaborative Filtering**: "Users like you also applied to..."
- **Real-time Updates**: Live recommendation updates
- **A/B Testing**: Test different recommendation algorithms
- **Analytics Dashboard**: Track recommendation effectiveness

### Integration Possibilities
- **Email Notifications**: Daily/weekly recommendation digests
- **Mobile App**: Push notifications for new matches
- **Chatbot**: Interactive job search assistance
- **External APIs**: Integrate with job boards (Indeed, LinkedIn)

## 📈 Performance Metrics

### Key Performance Indicators
- **Recommendation Click-through Rate**
- **Application Conversion Rate**
- **User Satisfaction Scores**
- **Profile Completion Rates**
- **Recommendation Relevance Scores**

### Monitoring
```python
# Log recommendation performance
logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
logger.info(f"Average recommendation score: {avg_score:.3f}")
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Implement your changes**
4. **Add tests**
5. **Submit a pull request**

## 📄 License

This project is part of the CareerConnect platform. See the main LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check this documentation
2. Run the test script
3. Review the logs
4. Create an issue with detailed information

---

**🎯 The Job Recommendation System transforms job searching from a manual process to an intelligent, personalized experience that grows smarter with every interaction.**

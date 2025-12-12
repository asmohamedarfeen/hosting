import os
import tempfile
import json
import logging
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from auth_utils import get_current_user
from models import User, ResumeTestResult, ResumeathonParticipant
from resume_tester.ats_resume_scorer import ATSResumeScorer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/resume-tester", tags=["Resume Tester"])

# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Templates for resume tester
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# API key for Google Gemini (should be moved to environment variable in production)
API_KEY = "AIzaSyA3f8izcUDNQTik3utegfZ5bKvxeG0vwq8"

# Create scores directory if it doesn't exist
SCORES_DIR = os.path.join(BASE_DIR, "resume_tester", "scores")
os.makedirs(SCORES_DIR, exist_ok=True)

# Create resume_data directory if it doesn't exist
RESUME_DATA_DIR = os.path.join(BASE_DIR, "resume_data")
os.makedirs(RESUME_DATA_DIR, exist_ok=True)

def save_resume_to_folder(file_content: bytes, filename: str, user_id: int) -> str:
    """Save uploaded resume to resume_data folder with user-specific organization"""
    try:
        # Create user-specific subfolder
        user_folder = os.path.join(RESUME_DATA_DIR, f"user_{user_id}")
        os.makedirs(user_folder, exist_ok=True)
        
        # Create timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate unique filename
        base_name = os.path.splitext(filename)[0]
        extension = os.path.splitext(filename)[1]
        unique_filename = f"{base_name}_{timestamp}{extension}"
        
        # Save file to user folder
        file_path = os.path.join(user_folder, unique_filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Resume saved to: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving resume to folder: {str(e)}")
        return None

def save_scores_to_json(data, filename):
    """Save scores data to a JSON file"""
    try:
        # Create timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create scores data with additional metadata
        scores_data = {
            "analysis_timestamp": datetime.now().isoformat(),
            "resume_filename": filename,
            "total_score": data.get('total_score', 0),
            "category_scores": {
                "content_quality": {
                    "score": data.get('scores', [0])[0],
                    "max_score": 25,
                    "explanation": data.get('explanations', [''])[0]
                },
                "skills_match": {
                    "score": data.get('scores', [0, 0])[1],
                    "max_score": 25,
                    "explanation": data.get('explanations', ['', ''])[1]
                },
                "experience_achievements": {
                    "score": data.get('scores', [0, 0, 0])[2],
                    "max_score": 25,
                    "explanation": data.get('explanations', ['', '', ''])[2]
                },
                "format_structure": {
                    "score": data.get('scores', [0, 0, 0, 0])[3],
                    "max_score": 15,
                    "explanation": data.get('explanations', ['', '', '', ''])[3]
                },
                "education_certifications": {
                    "score": data.get('scores', [0, 0, 0, 0, 0])[4],
                    "max_score": 10,
                    "explanation": data.get('explanations', ['', '', '', '', ''])[4]
                }
            },
            "performance_summary": {
                "overall_grade": get_performance_grade(data.get('total_score', 0)),
                "strengths": identify_strengths(data.get('scores', [])),
                "improvements": identify_improvements(data.get('scores', [])),
                "recommendations": generate_recommendations(data.get('scores', []))
            },
            "metadata": {
                "api_version": "1.0",
                "model_used": "gemini-2.0-flash-exp",
                "analysis_duration_ms": data.get('metadata', {}).get('analysis_duration', 0)
            }
        }
        
        # Create filename with timestamp
        json_filename = f"resume_scores_{timestamp}_{filename.replace('.pdf', '')}.json"
        json_filepath = os.path.join(SCORES_DIR, json_filename)
        
        # Save to JSON file
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(scores_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Scores saved to: {json_filepath}")
        return json_filepath
        
    except Exception as e:
        logger.error(f"Error saving scores to JSON: {str(e)}")
        return None


def save_resume_test_to_db(data, filename, resume_filepath, user_id, job_title=None, company=None, db=None):
    """Save resume test results to database"""
    try:
        if not db:
            logger.error("Database session not provided")
            return None
        
        # Extract scores and explanations
        scores = data.get('scores', [0, 0, 0, 0, 0])
        explanations = data.get('explanations', ['', '', '', '', ''])
        total_score = data.get('total_score', 0)
        
        # Ensure total_score is properly calculated if not provided
        if total_score == 0 and scores:
            total_score = sum(scores)
        
        logger.info(f"Saving resume test result - Total Score: {total_score}, Scores: {scores}")
        
        # Create new resume test result
        resume_result = ResumeTestResult(
            user_id=user_id,
            filename=filename,
            filepath=resume_filepath,  # Store the actual resume file path
            job_title=job_title,
            company=company,
            content_quality_score=scores[0] if len(scores) > 0 else 0,
            content_quality_explanation=explanations[0] if len(explanations) > 0 else '',
            skills_match_score=scores[1] if len(scores) > 1 else 0,
            skills_match_explanation=explanations[1] if len(explanations) > 1 else '',
            experience_achievements_score=scores[2] if len(scores) > 2 else 0,
            experience_achievements_explanation=explanations[2] if len(explanations) > 2 else '',
            format_structure_score=scores[3] if len(scores) > 3 else 0,
            format_structure_explanation=explanations[3] if len(explanations) > 3 else '',
            education_certifications_score=scores[4] if len(scores) > 4 else 0,
            education_certifications_explanation=explanations[4] if len(explanations) > 4 else '',
            total_score=total_score,
            overall_grade=get_performance_grade(total_score),
            analysis_timestamp=datetime.now(),
            api_version="1.0",
            model_used="gemini-2.0-flash-exp",
            analysis_duration_ms=data.get('metadata', {}).get('analysis_duration', 0),
            file_size=os.path.getsize(resume_filepath) if os.path.exists(resume_filepath) else None,
            file_type=filename.split('.')[-1].upper() if '.' in filename else None
        )
        
        # Set strengths, improvements, and recommendations
        resume_result.set_strengths(identify_strengths(scores))
        resume_result.set_areas_for_improvement(identify_improvements(scores))
        resume_result.set_recommendations(generate_recommendations(scores))
        
        # Save to database
        db.add(resume_result)
        db.commit()
        db.refresh(resume_result)
        
        logger.info(f"Resume test result saved to database with ID: {resume_result.id}")
        
        # Update ResumeathonParticipant if user has joined the leaderboard
        try:
            participant = db.query(ResumeathonParticipant).filter(
                ResumeathonParticipant.user_id == user_id,
                ResumeathonParticipant.is_active == True
            ).first()
            
            if participant:
                # Update to use the latest resume test result
                participant.resume_test_result_id = resume_result.id
                db.commit()
                logger.info(f"Updated ResumeathonParticipant for user {user_id} to use latest score: {total_score}")
        except Exception as update_error:
            logger.warning(f"Failed to update ResumeathonParticipant: {update_error}")
            # Don't fail the whole operation if participant update fails
        
        return resume_result.id
        
    except Exception as e:
        logger.error(f"Error saving resume test result to database: {e}")
        if db:
            db.rollback()
        return None

def get_performance_grade(score):
    """Convert numerical score to letter grade"""
    if score >= 90: return "A+"
    elif score >= 85: return "A"
    elif score >= 80: return "A-"
    elif score >= 75: return "B+"
    elif score >= 70: return "B"
    elif score >= 65: return "B-"
    elif score >= 60: return "C+"
    elif score >= 55: return "C"
    elif score >= 50: return "C-"
    else: return "D"

def identify_strengths(scores):
    """Identify areas where the resume performed well"""
    strengths = []
    categories = ["Content Quality", "Skills Match", "Experience & Achievements", "Format & Structure", "Education & Certifications"]
    
    for i, score in enumerate(scores):
        max_score = 25 if i < 3 else (15 if i == 3 else 10)
        percentage = (score / max_score) * 100
        if percentage >= 80:
            strengths.append(f"{categories[i]} ({percentage:.0f}%)")
    
    return strengths if strengths else ["No specific strengths identified"]

def identify_improvements(scores):
    """Identify areas that need improvement"""
    improvements = []
    categories = ["Content Quality", "Skills Match", "Experience & Achievements", "Format & Structure", "Education & Certifications"]
    
    for i, score in enumerate(scores):
        max_score = 25 if i < 3 else (15 if i == 3 else 10)
        percentage = (score / max_score) * 100
        if percentage < 70:
            improvements.append(f"{categories[i]} ({percentage:.0f}%)")
    
    return improvements if improvements else ["All areas are performing well"]

def generate_recommendations(scores):
    """Generate specific recommendations based on scores"""
    recommendations = []
    
    if scores[0] < 20:  # Content Quality
        recommendations.append("Enhance professional writing style and add more detailed descriptions")
    
    if scores[1] < 20:  # Skills Match
        recommendations.append("Include more industry-specific keywords and technical skills")
    
    if scores[2] < 20:  # Experience & Achievements
        recommendations.append("Quantify achievements with specific metrics and numbers")
    
    if scores[3] < 12:  # Format & Structure
        recommendations.append("Improve layout and ensure consistent formatting throughout")
    
    if scores[4] < 8:  # Education & Certifications
        recommendations.append("Add relevant certifications and highlight educational achievements")
    
    if not recommendations:
        recommendations.append("Maintain current resume quality and continue professional development")
    
    return recommendations

@router.get("/public", response_class=HTMLResponse)
async def resume_tester_public():
    """Display resume tester interface (public, no authentication required)"""
    try:
        # Read the static HTML file and serve it as a template
        static_file_path = os.path.join(BASE_DIR, "resume_tester", "static", "index.html")
        
        if not os.path.exists(static_file_path):
            return HTMLResponse(
                content="<h1>Resume Tester</h1><p>Resume tester interface not found.</p>",
                status_code=404
            )
        
        with open(static_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error serving resume tester interface: {e}")
        return HTMLResponse(
            content=f"<h1>Error</h1><p>Failed to load resume tester: {str(e)}</p>",
            status_code=500
        )

@router.get("/", response_class=HTMLResponse)
async def resume_tester_home(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Display resume tester interface"""
    try:
        # Read the static HTML file and serve it as a template
        static_file_path = os.path.join(BASE_DIR, "resume_tester", "static", "index.html")
        
        with open(static_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Update static file paths to work with main app structure
        html_content = html_content.replace('href="/static/style.css"', 'href="/resume-tester/static/style.css"')
        html_content = html_content.replace('src="/static/app.js"', 'src="/resume-tester/static/app.js"')
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Resume tester home error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while loading resume tester"
        )

@router.get("/scores")
async def list_scores(current_user: User = Depends(get_current_user)):
    """List all saved score files"""
    try:
        if not os.path.exists(SCORES_DIR):
            return JSONResponse(content={"scores": [], "message": "No scores directory found"})
        
        scores = []
        for filename in os.listdir(SCORES_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(SCORES_DIR, filename)
                file_stats = os.stat(filepath)
                scores.append({
                    "filename": filename,
                    "filepath": filepath,
                    "size_bytes": file_stats.st_size,
                    "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                })
        
        # Sort by creation time (newest first)
        scores.sort(key=lambda x: x['created'], reverse=True)
        
        return JSONResponse(content={
            "scores": scores,
            "total_files": len(scores),
            "directory": SCORES_DIR
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/download/{filename}")
async def download_score(filename: str, current_user: User = Depends(get_current_user)):
    """Download a specific score JSON file"""
    try:
        filepath = os.path.join(SCORES_DIR, filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/json'
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.delete("/scores/{filename}")
async def delete_score(filename: str, current_user: User = Depends(get_current_user)):
    """Delete a specific score JSON file"""
    try:
        filepath = os.path.join(SCORES_DIR, filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        os.remove(filepath)
        return JSONResponse(content={"message": f"File {filename} deleted successfully"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/resumes")
async def list_user_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all resumes and test results for the current user"""
    try:
        # Get resume test results from database
        resume_results = db.query(ResumeTestResult).filter(
            ResumeTestResult.user_id == current_user.id
        ).order_by(ResumeTestResult.analysis_timestamp.desc()).all()
        
        resumes_data = []
        for result in resume_results:
            resume_info = {
                'id': result.id,
                'filename': result.filename,
                'total_score': result.total_score,
                'overall_grade': result.overall_grade,
                'analysis_timestamp': result.analysis_timestamp.isoformat(),
                'file_size': result.file_size,
                'file_type': result.file_type,
                'resume_filepath': result.filepath,
                'category_scores': {
                    'content_quality': result.content_quality_score,
                    'skills_match': result.skills_match_score,
                    'experience_achievements': result.experience_achievements_score,
                    'format_structure': result.format_structure_score,
                    'education_certifications': result.education_certifications_score
                },
                'strengths': result.get_strengths(),
                'improvements': result.get_areas_for_improvement(),
                'recommendations': result.get_recommendations()
            }
            resumes_data.append(resume_info)
        
        return JSONResponse(content={
            "resumes": resumes_data,
            "total_resumes": len(resumes_data),
            "user_id": current_user.id
        })
        
    except Exception as e:
        logger.error(f"Error listing user resumes: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/resume/{result_id}")
async def get_resume_detail(result_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed information about a specific resume test result"""
    try:
        result = db.query(ResumeTestResult).filter(
            ResumeTestResult.id == result_id,
            ResumeTestResult.user_id == current_user.id
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Resume test result not found")
        
        resume_detail = {
            'id': result.id,
            'filename': result.filename,
            'total_score': result.total_score,
            'overall_grade': result.overall_grade,
            'analysis_timestamp': result.analysis_timestamp.isoformat(),
            'file_size': result.file_size,
            'file_type': result.file_type,
            'resume_filepath': result.filepath,
            'category_scores': {
                'content_quality': {
                    'score': result.content_quality_score,
                    'explanation': result.content_quality_explanation
                },
                'skills_match': {
                    'score': result.skills_match_score,
                    'explanation': result.skills_match_explanation
                },
                'experience_achievements': {
                    'score': result.experience_achievements_score,
                    'explanation': result.experience_achievements_explanation
                },
                'format_structure': {
                    'score': result.format_structure_score,
                    'explanation': result.format_structure_explanation
                },
                'education_certifications': {
                    'score': result.education_certifications_score,
                    'explanation': result.education_certifications_explanation
                }
            },
            'strengths': result.get_strengths(),
            'improvements': result.get_areas_for_improvement(),
            'recommendations': result.get_recommendations(),
            'metadata': {
                'api_version': result.api_version,
                'model_used': result.model_used,
                'analysis_duration_ms': result.analysis_duration_ms
            }
        }
        
        return JSONResponse(content=resume_detail)
        
    except Exception as e:
        logger.error(f"Error getting resume detail: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/download-resume/{result_id}")
async def download_resume_file(result_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Download the actual resume file for a specific test result"""
    try:
        result = db.query(ResumeTestResult).filter(
            ResumeTestResult.id == result_id,
            ResumeTestResult.user_id == current_user.id
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Resume test result not found")
        
        if not result.filepath or not os.path.exists(result.filepath):
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        return FileResponse(
            path=result.filepath,
            filename=result.filename,
            media_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error downloading resume file: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/score-resume-public")
async def score_resume_public(
    file: UploadFile = File(...)
):
    """Score a resume using ATS criteria (public endpoint, no authentication required)"""
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Save uploaded file to a temp location for analysis
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        # Record start time for analysis duration
        start_time = datetime.now()
        
        scorer = ATSResumeScorer(api_key=API_KEY)
        result = scorer.score_resume(tmp_path)
        
        # Calculate analysis duration
        end_time = datetime.now()
        analysis_duration = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass  # File already deleted or doesn't exist
        
        # Add analysis metadata
        result['analysis_duration_ms'] = analysis_duration
        result['timestamp'] = datetime.now().isoformat()
        
        logger.info(f"Resume analysis completed in {analysis_duration:.2f}ms")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error scoring resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@router.post("/score-resume")
async def score_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Score a resume using ATS criteria (no authentication required)"""
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Save uploaded file to a temp location for analysis
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        # Record start time for analysis duration
        start_time = datetime.now()
        
        scorer = ATSResumeScorer(api_key=API_KEY)
        result = scorer.score_resume(tmp_path)
        
        # Calculate analysis duration
        end_time = datetime.now()
        analysis_duration = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        # Clean up temp file
        os.remove(tmp_path)
        
        if isinstance(result, dict):
            # Prepare data for graphing
            categories = [
                'content_quality',
                'skills_match',
                'experience_achievements',
                'format_structure',
                'education_certifications'
            ]
            
            # Extract scores and calculate total
            scores = [result[cat]['score'] for cat in categories if cat in result]
            total_score = result.get('total_score', sum(scores))
            
            graph_data = {
                'labels': [cat.replace('_', ' ').title() for cat in categories],
                'scores': scores,
                'explanations': [result[cat]['explanation'] for cat in categories if cat in result],
                'total_score': total_score,
                'metadata': {
                    **result.get('metadata', {}),
                    'analysis_duration': analysis_duration,
                    'user_id': getattr(current_user, 'id', None),
                    'user_name': getattr(current_user, 'full_name', None)
                }
            }
            
            # Save resume to resume_data folder if authenticated
            if not current_user:
                return JSONResponse(content={"error": "Authentication required to save scores"}, status_code=401)
            resume_filepath = save_resume_to_folder(file_content, file.filename, current_user.id)
            if not resume_filepath:
                logger.error("Failed to save resume to folder")
                return JSONResponse(content={"error": "Failed to save resume file"}, status_code=500)
            
            # Save scores to JSON file
            json_filepath = save_scores_to_json(graph_data, file.filename)
            if json_filepath:
                graph_data['json_file_path'] = json_filepath
            
            # Save results to database with resume file path
            db_result_id = save_resume_test_to_db(
                data=graph_data,
                filename=file.filename,
                resume_filepath=resume_filepath,
                user_id=current_user.id,
                db=db
            )
            
            if db_result_id:
                graph_data['db_result_id'] = db_result_id
                logger.info(f"Resume test result saved to database with ID: {db_result_id}")
                logger.info(f"Resume file saved to: {resume_filepath}")
                logger.info(f"Total score stored: {total_score}")
            else:
                logger.warning("Failed to save resume test result to database")
            
            return JSONResponse(content=graph_data)
        else:
            return JSONResponse(content={"error": result}, status_code=500)
    except Exception as e:
        logger.error(f"Resume scoring error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/analyze-resume")
async def analyze_resume_public(
    file: UploadFile = File(...)
):
    """Analyze a resume using ATS criteria (public endpoint, no authentication required)"""
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Save uploaded file to a temp location for analysis
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        # Record start time for analysis duration
        start_time = datetime.now()
        
        scorer = ATSResumeScorer(api_key=API_KEY)
        result = scorer.score_resume(tmp_path)
        
        # Calculate analysis duration
        end_time = datetime.now()
        analysis_duration = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass  # File already deleted or doesn't exist
        
        # Add analysis metadata
        result['analysis_duration_ms'] = analysis_duration
        result['timestamp'] = datetime.now().isoformat()
        
        logger.info(f"Resume analysis completed in {analysis_duration:.2f}ms")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error scoring resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@router.post("/join-resumeathon")
async def join_resumeathon_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join the Resumeathon leaderboard"""
    try:
        # Check if user already joined
        existing_participant = db.query(ResumeathonParticipant).filter(
            ResumeathonParticipant.user_id == current_user.id,
            ResumeathonParticipant.is_active == True
        ).first()
        
        if existing_participant:
            return JSONResponse(content={
                "success": True,
                "message": "Already joined Resumeathon leaderboard",
                "user": {
                    "id": current_user.id,
                    "name": current_user.full_name or current_user.username,
                    "username": current_user.username
                }
            })
        
        # Get user's latest resume test result
        # Order by id desc (most recent first) since id is auto-incrementing
        # This is more reliable than timestamp which might have NULL values
        latest_resume_test = db.query(ResumeTestResult).filter(
            ResumeTestResult.user_id == current_user.id
        ).order_by(ResumeTestResult.id.desc()).first()
        
        # If still not found, try a simpler query to check if any results exist
        if not latest_resume_test:
            # Check if user has any resume test results at all (for debugging)
            any_results = db.query(ResumeTestResult).filter(
                ResumeTestResult.user_id == current_user.id
            ).count()
            
            # Also check if there are results with NULL user_id (shouldn't happen, but for debugging)
            all_results = db.query(ResumeTestResult).count()
            
            logger.warning(f"User {current_user.id} ({current_user.username}) tried to join Resumeathon but has no resume test results. Total results for user: {any_results}, Total results in DB: {all_results}")
            
            return JSONResponse(content={
                "success": False,
                "message": "You need to test your resume first before joining the leaderboard. Please upload and analyze your resume using the ATS Checker.",
                "error": "NO_RESUME_TEST",
                "debug_info": {
                    "user_id": current_user.id,
                    "total_results": any_results
                }
            }, status_code=400)
        
        # Create new participant
        participant = ResumeathonParticipant(
            user_id=current_user.id,
            resume_test_result_id=latest_resume_test.id,
            joined_at=datetime.now(),
            is_active=True
        )
        
        db.add(participant)
        db.commit()
        db.refresh(participant)
        
        logger.info(f"User {current_user.id} ({current_user.full_name}) joined Resumeathon leaderboard with score {latest_resume_test.total_score}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Successfully joined Resumeathon leaderboard",
            "user": {
                "id": current_user.id,
                "name": current_user.full_name or current_user.username,
                "username": current_user.username,
                "score": latest_resume_test.total_score
            }
        })
        
    except Exception as e:
        logger.error(f"Error joining Resumeathon: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/resumeathon-leaderboard")
async def get_resumeathon_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the Resumeathon leaderboard"""
    try:
        logger.info(f"Fetching Resumeathon leaderboard for user {current_user.id}")
        
        # Get all active participants
        # For each participant, get their LATEST resume test result (not the one they joined with)
        participants_query = db.query(ResumeathonParticipant).join(
            User, ResumeathonParticipant.user_id == User.id, isouter=False
        ).filter(
            ResumeathonParticipant.is_active == True
        ).all()
        
        # Define patterns for dummy/test users to exclude
        dummy_email_patterns = [
            'testuser@example.com',
            'test@',
            'dummy@',
            'sample@',
            '@test.com',
            '@example.com',
            '@testcompany.com'
        ]
        
        # Build a list of participants with their latest scores
        participants_with_scores = []
        for participant in participants_query:
            user = participant.user
            user_email = (user.email or '').lower()
            
            # Skip dummy/test users based on email patterns
            is_dummy_user = any(pattern in user_email for pattern in dummy_email_patterns)
            if is_dummy_user:
                logger.info(f"Skipping dummy/test user: {user.email} ({user.full_name or user.username})")
                continue
            
            # Get the latest resume test result for this user
            latest_result = db.query(ResumeTestResult).filter(
                ResumeTestResult.user_id == participant.user_id
            ).order_by(ResumeTestResult.id.desc()).first()
            
            if latest_result:
                # Only skip test users with 0 scores, not real users
                # Real users might have 0 scores legitimately
                if is_dummy_user and latest_result.total_score == 0:
                    logger.info(f"Skipping dummy user with 0 score: {user.email} ({user.full_name or user.username})")
                    continue
                    
                participants_with_scores.append({
                    'participant': participant,
                    'user': user,
                    'resume_test': latest_result,
                    'score': latest_result.total_score
                })
        
        # Sort by score (high to low), then by joined_at (earlier join = better for same score)
        participants_with_scores.sort(
            key=lambda x: (-x['score'], x['participant'].joined_at.timestamp() if x['participant'].joined_at else float('inf'))
        )
        
        # Update participant records to point to latest results (for consistency)
        for item in participants_with_scores:
            if item['participant'].resume_test_result_id != item['resume_test'].id:
                item['participant'].resume_test_result_id = item['resume_test'].id
                db.commit()
        
        # Convert back to a list format similar to the original query
        participants = [item['participant'] for item in participants_with_scores]
        
        logger.info(f"Found {len(participants)} active participants")
        
        # Check if current user has joined
        user_participant = None
        try:
            user_participant = db.query(ResumeathonParticipant).filter(
                ResumeathonParticipant.user_id == current_user.id,
                ResumeathonParticipant.is_active == True
            ).first()
        except Exception as user_check_error:
            logger.warning(f"Error checking if user joined: {user_check_error}")
        
        leaderboard_data = []
        # Create a mapping for quick lookup
        participants_map = {item['participant'].id: item for item in participants_with_scores}
        
        for rank, participant in enumerate(participants, 1):
            try:
                # Get the latest resume test result from our pre-computed list
                participant_data = participants_map.get(participant.id)
                if not participant_data:
                    continue
                    
                user = participant_data['user']
                resume_test = participant_data['resume_test']
                
                if not user:
                    logger.warning(f"Participant {participant.id} has no user relationship")
                    continue
                
                if not resume_test:
                    logger.warning(f"Participant {participant.id} has no resume_test_result relationship")
                    continue
                
                # Determine badge based on rank
                if rank == 1:
                    badge = "Crown"
                    color = "text-yellow-600"
                elif rank == 2:
                    badge = "Trophy"
                    color = "text-gray-600"
                elif rank == 3:
                    badge = "Medal"
                    color = "text-orange-600"
                else:
                    badge = "Award"
                    color = "text-blue-600"
                
                # Create avatar from name
                name_parts = (user.full_name or user.username or "User").split()
                if len(name_parts) >= 2:
                    avatar = f"{name_parts[0][0]}{name_parts[1][0]}".upper()
                else:
                    avatar = (user.full_name or user.username or "U")[:2].upper()
                
                leaderboard_data.append({
                    "rank": rank,
                    "name": user.full_name or user.username or "Unknown User",
                    "score": resume_test.total_score if resume_test and resume_test.total_score is not None else 0,
                    "avatar": avatar,
                    "badge": badge,
                    "color": color,
                    "joined_at": participant.joined_at.isoformat() if participant.joined_at else None,
                    "user_id": user.id  # Include user_id so frontend can identify current user
                })
            except Exception as participant_error:
                logger.error(f"Error processing participant {participant.id}: {participant_error}", exc_info=True)
                continue
        
        # Explicitly sort leaderboard_data by score (high to low) as a safeguard
        # This ensures correct ordering even if the database query order is somehow incorrect
        leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
        
        # Re-assign ranks based on sorted order
        for idx, entry in enumerate(leaderboard_data, 1):
            entry['rank'] = idx
            # Update badge based on new rank
            if idx == 1:
                entry['badge'] = "Crown"
                entry['color'] = "text-yellow-600"
            elif idx == 2:
                entry['badge'] = "Trophy"
                entry['color'] = "text-gray-600"
            elif idx == 3:
                entry['badge'] = "Medal"
                entry['color'] = "text-orange-600"
            else:
                entry['badge'] = "Award"
                entry['color'] = "text-blue-600"
        
        logger.info(f"Returning leaderboard with {len(leaderboard_data)} entries for user {current_user.id}")
        
        return JSONResponse(content={
            "success": True,
            "leaderboard": leaderboard_data,
            "user_joined": user_participant is not None,
            "total_participants": len(leaderboard_data),
            "current_user_id": current_user.id  # Include current user ID for frontend highlighting
        })
        
    except Exception as e:
        logger.error(f"Error getting Resumeathon leaderboard: {e}", exc_info=True)
        return JSONResponse(content={
            "success": False,
            "error": str(e),
            "leaderboard": [],
            "user_joined": False,
            "total_participants": 0
        }, status_code=500)

@router.get("/stats")
async def get_resume_testing_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get statistics about resume testing for the current user"""
    try:
        # Get all resume test results for the user
        results = db.query(ResumeTestResult).filter(
            ResumeTestResult.user_id == current_user.id
        ).all()
        
        if not results:
            return JSONResponse(content={
                "total_resumes": 0,
                "average_score": 0,
                "best_score": 0,
                "worst_score": 0,
                "grade_distribution": {},
                "total_files_size": 0
            })
        
        # Calculate statistics
        total_resumes = len(results)
        scores = [r.total_score for r in results]
        average_score = sum(scores) / len(scores)
        best_score = max(scores)
        worst_score = min(scores)
        
        # Grade distribution
        grade_distribution = {}
        for result in results:
            grade = result.overall_grade
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # Total file size
        total_files_size = sum(r.file_size or 0 for r in results)
        
        stats = {
            "total_resumes": total_resumes,
            "average_score": round(average_score, 2),
            "best_score": best_score,
            "worst_score": worst_score,
            "grade_distribution": grade_distribution,
            "total_files_size": total_files_size,
            "recent_activity": {
                "last_test": max(r.analysis_timestamp for r in results).isoformat(),
                "first_test": min(r.analysis_timestamp for r in results).isoformat()
            }
        }
        
        return JSONResponse(content=stats)
        
    except Exception as e:
        logger.error(f"Error getting resume testing stats: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

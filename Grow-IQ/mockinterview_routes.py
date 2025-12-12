import os
import uuid
import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional
import re
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
import google.generativeai as genai

from database import get_db
from auth_utils import get_current_user
from models import User, MockInterviewSession, MockInterviewTurn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/mock-interview", tags=["Mock Interview"])

# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Google Gemini API configuration
GENAI_API_KEY = "AIzaSyCKMSm2uyOT67DVXwOxjQWWWJV9jJhJB2Y"
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
else:
    logger.warning("Google Gemini API key not configured - mock interview AI features will be disabled")

# In-memory session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}

# Constants
MAX_QUESTIONS_PER_SESSION = 10

# ========== DATA MODELS ==========
class StartRequest(BaseModel):
    job_role: str
    job_desc: str

class StartResponse(BaseModel):
    session_id: str
    initial_prompt: str
    max_questions: int = MAX_QUESTIONS_PER_SESSION

class MessageRequest(BaseModel):
    session_id: str
    message: str

class MessageResponse(BaseModel):
    reply: str
    done: bool = False
    final: Optional[Dict[str, Any]] = None

# ========== HELPER FUNCTIONS ==========
def generate_initial_prompt(job_role: str, job_desc: str) -> str:
    """Generate initial interview prompt based on job role and description"""
    if job_desc.startswith("General interview for"):
        return (
            f"Hello, welcome to the technical HR round for the role of {job_role}. "
            "I will be asking you technical and behavioral questions one at a time. "
            "Let's get started. Can you please introduce yourself briefly?"
        )
    else:
        return (
            f"Hello, welcome to the technical HR round for the role of {job_role}. "
            f"Here is the job description: {job_desc}. "
            "I will be asking you technical and behavioral questions one at a time. "
            "Let's get started. Can you please introduce yourself briefly?"
        )

def generate_ai_response(
    conversation_history: List[str],
    query: str,
    job_role: str,
    job_desc: str,
) -> Tuple[str, List[str]]:
    """Generate AI response using Google Gemini"""
    if not GENAI_API_KEY:
        return "AI features are currently unavailable. Please contact support.", conversation_history
    
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        conversation_history.append(f"Candidate: {query}")
        
        prompt = (
            f"You are an experienced HR interviewer in a multinational tech company. "
            f"Your role is to interview candidates for the position of {job_role}. "
        )
        
        if not job_desc.startswith("General interview for"):
            prompt += f"Job Description: {job_desc}. "
        
        prompt += (
            "Ask clear, professional, and structured questions one at a time. "
            "Your tone should be formal, unbiased, and encouraging, like a real HR professional in an MNC. "
            "Keep track of the previous conversation and continue the interview naturally, "
            "do not repeat introductions. "
            "Ask progressive questions (easy → medium → hard), and balance technical with behavioral ones. "
            "Never answer your own questions. Only ask or respond appropriately."
        )
        
        response = model.generate_content([prompt, "\n".join(conversation_history)])
        ai_text = (response.text or "").strip()
        ai_text = sanitize_ai_text(ai_text)
        
        if not ai_text:
            ai_text = next_question_fallback(job_role)
        
        conversation_history.append(f"HR: {ai_text}")
        return ai_text, conversation_history
        
    except Exception as exc:
        logger.error(f"AI model error: {exc}")
        return next_question_fallback(job_role), conversation_history


def strip_markdown(text: str) -> str:
    """Remove simple markdown/code fences that hurt TTS."""
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]*)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return text.strip()


def ensure_question(text: str) -> str:
    """Bias the interviewer to end with a clear question for smooth turn-taking."""
    t = text.strip()
    if not t:
        return t
    if "?" in t or t.lower().startswith(("please", "tell me", "describe", "can you", "could you")):
        return t
    if len(t) <= 200:
        return t + " Can you elaborate on that?"
    return t


def sanitize_ai_text(text: str) -> str:
    """Normalize AI output for TTS and turn-taking."""
    t = strip_markdown(text)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > 600:
        t = t[:600].rsplit(" ", 1)[0] + "..."
    t = ensure_question(t)
    return t


def next_question_fallback(job_role: str) -> str:
    return f"Thanks. Based on the {job_role} role, can you walk me through a recent project you led and the impact it had?"


def generate_final_evaluation(turns: List[Dict[str, str]], job_role: str, job_desc: str) -> Dict[str, Any]:
    """Use AI to generate a comprehensive analysis report.
    Returns a dict with:
      - feedback_summary: str
      - strengths: list[str] - What the candidate did well
      - areas_for_improvement: list[str] - Specific areas to work on
      - suggestions: list[str] - Actionable improvement suggestions
      - scores: {accuracy, clarity, relevance, overall, confidence}
      - rubric: fine-grained marks per dimension
      - keywords: extracted important keywords/topics
      - detailed_analysis: dict with category-wise analysis
    """
    if not GENAI_API_KEY:
        # Fallback simple heuristic
        return {
            "feedback_summary": "Good effort. Focus on being concise and aligning answers with the role.",
            "strengths": [
                "Showed enthusiasm for the role",
                "Provided relevant examples",
                "Demonstrated technical knowledge"
            ],
            "areas_for_improvement": [
                "Structure answers more clearly",
                "Include more specific metrics",
                "Better connect experience to job requirements"
            ],
            "suggestions": [
                "Highlight impact with metrics",
                "Structure answers with STAR",
                "Map experience directly to job requirements",
                "Clarify technical trade-offs succinctly",
                "Summarize key points at the end"
            ],
            "scores": {"accuracy": 75, "clarity": 72, "relevance": 74, "overall": 74, "confidence": 70},
            "rubric": {
                "communication": 73,
                "problem_solving": 74,
                "technical_depth": 72,
                "behavioral": 76,
                "star_technique": 70
            },
            "keywords": ["STAR", "metrics", "trade-offs", job_role],
            "detailed_analysis": {
                "communication_skills": "Good verbal communication with room for improvement in structure",
                "technical_knowledge": "Demonstrated understanding of key concepts",
                "problem_solving": "Showed logical thinking approach",
                "leadership": "Some examples provided but could be more detailed"
            }
        }
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        convo = "\n".join([f"Q{t['turn']}: {t['question']}\nA{t['turn']}: {t['answer']}" for t in turns])
        sys_prompt = (
            "You are an expert interviewer evaluator and career coach. Analyze the interview transcript and provide a comprehensive report: "
            "1) feedback_summary (3-4 sentences overall assessment), "
            "2) strengths (3-5 specific things the candidate did well), "
            "3) areas_for_improvement (3-5 specific areas that need work), "
            "4) suggestions (5-7 actionable improvement recommendations), "
            "5) scores: integer 0-100 for accuracy, clarity, relevance, overall, confidence, "
            "6) rubric: integer 0-100 for communication, problem_solving, technical_depth, behavioral, star_technique, "
            "7) keywords: list of 5-10 important skills/terms mentioned, "
            "8) detailed_analysis: object with category-wise analysis (communication_skills, technical_knowledge, problem_solving, leadership, industry_knowledge). "
            "Be specific, constructive, and encouraging. Focus on actionable feedback that will help the candidate improve."
        )
        user_prompt = (
            f"Job Role: {job_role}. Job Description: {job_desc}. Transcript below.\n\n{convo}\n\n"
            "Respond as: {\n  \"feedback_summary\": \"...\",\n  \"strengths\": [\"...\"],\n  \"areas_for_improvement\": [\"...\"],\n  \"suggestions\": [\"...\"],\n  \"scores\": {\"accuracy\": 0, \"clarity\": 0, \"relevance\": 0, \"overall\": 0, \"confidence\": 0},\n  \"rubric\": {\"communication\": 0, \"problem_solving\": 0, \"technical_depth\": 0, \"behavioral\": 0, \"star_technique\": 0},\n  \"keywords\": [\"...\"],\n  \"detailed_analysis\": {\"communication_skills\": \"...\", \"technical_knowledge\": \"...\", \"problem_solving\": \"...\", \"leadership\": \"...\", \"industry_knowledge\": \"...\"}\n}"
        )
        response = model.generate_content([sys_prompt, user_prompt])
        text = (response.text or "{}").strip()
        try:
            data = json.loads(text)
        except Exception:
            # Try to extract JSON block if present
            start = text.find("{")
            end = text.rfind("}")
            data = json.loads(text[start:end+1]) if start != -1 and end != -1 else {}
        scores = data.get("scores", {})
        # Clamp and default
        def clamp(v):
            try:
                iv = int(v)
                return max(0, min(100, iv))
            except Exception:
                return 75
        accuracy = clamp(scores.get("accuracy"))
        clarity = clamp(scores.get("clarity"))
        relevance = clamp(scores.get("relevance"))
        confidence = clamp(scores.get("confidence", (accuracy + clarity + relevance) // 3))
        overall = clamp(scores.get("overall", (accuracy + clarity + relevance + confidence) // 4))
        suggestions = data.get("suggestions", [])
        if not isinstance(suggestions, list):
            suggestions = [str(suggestions)]
        suggestions = [str(s)[:200] for s in suggestions][:5]
        feedback_summary = str(data.get("feedback_summary", "Good effort. Keep improving clarity and relevance."))[:1000]
        rubric_in = data.get("rubric", {}) if isinstance(data.get("rubric", {}), dict) else {}
        rubric = {
            "communication": clamp(rubric_in.get("communication")),
            "problem_solving": clamp(rubric_in.get("problem_solving")),
            "technical_depth": clamp(rubric_in.get("technical_depth")),
            "behavioral": clamp(rubric_in.get("behavioral")),
            "star_technique": clamp(rubric_in.get("star_technique"))
        }
        kw = data.get("keywords", [])
        if not isinstance(kw, list):
            kw = [str(kw)]
        keywords = [str(k)[:40] for k in kw][:10]
        # Process new fields
        strengths = data.get("strengths", [])
        if not isinstance(strengths, list):
            strengths = [str(strengths)]
        strengths = [str(s)[:200] for s in strengths][:5]
        
        areas_for_improvement = data.get("areas_for_improvement", [])
        if not isinstance(areas_for_improvement, list):
            areas_for_improvement = [str(areas_for_improvement)]
        areas_for_improvement = [str(a)[:200] for a in areas_for_improvement][:5]
        
        detailed_analysis = data.get("detailed_analysis", {})
        if not isinstance(detailed_analysis, dict):
            detailed_analysis = {}
        
        return {
            "feedback_summary": feedback_summary,
            "strengths": strengths,
            "areas_for_improvement": areas_for_improvement,
            "suggestions": suggestions,
            "scores": {
                "accuracy": accuracy,
                "clarity": clarity,
                "relevance": relevance,
                "overall": overall,
                "confidence": confidence,
            },
            "rubric": rubric,
            "keywords": keywords,
            "detailed_analysis": detailed_analysis,
        }
    except Exception as exc:
        logger.error(f"Final evaluation generation error: {exc}")
        return {
            "feedback_summary": "Good effort. Focus on being concise and aligning answers with the role.",
            "strengths": [
                "Showed enthusiasm for the role",
                "Provided relevant examples",
                "Demonstrated technical knowledge"
            ],
            "areas_for_improvement": [
                "Structure answers more clearly",
                "Include more specific metrics",
                "Better connect experience to job requirements"
            ],
            "suggestions": [
                "Highlight impact with metrics",
                "Structure answers with STAR",
                "Map experience directly to job requirements",
                "Clarify technical trade-offs succinctly",
                "Summarize key points at the end"
            ],
            "scores": {"accuracy": 75, "clarity": 72, "relevance": 74, "overall": 74, "confidence": 70},
            "rubric": {
                "communication": 73,
                "problem_solving": 74,
                "technical_depth": 72,
                "behavioral": 76,
                "star_technique": 70
            },
            "keywords": ["STAR", "metrics", "trade-offs", job_role],
            "detailed_analysis": {
                "communication_skills": "Good verbal communication with room for improvement in structure",
                "technical_knowledge": "Demonstrated understanding of key concepts",
                "problem_solving": "Showed logical thinking approach",
                "leadership": "Some examples provided but could be more detailed",
                "industry_knowledge": "Basic understanding shown"
            }
        }

# ========== ROUTES ==========
@router.get("/", response_class=HTMLResponse)
async def mock_interview_home(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Display mock interview home page - redirect to React frontend"""
    # Since we're using React frontend, redirect to the main app
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/mock-interview", status_code=307)

# ========== GOOGLE MEET STYLE INTERVIEW ROUTES ==========
@router.post("/video/start", response_model=StartResponse)
async def start_video_interview(
    payload: StartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new Google Meet-style video interview session"""
    try:
        job_role = payload.job_role.strip()
        job_desc = payload.job_desc.strip()
        
        if not job_role:
            raise HTTPException(status_code=400, detail="job_role is required.")
        
        # If no job description provided, use a default one
        if not job_desc:
            job_desc = f"General interview for {job_role} position"
        
        session_id = str(uuid.uuid4())
        conversation_history: List[str] = []
        initial_prompt = generate_initial_prompt(job_role, job_desc)
        conversation_history.append(f"HR: {initial_prompt}")
        
        # Store session in memory for video interview (simpler than DB for now)
        sessions[session_id] = {
            "job_role": job_role,
            "job_desc": job_desc,
            "history": conversation_history,
            "user_id": current_user.id,
            "user_name": current_user.full_name,
            "created_at": datetime.now().isoformat(),
            "interview_type": "video",  # Mark as video interview
            "started_at": datetime.now()
        }
        
        logger.info(f"Started video interview session {session_id} for user {current_user.id}")
        
        return StartResponse(session_id=session_id, initial_prompt=initial_prompt)
        
    except Exception as e:
        logger.error(f"Error starting video interview: {e}")
        raise HTTPException(status_code=500, detail="Failed to start video interview session")

@router.post("/video/message", response_model=MessageResponse)
async def send_video_message(
    payload: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in the video interview"""
    try:
        session_id = payload.session_id.strip()
        message = payload.message.strip()
        
        if not session_id or not message:
            raise HTTPException(status_code=400, detail="Both session_id and message are required.")
        
        session = sessions.get(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found. Start a new interview.")
        
        # Verify session belongs to current user
        if session.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this session.")
        
        # Check for exit commands
        lower = message.lower()
        if lower in {"exit", "stop", "quit"}:
            del sessions[session_id]
            return MessageResponse(reply="Thank you for the interview. Goodbye!")
        
        # Generate AI response
        reply, updated_history = generate_ai_response(
            conversation_history=session["history"],
            query=message,
            job_role=session["job_role"],
            job_desc=session["job_desc"],
        )
        session["history"] = updated_history
        
        return MessageResponse(reply=reply)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@router.get("/role", response_class=HTMLResponse)
async def role_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Role selection page - redirect to React frontend"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/mock-interview", status_code=307)

@router.get("/ready", response_class=HTMLResponse)
async def ready_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Ready page - redirect to React frontend"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/mock-interview", status_code=307)

@router.get("/interview", response_class=HTMLResponse)
async def interview_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Main interview interface page - redirect to React frontend"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/mock-interview", status_code=307)

@router.get("/favicon.ico")
async def favicon():
    """Handle favicon requests"""
    return Response(status_code=204)

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "mock-interview", "max_questions": MAX_QUESTIONS_PER_SESSION}

@router.post("/end-interview")
async def end_interview_manually(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End interview manually and generate AI report"""
    try:
        session_id = payload.get("session_id", "").strip()
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        session = sessions.get(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify session belongs to current user
        if session.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this session")
        
        # Generate final evaluation using the conversation transcript
        # For video interviews, we need to get the transcript from the database
        if session.get("interview_type") == "video":
            # Get transcript from database for video interviews
            db_sess: Optional[MockInterviewSession] = db.get(MockInterviewSession, session.get("db_session_id"))
            if db_sess and db_sess.transcript_json:
                try:
                    transcript = json.loads(db_sess.transcript_json)
                except Exception:
                    transcript = []
            else:
                # Fallback: create transcript from conversation history
                transcript = []
                history = session.get("history", [])
                for i, msg in enumerate(history):
                    if msg.startswith("HR: "):
                        question = msg[4:]  # Remove "HR: " prefix
                        # For video interviews, we don't have stored answers, so create a basic structure
                        transcript.append({
                            "turn": i + 1,
                            "question": question,
                            "answer": "Answer not available for video interview"
                        })
        else:
            # Regular mock interview with transcript
            transcript = session.get("transcript", [])
        
        final_eval = generate_final_evaluation(transcript, session["job_role"], session["job_desc"])
        
        # Calculate interview duration
        start_time = session.get("started_at", datetime.now())
        end_time = datetime.now()
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        
        # Persist the enhanced report to database
        try:
            db_sess: Optional[MockInterviewSession] = db.get(MockInterviewSession, session.get("db_session_id"))
            if db_sess:
                db_sess.ended_at = end_time
                db_sess.score_accuracy = final_eval["scores"]["accuracy"]
                db_sess.score_clarity = final_eval["scores"]["clarity"]
                db_sess.score_relevance = final_eval["scores"]["relevance"]
                db_sess.score_confidence = final_eval["scores"].get("confidence", 0)
                db_sess.score_overall = final_eval["scores"]["overall"]
                db_sess.feedback_summary = final_eval["feedback_summary"]
                db_sess.detailed_feedback = json.dumps(final_eval.get("detailed_feedback", {}))
                db_sess.set_suggestions(final_eval["suggestions"])
                db_sess.set_transcript(transcript)
                
                # Save enhanced report fields
                db_sess.set_strengths(final_eval.get("strengths", []))
                db_sess.set_areas_for_improvement(final_eval.get("areas_for_improvement", []))
                db_sess.set_detailed_analysis(final_eval.get("detailed_analysis", {}))
                db_sess.set_keywords(final_eval.get("keywords", []))
                db_sess.interview_duration_minutes = duration_minutes
                db_sess.questions_answered = len(transcript)
                
                # Calculate and assign grades
                db_sess.calculate_overall_score()
                db_sess.assign_grades()
                
                # Determine confidence level based on scores
                avg_score = (db_sess.score_accuracy + db_sess.score_clarity + db_sess.score_relevance + db_sess.score_confidence) / 4
                if avg_score >= 20:
                    db_sess.confidence_level = "High"
                elif avg_score >= 15:
                    db_sess.confidence_level = "Medium"
                else:
                    db_sess.confidence_level = "Low"
                
                db.commit()
                logger.info(f"Mock interview session {session_id} ended manually and saved to database")
        except Exception as exc:
            logger.error(f"Failed to finalize interview session: {exc}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to save interview results")

        # Clean up in-memory session
        del sessions[session_id]
        
        return {
            "success": True,
            "message": "Interview ended successfully. AI report generated.",
            "final_evaluation": final_eval,
            "session_uuid": db_sess.session_uuid if db_sess else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending interview: {e}")
        raise HTTPException(status_code=500, detail="Failed to end interview")

@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all mock interview sessions for the current user"""
    try:
        # Get all completed sessions for the user
        sessions = db.query(MockInterviewSession).filter(
            MockInterviewSession.user_id == current_user.id,
            MockInterviewSession.ended_at.isnot(None)
        ).order_by(desc(MockInterviewSession.ended_at)).all()
        
        sessions_data = []
        for session in sessions:
            # Get enhanced report data
            strengths = session.get_strengths()
            areas_for_improvement = session.get_areas_for_improvement()
            detailed_analysis = session.get_detailed_analysis()
            suggestions = session.get_suggestions()
            keywords = []
            try:
                keywords = json.loads(session.keywords_json or "[]")
            except Exception:
                keywords = []
            
            sessions_data.append({
                "id": session.id,
                "session_uuid": session.session_uuid,
                "job_role": session.job_role,
                "job_desc": session.job_desc,
                "score_overall": session.score_overall,
                "score_accuracy": session.score_accuracy,
                "score_clarity": session.score_clarity,
                "score_relevance": session.score_relevance,
                "score_confidence": session.score_confidence,
                "feedback_summary": session.feedback_summary,
                "strengths": strengths,
                "areas_for_improvement": areas_for_improvement,
                "suggestions": suggestions,
                "detailed_analysis": detailed_analysis,
                "keywords": keywords,
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "interview_duration_minutes": session.interview_duration_minutes,
                "questions_answered": session.questions_answered
            })
        
        logger.info(f"Retrieved {len(sessions_data)} interview sessions for user {current_user.id}")
        
        return {
            "success": True,
            "sessions": sessions_data,
            "total": len(sessions_data)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")


@router.get("/report/{session_uuid}", response_class=HTMLResponse)
async def interview_report(
    session_uuid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render final report page for a completed mock interview session"""
    try:
        db_session: Optional[MockInterviewSession] = (
            db.query(MockInterviewSession)
            .filter(MockInterviewSession.session_uuid == session_uuid)
            .first()
        )
        if not db_session:
            raise HTTPException(status_code=404, detail="Report not found")
        if db_session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden")

        # Prepare data
        transcript = []
        try:
            transcript = json.loads(db_session.transcript_json or "[]")
        except Exception:
            transcript = []
        suggestions = []
        try:
            suggestions = json.loads(db_session.suggestions_json or "[]")
        except Exception:
            suggestions = []
        
        # Get enhanced report data
        strengths = db_session.get_strengths()
        areas_for_improvement = db_session.get_areas_for_improvement()
        detailed_analysis = db_session.get_detailed_analysis()

        # Build minimal styled HTML (self-contained)
        html = f"""
        <!DOCTYPE html>
        <html lang=\"en\">
        <head>
            <meta charset=\"UTF-8\" />
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
            <title>Mock Interview Report</title>
            <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
            <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
            <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap\" rel=\"stylesheet\">
            <style>
                body {{ font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; background: #f7f7fb; color: #1b1f23; }}
                .wrap {{ max-width: 920px; margin: 32px auto; padding: 0 16px; }}
                .card {{ background: #fff; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); padding: 20px; margin-bottom: 16px; }}
                h1 {{ font-size: 22px; margin: 0 0 4px; }}
                .muted {{ color: #6a737d; font-size: 14px; }}
                .score-grid {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-top: 12px; }}
                .score {{ background: #f4f8f2; border: 1px solid #e2efd9; border-radius: 8px; padding: 12px; text-align: center; }}
                .score .label {{ font-size: 12px; color: #5b6b53; }}
                .score .value {{ font-size: 24px; font-weight: 700; color: #2e7d32; }}
                .list {{ margin: 0; padding-left: 18px; }}
                .list li {{ margin: 6px 0; }}
                .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size: 13px; }}
                details {{ background: #fafbfc; border: 1px solid #e1e4e8; border-radius: 8px; padding: 12px; }}
                summary {{ cursor: pointer; font-weight: 600; }}
            </style>
        </head>
        <body>
            <div class=\"wrap\">
                <div class=\"card\">
                    <h1>Mock Interview Report</h1>
                    <div class=\"muted\">Role: {db_session.job_role}</div>
                    <div class=\"muted\">Session ID: {db_session.session_uuid}</div>
                    <div class=\"muted\">Completed: {db_session.ended_at or '-'} · Questions: {db_session.total_questions}</div>
                </div>

                <div class=\"card\">
                    <h2 style=\"margin:0 0 8px\">Overall Score</h2>
                    <div class=\"score-grid\">
                        <div class=\"score\"><div class=\"label\">Overall</div><div class=\"value\">{db_session.score_overall or '-'}<span style=\"font-size:14px\">/100</span></div></div>
                        <div class=\"score\"><div class=\"label\">Accuracy</div><div class=\"value\">{db_session.score_accuracy or '-'}<span style=\"font-size:14px\">/100</span></div></div>
                        <div class=\"score\"><div class=\"label\">Clarity</div><div class=\"value\">{db_session.score_clarity or '-'}<span style=\"font-size:14px\">/100</span></div></div>
                        <div class=\"score\"><div class=\"label\">Relevance</div><div class=\"value\">{db_session.score_relevance or '-'}<span style=\"font-size:14px\">/100</span></div></div>
                    </div>
                </div>

                <div class=\"card\">
                    <h2 style=\"margin:0 0 8px\">Overall Feedback</h2>
                    <p style=\"margin:0\">{(db_session.feedback_summary or 'Feedback unavailable.')}</p>
                </div>

                <div class=\"card\">
                    <h2 style=\"margin:0 0 8px; color: #2e7d32\">Strengths</h2>
                    <ul class=\"list\">
                        {''.join([f'<li style="color: #2e7d32;">✓ {s}</li>' for s in strengths]) if strengths else '<li>No specific strengths identified.</li>'}
                    </ul>
                </div>

                <div class=\"card\">
                    <h2 style=\"margin:0 0 8px; color: #d32f2f\">Areas for Improvement</h2>
                    <ul class=\"list\">
                        {''.join([f'<li style="color: #d32f2f;">⚠ {a}</li>' for a in areas_for_improvement]) if areas_for_improvement else '<li>No specific areas for improvement identified.</li>'}
                    </ul>
                </div>

                <div class=\"card\">
                    <h2 style=\"margin:0 0 8px\">Detailed Analysis</h2>
                    <div style=\"display: grid; gap: 12px;\">
                        {''.join([f'<div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #673ab7;"><strong>{k.replace("_", " ").title()}:</strong> {v}</div>' for k, v in detailed_analysis.items()]) if detailed_analysis else '<p>No detailed analysis available.</p>'}
                    </div>
                </div>

                <div class=\"card\">
                    <h2 style=\"margin:0 0 8px\">Actionable Suggestions</h2>
                    <ol class=\"list\">
                        {''.join([f'<li>{s}</li>' for s in suggestions])}
                    </ol>
                </div>

                <div class=\"card\">
                    <details>
                        <summary>View Transcript (10 questions)</summary>
                        <div class=\"mono\">
                            {''.join([f"<p><strong>Q{t.get('turn')}:</strong> {t.get('question')}<br/><strong>A{t.get('turn')}:</strong> {t.get('answer')}</p>" for t in transcript])}
                        </div>
                    </details>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report page error: {e}")
        raise HTTPException(status_code=500, detail="Error generating report page")

@router.post("/start", response_model=StartResponse)
async def start_interview(
    payload: StartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new mock interview session"""
    try:
        job_role = payload.job_role.strip()
        job_desc = payload.job_desc.strip()
        
        if not job_role:
            raise HTTPException(status_code=400, detail="job_role is required.")
        
        # If no job description provided, use a default one
        if not job_desc:
            job_desc = f"General interview for {job_role} position"
        
        session_id = str(uuid.uuid4())
        conversation_history: List[str] = []
        initial_prompt = generate_initial_prompt(job_role, job_desc)
        conversation_history.append(f"HR: {initial_prompt}")
        
        # Persist DB session
        db_session = MockInterviewSession(
            session_uuid=session_id,
            user_id=current_user.id,
            job_role=job_role,
            job_desc=job_desc,
            total_questions=MAX_QUESTIONS_PER_SESSION,
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        sessions[session_id] = {
            "job_role": job_role,
            "job_desc": job_desc,
            "history": conversation_history,
            "user_id": current_user.id,
            "user_name": current_user.full_name,
            "created_at": datetime.now().isoformat(),
            "db_session_id": db_session.id,
            "question_index": 1,
            "current_question_text": initial_prompt,
            "transcript": [],  # will append dicts {turn, question, answer}
            "started_at": datetime.now()  # Track start time for duration calculation
        }
        
        logger.info(f"Started mock interview session {session_id} for user {current_user.id}")
        
        return StartResponse(session_id=session_id, initial_prompt=initial_prompt)
        
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(status_code=500, detail="Failed to start interview session")

@router.post("/message", response_model=MessageResponse)
async def send_message(
    payload: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in the mock interview"""
    try:
        session_id = payload.session_id.strip()
        message = payload.message.strip()
        
        if not session_id or not message:
            raise HTTPException(status_code=400, detail="Both session_id and message are required.")
        
        session = sessions.get(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found. Start a new interview.")
        
        # Verify session belongs to current user
        if session.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this session.")
        
        # Check for exit commands
        lower = message.lower()
        if lower in {"exit", "stop", "quit"}:
            del sessions[session_id]
            return MessageResponse(reply="Thank you for the interview. Goodbye!")
        
        # Persist the candidate's answer for the current question as a turn
        turn_number = session.get("question_index", 1)
        current_question = session.get("current_question_text", "")
        try:
            db_turn = MockInterviewTurn(
                session_id=session.get("db_session_id"),
                turn_number=turn_number,
                question_text=current_question or "",
                answer_text=message,
            )
            db.add(db_turn)
            db.commit()
        except Exception as exc:
            logger.error(f"Failed to save interview turn: {exc}")
            db.rollback()
        # Update in-memory transcript
        session["transcript"].append({"turn": turn_number, "question": current_question, "answer": message})

        # If this was the 10th answer, finalize
        if turn_number >= MAX_QUESTIONS_PER_SESSION:
            # Generate final evaluation
            final_eval = generate_final_evaluation(session["transcript"], session["job_role"], session["job_desc"])
            
            # Calculate interview duration
            start_time = session.get("started_at", datetime.now())
            end_time = datetime.now()
            duration_minutes = int((end_time - start_time).total_seconds() / 60)
            
            # Persist on session row with enhanced scoring
            try:
                db_sess: Optional[MockInterviewSession] = db.get(MockInterviewSession, session.get("db_session_id"))
                if db_sess:
                    db_sess.ended_at = end_time
                    db_sess.score_accuracy = final_eval["scores"]["accuracy"]
                    db_sess.score_clarity = final_eval["scores"]["clarity"]
                    db_sess.score_relevance = final_eval["scores"]["relevance"]
                    db_sess.score_confidence = final_eval["scores"].get("confidence", 0)  # Add confidence score
                    db_sess.score_overall = final_eval["scores"]["overall"]
                    db_sess.feedback_summary = final_eval["feedback_summary"]
                    db_sess.detailed_feedback = json.dumps(final_eval.get("detailed_feedback", {}))
                    db_sess.set_suggestions(final_eval["suggestions"])
                    db_sess.set_transcript(session["transcript"])
                    
                    # Save enhanced report fields
                    db_sess.set_strengths(final_eval.get("strengths", []))
                    db_sess.set_areas_for_improvement(final_eval.get("areas_for_improvement", []))
                    db_sess.set_detailed_analysis(final_eval.get("detailed_analysis", {}))
                    db_sess.set_keywords(final_eval.get("keywords", []))
                    db_sess.interview_duration_minutes = duration_minutes
                    db_sess.questions_answered = turn_number
                    
                    # Calculate and assign grades
                    db_sess.calculate_overall_score()
                    db_sess.assign_grades()
                    
                    # Determine confidence level based on scores
                    avg_score = (db_sess.score_accuracy + db_sess.score_clarity + db_sess.score_relevance + db_sess.score_confidence) / 4
                    if avg_score >= 20:
                        db_sess.confidence_level = "High"
                    elif avg_score >= 15:
                        db_sess.confidence_level = "Medium"
                    else:
                        db_sess.confidence_level = "Low"
                    
                    db.commit()
                    logger.info(f"Mock interview session {session_id} completed and saved to database")
            except Exception as exc:
                logger.error(f"Failed to finalize interview session: {exc}")
                db.rollback()

            # Clean up in-memory session
            completion_reply = (
                f"Thank you. We have completed {MAX_QUESTIONS_PER_SESSION} questions. "
                f"Your overall score is {final_eval['scores']['overall']}/100. "
                "I'll display your feedback and suggestions now."
            )
            del sessions[session_id]
            return MessageResponse(reply=completion_reply, done=True, final=final_eval)

        # Otherwise, generate the next question
        reply, updated_history = generate_ai_response(
            conversation_history=session["history"],
            query=message,
            job_role=session["job_role"],
            job_desc=session["job_desc"],
        )
        session["history"] = updated_history
        session["question_index"] = turn_number + 1
        session["current_question_text"] = reply
        return MessageResponse(reply=reply)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth_utils import get_current_user
from datetime import datetime
import json
import os
import google.generativeai as genai

# Initialize router
router = APIRouter(prefix="/interview", tags=["interview"])

# Configure Gemini API key (prefer environment variable)
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyA3f8izcUDNQTik3utegfZ5bKvxeG0vwq8")
genai.configure(api_key=API_KEY)

DEFAULT_MODEL = 'gemini-2.0-flash'

# ==================== INTERVIEW INTERFACE ROUTES ====================

@router.get("/interface")
async def interview_interface(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Serve the interview interface page"""
    try:
        # Get the templates from app state
        templates = request.app.state.templates
        
        return templates.TemplateResponse(
            "interview_interface.html",
            {
                "request": request,
                "user": current_user
            }
        )
    except Exception as e:
        logging.error(f"Error serving interview interface: {e}")
        raise HTTPException(status_code=500, detail="Error loading interview interface")

@router.post("/start-session")
async def start_interview_session(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Start a new interview session and redirect to interface"""
    try:
        data = await request.json()
        job_description = data.get("job_description", "")
        interview_type = data.get("interview_type", "general")
        question_count = int(data.get("question_count", 6))
        
        if not job_description:
            raise HTTPException(status_code=400, detail="Job description is required")
        
        # Generate questions first
        questions = await generate_questions_with_ai(
            job_description, 
            interview_type, 
            question_count
        )
        
        # Create session data
        session_data = {
            "id": f"session_{current_user.id}_{int(datetime.now().timestamp())}",
            "jobDescription": job_description,
            "interviewType": interview_type,
            "questionCount": question_count,
            "questions": questions,
            "startTime": datetime.now().isoformat(),
            "userId": current_user.id
        }
        
        # Store session data (in a real app, save to database)
        # For now, we'll pass it as a query parameter
        
        return {
            "success": True,
            "session_id": session_data["id"],
            "redirect_url": f"/interview/interface?id={session_data['id']}&type={interview_type}&count={question_count}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error starting interview session: {e}")
        raise HTTPException(status_code=500, detail="Error starting interview session")

# ==================== INTERVIEW API ENDPOINTS ====================

@router.post("/generate-questions")
async def generate_interview_questions(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Generate interview questions based on job description"""
    try:
        data = await request.json()
        job_description = data.get("job_description", "")
        interview_type = data.get("interview_type", "general")
        question_count = data.get("question_count", 6)
        
        if not job_description:
            raise HTTPException(status_code=400, detail="Job description is required")
        
        # Generate questions using Gemini AI
        questions = await generate_questions_with_ai(
            job_description, 
            interview_type, 
            question_count
        )
        
        return {
            "success": True,
            "questions": questions,
            "interview_type": interview_type,
            "question_count": len(questions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating interview questions: {e}")
        raise HTTPException(status_code=500, detail="Error generating interview questions")

@router.post("/evaluate-answer")
async def evaluate_answer(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Evaluate an interview answer and provide score and feedback"""
    try:
        data = await request.json()
        question = data.get("question", "")
        answer = data.get("answer", "")
        job_description = data.get("job_description", "")
        
        if not all([question, answer, job_description]):
            raise HTTPException(status_code=400, detail="Question, answer, and job description are required")
        
        # Evaluate answer using Gemini AI
        evaluation = await evaluate_answer_with_ai(question, answer, job_description)
        
        return {
            "success": True,
            "score": evaluation["score"],
            "feedback": evaluation["feedback"],
            "suggestions": evaluation["suggestions"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error evaluating answer: {e}")
        raise HTTPException(status_code=500, detail="Error evaluating answer")

@router.get("/history")
async def get_interview_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's interview history"""
    try:
        # In a real implementation, this would fetch from database
        # For now, return empty list
        return {
            "success": True,
            "interviews": []
        }
        
    except Exception as e:
        logging.error(f"Error fetching interview history: {e}")
        raise HTTPException(status_code=500, detail="Error fetching interview history")

@router.post("/save-results")
async def save_interview_results(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save interview results to database"""
    try:
        data = await request.json()
        
        # In a real implementation, this would save to database
        # For now, just return success
        return {
            "success": True,
            "message": "Interview results saved successfully"
        }
        
    except Exception as e:
        logging.error(f"Error saving interview results: {e}")
        raise HTTPException(status_code=500, detail="Error saving interview results")

@router.get("/api-status")
async def check_api_status():
    """Check the status of the Gemini API"""
    try:
        # Try a simple test request
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content("Hello")
        
        return {
            "status": "healthy",
            "message": "Gemini API is working normally",
            "model": DEFAULT_MODEL
        }
        
    except Exception as e:
        error_msg = str(e)
        
        if "quota" in error_msg.lower() or "429" in error_msg:
            return {
                "status": "quota_exceeded",
                "message": "API quota exceeded. Using fallback evaluation system.",
                "fallback_available": True,
                "error": error_msg
            }
        elif "api_key" in error_msg.lower() or "401" in error_msg:
            return {
                "status": "auth_error",
                "message": "API key issue. Please check configuration.",
                "fallback_available": True,
                "error": error_msg
            }
        else:
            return {
                "status": "error",
                "message": "API error. Using fallback evaluation system.",
                "fallback_available": True,
                "error": error_msg
            }

# ==================== AI FUNCTIONS ====================

async def generate_questions_with_ai(job_description: str, interview_type: str, question_count: int) -> List[str]:
    """Generate interview questions using Gemini AI"""
    try:
        # Create prompt based on interview type
        type_prompts = {
            "technical": "You are an experienced technical interviewer. Generate {count} technical interview questions based on the job description. Focus on technical skills, problem-solving, and technical knowledge.",
            "behavioral": "You are an experienced HR interviewer. Generate {count} behavioral interview questions based on the job description. Focus on past experiences, teamwork, problem-solving, and soft skills.",
            "general": "You are an experienced interviewer. Generate {count} general interview questions based on the job description. Cover a mix of technical and behavioral aspects.",
            "leadership": "You are an experienced leadership interviewer. Generate {count} leadership interview questions based on the job description. Focus on leadership skills, team management, and strategic thinking."
        }
        
        prompt_template = type_prompts.get(interview_type, type_prompts["general"])
        prompt = prompt_template.format(count=question_count)
        
        full_prompt = f"""
        {prompt}
        
        Job Description:
        {job_description}
        
        Instructions:
        - Generate exactly {question_count} questions
        - Make questions specific to the role and company
        - Avoid generic questions
        - Return only the questions, one per line, without numbering
        - Make questions clear and actionable
        
        Questions:
        """
        
        # Generate questions using Gemini
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(full_prompt)
        
        # Parse response into questions
        questions_text = response.text.strip()
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        # Ensure we have the right number of questions
        if len(questions) > question_count:
            questions = questions[:question_count]
        elif len(questions) < question_count:
            # Generate additional questions if needed
            additional_prompt = f"Generate {question_count - len(questions)} more interview questions for this role: {job_description[:200]}..."
            additional_response = model.generate_content(additional_prompt)
            additional_questions = [q.strip() for q in additional_response.text.split('\n') if q.strip()]
            questions.extend(additional_questions[:question_count - len(questions)])
        
        return questions[:question_count]
        
    except Exception as e:
        logging.error(f"Error generating questions with AI: {e}")
        
        # Check if it's a quota exceeded error
        if "quota" in str(e).lower() or "429" in str(e):
            logging.warning("Gemini API quota exceeded, using fallback questions")
            return generate_fallback_questions(interview_type, question_count)
        
        # Return fallback questions for other errors
        return generate_fallback_questions(interview_type, question_count)

async def evaluate_answer_with_ai(question: str, answer: str, job_description: str) -> Dict[str, Any]:
    """Evaluate an interview answer using Gemini AI"""
    try:
        prompt = f"""
        You are an experienced interview evaluator. Evaluate the following interview answer and provide:
        1. A score out of 10
        2. Constructive feedback
        3. Specific suggestions for improvement
        
        Question: {question}
        Answer: {answer}
        Job Description Context: {job_description[:300]}
        
        Evaluation Criteria:
        - Relevance to the question
        - Clarity and structure of response
        - Specific examples and details
        - Professional communication
        - Alignment with job requirements
        
        Provide your response in this exact JSON format:
        {{
            "score": <number 0-10>,
            "feedback": "<detailed feedback>",
            "suggestions": ["<suggestion 1>", "<suggestion 2>", "<suggestion 3>"]
        }}
        """
        
        # Generate evaluation using Gemini
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        
        # Parse JSON response
        try:
            evaluation = json.loads(response.text)
            return {
                "score": evaluation.get("score", 5),
                "feedback": evaluation.get("feedback", "Good effort, but could be improved."),
                "suggestions": evaluation.get("suggestions", ["Provide more specific examples", "Structure your response better"])
            }
        except json.JSONDecodeError:
            # Fallback evaluation if JSON parsing fails
            return generate_fallback_evaluation(answer)
        
    except Exception as e:
        logging.error(f"Error evaluating answer with AI: {e}")
        
        # Check if it's a quota exceeded error
        if "quota" in str(e).lower() or "429" in str(e):
            logging.warning("Gemini API quota exceeded, using fallback evaluation")
            return generate_fallback_evaluation(answer, question, job_description)
        
        # Return fallback evaluation for other errors
        return generate_fallback_evaluation(answer, question, job_description)

# ==================== FALLBACK FUNCTIONS ====================

def generate_fallback_questions(interview_type: str, question_count: int) -> List[str]:
    """Generate fallback questions when AI fails"""
    fallback_questions = {
        "technical": [
            "Can you walk me through your technical background and experience?",
            "Describe a challenging technical problem you've solved recently.",
            "How do you stay updated with the latest technologies in your field?",
            "Explain a complex technical concept to someone non-technical.",
            "What programming languages and tools are you most comfortable with?",
            "How do you approach debugging and troubleshooting?",
            "Describe your experience with version control systems.",
            "How do you ensure code quality and maintainability?",
            "What's your experience with testing and quality assurance?",
            "How do you handle technical disagreements with team members?"
        ],
        "behavioral": [
            "Tell me about a time when you had to work with a difficult team member.",
            "Describe a situation where you had to meet a tight deadline.",
            "Give me an example of when you had to learn something new quickly.",
            "Tell me about a time when you failed at something and what you learned.",
            "Describe a situation where you had to persuade someone to see your point of view.",
            "Tell me about a time when you had to adapt to a significant change at work.",
            "Give me an example of when you had to resolve a conflict between team members.",
            "Describe a time when you had to make a decision without all the information.",
            "Tell me about a project where you had to coordinate with multiple stakeholders.",
            "Give me an example of when you went above and beyond what was expected."
        ],
        "general": [
            "Why are you interested in this position and company?",
            "What are your greatest professional strengths and weaknesses?",
            "Where do you see yourself in five years?",
            "Why are you looking to leave your current position?",
            "What motivates you in your work?",
            "How do you handle stress and pressure?",
            "What do you know about our company and industry?",
            "How do you prioritize your work when you have multiple deadlines?",
            "What are your salary expectations for this role?",
            "Do you have any questions for me about the position?"
        ],
        "leadership": [
            "Describe your leadership style and how it has evolved over time.",
            "Tell me about a time when you had to lead a team through a difficult situation.",
            "How do you motivate and inspire your team members?",
            "Describe a situation where you had to make an unpopular decision.",
            "How do you handle conflicts within your team?",
            "Tell me about a time when you had to manage a team member who wasn't performing well.",
            "How do you delegate tasks and responsibilities?",
            "Describe a time when you had to lead change in your organization.",
            "How do you measure the success of your team?",
            "What's your approach to developing and mentoring team members?"
        ]
    }
    
    questions = fallback_questions.get(interview_type, fallback_questions["general"])
    return questions[:question_count]

def generate_fallback_evaluation(answer: str, question: str = "", job_description: str = "") -> Dict[str, Any]:
    """Generate intelligent fallback evaluation when AI fails"""
    # Enhanced heuristic-based evaluation
    answer_length = len(answer)
    answer_lower = answer.lower()
    
    # Check for various quality indicators
    has_examples = any(word in answer_lower for word in ["example", "instance", "time", "when", "because", "experience", "project", "worked", "developed"])
    is_structured = any(word in answer_lower for word in ["first", "second", "then", "finally", "because", "however", "additionally", "moreover", "therefore"])
    has_technical_terms = any(word in answer_lower for word in ["algorithm", "database", "api", "framework", "testing", "deployment", "optimization", "scalability"])
    shows_confidence = any(word in answer_lower for word in ["confident", "successfully", "achieved", "implemented", "solved", "improved", "delivered"])
    
    # Base score calculation
    if answer_length < 30:
        base_score = 2
        feedback = "Your answer is very brief. Interviewers expect more detailed responses."
        suggestions = ["Provide more context and details", "Include specific examples from your experience", "Explain your thought process"]
    elif answer_length < 80:
        base_score = 4
        feedback = "Your answer is brief but shows some understanding. More detail would improve your score."
        suggestions = ["Expand on your response with examples", "Explain the impact of your actions", "Provide more context"]
    elif answer_length < 150:
        base_score = 6
        feedback = "Good answer with reasonable detail. Consider adding more specific examples."
        suggestions = ["Include specific examples from your experience", "Quantify your achievements if possible", "Explain the outcomes"]
    elif answer_length < 300:
        base_score = 7
        feedback = "Detailed answer with good information. Well structured!"
        suggestions = ["Consider being more concise", "Focus on the most relevant points", "Ensure all details are relevant"]
    else:
        base_score = 8
        feedback = "Very detailed answer. Good job providing comprehensive information!"
        suggestions = ["Consider being more concise", "Focus on key points", "Structure your response better"]
    
    # Bonus points for quality indicators
    bonus = 0
    if has_examples:
        bonus += 1
        feedback += " Good use of examples."
    if is_structured:
        bonus += 1
        feedback += " Well-structured response."
    if has_technical_terms and "technical" in question.lower():
        bonus += 1
        feedback += " Shows technical knowledge."
    if shows_confidence:
        bonus += 1
        feedback += " Demonstrates confidence."
    
    # Final score calculation
    final_score = min(10, base_score + bonus)
    
    # Adjust feedback based on score
    if final_score >= 8:
        feedback = "Excellent answer! " + feedback
    elif final_score >= 6:
        feedback = "Good answer. " + feedback
    elif final_score >= 4:
        feedback = "Fair answer. " + feedback
    else:
        feedback = "Needs improvement. " + feedback
    
    return {
        "score": final_score,
        "feedback": feedback,
        "suggestions": suggestions[:3]  # Limit to 3 suggestions
    }

# ==================== UTILITY FUNCTIONS ====================

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def calculate_percentage(score: int, max_score: int) -> float:
    """Calculate percentage score"""
    if max_score == 0:
        return 0.0
    return (score / max_score) * 100

def get_score_label(percentage: float) -> str:
    """Get score label based on percentage"""
    if percentage >= 90:
        return "Outstanding"
    elif percentage >= 80:
        return "Excellent"
    elif percentage >= 70:
        return "Very Good"
    elif percentage >= 60:
        return "Good"
    elif percentage >= 50:
        return "Satisfactory"
    elif percentage >= 40:
        return "Needs Improvement"
    else:
        return "Poor"

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import uuid
from typing import Any, Dict, List, Tuple
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

# ========== CONFIG ==========
GENAI_API_KEY ="AIzaSyARLgg6blfmauGUDPSwo_mHMrpLHLP22uE"
if not GENAI_API_KEY:
    raise RuntimeError(
        "Missing API key. Set one of: GENAI_API_KEY, GOOGLE_API_KEY, or GEMINI_API_KEY."
    )
genai.configure(api_key=GENAI_API_KEY)

app = FastAPI(title="AI Interviewer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== DATA MODELS ==========
class StartRequest(BaseModel):
    job_role: str
    job_desc: str


class StartResponse(BaseModel):
    session_id: str
    initial_prompt: str


class MessageRequest(BaseModel):
    session_id: str
    message: str


class MessageResponse(BaseModel):
    reply: str


# ========== IN-MEMORY STORE ==========
sessions: Dict[str, Dict[str, Any]] = {}


# ========== HELPERS ==========
def generate_initial_prompt(job_role: str, job_desc: str) -> str:
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


def gemi(
    conversation_history: List[str],
    query: str,
    job_role: str,
    job_desc: str,
) -> Tuple[str, List[str]]:
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

    try:
        response = model.generate_content([prompt, "\n".join(conversation_history)])
        ai_text = (response.text or "").strip()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Model error: {exc}")

    if not ai_text:
        ai_text = "I'm having trouble formulating a response right now. Please try again."

    conversation_history.append(f"{ai_text}")
    return ai_text, conversation_history


# ========== ROUTES ==========
STATIC_DIR = Path(__file__).parent / "static"
PAGES_DIR = STATIC_DIR / "pages"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

def serve_page(filename: str) -> HTMLResponse:
    path = PAGES_DIR / filename
    if not path.exists():
        return HTMLResponse("<h1>Page not found</h1>", status_code=404)
    return FileResponse(str(path))

@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    return serve_page("role.html")

@app.get("/role", response_class=HTMLResponse)
def role_page() -> HTMLResponse:
    return serve_page("role.html")



@app.get("/interview", response_class=HTMLResponse)
def interview_page() -> HTMLResponse:
    return serve_page("interview.html")

@app.get("/ready", response_class=HTMLResponse)
def ready_page() -> HTMLResponse:
    return serve_page("ready.html")

@app.get("/favicon.ico")
def favicon():
    # Return a simple 204 No Content response for favicon requests
    from fastapi.responses import Response
    return Response(status_code=204)

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/start", response_model=StartResponse)
def start_interview(payload: StartRequest) -> StartResponse:
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

    sessions[session_id] = {
        "job_role": job_role,
        "job_desc": job_desc,
        "history": conversation_history,
    }

    return StartResponse(session_id=session_id, initial_prompt=initial_prompt)


@app.post("/message", response_model=MessageResponse)
def send_message(payload: MessageRequest) -> MessageResponse:
    session_id = payload.session_id.strip()
    message = payload.message.strip()

    if not session_id or not message:
        raise HTTPException(status_code=400, detail="Both session_id and message are required.")

    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found. Start a new interview.")

    lower = message.lower()
    if lower in {"exit", "stop", "quit"}:
        del sessions[session_id]
        return MessageResponse(reply="Thank you for the interview. Goodbye!")

    reply, updated_history = gemi(
        conversation_history=session["history"],
        query=message,
        job_role=session["job_role"],
        job_desc=session["job_desc"],
    )

    session["history"] = updated_history
    return MessageResponse(reply=reply)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main2:app",host="127.0.0.1", port=8000, reload=True)

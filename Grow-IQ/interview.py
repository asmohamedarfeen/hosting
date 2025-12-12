import os
import google.generativeai as genai
import cv2
import time
import pyttsx3
import speech_recognition as sr
import threading
import keyboard  # pip install keyboard
import json
from datetime import datetime

# Configure Gemini API key (prefer environment variable)
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyA3f8izcUDNQTik3utegfZ5bKvxeG0vwq8")  # Replace with your actual key or set GEMINI_API_KEY
genai.configure(api_key=API_KEY)

DEFAULT_MODEL = 'gemini-2.0-flash'


def generate_interview_questions(job_description):
    prompt = (
        "You are an experienced HR interviewer at a top MNC. Based on the following job description, "
        "generate a list of 6 short, clear, and role-relevant interview questions. "
        "Avoid prefacing text; return only the questions, one per line, without numbering.\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Questions:"
    )
    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating questions: {e}")
        return ""


def record_webcam_video(filename="interview_recording.avi", stop_event=None):
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

    print("Recording started. Press 'ESC' to stop.")

    while not (stop_event and stop_event.is_set()):
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('Recording (press ESC to stop)', frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                if stop_event:
                    stop_event.set()
                break
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Recording saved as {filename}")


def speak_text(text):
    if not text:
        return
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def listen_to_answer(timeout=20):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    print("Listening for your answer... (speak now)")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=timeout)
            print("Recognizing...")
            answer = recognizer.recognize_google(audio)
            print(f"You said: {answer}")
            return answer
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return ""
        except sr.UnknownValueError:
            print("Sorry, could not understand the audio.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""


def esc_listener(stop_event):
    print("Press ESC at any time to stop the interview and recording.")
    keyboard.wait('esc')
    stop_event.set()


# --------- Evaluation and reporting helpers ---------

def safe_json_from_text(text):
    """Attempt to parse JSON from model text. Returns dict or None."""
    if not text:
        return None
    # Direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to extract JSON object by braces window
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            return None
    return None


def evaluate_answer(job_description, question, answer, max_score=10):
    """Ask Gemini to grade the answer. Returns dict with score, feedback, optional follow_up."""
    if not answer:
        return {
            "score": 0,
            "feedback": "No audible answer captured.",
            "follow_up": None
        }

    # Check if user said they don't know or can't answer
    answer_lower = answer.lower()
    dont_know_phrases = [
        "i don't know", "i don't know", "i can't answer", "i can't answer this",
        "i'm not sure", "i'm not sure", "i don't have experience", "i don't have experience",
        "i can't think", "i can't think of", "i don't remember", "i don't remember"
    ]
    
    is_uncertain = any(phrase in answer_lower for phrase in dont_know_phrases)

    if is_uncertain:
        # Generate encouraging follow-up to help them think through it
        system_prompt = (
            "You are a supportive HR interviewer. The candidate seems uncertain about the question. "
            "Generate an encouraging follow-up question that helps them think through the topic "
            "or provides a different angle to approach the question. Be supportive and helpful.\n"
            "Respond with STRICT JSON only:\n"
            "{\n"
            "  \"score\": integer (0 to " + str(max_score) + "),\n"
            "  \"feedback\": string (encouraging feedback),\n"
            "  \"follow_up\": string (encouraging follow-up question to help them think)\n"
            "}\n"
        )
    else:
        # Normal evaluation with potential follow-up for clarification
        system_prompt = (
            "You are an HR interviewer at a top MNC. Grade the candidate's answer fairly and concisely.\n"
            "Consider role requirements and depth, accuracy, clarity, and examples.\n"
            "If the answer could benefit from more detail or clarification, suggest a follow-up question.\n"
            "Respond with STRICT JSON only, no code fences and no extra text, with this schema:\n"
            "{\n"
            "  \"score\": integer (0 to " + str(max_score) + "),\n"
            "  \"feedback\": string (2-4 sentences),\n"
            "  \"follow_up\": string or null (ask only if clarification would help)\n"
            "}\n"
        )

    user_context = (
        f"Job Description:\n{job_description}\n\n"
        f"Question: {question}\n"
        f"Candidate Answer: {answer}\n"
        f"Maximum Score: {max_score}\n"
    )

    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content([system_prompt, user_context])
        data = safe_json_from_text(getattr(response, 'text', '') or '')
        if not data:
            # Fallback minimal
            return {
                "score": 0,
                "feedback": "Could not parse evaluation.",
                "follow_up": None
            }
        # Clamp score
        try:
            score_val = int(data.get("score", 0))
        except Exception:
            score_val = 0
        score_val = max(0, min(max_score, score_val))
        return {
            "score": score_val,
            "feedback": data.get("feedback", ""),
            "follow_up": data.get("follow_up")
        }
    except Exception as e:
        print(f"Evaluation error: {e}")
        return {
            "score": 0,
            "feedback": "Evaluation failed due to an error.",
            "follow_up": None
        }


def generate_contextual_followup(job_description, all_previous_qa, current_question, current_answer, follow_up_answer=""):
    """Generate a contextual follow-up based on all previous Q&A and current responses."""
    
    # Build context from previous Q&A
    context_summary = ""
    if all_previous_qa:
        context_summary = "Previous Q&A Context:\n"
        for qa in all_previous_qa[-3:]:  # Last 3 Q&A for context
            context_summary += f"Q: {qa['question']}\nA: {qa.get('answer', '')}\n"
    
    system_prompt = (
        "You are a conversational HR interviewer. Based on the candidate's previous answers and current response, "
        "generate a natural follow-up question that builds on what they've shared or explores related areas. "
        "Be conversational, encouraging, and supportive. Consider their experience level and previous responses. "
        "If they seem uncertain, try to help them think through it from a different angle or relate it to their experience.\n"
        "Respond with STRICT JSON only:\n"
        "{\n"
        "  \"follow_up\": string (natural, conversational follow-up question)\n"
        "}\n"
    )
    
    user_context = (
        f"Job Description:\n{job_description}\n\n"
        f"{context_summary}\n"
        f"Current Question: {current_question}\n"
        f"Current Answer: {current_answer}\n"
        f"Follow-up Answer: {follow_up_answer}\n"
    )
    
    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content([system_prompt, user_context])
        data = safe_json_from_text(getattr(response, 'text', '') or '')
        if data and data.get("follow_up"):
            return data["follow_up"]
    except Exception as e:
        print(f"Contextual follow-up error: {e}")
    
    return None


def write_text_report(report_path, report):
    lines = []
    lines.append(f"Interview Report - {report.get('timestamp')}")
    lines.append("")
    lines.append(f"Job Summary: {report.get('job_summary','N/A')}")
    lines.append("")
    lines.append(f"Total Score: {report.get('total_score',0)} / {report.get('max_total',0)}")
    lines.append("")
    for idx, q in enumerate(report.get('questions', []), 1):
        lines.append(f"Q{idx}: {q['question']}")
        lines.append(f"Answer: {q.get('answer','')}")
        if q.get('follow_up'):
            lines.append(f"Follow-up asked: {q['follow_up']}")
            lines.append(f"Follow-up answer: {q.get('follow_up_answer','')}")
        lines.append(f"Score: {q['score']} / {q['max_score']}")
        if q.get('feedback'):
            lines.append(f"Feedback: {q['feedback']}")
        lines.append("")

    content = "\n".join(lines)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == "__main__":
    stop_event = threading.Event()

    # Start ESC listener
    esc_thread = threading.Thread(target=esc_listener, args=(stop_event,), daemon=True)
    esc_thread.start()

    # Start video recording in a separate thread
    video_thread = threading.Thread(
        target=record_webcam_video,
        kwargs={"filename": "interview_recording.avi", "stop_event": stop_event}
    )
    video_thread.start()

    # Proceed with the interview
    job_desc = input("Paste the job description:\n")
    questions_text = generate_interview_questions(job_desc)

    if not questions_text:
        print("Could not generate questions. Exiting.")
        stop_event.set()
        video_thread.join()
        raise SystemExit(1)

    print("\nGenerated Interview Questions:\n")

    # Prepare questions list: one per non-empty line, strip bullets/numbering
    raw_lines = [q.strip() for q in questions_text.split('\n') if q.strip()]
    question_list = []
    for line in raw_lines:
        # Remove leading numbering/bullets (e.g., "1.", "- ", "• ")
        cleaned = line
        if cleaned[:2].lower() in {"- ", "• ", "* "}:
            cleaned = cleaned[2:].strip()
        # Remove numeric prefixes like "1.", "2)"
        while cleaned and (cleaned[0].isdigit() or cleaned[0] in {')', '.', '-' }):
            # Find first space after prefix
            if '. ' in cleaned[:4]:
                cleaned = cleaned.split('. ', 1)[1]
                break
            if ') ' in cleaned[:4]:
                cleaned = cleaned.split(') ', 1)[1]
                break
            if ' ' in cleaned:
                # If just a single digit then space
                parts = cleaned.split(' ', 1)
                if parts[0].strip('.)(').isdigit():
                    cleaned = parts[1]
                    break
            break
        question_list.append(cleaned.strip())

    asked_questions = set()
    per_question_max = 10

    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "job_summary": job_desc[:300],
        "questions": [],
        "total_score": 0,
        "max_total": 0,
    }

    all_previous_qa = [] # Initialize list to store previous Q&A

    for idx, question in enumerate(question_list, 1):
        if stop_event.is_set():
            break
        normalized = question.lower().strip()
        if normalized in asked_questions:
            continue
        asked_questions.add(normalized)

        # Ask question
        print(f"Question {idx}: {question}")
        speak_text(question)
        answer = listen_to_answer(timeout=25)

        # Evaluate
        eval_result = evaluate_answer(job_desc, question, answer, max_score=per_question_max)
        score = eval_result.get("score", 0)
        feedback = eval_result.get("feedback", "")
        follow_up = eval_result.get("follow_up")

        # Optional follow-up - now more contextual and conversational
        follow_up_answer = ""
        if follow_up and isinstance(follow_up, str) and follow_up.strip():
            # Check if this is an encouraging follow-up (user was uncertain)
            answer_lower = answer.lower()
            is_uncertain_initial = any(phrase in answer_lower for phrase in [
                "i don't know", "i can't answer", "i'm not sure", "i don't have experience"
            ])
            
            if is_uncertain_initial:
                print("That's okay! Let me try to help you think through this...")
                speak_text("That's okay! Let me try to help you think through this.")
            
            print(f"Follow-up: {follow_up}")
            speak_text(follow_up)
            follow_up_answer = listen_to_answer(timeout=20)
            
            # If they still seem uncertain, try another encouraging approach
            if follow_up_answer:
                follow_up_lower = follow_up_answer.lower()
                still_uncertain = any(phrase in follow_up_lower for phrase in [
                    "i don't know", "i can't answer", "i'm not sure", "i don't have experience"
                ])
                
                if still_uncertain:
                    # Generate a second encouraging follow-up
                    print("I understand this might be challenging. Let me try a different approach...")
                    speak_text("I understand this might be challenging. Let me try a different approach.")
                    second_followup = generate_contextual_followup(
                        job_desc, all_previous_qa, question, answer, follow_up_answer
                    )
                    if second_followup:
                        print(f"Let me try a different angle: {second_followup}")
                        speak_text(second_followup)
                        second_followup_answer = listen_to_answer(timeout=20)
                        if second_followup_answer:
                            follow_up_answer += " " + second_followup_answer
                            # Light score boost for attempting the second follow-up
                            score = min(per_question_max, score + 1)
                            print("Thank you for trying to answer that follow-up question!")
            
            # Optionally do a light re-evaluation boost if follow-up was strong
            if follow_up_answer:
                # Simple heuristic: ask model to adjust up to +2 points
                try:
                    adjust_prompt = (
                        "Given the original question, original answer, and follow-up answer, "
                        "adjust the previous score by adding 0, 1, or 2 points if the follow-up meaningfully improved the answer.\n"
                        "Respond with STRICT JSON: {\"delta\": integer in [0,2]}"
                    )
                    context = (
                        f"Question: {question}\n"
                        f"Original Answer: {answer}\n"
                        f"Follow-up Answer: {follow_up_answer}\n"
                        f"Previous Score: {score}\n"
                        f"Max Score: {per_question_max}\n"
                    )
                    model = genai.GenerativeModel(DEFAULT_MODEL)
                    resp = model.generate_content([adjust_prompt, context])
                    data = safe_json_from_text(getattr(resp, 'text', '') or '')
                    if data and isinstance(data.get('delta'), int):
                        score = max(0, min(per_question_max, score + int(data['delta'])))
                except Exception as e:
                    print(f"Follow-up adjustment error: {e}")

        # Accumulate
        report["questions"].append({
            "question": question,
            "answer": answer,
            "score": score,
            "max_score": per_question_max,
            "feedback": feedback,
            "follow_up": follow_up,
            "follow_up_answer": follow_up_answer,
        })
        report["total_score"] += score
        report["max_total"] += per_question_max

        # Add current Q&A to history
        all_previous_qa.append({
            "question": question,
            "answer": answer,
            "follow_up_answer": follow_up_answer,
        })

        print(f"Score for this question: {score} / {per_question_max}\n")

    # Wrap up
    stop_event.set()
    video_thread.join()

    print("Interview complete.")
    print(f"Total Score: {report['total_score']} / {report['max_total']}")
    
    # Provide comprehensive feedback at the end
    print("\n" + "="*50)
    print("INTERVIEW FEEDBACK SUMMARY")
    print("="*50)
    
    # Calculate percentage
    percentage = (report['total_score'] / report['max_total']) * 100 if report['max_total'] > 0 else 0
    
    # Overall assessment
    if percentage >= 80:
        overall_assessment = "Excellent performance! You demonstrated strong knowledge and communication skills."
    elif percentage >= 60:
        overall_assessment = "Good performance! You showed solid understanding with room for improvement."
    elif percentage >= 40:
        overall_assessment = "Fair performance. Consider reviewing key areas and practicing responses."
    else:
        overall_assessment = "Needs improvement. Focus on understanding the role requirements and practicing interview skills."
    
    print(f"\nOverall Assessment: {overall_assessment}")
    print(f"Final Score: {report['total_score']}/{report['max_total']} ({percentage:.1f}%)")
    
    # Detailed feedback for each question
    print("\nDetailed Feedback:")
    print("-" * 30)
    for idx, q in enumerate(report['questions'], 1):
        print(f"\nQuestion {idx}: {q['question']}")
        print(f"Your Answer: {q.get('answer', 'No answer captured')}")
        if q.get('follow_up'):
            print(f"Follow-up: {q['follow_up']}")
            print(f"Follow-up Answer: {q.get('follow_up_answer', 'No answer captured')}")
        print(f"Score: {q['score']}/{q['max_score']}")
        if q.get('feedback'):
            print(f"Feedback: {q['feedback']}")
        print("-" * 30)
    
    # Speak the overall assessment
    speak_text(f"Interview complete. Your final score is {report['total_score']} out of {report['max_total']}. {overall_assessment}")

    # Save report
    out_txt = "interview_report.txt"
    out_json = "interview_report.json"
    write_text_report(out_txt, report)
    with open(out_json, 'w', encoding='utf-8') as jf:
        json.dump(report, jf, indent=2, ensure_ascii=False)

    print(f"\nReport saved to {out_txt} and {out_json}.")

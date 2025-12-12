from google import genai
from google.genai import types
import pathlib
import json
import os
from datetime import datetime

class ATSResumeScorer:
    def __init__(self, api_key=None):
        # Initialize the client with the API key from environment or provided
        if api_key is None:
            api_key = "AIzaSyA3f8izcUDNQTik3utegfZ5bKvxeG0vwq8"
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
        
    def score_resume(self, pdf_path):
        """Score a resume using ATS criteria"""
        
        filepath = pathlib.Path(pdf_path)
        
        # Check if file exists
        if not filepath.exists():
            return f"Error: File not found at {pdf_path}"
        
        # Structured ATS scoring prompt
        ats_prompt = """
        Analyze this resume as an ATS (Applicant Tracking System) and provide a scoring report.
        
        Evaluate the resume based on these criteria:
        
        1. **Content Quality (25 points)**
           - Professional writing style
           - Information relevance
           - Section completeness
        
        2. **Skills Match (25 points)**
           - Technical skills alignment
           - Soft skills demonstration
           - Industry keywords presence
        
        3. **Experience & Achievements (25 points)**
           - Quantified accomplishments
           - Relevant work history
           - Career growth pattern
        
        4. **Format & Structure (15 points)**
           - Clean, scannable layout
           - Logical information flow
           - Professional appearance
        
        5. **Education & Certifications (10 points)**
           - Educational qualifications
           - Professional certifications
           - Continuous learning evidence
        
        Return ONLY a Python dictionary in this exact format:
        {
            "content_quality": {"score": X, "explanation": "detailed explanation","total_score": X},
            "skills_match": {"score": X, "explanation": "detailed explanation","total_score": X},
            "experience_achievements": {"score": X, "explanation": "detailed explanation","total_score": X},
            "format_structure": {"score": X, "explanation": "detailed explanation","total_score": X},
            "education_certifications": {"score": X, "explanation": "detailed explanation","total_score": X},
            "total_score": X
        }
        
        Where X is the numerical score for each category. Do not include any other text, only the dictionary.
        """
        
        try:
            # Read PDF file bytes
            pdf_bytes = filepath.read_bytes()
            
            # Create content with proper structure matching the user's code pattern
            # Text parts are added as strings, binary parts use types.Part.from_bytes
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            mime_type="application/pdf",
                            data=pdf_bytes
                        ),
                        types.Part.from_text(text=ats_prompt)
                    ]
                )
            ]
            
            # Generate content using the model
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents
            )
            
            # Extract text from response
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            return self._parse_dictionary_response(response_text, pdf_path)
            
        except Exception as e:
            return f"Error analyzing resume: {str(e)}"
    
    def _parse_dictionary_response(self, response_text, pdf_path):
        """Parse the AI response and return a Python dictionary"""
        try:
            # Clean the response text to extract just the dictionary
            cleaned_text = response_text.strip()
            
            # Remove any markdown formatting if present
            if cleaned_text.startswith('```python'):
                cleaned_text = cleaned_text.replace('```python', '').replace('```', '').strip()
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text.replace('```', '').strip()
            
            # Parse the dictionary
            import ast
            result_dict = ast.literal_eval(cleaned_text)
            
            # Add metadata
            result_dict['metadata'] = {
                'filename': pathlib.Path(pdf_path).stem,
                'filepath': pdf_path,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return result_dict
            
        except Exception as e:
            # If parsing fails, return error with original response
            return {
                'error': f"Failed to parse response: {str(e)}",
                'raw_response': response_text,
                'metadata': {
                    'filename': pathlib.Path(pdf_path).stem,
                    'filepath': pdf_path,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
    
    def _format_report(self, analysis_text, pdf_path):
        """Format the analysis into a structured report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = pathlib.Path(pdf_path).stem
        
        report = f"""
{'='*70}
                    ATS RESUME SCORING REPORT
{'='*70}

Date: {timestamp}
Resume: {filename}
File Path: {pdf_path}

{'='*70}
                    ANALYSIS RESULTS
{'='*70}

{analysis_text}

{'='*70}
                    REPORT SUMMARY
{'='*70}

This report was generated using Google Gemini AI for ATS optimization.
The analysis evaluates resume effectiveness for automated screening systems.

Recommendations:
• Review and implement suggested improvements
• Add missing keywords relevant to target positions
• Consider format adjustments for better ATS parsing
• Quantify achievements where possible

{'='*70}
                    END OF REPORT
{'='*70}
"""
        return report
    
    def save_report(self, report_text, output_path=None):
        """Save the report to a file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"ats_report_{timestamp}.txt"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            return f"Report saved to: {output_path}"
        except Exception as e:
            return f"Error saving report: {str(e)}" 
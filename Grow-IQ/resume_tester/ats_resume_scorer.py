import google.generativeai as genai
import pathlib
import json
import os
import time
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class ATSResumeScorer:
    def __init__(self, api_key=None):
        # Initialize the API key from environment or provided
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyA3f8izcUDNQTik3utegfZ5bKvxeG0vwq8")
        genai.configure(api_key=api_key)
        self.model_name = "gemini-2.0-flash-exp"
        
    def _extract_retry_delay(self, error_message):
        """Extract retry delay from error message if available"""
        try:
            # Look for "Please retry in X.XXs" pattern
            import re
            match = re.search(r'Please retry in ([\d.]+)s', error_message)
            if match:
                return float(match.group(1))
        except Exception:
            pass
        return None
        
    def score_resume(self, pdf_path, max_retries=3):
        """Score a resume using ATS criteria with retry logic for quota errors"""
        
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
        
        CRITICAL: You must respond with ONLY a valid JSON object. No other text, no explanations, no markdown formatting. Start your response with { and end with }.

        Required JSON format (EXACT format required):
        {
            "content_quality": {"score": 20, "explanation": "detailed explanation here", "total_score": 25},
            "skills_match": {"score": 22, "explanation": "detailed explanation here", "total_score": 25},
            "experience_achievements": {"score": 18, "explanation": "detailed explanation here", "total_score": 25},
            "format_structure": {"score": 12, "explanation": "detailed explanation here", "total_score": 15},
            "education_certifications": {"score": 8, "explanation": "detailed explanation here", "total_score": 10},
            "total_score": 80
        }

        STRICT RULES - FOLLOW EXACTLY:
        1. Use ONLY double quotes for all strings
        2. All numbers must be integers (no decimals)
        3. total_score must equal the sum of all individual scores
        4. Start response with { and end with }
        5. No text before or after the JSON
        6. No markdown code blocks or formatting
        7. No additional text or explanations
        8. Response must be valid JSON that can be parsed directly
        """
        
        # Read PDF file bytes once
        pdf_bytes = filepath.read_bytes()
        
        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(max_retries):
            try:
                # Initialize the model
                model = genai.GenerativeModel(self.model_name)
                
                # Upload the PDF file to Google's servers
                # The upload_file function requires a file path, so we use the existing path
                uploaded_file = genai.upload_file(path=str(filepath), mime_type="application/pdf")
                
                # Generate content using the model with the uploaded file and prompt
                response = model.generate_content([uploaded_file, ats_prompt])
                
                # Clean up: delete the uploaded file after use
                try:
                    genai.delete_file(uploaded_file.name)
                except Exception:
                    pass  # Ignore cleanup errors
                
                # Extract text from response
                response_text = response.text if hasattr(response, 'text') else str(response)
                
                # Check if response is valid
                if not response_text:
                    return f"Error: No response received from AI model"
                
                # Parse the response
                result = self._parse_dictionary_response(response_text, pdf_path)
                
                # If result is a string (error), return it
                if isinstance(result, str):
                    return result
                
                # Validate the result structure
                if not isinstance(result, dict):
                    return f"Error: Invalid response format from AI model"
                
                # Check if it's an error response
                if 'error' in result:
                    return f"Error parsing AI response: {result['error']}"
                
                return result
                
            except Exception as e:
                error_str = str(e)
                last_exception = e
                
                # Check if it's a quota/rate limit error (429)
                is_quota_error = "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower()
                
                if is_quota_error and attempt < max_retries - 1:
                    # Extract retry delay from error message if available
                    retry_delay = self._extract_retry_delay(error_str)
                    if retry_delay is None:
                        # Use exponential backoff: 2^attempt seconds
                        retry_delay = min(2 ** attempt, 60)  # Cap at 60 seconds
                    else:
                        # Add a small buffer to the retry delay
                        retry_delay = retry_delay + 1
                    
                    logger.warning(f"Quota/rate limit error on attempt {attempt + 1}/{max_retries}. Retrying in {retry_delay:.2f} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    # Not a quota error or max retries reached
                    if attempt < max_retries - 1:
                        # For other errors, use shorter exponential backoff
                        retry_delay = min(2 ** attempt, 10)  # Cap at 10 seconds
                        logger.warning(f"Error on attempt {attempt + 1}/{max_retries}: {error_str}. Retrying in {retry_delay:.2f} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        # Max retries reached
                        return f"Error analyzing resume after {max_retries} attempts: {str(e)}"
        
        # If we get here, all retries failed
        return f"Error analyzing resume after {max_retries} attempts: {str(last_exception)}"
    
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
            
            # Try to find the dictionary in the response
            import re
            import ast
            
            # Find the JSON dictionary in the response
            # Look for the start and end of a JSON object
            dict_start = cleaned_text.find('{')
            dict_end = cleaned_text.rfind('}')
            
            if dict_start != -1 and dict_end != -1 and dict_end > dict_start:
                cleaned_text = cleaned_text[dict_start:dict_end + 1]
            else:
                # If no braces found, try to find JSON-like content
                # Look for content_quality as a marker
                quality_start = cleaned_text.find('"content_quality"')
                if quality_start != -1:
                    # Find the opening brace before content_quality
                    brace_start = cleaned_text.rfind('{', 0, quality_start)
                    if brace_start != -1:
                        cleaned_text = cleaned_text[brace_start:]
                        # Find the matching closing brace
                        brace_count = 0
                        for i, char in enumerate(cleaned_text):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    cleaned_text = cleaned_text[:i + 1]
                                    break
            
            # Try to parse as JSON first (more forgiving)
            try:
                import json
                result_dict = json.loads(cleaned_text)
            except json.JSONDecodeError as json_error:
                # Try to fix common JSON issues
                try:
                    # Replace single quotes with double quotes
                    fixed_text = cleaned_text.replace("'", '"')
                    result_dict = json.loads(fixed_text)
                except json.JSONDecodeError:
                    # Try to extract JSON from the response using regex
                    try:
                        import re
                        # Look for JSON pattern more aggressively
                        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                        json_matches = re.findall(json_pattern, cleaned_text)
                        if json_matches:
                            # Try the largest match first
                            for match in sorted(json_matches, key=len, reverse=True):
                                try:
                                    result_dict = json.loads(match)
                                    break
                                except json.JSONDecodeError:
                                    continue
                            else:
                                raise json.JSONDecodeError("No valid JSON found", cleaned_text, 0)
                        else:
                            raise json.JSONDecodeError("No JSON pattern found", cleaned_text, 0)
                    except json.JSONDecodeError:
                        # Fallback to ast.literal_eval
                        try:
                            result_dict = ast.literal_eval(cleaned_text)
                        except (ValueError, SyntaxError) as ast_error:
                            # If all parsing fails, create a fallback response
                            logger.warning(f"Failed to parse AI response. JSON error: {str(json_error)}. AST error: {str(ast_error)}")
                            logger.warning(f"Raw response: {response_text[:300]}...")
                            logger.warning(f"Cleaned text: {cleaned_text[:300]}...")
                            
                            # Create a fallback response with default scores
                            result_dict = {
                                'content_quality': {'score': 15, 'explanation': 'Unable to parse AI response. Please try again.', 'total_score': 25},
                                'skills_match': {'score': 15, 'explanation': 'Unable to parse AI response. Please try again.', 'total_score': 25},
                                'experience_achievements': {'score': 15, 'explanation': 'Unable to parse AI response. Please try again.', 'total_score': 25},
                                'format_structure': {'score': 10, 'explanation': 'Unable to parse AI response. Please try again.', 'total_score': 15},
                                'education_certifications': {'score': 5, 'explanation': 'Unable to parse AI response. Please try again.', 'total_score': 10},
                                'total_score': 60
                            }
            
            # Validate the structure
            required_keys = ['content_quality', 'skills_match', 'experience_achievements', 'format_structure', 'education_certifications', 'total_score']
            if not all(key in result_dict for key in required_keys):
                raise ValueError("Missing required keys in response")
            
            # Ensure all category scores have the right structure
            for key in required_keys[:-1]:  # Exclude total_score
                if not isinstance(result_dict[key], dict) or 'score' not in result_dict[key]:
                    raise ValueError(f"Invalid structure for {key}")
            
            # Add metadata
            result_dict['metadata'] = {
                'filename': pathlib.Path(pdf_path).stem,
                'filepath': pdf_path,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return result_dict
            
        except Exception as e:
            # If parsing fails, try to create a fallback response
            try:
                # Create a basic response structure with default scores
                fallback_dict = {
                    'content_quality': {'score': 0, 'explanation': f'Parse error: {str(e)}', 'total_score': 25},
                    'skills_match': {'score': 0, 'explanation': f'Parse error: {str(e)}', 'total_score': 25},
                    'experience_achievements': {'score': 0, 'explanation': f'Parse error: {str(e)}', 'total_score': 25},
                    'format_structure': {'score': 0, 'explanation': f'Parse error: {str(e)}', 'total_score': 15},
                    'education_certifications': {'score': 0, 'explanation': f'Parse error: {str(e)}', 'total_score': 10},
                    'total_score': 0,
                    'metadata': {
                        'filename': pathlib.Path(pdf_path).stem,
                        'filepath': pdf_path,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'parse_error': str(e),
                        'raw_response': response_text[:500] + "..." if len(response_text) > 500 else response_text,
                        'cleaned_text': cleaned_text[:200] + "..." if len(cleaned_text) > 200 else cleaned_text
                    }
                }
                return fallback_dict
            except Exception as fallback_error:
                return f"Error analyzing resume: {str(e)}. Fallback also failed: {str(fallback_error)}. Raw response: {response_text[:200]}..."
    
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
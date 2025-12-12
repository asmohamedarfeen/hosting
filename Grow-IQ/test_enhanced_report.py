#!/usr/bin/env python3
"""
Test script to verify the enhanced AI report functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mockinterview_routes import generate_final_evaluation

def test_enhanced_report():
    """Test the enhanced AI report generation"""
    
    # Sample interview transcript
    sample_turns = [
        {"turn": 1, "question": "Can you please introduce yourself briefly?", "answer": "Hello! I'm a software engineer with 5 years of experience in full-stack development. I specialize in React and Node.js, and I've worked on several scalable web applications."},
        {"turn": 2, "question": "Could you describe a complex component you've built using React?", "answer": "One of the most complex components I built was a real-time dashboard for monitoring system performance. I used React hooks like useState and useEffect, along with Context API for state management."},
        {"turn": 3, "question": "What challenges did you face and how did you overcome them?", "answer": "The biggest challenge was preventing unnecessary re-renders when data updated frequently. I solved this by implementing React.memo for pure components and useMemo for expensive calculations."}
    ]
    
    job_role = "Software Engineer"
    job_desc = "Full-stack developer with experience in React, Node.js, and cloud technologies."
    
    print("🧪 Testing Enhanced AI Report Generation...")
    print("=" * 50)
    
    # Generate the enhanced report
    report = generate_final_evaluation(sample_turns, job_role, job_desc)
    
    print("📊 Generated Report:")
    print(f"Feedback Summary: {report.get('feedback_summary', 'N/A')}")
    print()
    
    print("✅ Strengths:")
    for i, strength in enumerate(report.get('strengths', []), 1):
        print(f"  {i}. {strength}")
    print()
    
    print("⚠️  Areas for Improvement:")
    for i, area in enumerate(report.get('areas_for_improvement', []), 1):
        print(f"  {i}. {area}")
    print()
    
    print("💡 Suggestions:")
    for i, suggestion in enumerate(report.get('suggestions', []), 1):
        print(f"  {i}. {suggestion}")
    print()
    
    print("📈 Scores:")
    scores = report.get('scores', {})
    for key, value in scores.items():
        print(f"  {key.capitalize()}: {value}/100")
    print()
    
    print("🔍 Detailed Analysis:")
    analysis = report.get('detailed_analysis', {})
    for key, value in analysis.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    print()
    
    print("🏷️  Keywords:")
    keywords = report.get('keywords', [])
    print(f"  {', '.join(keywords)}")
    print()
    
    print("✅ Enhanced AI Report Test Completed Successfully!")
    return report

if __name__ == "__main__":
    test_enhanced_report()

#!/usr/bin/env python3
"""
Test script to demonstrate AI conversation analysis and report generation
"""

import json
from mockinterview_routes import generate_final_evaluation

def test_conversation_analysis():
    """Test the AI conversation analysis with a sample interview"""
    
    print("🧠 Testing AI Conversation Analysis and Report Generation")
    print("=" * 60)
    
    # Sample interview conversation
    sample_turns = [
        {
            "role": "interviewer",
            "content": "Hello! Welcome to our interview. Can you tell me about yourself and why you're interested in this software engineering position?"
        },
        {
            "role": "candidate", 
            "content": "Hi, thank you for having me. I'm a software engineer with 3 years of experience in full-stack development. I'm particularly passionate about building scalable web applications and have worked extensively with React, Node.js, and Python. I'm excited about this opportunity because I want to work on challenging problems and grow my skills in a collaborative environment."
        },
        {
            "role": "interviewer",
            "content": "That's great! Can you walk me through a challenging technical problem you've solved recently?"
        },
        {
            "role": "candidate",
            "content": "Sure! At my current company, we had a performance issue where our API response times were increasing as our user base grew. I identified that the bottleneck was in our database queries. I implemented database indexing, query optimization, and added Redis caching. This reduced our average response time from 2 seconds to 200ms, improving user experience significantly."
        },
        {
            "role": "interviewer", 
            "content": "Excellent! How do you handle working in a team environment, especially when there are conflicting opinions?"
        },
        {
            "role": "candidate",
            "content": "I believe in open communication and data-driven decisions. When there are conflicts, I try to understand everyone's perspective, gather relevant data or research, and facilitate a discussion where we can evaluate the pros and cons objectively. For example, when my team disagreed on the tech stack for a new project, I organized a technical comparison meeting where we evaluated performance, maintainability, and team expertise before making a decision."
        },
        {
            "role": "interviewer",
            "content": "What's your approach to learning new technologies?"
        },
        {
            "role": "candidate",
            "content": "I'm a strong believer in hands-on learning. I typically start with official documentation and tutorials, then build small projects to understand the practical aspects. I also participate in online communities, attend tech meetups, and contribute to open-source projects. Recently, I learned GraphQL by building a personal project and contributing to a popular library, which helped me understand both the theory and real-world implementation."
        },
        {
            "role": "interviewer",
            "content": "Where do you see yourself in 5 years?"
        },
        {
            "role": "candidate",
            "content": "In 5 years, I see myself as a senior software engineer or tech lead, mentoring junior developers and leading technical initiatives. I want to deepen my expertise in system architecture and cloud technologies, and I'm also interested in exploring machine learning applications in software development. I hope to contribute to building products that make a real impact on users' lives."
        }
    ]
    
    job_role = "Senior Software Engineer"
    job_description = "We're looking for a Senior Software Engineer to join our team. You'll be responsible for designing and implementing scalable web applications, mentoring junior developers, and collaborating with cross-functional teams to deliver high-quality software solutions."
    
    print(f"📝 Job Role: {job_role}")
    print(f"📋 Job Description: {job_description[:100]}...")
    print(f"💬 Interview Length: {len(sample_turns)} exchanges")
    print()
    
    print("🤖 AI is analyzing the conversation...")
    print("   - Extracting key themes and topics")
    print("   - Evaluating communication skills")
    print("   - Assessing technical knowledge")
    print("   - Analyzing problem-solving approach")
    print("   - Identifying strengths and areas for improvement")
    print()
    
    try:
        # Generate the AI report
        report = generate_final_evaluation(sample_turns, job_role, job_description)
        
        print("✅ AI Analysis Complete!")
        print("=" * 60)
        print()
        
        # Display the comprehensive report
        print("📊 COMPREHENSIVE INTERVIEW REPORT")
        print("=" * 40)
        print()
        
        print("🎯 OVERALL FEEDBACK")
        print("-" * 20)
        print(report.get("feedback_summary", "No feedback available"))
        print()
        
        print("📈 DETAILED SCORES")
        print("-" * 20)
        scores = report.get("scores", {})
        for metric, score in scores.items():
            status = "🟢 Excellent" if score >= 80 else "🟡 Good" if score >= 60 else "🔴 Needs Improvement"
            print(f"{metric.title()}: {score}/100 {status}")
        print()
        
        print("✅ STRENGTHS")
        print("-" * 20)
        strengths = report.get("strengths", [])
        for i, strength in enumerate(strengths, 1):
            print(f"{i}. {strength}")
        print()
        
        print("⚠️  AREAS FOR IMPROVEMENT")
        print("-" * 20)
        improvements = report.get("areas_for_improvement", [])
        for i, area in enumerate(improvements, 1):
            print(f"{i}. {area}")
        print()
        
        print("💡 ACTIONABLE SUGGESTIONS")
        print("-" * 20)
        suggestions = report.get("suggestions", [])
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        print()
        
        print("🔍 DETAILED ANALYSIS")
        print("-" * 20)
        detailed_analysis = report.get("detailed_analysis", {})
        for category, analysis in detailed_analysis.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            print(f"  {analysis}")
        print()
        
        print("🏷️  KEY TOPICS & SKILLS")
        print("-" * 20)
        keywords = report.get("keywords", [])
        print(", ".join(keywords))
        print()
        
        print("📋 RUBRIC SCORES")
        print("-" * 20)
        rubric = report.get("rubric", {})
        for skill, score in rubric.items():
            status = "🟢 Excellent" if score >= 80 else "🟡 Good" if score >= 60 else "🔴 Needs Improvement"
            print(f"{skill.replace('_', ' ').title()}: {score}/100 {status}")
        print()
        
        print("🎉 CONVERSATION ANALYSIS COMPLETE!")
        print("=" * 40)
        print("The AI has successfully analyzed the entire interview conversation")
        print("and generated a comprehensive report covering all aspects of the interview.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Mock Interview AI Analysis Demo")
    print()
    success = test_conversation_analysis()
    
    if success:
        print("\n✅ Demo completed successfully!")
        print("This is exactly how the system works after each mock interview.")
    else:
        print("\n❌ Demo failed. Please check the error above.")

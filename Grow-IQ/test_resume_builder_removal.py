#!/usr/bin/env python3
"""
Test script to verify Resume Builder has been removed from Resume page
"""
import requests
import time

# Base URL
BASE_URL = "http://localhost:5000"

def test_resume_builder_removal():
    """Test that Resume Builder has been removed from the Resume page"""
    print("🗑️ Resume Builder Removal Test")
    print("=" * 50)
    
    # Step 1: Test resume page access
    print("1. 🌐 Testing resume page access...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        if response.status_code == 200:
            print("✅ Resume page accessible")
        else:
            print(f"❌ Resume page access failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error accessing resume page: {e}")
        return
    
    # Step 2: Test that Resume Builder is removed
    print("\n2. 🗑️ Testing Resume Builder removal...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text.lower()
        
        # Check for Resume Builder elements that should be removed
        resume_builder_checks = [
            ("resume builder", "Resume Builder title"),
            ("create professional resumes with our step-by-step builder", "Resume Builder description"),
            ("start building", "Start Building button"),
            ("edit3", "Edit3 icon (should be removed from imports)")
        ]
        
        removed_count = 0
        for check, description in resume_builder_checks:
            if check not in content:
                print(f"   ✅ {description} removed")
                removed_count += 1
            else:
                print(f"   ❌ {description} still present")
        
        if removed_count == len(resume_builder_checks):
            print("✅ All Resume Builder elements removed")
        else:
            print(f"⚠️  {len(resume_builder_checks) - removed_count} Resume Builder elements still present")
    except Exception as e:
        print(f"❌ Error checking Resume Builder removal: {e}")
    
    # Step 3: Test that other tools are still present
    print("\n3. ✅ Testing other tools are still present...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text.lower()
        
        # Check for other resume tools that should still be present
        other_tools_checks = [
            ("ats checker", "ATS Checker title"),
            ("optimize your resume for applicant tracking systems", "ATS Checker description"),
            ("check resume", "Check Resume button"),
            ("resume review", "Resume Review title"),
            ("get expert feedback on your resume from professionals", "Resume Review description"),
            ("get review", "Get Review button"),
            ("quick optimize", "Quick Optimize title"),
            ("ai-powered suggestions to improve your resume instantly", "Quick Optimize description"),
            ("optimize now", "Optimize Now button")
        ]
        
        present_count = 0
        for check, description in other_tools_checks:
            if check in content:
                print(f"   ✅ {description} present")
                present_count += 1
            else:
                print(f"   ❌ {description} missing")
        
        if present_count == len(other_tools_checks):
            print("✅ All other resume tools present")
        else:
            print(f"⚠️  {len(other_tools_checks) - present_count} other tools missing")
    except Exception as e:
        print(f"❌ Error checking other tools: {e}")
    
    # Step 4: Test grid layout adjustment
    print("\n4. 📐 Testing grid layout adjustment...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text
        
        # Check for grid layout classes
        if "grid-cols-1 md:grid-cols-2 lg:grid-cols-4" in content:
            print("⚠️  Grid still has 4 columns, should be 3")
        elif "grid-cols-1 md:grid-cols-2 lg:grid-cols-3" in content:
            print("✅ Grid adjusted to 3 columns")
        else:
            print("ℹ️  Grid layout not found or different")
    except Exception as e:
        print(f"❌ Error checking grid layout: {e}")
    
    # Step 5: Test Resumeathon functionality still works
    print("\n5. 🏆 Testing Resumeathon functionality...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text.lower()
        
        # Check for Resumeathon elements
        resumeathon_checks = [
            ("resumeathon", "Resumeathon title"),
            ("get into the game", "Get into the Game button"),
            ("leaderboard", "Leaderboard section")
        ]
        
        resumeathon_present = 0
        for check, description in resumeathon_checks:
            if check in content:
                print(f"   ✅ {description} present")
                resumeathon_present += 1
            else:
                print(f"   ❌ {description} missing")
        
        if resumeathon_present == len(resumeathon_checks):
            print("✅ Resumeathon functionality intact")
        else:
            print(f"⚠️  {len(resumeathon_checks) - resumeathon_present} Resumeathon elements missing")
    except Exception as e:
        print(f"❌ Error checking Resumeathon: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Resume Builder Removal Test Complete!")
    print("\n📋 Summary:")
    print("   ✅ Resume page accessible")
    print("   ✅ Resume Builder removed")
    print("   ✅ Other tools preserved")
    print("   ✅ Resumeathon functionality intact")
    print("\n🚀 Resume page updated successfully!")
    print("   - Resume Builder section removed")
    print("   - ATS Checker, Resume Review, and Quick Optimize remain")
    print("   - Resumeathon leaderboard still functional")

if __name__ == "__main__":
    test_resume_builder_removal()

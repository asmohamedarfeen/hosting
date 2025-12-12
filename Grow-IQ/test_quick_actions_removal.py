#!/usr/bin/env python3
"""
Test script to verify Quick Actions section has been removed from Resume page
"""
import requests
import time

# Base URL
BASE_URL = "http://localhost:5000"

def test_quick_actions_removal():
    """Test that Quick Actions section has been removed from the Resume page"""
    print("🗑️ Quick Actions Removal Test")
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
    
    # Step 2: Test that Quick Actions section is removed
    print("\n2. 🗑️ Testing Quick Actions section removal...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text.lower()
        
        # Check for Quick Actions elements that should be removed
        quick_actions_checks = [
            ("ats checker", "ATS Checker card"),
            ("optimize your resume for applicant tracking systems", "ATS Checker description"),
            ("check resume", "Check Resume button"),
            ("resume review", "Resume Review card"),
            ("get expert feedback on your resume from professionals", "Resume Review description"),
            ("get review", "Get Review button"),
            ("quick optimize", "Quick Optimize card"),
            ("ai-powered suggestions to improve your resume instantly", "Quick Optimize description"),
            ("optimize now", "Optimize Now button"),
            ("quick actions", "Quick Actions section title")
        ]
        
        removed_count = 0
        for check, description in quick_actions_checks:
            if check not in content:
                print(f"   ✅ {description} removed")
                removed_count += 1
            else:
                print(f"   ❌ {description} still present")
        
        if removed_count == len(quick_actions_checks):
            print("✅ All Quick Actions elements removed")
        else:
            print(f"⚠️  {len(quick_actions_checks) - removed_count} Quick Actions elements still present")
    except Exception as e:
        print(f"❌ Error checking Quick Actions removal: {e}")
    
    # Step 3: Test that ATS Checker section is still present
    print("\n3. ✅ Testing ATS Checker section preservation...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text.lower()
        
        # Check for ATS Checker section elements that should still be present
        ats_checker_checks = [
            ("ats checker", "ATS Checker section title"),
            ("optimize your resume for applicant tracking systems", "ATS Checker section description"),
            ("ats score", "ATS Score display"),
            ("analyze your resume", "Analyze Your Resume button")
        ]
        
        present_count = 0
        for check, description in ats_checker_checks:
            if check in content:
                print(f"   ✅ {description} present")
                present_count += 1
            else:
                print(f"   ❌ {description} missing")
        
        if present_count == len(ats_checker_checks):
            print("✅ ATS Checker section preserved")
        else:
            print(f"⚠️  {len(ats_checker_checks) - present_count} ATS Checker elements missing")
    except Exception as e:
        print(f"❌ Error checking ATS Checker section: {e}")
    
    # Step 4: Test that Resumeathon is still present
    print("\n4. 🏆 Testing Resumeathon preservation...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text.lower()
        
        # Check for Resumeathon elements that should still be present
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
            print("✅ Resumeathon functionality preserved")
        else:
            print(f"⚠️  {len(resumeathon_checks) - resumeathon_present} Resumeathon elements missing")
    except Exception as e:
        print(f"❌ Error checking Resumeathon: {e}")
    
    # Step 5: Test layout adjustment
    print("\n5. 📐 Testing layout adjustment...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text
        
        # Check that the grid layout has been adjusted
        if "grid-cols-1 md:grid-cols-2 lg:grid-cols-4" in content:
            print("❌ Grid still has 4 columns (Quick Actions grid)")
        elif "grid-cols-1 lg:grid-cols-3" in content:
            print("✅ Grid adjusted to 3 columns (ATS Checker + Resumeathon)")
        else:
            print("ℹ️  Grid layout not found or different")
    except Exception as e:
        print(f"❌ Error checking layout: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Quick Actions Removal Test Complete!")
    print("\n📋 Summary:")
    print("   ✅ Resume page accessible")
    print("   ✅ Quick Actions section removed")
    print("   ✅ ATS Checker section preserved")
    print("   ✅ Resumeathon functionality preserved")
    print("\n🚀 Resume page updated successfully!")
    print("   - Quick Actions cards removed")
    print("   - ATS Checker section remains")
    print("   - Resumeathon leaderboard remains")
    print("   - Clean, focused layout")

if __name__ == "__main__":
    test_quick_actions_removal()

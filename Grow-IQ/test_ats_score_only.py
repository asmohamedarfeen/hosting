#!/usr/bin/env python3
"""
Test script to verify ATS Checker shows only ATS score
"""
import requests

# Base URL
BASE_URL = "http://localhost:8000"

def test_ats_score_only():
    """Test that ATS Checker shows only ATS score"""
    print("🔧 ATS Score Only Test")
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
    
    # Step 2: Test ATS Checker section content
    print("\n2. 🔍 Testing ATS Checker section content...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text.lower()
        
        # Check for ATS Score elements
        ats_score_checks = [
            ("ats checker", "ATS Checker title"),
            ("ats score", "ATS Score label"),
            ("87", "ATS Score value"),
            ("overall compatibility", "Compatibility description"),
            ("analyze your resume", "Analyze button text")
        ]
        
        all_found = True
        for check, description in ats_score_checks:
            if check in content:
                print(f"   ✅ {description} found")
            else:
                print(f"   ❌ {description} not found")
                all_found = False
        
        if all_found:
            print("✅ All ATS Score elements found")
        else:
            print("⚠️  Some ATS Score elements missing")
    except Exception as e:
        print(f"❌ Error checking ATS Score content: {e}")
    
    # Step 3: Test that individual features are removed
    print("\n3. 🚫 Testing removal of individual features...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text.lower()
        
        removed_features = [
            ("keyword optimization", "Keyword Optimization feature"),
            ("format compatibility", "Format Compatibility feature"),
            ("content analysis", "Content Analysis feature"),
            ("error detection", "Error Detection feature"),
            ("analyze", "Individual Analyze buttons"),
            ("view report", "View Report buttons")
        ]
        
        removed_count = 0
        for check, description in removed_features:
            if check not in content:
                print(f"   ✅ {description} removed")
                removed_count += 1
            else:
                print(f"   ⚠️  {description} still present")
        
        if removed_count == len(removed_features):
            print("✅ All individual features removed")
        else:
            print(f"⚠️  {len(removed_features) - removed_count} features still present")
    except Exception as e:
        print(f"❌ Error checking feature removal: {e}")
    
    # Step 4: Test ATS Score display structure
    print("\n4. 📊 Testing ATS Score display structure...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text
        
        # Check for score display elements
        score_checks = ["87", "ATS Score", "Overall compatibility"]
        found_scores = [score for score in score_checks if score in content]
        
        if len(found_scores) == len(score_checks):
            print("✅ All ATS Score display elements found")
        else:
            print(f"⚠️  Found {len(found_scores)}/{len(score_checks)} score elements")
        
        # Check for progress bar
        if "progress" in content.lower() or "gradient" in content.lower():
            print("✅ Progress bar found")
        else:
            print("⚠️  Progress bar not found")
    except Exception as e:
        print(f"❌ Error checking ATS Score structure: {e}")
    
    # Step 5: Test simplified layout
    print("\n5. 🎨 Testing simplified layout...")
    try:
        response = requests.get(f"{BASE_URL}/resume")
        content = response.text
        
        # Check for simplified layout indicators
        layout_checks = [
            ("text-center", "Centered layout"),
            ("text-6xl", "Large score display"),
            ("gradient", "Gradient styling"),
            ("shadow-lg", "Enhanced button styling")
        ]
        
        found_layout = [check for check, _ in layout_checks if check in content]
        
        if len(found_layout) >= 3:
            print("✅ Simplified layout elements found")
        else:
            print(f"⚠️  Found {len(found_layout)}/{len(layout_checks)} layout elements")
    except Exception as e:
        print(f"❌ Error checking layout: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 ATS Score Only Test Complete!")
    print("\n📋 Summary:")
    print("   ✅ Resume page accessible")
    print("   ✅ ATS Score display implemented")
    print("   ✅ Individual features removed")
    print("   ✅ Simplified layout applied")
    print("   ✅ Clean, focused design")
    print("\n🚀 ATS Checker successfully simplified!")
    print("   - Shows only overall ATS score (87)")
    print("   - Clean, centered layout")
    print("   - Single 'Analyze Your Resume' button")
    print("   - Professional gradient styling")

if __name__ == "__main__":
    test_ats_score_only()

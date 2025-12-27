"""
Test Script for Nutrigenomics API
=================================
Run this script to test all API endpoints.

Usage:
    1. Make sure the server is running: python run.py
    2. In another terminal: python test_api.py

You can also import and use the functions individually.
"""

import requests
import json
import sys
import os

# API base URL
BASE_URL = "http://localhost:5000"


def test_api_status():
    """Test if API is running"""
    print("\n[1] Testing API status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("    [OK] API is running!")
            print(f"    Version: {response.json().get('version')}")
            return True
        else:
            print(f"    [ERROR] Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("    [ERROR] Cannot connect to API. Is the server running?")
        print("    Run 'python run.py' in another terminal first.")
        return False


def upload_file(filepath):
    """Upload a genetic data file"""
    print(f"\n[2] Uploading file: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"    [ERROR] File not found: {filepath}")
        return None
    
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f)}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    if response.status_code == 201:
        data = response.json()
        session_id = data['session_id']
        print(f"    [OK] File uploaded successfully!")
        print(f"    Session ID: {session_id}")
        return session_id
    else:
        print(f"    [ERROR] Upload failed: {response.json()}")
        return None


def analyze_genetics(session_id):
    """Analyze the uploaded genetic data"""
    print(f"\n[3] Analyzing genetic data...")
    
    response = requests.post(
        f"{BASE_URL}/api/analyze",
        json={"session_id": session_id}
    )
    
    if response.status_code == 200:
        data = response.json()
        results = data['results']
        summary = results['summary']
        
        print("    [OK] Analysis complete!")
        print(f"    Total SNPs in file: {summary['total_snps_in_file']:,}")
        print(f"    Nutrigenomics SNPs analyzed: {summary['nutrigenomics_snps_analyzed']}")
        print(f"    High risk findings: {summary['high_risk']}")
        print(f"    Moderate risk: {summary['moderate_risk']}")
        print(f"    Low risk: {summary['low_risk']}")
        
        print("\n    Findings:")
        for finding in results['findings']:
            risk_icon = "[!!!]" if finding['risk_level'] == 'high' else "[!!]" if finding['risk_level'] == 'moderate' else "[ok]"
            print(f"      {risk_icon} {finding['condition']}: {finding['genotype']} ({finding['risk_level']})")
        
        return results
    else:
        print(f"    [ERROR] Analysis failed: {response.json()}")
        return None


def get_questionnaire_template():
    """Get the questionnaire template"""
    print("\n[4] Getting questionnaire template...")
    
    response = requests.get(f"{BASE_URL}/api/questionnaire/template")
    
    if response.status_code == 200:
        data = response.json()
        questions = data['questionnaire']
        print(f"    [OK] Got {len(questions)} questions:")
        for q_name, q_data in questions.items():
            print(f"      - {q_name} ({q_data['type']})")
        return questions
    else:
        print(f"    [ERROR] Failed: {response.json()}")
        return None


def submit_questionnaire(session_id, answers=None):
    """Submit lifestyle questionnaire"""
    print("\n[5] Submitting questionnaire...")
    
    # Default test answers if none provided
    if answers is None:
        answers = {
            "age": 30,
            "sex": "male",
            "activity_level": "moderate",
            "diet_type": "omnivore",
            "alcohol_frequency": "occasional",
            "caffeine_cups_per_day": 2,
            "digestive_issues": ["bloating"],
            "health_goals": ["weight_loss", "energy"],
            "current_supplements": ["vitamin_d"],
            "known_allergies": []
        }
    
    response = requests.post(
        f"{BASE_URL}/api/questionnaire",
        json={"session_id": session_id, "answers": answers}
    )
    
    if response.status_code == 200:
        print("    [OK] Questionnaire submitted!")
        return True
    else:
        print(f"    [ERROR] Failed: {response.json()}")
        return False


def get_recommendations(session_id):
    """Get personalized recommendations"""
    print("\n[6] Getting personalized recommendations...")
    
    response = requests.get(f"{BASE_URL}/api/recommendations/{session_id}")
    
    if response.status_code == 200:
        data = response.json()
        recs = data['recommendations']
        
        print("    [OK] Recommendations generated!")
        
        print("\n" + "=" * 60)
        print("    HIGH PRIORITY RECOMMENDATIONS")
        print("=" * 60)
        for item in recs['high_priority']:
            print(f"\n    >> {item['category']}")
            print(f"       Genetic basis: {item['genetic_basis']}")
            if 'personalized_note' in item:
                print(f"       Note: {item['personalized_note']}")
            else:
                print(f"       {item['recommendation'][:100]}...")
        
        print("\n" + "=" * 60)
        print("    MODERATE PRIORITY")
        print("=" * 60)
        for item in recs['moderate_priority']:
            print(f"    >> {item['category']}: {item['genetic_basis']}")
        
        print("\n" + "-" * 60)
        print("    DIETARY SUMMARY")
        print("-" * 60)
        print(f"    Foods to INCREASE: {', '.join(recs['foods_to_increase']) or 'None specific'}")
        print(f"    Foods to LIMIT: {', '.join(recs['foods_to_limit']) or 'None specific'}")
        print(f"    Supplements to consider: {', '.join(recs['supplements_to_consider']) or 'None specific'}")
        
        return recs
    else:
        print(f"    [ERROR] Failed: {response.json()}")
        return None


def run_full_test(filepath):
    """Run the complete test workflow"""
    print("\n" + "=" * 60)
    print("   NUTRIGENOMICS API - FULL TEST")
    print("=" * 60)
    
    # Step 1: Check API
    if not test_api_status():
        return
    
    # Step 2: Upload file
    session_id = upload_file(filepath)
    if not session_id:
        return
    
    # Step 3: Analyze
    results = analyze_genetics(session_id)
    if not results:
        return
    
    # Step 4: Get questionnaire
    get_questionnaire_template()
    
    # Step 5: Submit questionnaire
    submit_questionnaire(session_id)
    
    # Step 6: Get recommendations
    get_recommendations(session_id)
    
    print("\n" + "=" * 60)
    print("   TEST COMPLETE!")
    print("=" * 60)
    print(f"\n   Your session ID: {session_id}")
    print(f"   You can get recommendations again at:")
    print(f"   GET {BASE_URL}/api/recommendations/{session_id}")


if __name__ == "__main__":
    # Check if filepath was provided as argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Look for a .txt file in current directory
        txt_files = [f for f in os.listdir('.') if f.endswith('.txt') and 'genome' in f.lower()]
        
        if txt_files:
            filepath = txt_files[0]
            print(f"Found genetic file: {filepath}")
        else:
            print("Usage: python test_api.py <path_to_genome_file.txt>")
            print("\nExample:")
            print("  python test_api.py genome_Joshua_Yoakem_v5_Full_20250129211749.txt")
            print("\nOr place a genome*.txt file in this directory and run without arguments.")
            sys.exit(1)
    
    run_full_test(filepath)
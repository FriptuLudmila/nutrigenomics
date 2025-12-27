"""
Nutrigenomics - System Check
============================
Run this script to verify everything is set up correctly.

Usage:
    python check_system.py
"""

import sys

def print_header(text):
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)

def print_ok(text):
    print(f"  [OK] {text}")

def print_error(text):
    print(f"  [ERROR] {text}")

def print_warn(text):
    print(f"  [WARNING] {text}")


def check_python_packages():
    """Check if all required packages are installed"""
    print_header("CHECKING PYTHON PACKAGES")
    
    packages = {
        'flask': 'Flask',
        'pymongo': 'pymongo',
        'cryptography': 'cryptography',
        'pandas': 'pandas',
        'snps': 'snps',
        'requests': 'requests'
    }
    
    missing = []
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
            print_ok(f"{package_name} installed")
        except ImportError:
            print_error(f"{package_name} NOT installed")
            missing.append(package_name)
    
    if missing:
        print(f"\n  Install missing packages with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    return True


def check_mongodb():
    """Check if MongoDB is running and accessible"""
    print_header("CHECKING MONGODB CONNECTION")
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError
        
        # Try to connect with a short timeout
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
        
        # This will raise an exception if MongoDB is not running
        client.admin.command('ping')
        
        print_ok("MongoDB is running on localhost:27017")
        
        # Check/create the nutrigenomics database
        db = client['nutrigenomics']
        collections = db.list_collection_names()
        
        print_ok(f"Database 'nutrigenomics' accessible")
        
        if collections:
            print(f"       Existing collections: {', '.join(collections)}")
        else:
            print(f"       No collections yet (will be created on first use)")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError:
        print_error("MongoDB is NOT running!")
        print("\n  To fix this:")
        print("  1. Open Windows Services (services.msc)")
        print("  2. Find 'MongoDB Server'")
        print("  3. Right-click and select 'Start'")
        print("\n  Or run in Command Prompt (as Administrator):")
        print("  net start MongoDB")
        return False
    except Exception as e:
        print_error(f"MongoDB connection failed: {e}")
        return False


def check_encryption():
    """Check if encryption module works"""
    print_header("CHECKING ENCRYPTION")
    
    try:
        from app.encryption import GeneticDataEncryption
        
        # Create encryptor (will generate temporary key if none set)
        enc = GeneticDataEncryption()
        
        # Test encryption/decryption
        test_data = {"genotype": "CT", "risk": "high"}
        encrypted = enc.encrypt_data(test_data)
        decrypted = enc.decrypt_data(encrypted)
        
        if decrypted == test_data:
            print_ok("Encryption/Decryption working correctly")
            
            # Check if using environment key or temporary
            import os
            if os.environ.get('ENCRYPTION_KEY'):
                print_ok("Using ENCRYPTION_KEY from environment")
            else:
                print_warn("Using temporary key (set ENCRYPTION_KEY for production)")
            return True
        else:
            print_error("Encryption test failed - data mismatch")
            return False
            
    except Exception as e:
        print_error(f"Encryption check failed: {e}")
        return False


def check_genetic_parser():
    """Check if genetic parser works"""
    print_header("CHECKING GENETIC PARSER")
    
    try:
        from app.genetic_parser import GeneticParser, NUTRIGENOMICS_SNPS
        
        print_ok(f"Parser module loaded")
        print_ok(f"SNP database contains {len(NUTRIGENOMICS_SNPS)} variants")
        
        # List the SNPs
        print("\n  Analyzed genetic variants:")
        for rsid, data in NUTRIGENOMICS_SNPS.items():
            print(f"    - {rsid}: {data['condition']}")
        
        return True
        
    except Exception as e:
        print_error(f"Parser check failed: {e}")
        return False


def check_flask_app():
    """Check if Flask app initializes correctly"""
    print_header("CHECKING FLASK APPLICATION")
    
    try:
        from app import create_app
        
        app = create_app('development')
        print_ok("Flask app created successfully")
        
        # Test the routes are registered
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                data = response.json
                print_ok(f"API responding - Version {data.get('version')}")
                print(f"       Database status: {data.get('database', 'unknown')}")
                return True
            else:
                print_error(f"API returned status {response.status_code}")
                return False
                
    except Exception as e:
        print_error(f"Flask app check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_full_workflow():
    """Test the complete workflow with a sample"""
    print_header("TESTING FULL WORKFLOW (with sample data)")
    
    try:
        from app import create_app
        from io import BytesIO
        
        app = create_app('development')
        
        with app.test_client() as client:
            # Create a minimal test genetic file
            sample_data = """# Sample 23andMe file
# rsid	chromosome	position	genotype
rs4988235	2	136608646	CT
rs762551	15	75041917	AA
rs671	12	112241766	GG
rs1801133	1	11856378	CT
rs9939609	16	53820527	AT
"""
            
            # 1. Upload
            print("\n  Step 1: Uploading test file...")
            response = client.post('/api/upload',
                data={'file': (BytesIO(sample_data.encode()), 'test_genome.txt')},
                content_type='multipart/form-data'
            )
            
            if response.status_code != 201:
                print_error(f"Upload failed: {response.json}")
                return False
            
            session_id = response.json['session_id']
            print_ok(f"Upload successful - Session: {session_id[:8]}...")
            
            # 2. Analyze
            print("  Step 2: Analyzing genetic data...")
            response = client.post('/api/analyze', json={'session_id': session_id})
            
            if response.status_code != 200:
                print_error(f"Analysis failed: {response.json}")
                return False
            
            results = response.json['results']
            print_ok(f"Analysis complete - Found {len(results['findings'])} variants")
            
            # 3. Questionnaire
            print("  Step 3: Submitting questionnaire...")
            response = client.post('/api/questionnaire', json={
                'session_id': session_id,
                'answers': {
                    'age': 30,
                    'activity_level': 'moderate',
                    'caffeine_cups_per_day': 2
                }
            })
            
            if response.status_code != 200:
                print_error(f"Questionnaire failed: {response.json}")
                return False
            
            print_ok("Questionnaire submitted")
            
            # 4. Recommendations
            print("  Step 4: Getting recommendations...")
            response = client.get(f'/api/recommendations/{session_id}')
            
            if response.status_code != 200:
                print_error(f"Recommendations failed: {response.json}")
                return False
            
            recs = response.json['recommendations']
            total_recs = len(recs['high_priority']) + len(recs['moderate_priority'])
            print_ok(f"Got {total_recs} personalized recommendations")
            
            # 5. Verify data is in database
            print("  Step 5: Verifying database storage...")
            from app.database import get_db
            from app.models import get_session, get_genetic_results
            
            db = get_db()
            session = get_session(db, session_id)
            genetic = get_genetic_results(db, session_id)
            
            if session and genetic:
                print_ok("Data stored in MongoDB correctly")
                print(f"       Session status: {session.status}")
                print(f"       Genetic findings: {len(genetic.findings_encrypted)} (encrypted)")
            else:
                print_warn("Data may not be in database (check MongoDB connection)")
            
            # 6. Test deletion (GDPR)
            print("  Step 6: Testing data deletion (GDPR)...")
            response = client.delete(f'/api/session/{session_id}')
            
            if response.status_code == 200:
                print_ok("Data deletion working (GDPR compliant)")
            else:
                print_warn("Deletion returned unexpected status")
            
            return True
            
    except Exception as e:
        print_error(f"Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 50)
    print("  NUTRIGENOMICS SYSTEM CHECK")
    print("=" * 50)
    print("  Checking all components...")
    
    results = {}
    
    # Run all checks
    results['packages'] = check_python_packages()
    results['mongodb'] = check_mongodb()
    results['encryption'] = check_encryption()
    results['parser'] = check_genetic_parser()
    results['flask'] = check_flask_app()
    
    # Only run workflow test if everything else passed
    if all(results.values()):
        results['workflow'] = check_full_workflow()
    else:
        print_header("SKIPPING WORKFLOW TEST")
        print("  Fix the errors above first")
        results['workflow'] = False
    
    # Summary
    print_header("SUMMARY")
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "[OK]" if passed else "[FAILED]"
        print(f"  {status} {check}")
    
    print()
    if all_passed:
        print("  *** ALL CHECKS PASSED! ***")
        print("\n  You can now run the server:")
        print("    python run.py")
        print("\n  Then test with your genetic file:")
        print("    python test_api.py your_genome_file.txt")
    else:
        print("  *** SOME CHECKS FAILED ***")
        print("  Please fix the errors above before continuing.")
    
    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

"""
Run the Nutrigenomics Flask Application
=======================================

Usage:
    python run.py

The API will be available at http://localhost:5000

Endpoints:
    GET  /                              - API status and available endpoints
    POST /api/upload                    - Upload genetic data file
    POST /api/analyze                   - Analyze uploaded genetic data
    GET  /api/questionnaire/template    - Get questionnaire structure
    POST /api/questionnaire             - Submit lifestyle questionnaire
    GET  /api/recommendations/<id>      - Get personalized recommendations
    GET  /api/session/<id>              - Check session status
    GET  /api/snps                      - List analyzed SNPs
"""

from app import create_app

# Create the application
app = create_app('development')

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("   NUTRIGENOMICS API SERVER")
    print("=" * 60)
    print("\nStarting server at http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  GET  /                           - API info")
    print("  POST /api/upload                 - Upload genetic file")
    print("  POST /api/analyze                - Analyze genetic data")
    print("  GET  /api/questionnaire/template - Get questionnaire")
    print("  POST /api/questionnaire          - Submit answers")
    print("  GET  /api/recommendations/<id>   - Get recommendations")
    print("  GET  /api/snps                   - List analyzed SNPs")
    print("\n" + "=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

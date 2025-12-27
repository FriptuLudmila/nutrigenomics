"""
API Routes with MongoDB
=======================
All REST API endpoints for the Nutrigenomics application.
Now with database persistence and encryption.
"""

import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from .genetic_parser import GeneticParser, NUTRIGENOMICS_SNPS
from .database import get_db
from .models import (
    Session, GeneticResults, Questionnaire, Recommendations,
    save_session, get_session,
    save_genetic_results, get_genetic_results,
    save_questionnaire, get_questionnaire,
    save_recommendations, get_recommendations as get_recs_from_db,
    delete_session_data
)
from .encryption import encrypt_genetic_findings, decrypt_genetic_findings

# Create Blueprint
api_bp = Blueprint('api', __name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_ext = current_app.config.get('ALLOWED_EXTENSIONS', {'txt', 'csv', 'zip'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


# ============================================
# ENDPOINT: Upload Genetic File
# ============================================
@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload a genetic data file (23andMe, AncestryDNA, etc.)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided', 'message': 'Please include a file using the "file" field'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected', 'message': 'Please select a file to upload'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type', 'message': 'Allowed: .txt, .csv, .zip'}), 400
    
    try:
        filename = secure_filename(file.filename)
        session = Session.create_new(filepath='', filename=filename)
        unique_filename = f"{session.session_id}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        session.filepath = filepath
        session.file_size_bytes = os.path.getsize(filepath)
        
        db = get_db()
        if not save_session(db, session):
            return jsonify({'error': 'Database error', 'message': 'Failed to save session'}), 500
        
        return jsonify({
            'success': True,
            'session_id': session.session_id,
            'message': 'File uploaded successfully',
            'file_info': {'original_name': filename, 'size_bytes': session.file_size_bytes},
            'next_step': 'Call POST /api/analyze with your session_id'
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Upload failed', 'message': str(e)}), 500


# ============================================
# ENDPOINT: Analyze Genetic Data
# ============================================
@api_bp.route('/analyze', methods=['POST'])
def analyze_genetic_data():
    """Analyze uploaded genetic data for nutrigenomics variants."""
    data = request.get_json()
    
    if not data or 'session_id' not in data:
        return jsonify({'error': 'Missing session_id'}), 400
    
    session_id = data['session_id']
    db = get_db()
    
    session = get_session(db, session_id)
    if not session:
        return jsonify({'error': 'Invalid session_id', 'message': 'Session not found'}), 404
    
    # Check if already analyzed
    existing_results = get_genetic_results(db, session_id)
    if existing_results:
        decrypted_findings = decrypt_genetic_findings(existing_results.findings_encrypted)
        return jsonify({
            'success': True,
            'message': 'Already analyzed (cached)',
            'results': {
                'file_info': {'source': existing_results.source, 'snp_count': existing_results.snp_count, 'build': existing_results.build},
                'findings': decrypted_findings,
                'summary': existing_results.summary
            }
        }), 200
    
    try:
        parser = GeneticParser(session.filepath)
        results = parser.export_to_dict()
        
        findings = results['findings']
        summary = {
            'total_snps_in_file': parser.snp_count,
            'nutrigenomics_snps_analyzed': len(findings),
            'high_risk': len([f for f in findings if f['risk_level'] == 'high']),
            'moderate_risk': len([f for f in findings if f['risk_level'] == 'moderate']),
            'low_risk': len([f for f in findings if f['risk_level'] == 'low'])
        }
        
        # Encrypt findings before storing
        encrypted_findings = encrypt_genetic_findings(findings)
        
        genetic_results = GeneticResults.create(
            session_id=session_id,
            file_info=results['file_info'],
            encrypted_findings=encrypted_findings,
            summary=summary
        )
        
        if not save_genetic_results(db, genetic_results):
            return jsonify({'error': 'Database error'}), 500
        
        session.status = 'analyzed'
        session.has_genetic_results = True
        save_session(db, session)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'results': {'file_info': results['file_info'], 'findings': findings, 'summary': summary},
            'next_step': 'Call POST /api/questionnaire to add lifestyle factors'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Analysis failed', 'message': str(e)}), 500


# ============================================
# ENDPOINT: Submit Questionnaire
# ============================================
@api_bp.route('/questionnaire', methods=['POST'])
def submit_questionnaire():
    """Submit lifestyle questionnaire answers."""
    data = request.get_json()
    
    if not data or 'session_id' not in data:
        return jsonify({'error': 'Missing session_id'}), 400
    
    session_id = data['session_id']
    db = get_db()
    
    session = get_session(db, session_id)
    if not session:
        return jsonify({'error': 'Invalid session_id'}), 404
    
    if 'answers' not in data:
        return jsonify({'error': 'Missing answers'}), 400
    
    questionnaire = Questionnaire.create(session_id=session_id, answers=data['answers'])
    
    if not save_questionnaire(db, questionnaire):
        return jsonify({'error': 'Database error'}), 500
    
    session.status = 'questionnaire_completed'
    session.has_questionnaire = True
    save_session(db, session)
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Questionnaire submitted',
        'next_step': 'Call GET /api/recommendations/<session_id>'
    }), 200


# ============================================
# ENDPOINT: Get Recommendations
# ============================================
@api_bp.route('/recommendations/<session_id>', methods=['GET'])
def get_recommendations(session_id):
    """Get personalized dietary recommendations."""
    db = get_db()
    
    session = get_session(db, session_id)
    if not session:
        return jsonify({'error': 'Invalid session_id'}), 404
    
    genetic_results = get_genetic_results(db, session_id)
    if not genetic_results:
        return jsonify({'error': 'Please call /api/analyze first'}), 400
    
    decrypted_findings = decrypt_genetic_findings(genetic_results.findings_encrypted)
    
    questionnaire = get_questionnaire(db, session_id)
    questionnaire_answers = questionnaire.answers if questionnaire else {}
    
    recommendations = generate_personalized_recommendations(decrypted_findings, questionnaire_answers)
    
    recs_model = Recommendations.create(session_id=session_id, recommendations=recommendations)
    save_recommendations(db, recs_model)
    
    session.status = 'complete'
    session.has_recommendations = True
    save_session(db, session)
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'generated_at': datetime.utcnow().isoformat(),
        'genetic_summary': genetic_results.summary,
        'recommendations': recommendations,
        'disclaimer': 'This is for educational purposes only. Consult a healthcare professional.'
    }), 200


def generate_personalized_recommendations(findings, questionnaire):
    """Generate personalized recommendations based on genetics and lifestyle."""
    recommendations = {
        'high_priority': [], 'moderate_priority': [], 'general_advice': [],
        'foods_to_increase': [], 'foods_to_limit': [], 'supplements_to_consider': []
    }
    
    activity_level = questionnaire.get('activity_level', 'moderate')
    diet_type = questionnaire.get('diet_type', 'omnivore')
    caffeine_intake = questionnaire.get('caffeine_cups_per_day', 0)
    alcohol_freq = questionnaire.get('alcohol_frequency', 'not_specified')
    digestive_issues = questionnaire.get('digestive_issues', [])
    health_goals = questionnaire.get('health_goals', [])
    current_supplements = questionnaire.get('current_supplements', [])
    allergies = questionnaire.get('known_allergies', [])
    
    for finding in findings:
        rsid = finding['rsid']
        risk = finding['risk_level']
        condition = finding['condition']
        genotype = finding['genotype']
        base_rec = finding['recommendation']
        
        if genotype is None or 'not found' in finding['interpretation'].lower():
            continue
        
        # LACTOSE
        if rsid == 'rs4988235' and risk in ['high', 'moderate']:
            rec = {'category': 'Dairy/Lactose', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if 'bloating' in digestive_issues or 'gas' in digestive_issues:
                rec['personalized_note'] = 'You reported digestive issues - lactose intolerance may be contributing.'
            if risk == 'high':
                recommendations['high_priority'].append(rec)
                recommendations['foods_to_limit'].append('Regular dairy products')
                recommendations['foods_to_increase'].append('Lactose-free alternatives')
            else:
                recommendations['moderate_priority'].append(rec)
        
        # CAFFEINE
        elif rsid == 'rs762551' and risk in ['high', 'moderate']:
            rec = {'category': 'Caffeine', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if caffeine_intake > 2 and risk == 'high':
                rec['personalized_note'] = f'You drink {caffeine_intake} cups/day but are a slow metabolizer.'
                recommendations['high_priority'].append(rec)
                recommendations['foods_to_limit'].append('Coffee after noon')
            else:
                recommendations['moderate_priority'].append(rec)
        
        # ALCOHOL
        elif rsid == 'rs671' and risk == 'high':
            rec = {'category': 'Alcohol', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if alcohol_freq in ['moderate', 'frequent']:
                rec['personalized_note'] = f'You drink {alcohol_freq}ly but have increased health risks.'
            recommendations['high_priority'].append(rec)
            recommendations['foods_to_limit'].append('Alcoholic beverages')
        
        # MTHFR
        elif rsid in ['rs1801133', 'rs1801131'] and risk in ['high', 'moderate']:
            rec = {'category': 'Folate/B-Vitamins', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if risk == 'high':
                recommendations['high_priority'].append(rec)
                recommendations['supplements_to_consider'].append('Methylfolate (L-5-MTHF)')
            else:
                recommendations['moderate_priority'].append(rec)
            recommendations['foods_to_increase'].append('Leafy greens, legumes')
        
        # OMEGA-3
        elif rsid == 'rs174546' and risk in ['high', 'moderate']:
            rec = {'category': 'Omega-3', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if diet_type in ['vegan', 'vegetarian']:
                rec['personalized_note'] = f'As a {diet_type}, consider algae-based omega-3 supplements.'
                recommendations['supplements_to_consider'].append('Algae omega-3')
            else:
                recommendations['foods_to_increase'].append('Fatty fish')
            if risk == 'high':
                recommendations['high_priority'].append(rec)
            else:
                recommendations['moderate_priority'].append(rec)
        
        # FTO
        elif rsid == 'rs9939609' and risk in ['high', 'moderate']:
            rec = {'category': 'Weight Management', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if 'weight_loss' in health_goals:
                rec['personalized_note'] = 'Focus on protein and exercise rather than just calorie restriction.'
            if risk == 'high':
                recommendations['high_priority'].append(rec)
            else:
                recommendations['moderate_priority'].append(rec)
            recommendations['foods_to_increase'].append('High-protein foods')
        
        # CELIAC
        elif rsid == 'rs2187668' and risk == 'high':
            rec = {'category': 'Celiac Risk', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if any(issue in digestive_issues for issue in ['bloating', 'diarrhea', 'gas']):
                rec['personalized_note'] = 'Consider celiac testing (do NOT eliminate gluten before testing).'
            recommendations['high_priority'].append(rec)
        
        # IRON
        elif rsid == 'rs1799945' and risk == 'moderate':
            rec = {'category': 'Iron', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            recommendations['moderate_priority'].append(rec)
    
    # Remove duplicates
    for key in ['foods_to_increase', 'foods_to_limit', 'supplements_to_consider']:
        recommendations[key] = list(set(recommendations[key]))
    
    return recommendations


# ============================================
# ENDPOINT: Questionnaire Template
# ============================================
@api_bp.route('/questionnaire/template', methods=['GET'])
def get_questionnaire_template():
    """Get questionnaire structure."""
    return jsonify({
        'questionnaire': {
            'age': {'type': 'number', 'label': 'Age', 'min': 18, 'max': 100},
            'sex': {'type': 'select', 'label': 'Biological Sex', 'options': ['male', 'female', 'other']},
            'activity_level': {'type': 'select', 'label': 'Activity Level', 'options': ['sedentary', 'light', 'moderate', 'active', 'very_active']},
            'diet_type': {'type': 'select', 'label': 'Diet Type', 'options': ['omnivore', 'vegetarian', 'vegan', 'pescatarian', 'keto', 'other']},
            'alcohol_frequency': {'type': 'select', 'label': 'Alcohol', 'options': ['never', 'rare', 'occasional', 'moderate', 'frequent']},
            'caffeine_cups_per_day': {'type': 'number', 'label': 'Caffeine (cups/day)', 'min': 0, 'max': 10},
            'digestive_issues': {'type': 'multiselect', 'label': 'Digestive Issues', 'options': ['bloating', 'gas', 'diarrhea', 'constipation', 'heartburn', 'none']},
            'health_goals': {'type': 'multiselect', 'label': 'Health Goals', 'options': ['weight_loss', 'weight_gain', 'energy', 'sleep', 'digestion', 'muscle', 'general']},
            'current_supplements': {'type': 'multiselect', 'label': 'Supplements', 'options': ['vitamin_d', 'vitamin_b12', 'iron', 'omega_3', 'methylfolate', 'none']},
            'known_allergies': {'type': 'multiselect', 'label': 'Allergies', 'options': ['dairy', 'gluten', 'nuts', 'shellfish', 'soy', 'eggs', 'none']}
        }
    }), 200


# ============================================
# ENDPOINT: Session Status
# ============================================
@api_bp.route('/session/<session_id>', methods=['GET'])
def get_session_status(session_id):
    """Get session status."""
    db = get_db()
    session = get_session(db, session_id)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session_id': session.session_id,
        'status': session.status,
        'created_at': session.created_at.isoformat(),
        'has_genetic_results': session.has_genetic_results,
        'has_questionnaire': session.has_questionnaire,
        'has_recommendations': session.has_recommendations
    }), 200


# ============================================
# ENDPOINT: Delete Session (GDPR)
# ============================================
@api_bp.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete all session data (GDPR compliance)."""
    db = get_db()
    session = get_session(db, session_id)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    try:
        if os.path.exists(session.filepath):
            os.remove(session.filepath)
    except Exception:
        pass
    
    if delete_session_data(db, session_id):
        return jsonify({'success': True, 'message': 'All data deleted'}), 200
    else:
        return jsonify({'error': 'Deletion failed'}), 500


# ============================================
# ENDPOINT: List SNPs
# ============================================
@api_bp.route('/snps', methods=['GET'])
def list_available_snps():
    """List analyzed SNPs."""
    snps_list = [{'rsid': rsid, 'gene': data['gene'], 'condition': data['condition']} 
                 for rsid, data in NUTRIGENOMICS_SNPS.items()]
    return jsonify({'total_snps': len(snps_list), 'snps': snps_list}), 200

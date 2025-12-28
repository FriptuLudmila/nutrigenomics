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

api_bp = Blueprint('api', __name__)


def allowed_file(filename):
    allowed_ext = current_app.config.get('ALLOWED_EXTENSIONS', {'txt', 'csv', 'zip'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


# ============================================
# ENDPOINT: Upload Genetic File
# ============================================
@api_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type', 'allowed': '.txt, .csv, .zip'}), 400
    
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
            return jsonify({'error': 'Database error'}), 500
        
        return jsonify({
            'success': True,
            'session_id': session.session_id,
            'message': 'File uploaded successfully',
            'file_info': {'original_name': filename, 'size_bytes': session.file_size_bytes},
            'next_step': 'POST /api/analyze with session_id'
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Upload failed', 'message': str(e)}), 500


# ============================================
# ENDPOINT: Analyze Genetic Data
# ============================================
@api_bp.route('/analyze', methods=['POST'])
def analyze_genetic_data():
    data = request.get_json()
    if not data or 'session_id' not in data:
        return jsonify({'error': 'Missing session_id'}), 400
    
    session_id = data['session_id']
    db = get_db()
    
    session = get_session(db, session_id)
    if not session:
        return jsonify({'error': 'Invalid session_id'}), 404
    
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
            'low_risk': len([f for f in findings if f['risk_level'] == 'low']),
            'protective': len([f for f in findings if f['risk_level'] == 'protective'])
        }
        
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
            'next_step': 'POST /api/questionnaire'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Analysis failed', 'message': str(e)}), 500


# ============================================
# ENDPOINT: Submit Questionnaire
# ============================================
@api_bp.route('/questionnaire', methods=['POST'])
def submit_questionnaire():
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
        'next_step': 'GET /api/recommendations/<session_id>'
    }), 200


# ============================================
# ENDPOINT: Get Recommendations
# ============================================
@api_bp.route('/recommendations/<session_id>', methods=['GET'])
def get_recommendations(session_id):
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
    """Generate personalized recommendations based on 25 genetic variants and lifestyle."""
    recommendations = {
        'high_priority': [],
        'moderate_priority': [],
        'general_advice': [],
        'foods_to_increase': [],
        'foods_to_limit': [],
        'supplements_to_consider': []
    }
    
    # Extract questionnaire data
    activity_level = questionnaire.get('activity_level', 'moderate')
    diet_type = questionnaire.get('diet_type', 'omnivore')
    caffeine_intake = questionnaire.get('caffeine_cups_per_day', 0)
    alcohol_freq = questionnaire.get('alcohol_frequency', 'not_specified')
    digestive_issues = questionnaire.get('digestive_issues', [])
    health_goals = questionnaire.get('health_goals', [])
    current_supplements = questionnaire.get('current_supplements', [])
    allergies = questionnaire.get('known_allergies', [])
    age = questionnaire.get('age', 30)
    
    for finding in findings:
        rsid = finding['rsid']
        risk = finding['risk_level']
        condition = finding['condition']
        genotype = finding['genotype']
        base_rec = finding['recommendation']
        gene = finding['gene']
        
        if genotype is None or 'not found' in finding['interpretation'].lower():
            continue
        
        # ==========================================
        # DIGESTIVE & TASTE VARIANTS
        # ==========================================
        
        # Lactose Intolerance
        if rsid == 'rs4988235' and risk in ['high', 'moderate']:
            rec = {'category': 'Dairy/Lactose', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if 'bloating' in digestive_issues or 'gas' in digestive_issues:
                rec['personalized_note'] = 'Your digestive issues may be related to lactose intolerance.'
            if risk == 'high':
                recommendations['high_priority'].append(rec)
                recommendations['foods_to_limit'].append('Regular dairy (milk, ice cream, soft cheese)')
                recommendations['foods_to_increase'].append('Lactose-free dairy or plant-based alternatives')
            else:
                recommendations['moderate_priority'].append(rec)
        
        # Celiac Risk
        elif rsid == 'rs2187668' and risk == 'high':
            rec = {'category': 'Celiac Risk', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if any(issue in digestive_issues for issue in ['bloating', 'diarrhea', 'gas']):
                rec['personalized_note'] = 'You have symptoms AND genetic risk. Consider celiac testing (do NOT eliminate gluten first).'
            recommendations['high_priority'].append(rec)
        
        # Bitter Taste
        elif rsid == 'rs1726866' and risk == 'high':
            rec = {'category': 'Taste Perception', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            recommendations['moderate_priority'].append(rec)
            recommendations['general_advice'].append({
                'category': 'Vegetables',
                'advice': 'You are a super-taster. Roasting vegetables and adding olive oil/cheese can reduce bitterness.'
            })
        
        # Fat Taste
        elif rsid == 'rs1761667' and risk == 'high':
            rec = {'category': 'Fat Perception', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if 'weight_loss' in health_goals:
                rec['personalized_note'] = 'You may not taste fat well, leading to overeating. Be mindful of portion sizes.'
            recommendations['moderate_priority'].append(rec)
        
        # ==========================================
        # CAFFEINE & ALCOHOL
        # ==========================================
        
        # Caffeine
        elif rsid == 'rs762551':
            if risk == 'high':
                rec = {'category': 'Caffeine', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
                if caffeine_intake > 1:
                    rec['personalized_note'] = f'You drink {caffeine_intake} cups/day but are a slow metabolizer. Limit to 1 cup before noon.'
                    recommendations['high_priority'].append(rec)
                    recommendations['foods_to_limit'].append('Coffee after noon, energy drinks')
                else:
                    recommendations['moderate_priority'].append(rec)
            elif risk == 'low' and caffeine_intake <= 4:
                recommendations['general_advice'].append({
                    'category': 'Caffeine',
                    'advice': f'You are a fast caffeine metabolizer. Your {caffeine_intake} cups/day is fine and may have health benefits.'
                })
        
        # Alcohol (ALDH2)
        elif rsid == 'rs671' and risk == 'high':
            rec = {'category': 'Alcohol', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec, 'urgency': 'high'}
            if alcohol_freq in ['moderate', 'frequent']:
                rec['personalized_note'] = f'You drink {alcohol_freq}ly but have the flush reaction. This significantly increases cancer risk.'
            recommendations['high_priority'].append(rec)
            recommendations['foods_to_limit'].append('Alcoholic beverages')
        
        # Alcohol (ADH1B)
        elif rsid == 'rs1229984' and risk == 'protective':
            recommendations['general_advice'].append({
                'category': 'Alcohol',
                'advice': 'You have a protective variant that may reduce alcoholism risk through faster alcohol metabolism.'
            })
        
        # ==========================================
        # VITAMINS
        # ==========================================
        
        # MTHFR C677T
        elif rsid == 'rs1801133' and risk in ['high', 'moderate']:
            rec = {'category': 'Folate/B-Vitamins', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if 'methylfolate' in [s.lower() for s in current_supplements]:
                rec['personalized_note'] = 'Good - you are already taking methylfolate.'
            elif 'folic_acid' in [s.lower() for s in current_supplements]:
                rec['personalized_note'] = 'Switch from folic acid to methylfolate (L-5-MTHF) for better absorption.'
            if risk == 'high':
                recommendations['high_priority'].append(rec)
                recommendations['supplements_to_consider'].append('Methylfolate (L-5-MTHF)')
                recommendations['supplements_to_consider'].append('Methylcobalamin (B12)')
            else:
                recommendations['moderate_priority'].append(rec)
            recommendations['foods_to_increase'].append('Leafy greens, legumes, asparagus')
        
        # MTHFR A1298C
        elif rsid == 'rs1801131' and risk == 'moderate':
            rec = {'category': 'Folate Pathway', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            recommendations['moderate_priority'].append(rec)
        
        # Vitamin B12 Absorption (FUT2)
        elif rsid == 'rs602662' and risk in ['high', 'moderate']:
            rec = {'category': 'Vitamin B12', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if diet_type in ['vegan', 'vegetarian']:
                rec['personalized_note'] = f'As a {diet_type} with reduced B12 absorption, supplementation is essential.'
                recommendations['high_priority'].append(rec)
            else:
                recommendations['moderate_priority'].append(rec)
            recommendations['supplements_to_consider'].append('Methylcobalamin (B12)')
            recommendations['foods_to_increase'].append('Meat, fish, eggs, dairy (or supplements if vegan)')
        
        # B12 Utilization (MTRR)
        elif rsid == 'rs1801394' and risk == 'high':
            rec = {'category': 'B12 Utilization', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if diet_type in ['vegan', 'vegetarian']:
                rec['personalized_note'] = 'Combined with plant-based diet, B12 supplementation is important.'
            recommendations['moderate_priority'].append(rec)
        
        # Vitamin D Receptor
        elif rsid == 'rs2228570' and risk == 'high':
            rec = {'category': 'Vitamin D', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if 'vitamin_d' in [s.lower() for s in current_supplements]:
                rec['personalized_note'] = 'Good - you are supplementing vitamin D, which is important for your genotype.'
            recommendations['moderate_priority'].append(rec)
            recommendations['supplements_to_consider'].append('Vitamin D3 (test blood levels)')
        
        # Vitamin D Transport
        elif rsid == 'rs7041' and risk == 'high':
            recommendations['general_advice'].append({
                'category': 'Vitamin D',
                'advice': 'Your total vitamin D may test low but free vitamin D may be normal. Discuss with your doctor.'
            })
        
        # Vitamin C
        elif rsid == 'rs33972313' and risk in ['high', 'moderate']:
            rec = {'category': 'Vitamin C', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            recommendations['moderate_priority'].append(rec)
            recommendations['foods_to_increase'].append('Citrus fruits, berries, peppers, broccoli')
        
        # Beta-Carotene Conversion
        elif rsid == 'rs7501331' and risk == 'high':
            rec = {'category': 'Vitamin A', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if diet_type == 'vegan':
                rec['personalized_note'] = 'As a vegan with poor beta-carotene conversion, you may need retinol supplements.'
                recommendations['high_priority'].append(rec)
            else:
                recommendations['moderate_priority'].append(rec)
            recommendations['foods_to_increase'].append('Eggs, dairy, fish (preformed vitamin A)')
        
        # Choline
        elif rsid == 'rs7946' and risk in ['high', 'moderate']:
            rec = {'category': 'Choline', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if diet_type == 'vegan':
                rec['personalized_note'] = 'Choline is mainly in eggs/liver. Vegans with your genotype need supplements.'
            recommendations['moderate_priority'].append(rec)
            recommendations['foods_to_increase'].append('Eggs (best source), liver, fish')
        
        # ==========================================
        # MACRONUTRIENTS & WEIGHT
        # ==========================================
        
        # Omega-3 Conversion
        elif rsid == 'rs174546' and risk in ['high', 'moderate']:
            rec = {'category': 'Omega-3', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if diet_type in ['vegan', 'vegetarian']:
                rec['personalized_note'] = f'As a {diet_type} with poor omega-3 conversion, consider algae-based EPA/DHA.'
                recommendations['supplements_to_consider'].append('Algae omega-3 (EPA/DHA)')
            else:
                recommendations['foods_to_increase'].append('Fatty fish (salmon, sardines, mackerel)')
            if risk == 'high':
                recommendations['high_priority'].append(rec)
            else:
                recommendations['moderate_priority'].append(rec)
        
        # Saturated Fat Sensitivity
        elif rsid == 'rs5082' and risk == 'high':
            rec = {'category': 'Saturated Fat', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if diet_type in ['keto', 'paleo']:
                rec['personalized_note'] = f'Your {diet_type} diet is high in saturated fat, which may cause weight gain with your genotype.'
            recommendations['high_priority'].append(rec)
            recommendations['foods_to_limit'].append('Butter, coconut oil, high-fat dairy')
            recommendations['foods_to_increase'].append('Olive oil, avocado, nuts')
        
        # Carb/Diabetes Risk
        elif rsid == 'rs7903146' and risk in ['high', 'moderate']:
            rec = {'category': 'Carb Metabolism', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if 'weight_loss' in health_goals:
                rec['personalized_note'] = 'Low-carb, Mediterranean-style diet is especially beneficial for your genotype.'
            if risk == 'high':
                recommendations['high_priority'].append(rec)
                recommendations['foods_to_limit'].append('Refined carbs, white bread, sugary foods')
                recommendations['foods_to_increase'].append('Protein, healthy fats, non-starchy vegetables')
            else:
                recommendations['moderate_priority'].append(rec)
        
        # FTO Obesity Risk
        elif rsid == 'rs9939609' and risk in ['high', 'moderate']:
            rec = {'category': 'Weight Management', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if 'weight_loss' in health_goals:
                rec['personalized_note'] = 'Focus on protein and exercise rather than just calorie restriction.'
            if activity_level in ['sedentary', 'light']:
                rec['personalized_note'] = 'Exercise is particularly effective at counteracting your FTO variant.'
            if risk == 'high':
                recommendations['high_priority'].append(rec)
            else:
                recommendations['moderate_priority'].append(rec)
            recommendations['foods_to_increase'].append('High-protein foods, fiber-rich vegetables')
        
        # ==========================================
        # IRON & MINERALS
        # ==========================================
        
        # Iron Absorption
        elif rsid == 'rs1799945' and risk in ['high', 'moderate']:
            rec = {'category': 'Iron', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            if 'iron' in [s.lower() for s in current_supplements]:
                rec['personalized_note'] = 'You are taking iron supplements but have increased absorption. Check ferritin levels.'
            if risk == 'high':
                recommendations['high_priority'].append(rec)
            else:
                recommendations['moderate_priority'].append(rec)
            recommendations['foods_to_limit'].append('Iron supplements (unless prescribed)')
            recommendations['general_advice'].append({
                'category': 'Iron',
                'advice': 'Monitor ferritin levels annually. Consider blood donation if levels are high.'
            })
        
        # ==========================================
        # ANTIOXIDANTS & DETOX
        # ==========================================
        
        # SOD2 Antioxidant
        elif rsid == 'rs4880' and risk == 'moderate':
            rec = {'category': 'Antioxidants', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            recommendations['moderate_priority'].append(rec)
            recommendations['foods_to_increase'].append('Berries, leafy greens, colorful vegetables')
        
        # Glutathione Detox
        elif rsid == 'rs1695' and risk in ['high', 'moderate']:
            rec = {'category': 'Detoxification', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            recommendations['moderate_priority'].append(rec)
            recommendations['foods_to_increase'].append('Cruciferous vegetables (broccoli, cauliflower, Brussels sprouts)')
            recommendations['foods_to_increase'].append('Garlic, onions (sulfur-rich foods)')
        
        # Exercise Response
        elif rsid == 'rs4341':
            rec = {'category': 'Exercise', 'genetic_basis': f'{condition} - {genotype}', 'recommendation': base_rec}
            recommendations['general_advice'].append({
                'category': 'Fitness',
                'advice': base_rec
            })
    
    # Remove duplicates
    for key in ['foods_to_increase', 'foods_to_limit', 'supplements_to_consider']:
        recommendations[key] = list(dict.fromkeys(recommendations[key]))
    
    return recommendations


# ============================================
# ENDPOINT: Questionnaire Template
# ============================================
@api_bp.route('/questionnaire/template', methods=['GET'])
def get_questionnaire_template():
    return jsonify({
        'questionnaire': {
            'age': {'type': 'number', 'label': 'Age', 'min': 18, 'max': 100},
            'sex': {'type': 'select', 'label': 'Biological Sex', 'options': ['male', 'female', 'other']},
            'activity_level': {'type': 'select', 'label': 'Activity Level', 'options': ['sedentary', 'light', 'moderate', 'active', 'very_active']},
            'diet_type': {'type': 'select', 'label': 'Diet Type', 'options': ['omnivore', 'vegetarian', 'vegan', 'pescatarian', 'keto', 'paleo', 'other']},
            'alcohol_frequency': {'type': 'select', 'label': 'Alcohol', 'options': ['never', 'rare', 'occasional', 'moderate', 'frequent']},
            'caffeine_cups_per_day': {'type': 'number', 'label': 'Caffeine (cups/day)', 'min': 0, 'max': 10},
            'digestive_issues': {'type': 'multiselect', 'label': 'Digestive Issues', 'options': ['bloating', 'gas', 'diarrhea', 'constipation', 'heartburn', 'none']},
            'health_goals': {'type': 'multiselect', 'label': 'Health Goals', 'options': ['weight_loss', 'weight_gain', 'energy', 'sleep', 'digestion', 'muscle', 'longevity', 'general']},
            'current_supplements': {'type': 'multiselect', 'label': 'Supplements', 'options': ['vitamin_d', 'vitamin_b12', 'iron', 'omega_3', 'methylfolate', 'folic_acid', 'multivitamin', 'none']},
            'known_allergies': {'type': 'multiselect', 'label': 'Allergies', 'options': ['dairy', 'gluten', 'nuts', 'shellfish', 'soy', 'eggs', 'none']}
        }
    }), 200


# ============================================
# ENDPOINT: Session Status
# ============================================
@api_bp.route('/session/<session_id>', methods=['GET'])
def get_session_status(session_id):
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
# ENDPOINT: List SNPs (Updated for 25)
# ============================================
@api_bp.route('/snps', methods=['GET'])
def list_available_snps():
    snps_list = []
    categories = {}
    
    for rsid, data in NUTRIGENOMICS_SNPS.items():
        cat = data.get('category', 'other')
        if cat not in categories:
            categories[cat] = []
        
        snp_info = {
            'rsid': rsid,
            'gene': data['gene'],
            'condition': data['condition'],
            'category': cat
        }
        snps_list.append(snp_info)
        categories[cat].append(snp_info)
    
    return jsonify({
        'total_snps': len(snps_list),
        'by_category': {cat: len(snps) for cat, snps in categories.items()},
        'snps': snps_list
    }), 200
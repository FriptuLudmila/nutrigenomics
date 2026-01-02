"""
AI-Powered Meal Plan Generator
================================
Uses Groq API (Llama 3) to generate personalized meal plans based on genetic data and lifestyle.

Author: Caraman (Bachelor Thesis Project)
Date: December 2024
"""

import os
import json
from groq import Groq
from typing import Dict, List

# Configure Groq API
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None


def generate_meal_plan(genetic_summary: Dict, recommendations: Dict, questionnaire: Dict, days: int = 3) -> Dict:
    """
    Generate AI-powered personalized meal plan using Gemini API.

    Args:
        genetic_summary: Summary of genetic analysis (high_risk, moderate_risk counts)
        recommendations: Personalized recommendations with foods to increase/limit
        questionnaire: User's lifestyle data (diet_type, activity_level, etc.)
        days: Number of days for the meal plan (default: 3)

    Returns:
        Dictionary containing meal plan with breakfast, lunch, dinner, snacks for each day
    """

    if not client:
        return {
            'error': 'Groq API not configured. Please set GROQ_API_KEY environment variable.',
            'fallback_advice': 'Focus on the dietary recommendations provided in your report.'
        }

    # Build context from genetic and lifestyle data
    prompt = _build_meal_plan_prompt(genetic_summary, recommendations, questionnaire, days)

    try:
        # Use Groq with Llama 3.3 70B (fast and smart)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a nutrigenomics expert who creates personalized meal plans. You MUST respond with valid JSON only, no additional text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )

        # Parse the JSON response
        meal_plan = json.loads(response.choices[0].message.content)

        return {
            'success': True,
            'days': days,
            'meal_plan': meal_plan,
            'generated_by': 'Llama 3.3 70B (via Groq)',
            'disclaimer': 'This meal plan is AI-generated based on your genetic profile and should be reviewed with a healthcare professional or registered dietitian.'
        }

    except json.JSONDecodeError as e:
        # If JSON parsing fails, return structured fallback
        return {
            'error': f'Failed to parse AI response: {str(e)}',
            'raw_response': response.choices[0].message.content if response else None,
            'fallback_advice': 'Please consult with a registered dietitian for personalized meal planning.'
        }
    except Exception as e:
        return {
            'error': f'AI generation failed: {str(e)}',
            'fallback_advice': 'Focus on the dietary recommendations in your report.'
        }


def _build_meal_plan_prompt(genetic_summary: Dict, recommendations: Dict, questionnaire: Dict, days: int) -> str:
    """Build the prompt for Groq API based on user data."""

    # Extract key dietary constraints
    diet_type = questionnaire.get('diet_type', 'omnivore')
    allergies = questionnaire.get('known_allergies', [])
    activity_level = questionnaire.get('activity_level', 'moderate')
    health_goals = questionnaire.get('health_goals', [])

    # Extract genetic insights
    foods_to_increase = recommendations.get('foods_to_increase', [])
    foods_to_limit = recommendations.get('foods_to_limit', [])
    supplements = recommendations.get('supplements_to_consider', [])

    # Get high priority genetic concerns
    high_priority = recommendations.get('high_priority', [])
    genetic_concerns = [rec.get('category', '') for rec in high_priority[:3]]  # Top 3 concerns

    prompt = f"""You are a nutrigenomics-informed meal planning expert. Generate a {days}-day personalized meal plan in JSON format.

**USER PROFILE:**
- Diet Type: {diet_type.capitalize()}
- Activity Level: {activity_level.capitalize()}
- Allergies/Intolerances: {', '.join(allergies) if allergies else 'None'}
- Health Goals: {', '.join(health_goals) if health_goals else 'General wellness'}

**GENETIC INSIGHTS:**
Top Genetic Concerns: {', '.join(genetic_concerns) if genetic_concerns else 'None identified'}

Foods to PRIORITIZE (based on genetics):
{chr(10).join('- ' + food for food in foods_to_increase[:8]) if foods_to_increase else '- No specific prioritization'}

Foods to MINIMIZE (based on genetics):
{chr(10).join('- ' + food for food in foods_to_limit[:5]) if foods_to_limit else '- No specific restrictions'}

**INSTRUCTIONS:**
1. Create exactly {days} days of meals (breakfast, lunch, dinner, snacks)
2. Each meal should:
   - Align with {diet_type} diet requirements
   - Avoid all listed allergens
   - Emphasize genetically-prioritized foods
   - Minimize genetically-restricted foods
   - Match {activity_level} activity level caloric needs
3. Include brief macronutrient breakdown for each meal (protein, carbs, fats in grams)
4. Make meals practical, delicious, and easy to prepare
5. Add one "Genetic Note" per day explaining how the meals address their top genetic concern

**REQUIRED JSON FORMAT:**
{{
  "days": [
    {{
      "day": 1,
      "genetic_note": "Brief explanation of how today's meals address your genetic profile",
      "meals": {{
        "breakfast": {{
          "name": "Meal name",
          "description": "Brief description",
          "ingredients": ["ingredient1", "ingredient2", "..."],
          "macros": {{"protein_g": 25, "carbs_g": 40, "fats_g": 15}}
        }},
        "lunch": {{ ... }},
        "dinner": {{ ... }},
        "snacks": [
          {{
            "name": "Snack name",
            "description": "Brief description",
            "macros": {{"protein_g": 10, "carbs_g": 20, "fats_g": 8}}
          }}
        ]
      }}
    }}
  ]
}}

Return ONLY the JSON object, no additional text."""

    return prompt


def get_fallback_meal_plan() -> Dict:
    """Return a simple fallback meal plan when AI is unavailable."""
    return {
        'success': False,
        'fallback': True,
        'message': 'AI meal planner is currently unavailable. Please follow the dietary recommendations in your report.',
        'quick_tips': [
            'Focus on whole, unprocessed foods',
            'Include plenty of vegetables and fruits',
            'Choose lean proteins appropriate for your diet type',
            'Stay hydrated with water throughout the day',
            'Consider meal prep to ensure consistency'
        ]
    }

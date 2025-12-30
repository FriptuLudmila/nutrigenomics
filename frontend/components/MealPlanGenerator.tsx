'use client';

import { useState } from 'react';
import { nutrigenomicsAPI, type MealPlanResponse, type DayMealPlan } from '@/lib/api';
import { Utensils, ChefHat, Loader2, AlertCircle, Sparkles } from 'lucide-react';

interface MealPlanGeneratorProps {
  sessionId: string;
}

export default function MealPlanGenerator({ sessionId }: MealPlanGeneratorProps) {
  const [mealPlan, setMealPlan] = useState<MealPlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [days, setDays] = useState(3);

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await nutrigenomicsAPI.generateMealPlan(sessionId, days);
      setMealPlan(response);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to generate meal plan');
      console.error('Meal plan generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderMealCard = (meal: any, mealType: string) => (
    <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
      <h5 className="font-semibold text-slate-900 mb-1 capitalize">{mealType}</h5>
      <p className="text-sm font-medium text-slate-800 mb-2">{meal.name}</p>
      <p className="text-xs text-slate-600 mb-3">{meal.description}</p>
      {meal.ingredients && meal.ingredients.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-medium text-slate-700 mb-1">Ingredients:</p>
          <ul className="text-xs text-slate-600 space-y-0.5">
            {meal.ingredients.slice(0, 5).map((ing: string, idx: number) => (
              <li key={idx}>• {ing}</li>
            ))}
            {meal.ingredients.length > 5 && <li className="text-slate-500">...and more</li>}
          </ul>
        </div>
      )}
      <div className="flex gap-3 text-xs">
        <span className="text-blue-700">P: {meal.macros.protein_g}g</span>
        <span className="text-green-700">C: {meal.macros.carbs_g}g</span>
        <span className="text-yellow-700">F: {meal.macros.fats_g}g</span>
      </div>
    </div>
  );

  const renderDayPlan = (dayPlan: DayMealPlan) => (
    <div key={dayPlan.day} className="bg-white rounded-lg border border-slate-200 p-6">
      <div className="flex items-center gap-2 mb-4">
        <ChefHat className="w-5 h-5 text-blue-600" />
        <h4 className="text-lg font-bold text-slate-900">Day {dayPlan.day}</h4>
      </div>

      {dayPlan.genetic_note && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-xs text-blue-900">
            <strong>Genetic Insight:</strong> {dayPlan.genetic_note}
          </p>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {renderMealCard(dayPlan.meals.breakfast, 'Breakfast')}
        {renderMealCard(dayPlan.meals.lunch, 'Lunch')}
        {renderMealCard(dayPlan.meals.dinner, 'Dinner')}

        {dayPlan.meals.snacks && dayPlan.meals.snacks.length > 0 && (
          <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
            <h5 className="font-semibold text-slate-900 mb-3">Snacks</h5>
            <div className="space-y-2">
              {dayPlan.meals.snacks.map((snack, idx) => (
                <div key={idx} className="text-xs">
                  <p className="font-medium text-slate-800">{snack.name}</p>
                  <p className="text-slate-600 mb-1">{snack.description}</p>
                  <div className="flex gap-2">
                    <span className="text-blue-700">P: {snack.macros.protein_g}g</span>
                    <span className="text-green-700">C: {snack.macros.carbs_g}g</span>
                    <span className="text-yellow-700">F: {snack.macros.fats_g}g</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-2xl font-bold text-slate-900">AI Meal Planner</h3>
          <p className="text-sm text-slate-600">Genetically optimized meals powered by AI</p>
        </div>
      </div>

      {!mealPlan && (
        <div className="text-center py-8">
          <Utensils className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-600 mb-6">
            Generate a personalized meal plan based on your genetic profile and dietary preferences.
          </p>

          <div className="max-w-xs mx-auto mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Meal Plan Duration
            </label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-slate-900"
              disabled={loading}
            >
              <option value={1}>1 Day</option>
              <option value={3}>3 Days</option>
              <option value={5}>5 Days</option>
              <option value={7}>7 Days (Full Week)</option>
            </select>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="btn btn-primary flex items-center gap-2 mx-auto"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Meal Plan
              </>
            )}
          </button>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>
      )}

      {mealPlan?.meal_plan?.error && (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-900 mb-2">
            <strong>Note:</strong> {mealPlan.meal_plan.error}
          </p>
          {mealPlan.meal_plan.fallback_advice && (
            <p className="text-sm text-yellow-800">{mealPlan.meal_plan.fallback_advice}</p>
          )}
        </div>
      )}

      {mealPlan?.meal_plan?.meal_plan?.days && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <p className="text-sm text-slate-600">
              Generated by {mealPlan.meal_plan.generated_by || 'AI'}
            </p>
            <button
              onClick={() => setMealPlan(null)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Generate New Plan
            </button>
          </div>

          {mealPlan.meal_plan.meal_plan.days.map(renderDayPlan)}

          {mealPlan.meal_plan.disclaimer && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-xs text-blue-900">{mealPlan.meal_plan.disclaimer}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

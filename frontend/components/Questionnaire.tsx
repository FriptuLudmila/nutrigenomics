'use client';

import { useState } from 'react';
import type { QuestionnaireAnswers } from '@/lib/api';

interface QuestionnaireProps {
  onSubmit: (answers: QuestionnaireAnswers) => void;
  loading: boolean;
}

export default function Questionnaire({ onSubmit, loading }: QuestionnaireProps) {
  const [answers, setAnswers] = useState<QuestionnaireAnswers>({
    age: 30,
    sex: 'male',
    activity_level: 'moderate',
    diet_type: 'omnivore',
    alcohol_frequency: 'occasional',
    caffeine_cups_per_day: 1,
    digestive_issues: [],
    health_goals: [],
    current_supplements: [],
    known_allergies: [],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(answers);
  };

  const handleMultiSelect = (field: keyof QuestionnaireAnswers, value: string) => {
    const currentValues = answers[field] as string[];
    const newValues = currentValues.includes(value)
      ? currentValues.filter(v => v !== value)
      : [...currentValues, value];
    setAnswers({ ...answers, [field]: newValues });
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">
          Lifestyle Assessment
        </h2>
        <p className="text-sm text-slate-600">
          Complete this brief assessment to personalize your recommendations
        </p>
      </div>

      <div className="space-y-6">
        {/* Age */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Age</label>
          <input
            type="number"
            min="18"
            max="100"
            value={answers.age}
            onChange={(e) => setAnswers({ ...answers, age: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-slate-900"
            required
          />
        </div>

        {/* Sex */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Biological Sex</label>
          <select
            value={answers.sex}
            onChange={(e) => setAnswers({ ...answers, sex: e.target.value as any })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-slate-900"
            required
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* Activity Level */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Activity Level</label>
          <select
            value={answers.activity_level}
            onChange={(e) => setAnswers({ ...answers, activity_level: e.target.value as any })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-slate-900"
            required
          >
            <option value="sedentary">Sedentary (little or no exercise)</option>
            <option value="light">Light (exercise 1-3 days/week)</option>
            <option value="moderate">Moderate (exercise 3-5 days/week)</option>
            <option value="active">Active (exercise 6-7 days/week)</option>
            <option value="very_active">Very Active (intense exercise daily)</option>
          </select>
        </div>

        {/* Diet Type */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Diet Type</label>
          <select
            value={answers.diet_type}
            onChange={(e) => setAnswers({ ...answers, diet_type: e.target.value as any })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          >
            <option value="omnivore">Omnivore</option>
            <option value="vegetarian">Vegetarian</option>
            <option value="vegan">Vegan</option>
            <option value="pescatarian">Pescatarian</option>
            <option value="keto">Keto</option>
            <option value="paleo">Paleo</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* Alcohol */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Alcohol Frequency</label>
          <select
            value={answers.alcohol_frequency}
            onChange={(e) => setAnswers({ ...answers, alcohol_frequency: e.target.value as any })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          >
            <option value="never">Never</option>
            <option value="rare">Rare (few times a year)</option>
            <option value="occasional">Occasional (1-2 times a month)</option>
            <option value="moderate">Moderate (1-2 times a week)</option>
            <option value="frequent">Frequent (3+ times a week)</option>
          </select>
        </div>

        {/* Caffeine */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Caffeine (cups of coffee/tea per day)
          </label>
          <input
            type="number"
            min="0"
            max="10"
            value={answers.caffeine_cups_per_day}
            onChange={(e) => setAnswers({ ...answers, caffeine_cups_per_day: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        {/* Digestive Issues */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Digestive Issues (select all that apply)
          </label>
          <div className="grid grid-cols-2 gap-2">
            {['bloating', 'gas', 'diarrhea', 'constipation', 'heartburn', 'none'].map((issue) => (
              <label key={issue} className="flex items-center space-x-2 p-2 border rounded hover:bg-slate-50 border-slate-200 cursor-pointer">
                <input
                  type="checkbox"
                  checked={answers.digestive_issues.includes(issue)}
                  onChange={() => handleMultiSelect('digestive_issues', issue)}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <span className="text-xs capitalize">{issue}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Health Goals */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Health Goals (select all that apply)
          </label>
          <div className="grid grid-cols-2 gap-2">
            {['weight_loss', 'weight_gain', 'energy', 'sleep', 'digestion', 'muscle', 'longevity', 'general'].map((goal) => (
              <label key={goal} className="flex items-center space-x-2 p-2 border rounded hover:bg-slate-50 border-slate-200 cursor-pointer">
                <input
                  type="checkbox"
                  checked={answers.health_goals.includes(goal)}
                  onChange={() => handleMultiSelect('health_goals', goal)}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <span className="text-xs capitalize">{goal.replace('_', ' ')}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Current Supplements */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Current Supplements (select all that apply)
          </label>
          <div className="grid grid-cols-2 gap-2">
            {['vitamin_d', 'vitamin_b12', 'iron', 'omega_3', 'methylfolate', 'folic_acid', 'multivitamin', 'none'].map((supp) => (
              <label key={supp} className="flex items-center space-x-2 p-2 border rounded hover:bg-slate-50 border-slate-200 cursor-pointer">
                <input
                  type="checkbox"
                  checked={answers.current_supplements.includes(supp)}
                  onChange={() => handleMultiSelect('current_supplements', supp)}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <span className="text-xs capitalize">{supp.replace('_', ' ')}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Allergies */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Known Allergies (select all that apply)
          </label>
          <div className="grid grid-cols-2 gap-2">
            {['dairy', 'gluten', 'nuts', 'shellfish', 'soy', 'eggs', 'none'].map((allergy) => (
              <label key={allergy} className="flex items-center space-x-2 p-2 border rounded hover:bg-slate-50 border-slate-200 cursor-pointer">
                <input
                  type="checkbox"
                  checked={answers.known_allergies.includes(allergy)}
                  onChange={() => handleMultiSelect('known_allergies', allergy)}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <span className="text-xs capitalize">{allergy}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-8">
        <button
          type="submit"
          disabled={loading}
          className="w-full btn btn-primary py-3"
        >
          {loading ? 'Processing...' : 'Generate Recommendations'}
        </button>
      </div>
    </form>
  );
}

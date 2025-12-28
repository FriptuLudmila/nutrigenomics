'use client';

import { useState, useEffect } from 'react';
import { nutrigenomicsAPI, type RecommendationsResponse } from '@/lib/api';
import { AlertCircle, AlertTriangle, CheckCircle, Pill, Printer, RotateCw, Info, TrendingUp } from 'lucide-react';

interface RecommendationsReportProps {
  sessionId: string;
  onReset: () => void;
}

export default function RecommendationsReport({ sessionId, onReset }: RecommendationsReportProps) {
  const [data, setData] = useState<RecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        const response = await nutrigenomicsAPI.getRecommendations(sessionId);
        setData(response);
      } catch (err: any) {
        setError(err.response?.data?.message || 'Failed to load recommendations');
        console.error('Error fetching recommendations:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mb-4"></div>
        <h2 className="text-2xl font-semibold text-slate-900">Generating Your Report...</h2>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error || 'No data available'}</p>
        <button
          onClick={onReset}
          className="btn btn-primary"
        >
          Start Over
        </button>
      </div>
    );
  }

  const { recommendations, genetic_summary, disclaimer } = data;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-slate-900 mb-2">
          Your Personalized Nutrigenomics Report
        </h2>
        <p className="text-slate-600">
          Based on {genetic_summary.nutrigenomics_snps_analyzed} genetic variants analyzed
        </p>
      </div>

      {/* Genetic Summary */}
      <div className="bg-white rounded-lg p-6 border border-slate-200">
        <h3 className="text-xl font-semibold mb-4 text-slate-900">Genetic Analysis Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="High Risk" value={genetic_summary.high_risk} color="red" />
          <StatCard label="Moderate Risk" value={genetic_summary.moderate_risk} color="yellow" />
          <StatCard label="Low Risk" value={genetic_summary.low_risk} color="green" />
          <StatCard label="Protective" value={genetic_summary.protective} color="blue" />
        </div>
      </div>

      {/* High Priority Recommendations */}
      {recommendations.high_priority.length > 0 && (
        <section>
          <h3 className="text-2xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-6 h-6 text-red-600" />
            High Priority Recommendations
          </h3>
          <div className="space-y-4">
            {recommendations.high_priority.map((rec, idx) => (
              <RecommendationCard key={idx} recommendation={rec} priority="high" />
            ))}
          </div>
        </section>
      )}

      {/* Moderate Priority Recommendations */}
      {recommendations.moderate_priority.length > 0 && (
        <section>
          <h3 className="text-2xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-yellow-600" />
            Moderate Priority Recommendations
          </h3>
          <div className="space-y-4">
            {recommendations.moderate_priority.map((rec, idx) => (
              <RecommendationCard key={idx} recommendation={rec} priority="moderate" />
            ))}
          </div>
        </section>
      )}

      {/* Dietary Summary */}
      <section className="bg-white rounded-lg border border-slate-200 p-6">
        <h3 className="text-2xl font-bold text-slate-900 mb-6">Dietary Summary</h3>
        <div className="grid md:grid-cols-3 gap-6">
          {/* Foods to Increase */}
          <div>
            <h4 className="font-semibold text-green-700 mb-3 flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              Foods to Increase
            </h4>
            <ul className="space-y-2">
              {recommendations.foods_to_increase.length > 0 ? (
                recommendations.foods_to_increase.map((food, idx) => (
                  <li key={idx} className="text-sm text-slate-700 pl-4">
                    • {food}
                  </li>
                ))
              ) : (
                <li className="text-sm text-slate-500">No specific recommendations</li>
              )}
            </ul>
          </div>

          {/* Foods to Limit */}
          <div>
            <h4 className="font-semibold text-red-700 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Foods to Limit
            </h4>
            <ul className="space-y-2">
              {recommendations.foods_to_limit.length > 0 ? (
                recommendations.foods_to_limit.map((food, idx) => (
                  <li key={idx} className="text-sm text-slate-700 pl-4">
                    • {food}
                  </li>
                ))
              ) : (
                <li className="text-sm text-slate-500">No specific restrictions</li>
              )}
            </ul>
          </div>

          {/* Supplements to Consider */}
          <div>
            <h4 className="font-semibold text-blue-700 mb-3 flex items-center gap-2">
              <Pill className="w-5 h-5" />
              Supplements to Consider
            </h4>
            <ul className="space-y-2">
              {recommendations.supplements_to_consider.length > 0 ? (
                recommendations.supplements_to_consider.map((supp, idx) => (
                  <li key={idx} className="text-sm text-slate-700 pl-4">
                    • {supp}
                  </li>
                ))
              ) : (
                <li className="text-sm text-slate-500">None needed based on your genetics</li>
              )}
            </ul>
          </div>
        </div>
      </section>

      {/* General Advice */}
      {recommendations.general_advice.length > 0 && (
        <section>
          <h3 className="text-2xl font-bold text-slate-900 mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            General Health Insights
          </h3>
          <div className="space-y-3">
            {recommendations.general_advice.map((advice, idx) => (
              <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-1">{advice.category}</h4>
                <p className="text-sm text-blue-800">{advice.advice}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-700 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-yellow-900">
            <strong>Disclaimer:</strong> {disclaimer}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center gap-4 no-print">
        <button
          onClick={() => window.print()}
          className="btn btn-primary flex items-center gap-2"
        >
          <Printer className="w-4 h-4" />
          Print Report
        </button>
        <button
          onClick={onReset}
          className="btn bg-slate-600 text-white hover:bg-slate-700"
        >
          <RotateCw className="w-4 h-4" />
          Start New Analysis
        </button>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  const colorClasses = {
    red: 'bg-red-100 text-red-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    green: 'bg-green-100 text-green-800',
    blue: 'bg-blue-100 text-blue-800',
  };

  return (
    <div className={`rounded-lg p-4 ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm font-medium">{label}</div>
    </div>
  );
}

function RecommendationCard({ recommendation, priority }: { recommendation: any; priority: 'high' | 'moderate' }) {
  const bgColor = priority === 'high' ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200';
  const textColor = priority === 'high' ? 'text-red-900' : 'text-yellow-900';

  return (
    <div className={`border rounded-lg p-6 ${bgColor}`}>
      <div className="flex justify-between items-start mb-3">
        <h4 className={`text-lg font-semibold ${textColor}`}>{recommendation.category}</h4>
        <span className="text-xs bg-white px-2 py-1 rounded font-medium text-slate-700">{recommendation.genetic_basis}</span>
      </div>
      <p className="text-slate-700 mb-3">{recommendation.recommendation}</p>
      {recommendation.personalized_note && (
        <div className="bg-white bg-opacity-50 rounded p-3 mt-3 flex items-start gap-2">
          <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm font-medium text-slate-800">
            <strong>Personalized Note:</strong> {recommendation.personalized_note}
          </p>
        </div>
      )}
    </div>
  );
}

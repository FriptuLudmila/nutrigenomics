'use client';

import { useState } from 'react';
import { nutrigenomicsAPI, type QuestionnaireAnswers } from '@/lib/api';
import { CheckCircle2, Circle } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import Questionnaire from '@/components/Questionnaire';
import RecommendationsReport from '@/components/RecommendationsReport';

type Step = 'upload' | 'analyzing' | 'questionnaire' | 'recommendations';

export default function Home() {
  const [step, setStep] = useState<Step>('upload');
  const [sessionId, setSessionId] = useState<string>('');
  const [fileName, setFileName] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleFileUpload = async (file: File) => {
    try {
      setLoading(true);
      setError('');
      setFileName(file.name);

      // Upload file
      const uploadResponse = await nutrigenomicsAPI.uploadFile(file);
      setSessionId(uploadResponse.session_id);

      // Automatically analyze
      setStep('analyzing');
      await nutrigenomicsAPI.analyzeGenetics(uploadResponse.session_id);

      // Move to questionnaire
      setStep('questionnaire');
    } catch (err) {
      const error = err as { response?: { data?: { message?: string } } };
      setError(error.response?.data?.message || 'Upload failed. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionnaireSubmit = async (answers: QuestionnaireAnswers) => {
    try {
      setLoading(true);
      setError('');

      await nutrigenomicsAPI.submitQuestionnaire(sessionId, answers);
      setStep('recommendations');
    } catch (err) {
      const error = err as { response?: { data?: { message?: string } } };
      setError(error.response?.data?.message || 'Failed to submit questionnaire.');
      console.error('Questionnaire error:', err);
    } finally {
      setLoading(false);
    }
  };

  const resetAnalysis = () => {
    setStep('upload');
    setSessionId('');
    setFileName('');
    setError('');
  };

  const steps = [
    { id: 'upload', label: 'Upload Data' },
    { id: 'analyzing', label: 'Analysis' },
    { id: 'questionnaire', label: 'Lifestyle' },
    { id: 'recommendations', label: 'Results' }
  ];

  const currentStepIndex = steps.findIndex(s => s.id === step);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 relative overflow-hidden">
        {/* Background Image - Repeating Pattern */}
        <div
          className="absolute inset-0 opacity-15"
          style={{
            backgroundImage: 'url(/genes.png)',
            backgroundRepeat: 'repeat-x',
            backgroundSize: 'auto 100%',
            backgroundPosition: 'center'
          }}
        />

        {/* Content */}
        <div className="container mx-auto px-4 py-8 max-w-7xl relative z-10">
          <div className="text-center relative top-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Nutrigenomics Analysis</h1>
            <p className="text-base text-slate-700">Personalized nutrition based on your genetics</p>
          </div>
        </div>
      </header>

      {/* Progress Indicator */}
      <div className="bg-white border-b border-slate-200">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <div className="flex items-center justify-between">
            {steps.map((s, idx) => (
              <div key={s.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                    idx < currentStepIndex
                      ? 'border-blue-600 bg-blue-600'
                      : idx === currentStepIndex
                      ? 'border-blue-600 bg-white'
                      : 'border-slate-300 bg-white'
                  }`}>
                    {idx < currentStepIndex ? (
                      <CheckCircle2 className="w-6 h-6 text-white" />
                    ) : (
                      <Circle className={`w-5 h-5 ${idx === currentStepIndex ? 'text-blue-600' : 'text-slate-300'}`} />
                    )}
                  </div>
                  <span className={`mt-2 text-xs font-medium ${
                    idx <= currentStepIndex ? 'text-slate-900' : 'text-slate-400'
                  }`}>
                    {s.label}
                  </span>
                </div>
                {idx < steps.length - 1 && (
                  <div className={`h-0.5 flex-1 mx-2 ${
                    idx < currentStepIndex ? 'bg-blue-600' : 'bg-slate-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="card p-8">
          {step === 'upload' && (
            <FileUpload onUpload={handleFileUpload} loading={loading} />
          )}

          {step === 'analyzing' && (
            <div className="text-center py-16">
              <div className="inline-block relative">
                <div className="w-16 h-16 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin"></div>
              </div>
              <h2 className="text-xl font-semibold text-slate-900 mt-6">Analyzing Your Genetics</h2>
              <p className="text-sm text-slate-600 mt-2">Processing {fileName}</p>
              <div className="mt-8 max-w-md mx-auto">
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-600 rounded-full animate-pulse" style={{ width: '70%' }}></div>
                </div>
              </div>
            </div>
          )}

          {step === 'questionnaire' && (
            <Questionnaire onSubmit={handleQuestionnaireSubmit} loading={loading} />
          )}

          {step === 'recommendations' && (
            <RecommendationsReport sessionId={sessionId} onReset={resetAnalysis} />
          )}
        </div>

        {/* Footer */}
        <footer className="mt-12 pt-8 border-t border-slate-200">
          <div className="text-center">
            <p className="text-xs text-slate-500">
              <strong>Medical Disclaimer:</strong> This analysis is for educational and informational purposes only.
              Always consult qualified healthcare professionals before making dietary or lifestyle changes.
            </p>
            <p className="text-xs text-slate-400 mt-2">
              Your genetic data is encrypted and secure. GDPR compliant.
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}

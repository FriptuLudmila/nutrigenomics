'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { nutrigenomicsAPI, type QuestionnaireAnswers } from '@/lib/api';
import { CheckCircle2, Circle, User, LogOut, Dna } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import Questionnaire from '@/components/Questionnaire';
import RecommendationsReport from '@/components/RecommendationsReport';

type Step = 'upload' | 'analyzing' | 'questionnaire' | 'recommendations';

const SESSION_KEY = 'genyo_session';

interface PersistedSession {
  sessionId: string;
  step: Step;
  fileName: string;
}

function persistSession(sessionId: string, step: Step, fileName: string) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify({ sessionId, step, fileName }));
}

function restoreSession(): PersistedSession | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? (JSON.parse(raw) as PersistedSession) : null;
  } catch {
    return null;
  }
}

function clearPersistedSession() {
  sessionStorage.removeItem(SESSION_KEY);
}

export default function Home() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('upload');
  const [sessionId, setSessionId] = useState<string>('');
  const [fileName, setFileName] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    if (!token) {
      router.replace('/landing');
      return;
    }

    const saved = restoreSession();
    if (!saved) return;

    setSessionId(saved.sessionId);
    setFileName(saved.fileName);

    if (saved.step === 'analyzing') {
      setStep('analyzing');
      setLoading(true);
      nutrigenomicsAPI
        .analyzeGenetics(saved.sessionId)
        .then(() => {
          setStep('questionnaire');
          persistSession(saved.sessionId, 'questionnaire', saved.fileName);
        })
        .catch(() => {
          clearPersistedSession();
          setStep('upload');
          setSessionId('');
          setFileName('');
          setError('Previous analysis could not be resumed. Please upload your file again.');
        })
        .finally(() => setLoading(false));
    } else {
      setStep(saved.step);
    }
  }, [router]);

  const handleFileUpload = async (file: File) => {
    try {
      setLoading(true);
      setError('');
      setFileName(file.name);

      const uploadResponse = await nutrigenomicsAPI.uploadFile(file);
      setSessionId(uploadResponse.session_id);
      setStep('analyzing');
      persistSession(uploadResponse.session_id, 'analyzing', file.name);

      await nutrigenomicsAPI.analyzeGenetics(uploadResponse.session_id);
      setStep('questionnaire');
      persistSession(uploadResponse.session_id, 'questionnaire', file.name);
    } catch (err) {
      const error = err as { response?: { data?: { error?: string; message?: string } } };
      setError(error.response?.data?.error || error.response?.data?.message || 'Upload failed. Please try again.');
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
      persistSession(sessionId, 'recommendations', fileName);
    } catch (err) {
      const error = err as { response?: { data?: { error?: string; message?: string } } };
      setError(error.response?.data?.error || error.response?.data?.message || 'Failed to submit questionnaire.');
      console.error('Questionnaire error:', err);
    } finally {
      setLoading(false);
    }
  };

  const resetAnalysis = () => {
    clearPersistedSession();
    setStep('upload');
    setSessionId('');
    setFileName('');
    setError('');
  };

  const handleLogout = () => {
    localStorage.clear();
    sessionStorage.clear();
    router.push('/landing');
  };

  const steps = [
    { id: 'upload',          label: 'Upload Data' },
    { id: 'analyzing',       label: 'Analysis' },
    { id: 'questionnaire',   label: 'Lifestyle' },
    { id: 'recommendations', label: 'Results' }
  ];

  const currentStepIndex = steps.findIndex(s => s.id === step);

  return (
    <div className="min-h-screen bg-ng-cream">
      {/* Header */}
      <header className="bg-ng-dark border-b border-ng-dark-2 relative overflow-hidden">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: 'url(/genes.png)',
            backgroundRepeat: 'repeat-x',
            backgroundSize: 'auto 100%',
            backgroundPosition: 'center'
          }}
        />
        <div className="container mx-auto px-4 py-6 max-w-7xl relative z-10">
          <div className="flex justify-between items-center mb-6">
            <button onClick={() => router.push('/landing')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <Dna className="w-7 h-7 text-ng-lime" />
              <span className="text-lg font-bold text-white">GenyO</span>
            </button>
            <div className="flex gap-2">
              <button
                onClick={() => router.push('/app/profile')}
                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-ng-cream hover:text-ng-lime hover:bg-ng-dark-2 rounded-lg transition-colors"
              >
                <User className="w-4 h-4" />
                Profile
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-[#E6E6E6] hover:text-red-400 hover:bg-ng-dark-2 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-2">GenyO Analysis</h1>
            <p className="text-base text-[#A0B8A0] font-medium">Personalized nutrition based on your genetics</p>
          </div>
        </div>
      </header>

      {/* Progress Indicator */}
      <div className="bg-ng-dark-2 border-b border-ng-dark-3">
        <div className="container mx-auto px-4 py-5 max-w-4xl">
          <div className="flex items-center justify-between">
            {steps.map((s, idx) => (
              <div key={s.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                    idx < currentStepIndex
                      ? 'border-ng-lime bg-ng-lime'
                      : idx === currentStepIndex
                      ? 'border-ng-lime bg-transparent'
                      : 'border-ng-dark-3 bg-transparent'
                  }`}>
                    {idx < currentStepIndex ? (
                      <CheckCircle2 className="w-6 h-6 text-ng-dark" />
                    ) : (
                      <Circle className={`w-5 h-5 ${idx === currentStepIndex ? 'text-ng-lime' : 'text-ng-dark-3'}`} />
                    )}
                  </div>
                  <span className={`mt-2 text-xs font-semibold ${
                    idx <= currentStepIndex ? 'text-ng-cream' : 'text-ng-dark-3'
                  }`}>
                    {s.label}
                  </span>
                </div>
                {idx < steps.length - 1 && (
                  <div className={`h-0.5 flex-1 mx-2 ${
                    idx < currentStepIndex ? 'bg-ng-lime' : 'bg-ng-dark-3'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-10 max-w-7xl">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-sm text-red-800 font-medium">{error}</p>
          </div>
        )}

        <div className="card p-8">
          {step === 'upload' && (
            <FileUpload onUpload={handleFileUpload} loading={loading} />
          )}

          {step === 'analyzing' && (
            <div className="text-center py-16">
              <div className="inline-block relative">
                <div className="w-16 h-16 border-4 border-ng-border border-t-ng-lime rounded-full animate-spin" />
              </div>
              <h2 className="text-xl font-semibold text-ng-text mt-6">Analyzing Your Genetics</h2>
              <p className="text-sm text-ng-muted mt-2 font-medium">Processing {fileName}</p>
              <div className="mt-8 max-w-md mx-auto">
                <div className="h-2 bg-ng-border rounded-full overflow-hidden">
                  <div className="h-full bg-ng-lime rounded-full animate-pulse" style={{ width: '70%' }} />
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
        <footer className="mt-12 pt-8 border-t border-ng-border">
          <div className="text-center">
            <p className="text-xs text-ng-muted font-medium">
              <strong className="text-ng-text-2">Medical Disclaimer:</strong> This analysis is for educational and informational purposes only.
              Always consult qualified healthcare professionals before making dietary or lifestyle changes.
            </p>
            <p className="text-xs text-ng-muted mt-2">
              Your genetic data is encrypted and secure. GDPR compliant.
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}

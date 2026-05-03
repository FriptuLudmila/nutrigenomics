'use client';

import { useState } from 'react';
import { X, Eye, EyeOff, Dna } from 'lucide-react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type AuthMode = 'signin' | 'signup' | 'verify' | 'forgot';

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const router = useRouter();
  const [mode, setMode] = useState<AuthMode>('signin');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    age: '',
    sex: 'other',
    verificationCode: ''
  });

  if (!isOpen) return null;

  const validatePassword = (pw: string): string | null => {
    if (pw.length < 10) return 'Password must be at least 10 characters';
    if (!/[A-Z]/.test(pw)) return 'Password must contain at least one uppercase letter';
    if (!/[0-9]/.test(pw)) return 'Password must contain at least one digit';
    if (!/[!@#$%^&*()\-_=+[\]{}|;:'",.<>?/`~\\]/.test(pw)) return 'Password must contain at least one symbol';
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      if (mode === 'forgot') {
        const response = await fetch(`${API_BASE_URL}/api/auth/reset-password-request`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email: formData.email }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Failed to send reset email');
        setSuccessMessage('If an account exists with this email, a reset link has been sent. Check your inbox.');
        return;
      } else if (mode === 'signin') {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email: formData.email, password: formData.password, remember_me: rememberMe }),
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Sign in failed');

        localStorage.setItem('logged_in', 'true');
        router.push('/app');
      } else if (mode === 'signup') {
        const pwError = validatePassword(formData.password);
        if (pwError) {
          setError(pwError);
          setLoading(false);
          return;
        }
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            name: formData.name,
            age: parseInt(formData.age),
            sex: formData.sex,
            email: formData.email,
            password: formData.password
          }),
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Registration failed');

        setSuccessMessage(`Verification code sent to ${formData.email}`);
        setMode('verify');
      } else if (mode === 'verify') {
        const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email: formData.email, code: formData.verificationCode }),
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Verification failed');

        localStorage.setItem('logged_in', 'true');
        router.push('/app');
      }
    } catch (err: unknown) {
      const error = err as { message?: string };
      setError(error.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/resend-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email: formData.email }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Failed to resend code');

      setSuccessMessage('Verification code resent!');
    } catch (err: unknown) {
      const error = err as { message?: string };
      setError(error.message || 'Failed to resend code');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
    setSuccessMessage('');
  };

  const switchMode = (newMode: AuthMode) => {
    setMode(newMode);
    setError('');
    setSuccessMessage('');
    setFormData({ email: formData.email, password: '', name: '', age: '', sex: 'other', verificationCode: '' });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ng-dark/70 backdrop-blur-sm">
      <div className="bg-ng-cream rounded-2xl shadow-2xl max-w-md w-full mx-4 relative border border-ng-border">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-ng-muted hover:text-ng-text transition-colors"
        >
          <X className="w-6 h-6" />
        </button>

        {/* Content */}
        <div className="p-8">
          {/* Logo */}
          <div className="flex items-center gap-2 mb-6">
            <div className="w-9 h-9 rounded-lg bg-ng-dark flex items-center justify-center">
              <Dna className="w-5 h-5 text-ng-lime" />
            </div>
            <span className="font-bold text-ng-text text-lg">GenyO</span>
          </div>

          <h2 className="text-2xl font-bold text-ng-text mb-1">
            {mode === 'signin' && 'Welcome Back'}
            {mode === 'signup' && 'Create Account'}
            {mode === 'verify' && 'Verify Email'}
            {mode === 'forgot' && 'Reset Password'}
          </h2>
          <p className="text-ng-muted font-medium mb-6">
            {mode === 'signin' && 'Sign in to access your personalized nutrition insights'}
            {mode === 'signup' && 'Start your personalized nutrition journey'}
            {mode === 'verify' && 'Enter the verification code sent to your email'}
            {mode === 'forgot' && "Enter your email and we'll send you a reset link"}
          </p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-800 font-medium">
              {error}
            </div>
          )}
          {successMessage && (
            <div className="mb-4 p-3 bg-ng-light border border-ng-border rounded-xl text-sm text-ng-dark font-medium">
              {successMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'forgot' ? (
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-ng-text-2 mb-1.5">Email</label>
                <input
                  type="email" id="email" name="email"
                  value={formData.email} onChange={handleChange}
                  required className="input-field" placeholder="you@example.com"
                />
              </div>
            ) : mode === 'verify' ? (
              <>
                <div>
                  <label htmlFor="verificationCode" className="block text-sm font-semibold text-ng-text-2 mb-1.5">
                    Verification Code
                  </label>
                  <input
                    type="text"
                    id="verificationCode"
                    name="verificationCode"
                    value={formData.verificationCode}
                    onChange={handleChange}
                    required
                    maxLength={6}
                    className="input-field text-center text-2xl tracking-widest"
                    placeholder="000000"
                  />
                </div>
                <button
                  type="button"
                  onClick={handleResendCode}
                  disabled={loading}
                  className="w-full text-sm text-ng-dark hover:text-ng-dark-2 font-semibold transition-colors"
                >
                  Resend Code
                </button>
              </>
            ) : (
              <>
                {mode === 'signup' && (
                  <>
                    <div>
                      <label htmlFor="name" className="block text-sm font-semibold text-ng-text-2 mb-1.5">
                        Full Name
                      </label>
                      <input
                        type="text" id="name" name="name"
                        value={formData.name} onChange={handleChange}
                        required className="input-field" placeholder="Jane Doe"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="age" className="block text-sm font-semibold text-ng-text-2 mb-1.5">Age</label>
                        <input
                          type="number" id="age" name="age"
                          value={formData.age} onChange={handleChange}
                          required min="18" max="120"
                          className="input-field" placeholder="30"
                        />
                      </div>
                      <div>
                        <label htmlFor="sex" className="block text-sm font-semibold text-ng-text-2 mb-1.5">Sex</label>
                        <select
                          id="sex" name="sex"
                          value={formData.sex} onChange={handleChange}
                          required className="input-field"
                        >
                          <option value="male">Male</option>
                          <option value="female">Female</option>
                          <option value="other">Other</option>
                        </select>
                      </div>
                    </div>
                  </>
                )}

                <div>
                  <label htmlFor="email" className="block text-sm font-semibold text-ng-text-2 mb-1.5">Email</label>
                  <input
                    type="email" id="email" name="email"
                    value={formData.email} onChange={handleChange}
                    required className="input-field" placeholder="you@example.com"
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-semibold text-ng-text-2 mb-1.5">Password</label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="password" name="password"
                      value={formData.password} onChange={handleChange}
                      required minLength={10}
                      className="input-field pr-10" placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-ng-muted hover:text-ng-text transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  {mode === 'signup' && (
                    <p className="mt-1.5 text-xs text-ng-muted">
                      Min. 10 characters, one uppercase, one digit, one symbol
                    </p>
                  )}
                </div>
              </>
            )}

            {mode === 'signin' && (
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => switchMode('forgot')}
                  className="text-sm text-ng-dark font-semibold hover:text-ng-dark-2 transition-colors"
                >
                  Forgot password?
                </button>
              </div>
            )}

            {mode === 'signin' && (
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={e => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-ng-border accent-ng-dark"
                />
                <span className="text-sm text-ng-muted font-medium">Keep me logged in</span>
              </label>
            )}

            <button type="submit" disabled={loading} className="w-full btn btn-primary py-3 mt-2">
              {loading ? 'Loading...' :
                mode === 'signin' ? 'Sign In' :
                mode === 'signup' ? 'Create Account' :
                mode === 'forgot' ? 'Send Reset Link' :
                'Verify'}
            </button>
          </form>

          {(mode === 'signin' || mode === 'signup') && (
            <div className="mt-5 text-center">
              <button
                onClick={() => switchMode(mode === 'signin' ? 'signup' : 'signin')}
                className="text-sm text-ng-dark font-semibold hover:text-ng-dark-2 transition-colors"
              >
                {mode === 'signin' ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
              </button>
            </div>
          )}

          {(mode === 'verify' || mode === 'forgot') && (
            <div className="mt-5 text-center">
              <button
                onClick={() => switchMode('signin')}
                className="text-sm text-ng-muted hover:text-ng-text font-medium transition-colors"
              >
                Back to sign in
              </button>
            </div>
          )}

          <p className="mt-5 text-xs text-ng-muted text-center">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
}

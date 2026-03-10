'use client';

import { useState } from 'react';
import { X, Eye, EyeOff } from 'lucide-react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type AuthMode = 'signin' | 'signup' | 'verify';

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      if (mode === 'signin') {
        // Sign in
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Sign in failed');
        }

        // Store token and user info
        const storage = rememberMe ? localStorage : sessionStorage;
        storage.setItem('auth_token', data.token);
        storage.setItem('user_email', data.user.email);
        storage.setItem('user_name', data.user.name);

        // Redirect to app
        router.push('/app');
      } else if (mode === 'signup') {
        // Register - send verification code
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: formData.name,
            age: parseInt(formData.age),
            sex: formData.sex,
            email: formData.email,
            password: formData.password
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Registration failed');
        }

        // Show success message and switch to verification mode
        setSuccessMessage(`Verification code sent to ${formData.email}`);

        // If email wasn't sent (development), show the code
        if (data.debug_code) {
          setSuccessMessage(`Development mode - Your code: ${data.debug_code}`);
        }

        setMode('verify');
      } else if (mode === 'verify') {
        // Verify email with code
        const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            code: formData.verificationCode
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Verification failed');
        }

        // Store token and user info
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user_email', data.user.email);
        localStorage.setItem('user_name', data.user.name);

        // Redirect to app
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
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to resend code');
      }

      setSuccessMessage('Verification code resent!');

      if (data.debug_code) {
        setSuccessMessage(`Development mode - Your code: ${data.debug_code}`);
      }
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
    setFormData({
      email: formData.email,
      password: '',
      name: '',
      age: '',
      sex: 'other',
      verificationCode: ''
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
        >
          <X className="w-6 h-6" />
        </button>

        {/* Content */}
        <div className="p-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">
            {mode === 'signin' && 'Welcome Back'}
            {mode === 'signup' && 'Create Account'}
            {mode === 'verify' && 'Verify Email'}
          </h2>
          <p className="text-slate-600 mb-6">
            {mode === 'signin' && 'Sign in to access your personalized nutrition insights'}
            {mode === 'signup' && 'Start your personalized nutrition journey'}
            {mode === 'verify' && 'Enter the verification code sent to your email'}
          </p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-800">
              {error}
            </div>
          )}

          {successMessage && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded text-sm text-green-800">
              {successMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'verify' ? (
              <>
                <div>
                  <label htmlFor="verificationCode" className="block text-sm font-medium text-slate-700 mb-1">
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
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-center text-2xl tracking-widest"
                    placeholder="000000"
                  />
                </div>

                <button
                  type="button"
                  onClick={handleResendCode}
                  disabled={loading}
                  className="w-full text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Resend Code
                </button>
              </>
            ) : (
              <>
                {mode === 'signup' && (
                  <>
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-slate-700 mb-1">
                        Full Name
                      </label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="John Doe"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="age" className="block text-sm font-medium text-slate-700 mb-1">
                          Age
                        </label>
                        <input
                          type="number"
                          id="age"
                          name="age"
                          value={formData.age}
                          onChange={handleChange}
                          required
                          min="18"
                          max="120"
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="30"
                        />
                      </div>

                      <div>
                        <label htmlFor="sex" className="block text-sm font-medium text-slate-700 mb-1">
                          Sex
                        </label>
                        <select
                          id="sex"
                          name="sex"
                          value={formData.sex}
                          onChange={handleChange}
                          required
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                  <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="you@example.com"
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      minLength={6}
                      className="w-full px-3 py-2 pr-10 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    >
                      {showPassword ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              </>
            )}

            {mode === 'signin' && (
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={e => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-slate-600">Keep me logged in</span>
              </label>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary py-3"
            >
              {loading ? 'Loading...' : mode === 'signin' ? 'Sign In' : mode === 'signup' ? 'Create Account' : 'Verify'}
            </button>
          </form>

          {mode !== 'verify' && (
            <div className="mt-6 text-center">
              <button
                onClick={() => switchMode(mode === 'signin' ? 'signup' : 'signin')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                {mode === 'signin'
                  ? "Don't have an account? Sign up"
                  : 'Already have an account? Sign in'}
              </button>
            </div>
          )}

          {mode === 'verify' && (
            <div className="mt-6 text-center">
              <button
                onClick={() => switchMode('signup')}
                className="text-sm text-slate-600 hover:text-slate-700"
              >
                Back to sign up
              </button>
            </div>
          )}

          <p className="mt-6 text-xs text-slate-500 text-center">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
}

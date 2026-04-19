'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Dna, Eye, EyeOff, CheckCircle } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!token) {
      setError('Invalid reset link. Please request a new password reset.');
    }
  }, [token]);

  const validatePassword = (pw: string): string | null => {
    if (pw.length < 10) return 'Password must be at least 10 characters.';
    if (!/[A-Z]/.test(pw)) return 'Password must contain at least one uppercase letter.';
    if (!/[0-9]/.test(pw)) return 'Password must contain at least one digit.';
    if (!/[!@#$%^&*()\-_=+[\]{}|;:'",.<>?/`~\\]/.test(pw)) return 'Password must contain at least one symbol.';
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const pwError = validatePassword(password);
    if (pwError) {
      setError(pwError);
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/reset-password-confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Failed to reset password');
      setSuccess(true);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setError(e.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-ng-cream flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg border border-ng-border max-w-md w-full p-8">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-9 h-9 rounded-lg bg-ng-dark flex items-center justify-center">
            <Dna className="w-5 h-5 text-ng-lime" />
          </div>
          <span className="font-bold text-ng-text text-lg">GenyO</span>
        </div>

        {success ? (
          <div className="text-center py-4">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-ng-light mb-4">
              <CheckCircle className="w-8 h-8 text-ng-dark" />
            </div>
            <h2 className="text-2xl font-bold text-ng-text mb-2">Password Reset!</h2>
            <p className="text-ng-muted font-medium mb-6">Your password has been updated successfully.</p>
            <button
              onClick={() => router.push('/landing')}
              className="btn btn-primary px-8 py-3"
            >
              Sign In
            </button>
          </div>
        ) : (
          <>
            <h2 className="text-2xl font-bold text-ng-text mb-1">Set New Password</h2>
            <p className="text-ng-muted font-medium mb-6">Enter a new password for your account.</p>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-800 font-medium">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-ng-text-2 mb-1.5">New Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={10}
                    className="input-field pr-10"
                    placeholder="••••••••"
                    disabled={!token}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-ng-muted hover:text-ng-text transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <p className="text-xs text-ng-muted -mt-2">
                Min. 10 characters, one uppercase, one digit, one symbol
              </p>

              <div>
                <label className="block text-sm font-semibold text-ng-text-2 mb-1.5">Confirm Password</label>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="input-field"
                  placeholder="••••••••"
                  disabled={!token}
                />
              </div>

              <button
                type="submit"
                disabled={loading || !token}
                className="w-full btn btn-primary py-3 mt-2"
              >
                {loading ? 'Resetting...' : 'Reset Password'}
              </button>
            </form>

            <div className="mt-5 text-center">
              <button
                onClick={() => router.push('/landing')}
                className="text-sm text-ng-muted hover:text-ng-text font-medium transition-colors"
              >
                Back to sign in
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense>
      <ResetPasswordForm />
    </Suspense>
  );
}

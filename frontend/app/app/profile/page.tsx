'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { nutrigenomicsAPI, type UserProfile, type Report } from '@/lib/api';
import { User, Mail, Calendar, Users, ArrowLeft, Save, FileText, CheckCircle, Clock, Dna, Trash2 } from 'lucide-react';

const SESSION_KEY = 'genyo_session';

type Step = 'upload' | 'analyzing' | 'questionnaire' | 'recommendations';

function getStepFromReport(report: Report): Step {
  if (report.has_recommendations || report.has_questionnaire) return 'recommendations';
  if (report.has_genetic_results) return 'questionnaire';
  return 'upload';
}

export default function ProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [reports, setReports] = useState<Report[]>([]);
  const [reportsLoading, setReportsLoading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const [profile, setProfile] = useState<UserProfile>({
    user_id: '',
    email: '',
    name: '',
    age: 0,
    sex: 'other',
    email_verified: false,
    created_at: '',
  });

  const [editForm, setEditForm] = useState({ name: '', age: '', sex: 'other' });

  useEffect(() => {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    if (!token) {
      router.replace('/landing');
      return;
    }
    loadProfile();
    loadReports();
  }, [router]);

  const loadProfile = async () => {
    try {
      const data = await nutrigenomicsAPI.getMe();
      setProfile(data.user);
      setEditForm({ name: data.user.name, age: data.user.age.toString(), sex: data.user.sex });
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const loadReports = async () => {
    setReportsLoading(true);
    try {
      const data = await nutrigenomicsAPI.getMyReports();
      setReports(data.reports || []);
    } catch {
      // non-critical — silently ignore, reports section shows empty state
    } finally {
      setReportsLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccessMessage('');
    try {
      const data = await nutrigenomicsAPI.updateProfile({
        name: editForm.name,
        age: parseInt(editForm.age),
        sex: editForm.sex,
      });
      setProfile(data.user);
      setSuccessMessage('Profile updated successfully!');
      setIsEditing(false);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditForm({ name: profile.name, age: profile.age.toString(), sex: profile.sex });
    setIsEditing(false);
    setError('');
    setSuccessMessage('');
  };

  const handleDeleteReport = async (sessionId: string) => {
    setDeletingId(sessionId);
    try {
      await nutrigenomicsAPI.deleteReport(sessionId);
      setReports((prev) => prev.filter((r) => r.session_id !== sessionId));
    } catch {
      setError('Failed to delete report. Please try again.');
    } finally {
      setDeletingId(null);
      setConfirmDeleteId(null);
    }
  };

  const handleViewReport = (report: Report) => {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify({
      sessionId: report.session_id,
      step: getStepFromReport(report),
      fileName: report.original_filename,
    }));
    router.push('/app');
  };

  const handleLogout = () => {
    localStorage.clear();
    sessionStorage.clear();
    router.push('/landing');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-ng-cream flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-ng-border border-t-ng-lime rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-ng-muted font-medium">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-ng-cream">
      <header className="bg-ng-dark border-b border-ng-dark-2">
        <div className="container mx-auto px-4 py-5 max-w-7xl">
          <div className="flex justify-between items-center">
            <button
              onClick={() => router.push('/app')}
              className="flex items-center gap-2 text-ng-cream hover:text-ng-lime transition-colors font-semibold"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Analysis</span>
            </button>
            <button onClick={() => router.push('/landing')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <Dna className="w-6 h-6 text-ng-lime" />
              <span className="font-bold text-white">GenyO</span>
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-semibold text-[#E6E6E6] hover:text-red-400 hover:bg-ng-dark-2 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12 max-w-2xl">

        {/* Profile Card */}
        <div className="card p-8 mb-6">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-ng-text">My Profile</h1>
            {!isEditing && (
              <button onClick={() => setIsEditing(true)} className="btn btn-primary text-sm px-5 py-2.5">
                Edit Profile
              </button>
            )}
          </div>

          {error && (
            <div className="mb-5 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-800 font-medium">{error}</div>
          )}
          {successMessage && (
            <div className="mb-5 p-4 bg-ng-light border border-ng-border rounded-xl text-sm text-ng-dark font-medium">{successMessage}</div>
          )}

          {isEditing ? (
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-ng-text-2 mb-1.5">Full Name</label>
                <input
                  type="text"
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                  className="input-field"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-ng-text-2 mb-1.5">Age</label>
                  <input
                    type="number"
                    value={editForm.age}
                    onChange={(e) => setEditForm({ ...editForm, age: e.target.value })}
                    min="18" max="120"
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-ng-text-2 mb-1.5">Sex</label>
                  <select
                    value={editForm.sex}
                    onChange={(e) => setEditForm({ ...editForm, sex: e.target.value })}
                    className="input-field"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-3 pt-2">
                <button onClick={handleSave} disabled={saving} className="btn btn-primary flex items-center gap-2">
                  <Save className="w-4 h-4" />
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  onClick={handleCancel}
                  disabled={saving}
                  className="px-5 py-2.5 border border-ng-border rounded-lg text-ng-text-2 font-semibold hover:bg-ng-light transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-5">
              {[
                { Icon: User,     label: 'Name',  value: profile.name },
                { Icon: Mail,     label: 'Email', value: profile.email, badge: profile.email_verified ? 'Verified' : null },
                { Icon: Calendar, label: 'Age',   value: `${profile.age} years old` },
                { Icon: Users,    label: 'Sex',   value: profile.sex, capitalize: true },
              ].map(({ Icon, label, value, badge, capitalize }) => (
                <div key={label} className="flex items-start gap-4 p-4 bg-white rounded-xl border border-ng-border">
                  <div className="w-9 h-9 rounded-lg bg-ng-lime flex items-center justify-center flex-shrink-0">
                    <Icon className="w-4 h-4 text-ng-dark" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-ng-muted uppercase tracking-wide">{label}</p>
                    <p className={`text-base font-semibold text-ng-text mt-0.5 ${capitalize ? 'capitalize' : ''}`}>{value}</p>
                    {badge && (
                      <span className="inline-block mt-1 px-2 py-0.5 bg-ng-light border border-ng-border text-ng-dark text-xs font-semibold rounded-full">
                        {badge}
                      </span>
                    )}
                  </div>
                </div>
              ))}
              <div className="pt-4 border-t border-ng-border">
                <p className="text-xs font-semibold text-ng-muted uppercase tracking-wide">Member since</p>
                <p className="text-sm text-ng-text-2 font-medium mt-1">
                  {new Date(profile.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Analysis Reports */}
        <div className="card p-8">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold text-ng-text">My Analysis Reports</h2>
            <button onClick={() => router.push('/app')} className="btn btn-primary text-sm px-5 py-2.5">
              New Analysis
            </button>
          </div>

          {reportsLoading ? (
            <div className="text-center py-10">
              <div className="w-8 h-8 border-4 border-ng-border border-t-ng-lime rounded-full animate-spin mx-auto" />
              <p className="mt-3 text-ng-muted font-medium">Loading reports...</p>
            </div>
          ) : reports.length === 0 ? (
            <div className="text-center py-14 border-2 border-dashed border-ng-border rounded-xl bg-white">
              <FileText className="w-12 h-12 text-ng-border mx-auto mb-3" />
              <p className="text-ng-text-2 font-semibold mb-1">No analysis reports yet</p>
              <p className="text-sm text-ng-muted mb-5">Upload your genetic data to get started</p>
              <button onClick={() => router.push('/app')} className="btn btn-primary">
                Create Your First Report
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {reports.map((report) => (
                <div
                  key={report.session_id}
                  className="bg-white border border-ng-border rounded-xl p-5 hover:border-ng-lime hover:shadow-sm transition-all cursor-pointer"
                  onClick={() => handleViewReport(report)}
                >
                  <div className="flex items-start justify-between gap-3 min-w-0">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2 min-w-0">
                        <FileText className="w-5 h-5 text-ng-dark flex-shrink-0" />
                        <h3 className="font-semibold text-ng-text truncate" title={report.original_filename}>
                          {report.original_filename}
                        </h3>
                        {report.is_complete
                          ? <CheckCircle className="w-4 h-4 text-ng-lime" />
                          : <Clock className="w-4 h-4 text-orange-400" />
                        }
                      </div>

                      <div className="flex flex-wrap gap-2 mb-2">
                        <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                          report.is_complete
                            ? 'bg-ng-light text-ng-dark border border-ng-border'
                            : 'bg-orange-50 text-orange-700 border border-orange-200'
                        }`}>
                          {report.status === 'complete'                  ? 'Complete' :
                           report.status === 'questionnaire_completed'   ? 'Questionnaire Done' :
                           report.status === 'analyzed'                  ? 'Analyzed' : 'Uploaded'}
                        </span>
                        {report.has_genetic_results && (
                          <span className="text-xs px-2 py-1 bg-ng-light text-ng-dark border border-ng-border rounded-full font-semibold">
                            Genetic Results
                          </span>
                        )}
                        {report.has_recommendations && (
                          <span className="text-xs px-2 py-1 bg-ng-dark text-white rounded-full font-semibold">
                            Recommendations
                          </span>
                        )}
                      </div>

                      <p className="text-sm text-ng-muted font-medium">
                        {new Date(report.created_at).toLocaleDateString('en-US', {
                          year: 'numeric', month: 'short', day: 'numeric',
                          hour: '2-digit', minute: '2-digit',
                        })}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 ml-3 flex-shrink-0">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleViewReport(report); }}
                        className="px-4 py-2 text-sm font-semibold text-ng-dark hover:text-ng-dark-2 hover:bg-ng-light rounded-lg transition-colors border border-ng-border"
                      >
                        View
                      </button>
                      {confirmDeleteId === report.session_id ? (
                        <>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleDeleteReport(report.session_id); }}
                            disabled={deletingId === report.session_id}
                            className="px-3 py-2 text-sm font-semibold text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors disabled:opacity-50"
                          >
                            {deletingId === report.session_id ? 'Deleting...' : 'Confirm'}
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); setConfirmDeleteId(null); }}
                            className="px-3 py-2 text-sm font-semibold text-ng-text-2 hover:bg-ng-light rounded-lg transition-colors border border-ng-border"
                          >
                            Cancel
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={(e) => { e.stopPropagation(); setConfirmDeleteId(report.session_id); }}
                          className="p-2 text-ng-muted hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors border border-ng-border"
                          title="Delete report"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

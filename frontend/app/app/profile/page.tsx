'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { User, Mail, Calendar, Users, ArrowLeft, Save, FileText, CheckCircle, Clock } from 'lucide-react';

export default function ProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [reports, setReports] = useState<any[]>([]);
  const [reportsLoading, setReportsLoading] = useState(false);

  const [profile, setProfile] = useState({
    user_id: '',
    email: '',
    name: '',
    age: 0,
    sex: 'other',
    email_verified: false,
    created_at: ''
  });

  const [editForm, setEditForm] = useState({
    name: '',
    age: '',
    sex: 'other'
  });

  useEffect(() => {
    loadProfile();
    loadReports();
  }, []);

  const loadProfile = async () => {
    const token = localStorage.getItem('auth_token');

    if (!token) {
      router.push('/landing');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to load profile');
      }

      setProfile(data.user);
      setEditForm({
        name: data.user.name,
        age: data.user.age.toString(),
        sex: data.user.sex
      });
    } catch (err: any) {
      setError(err.message || 'Failed to load profile');
      if (err.message.includes('Authentication')) {
        localStorage.clear();
        router.push('/landing');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccessMessage('');

    const token = localStorage.getItem('auth_token');

    try {
      const response = await fetch('http://localhost:5000/api/auth/update-profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: editForm.name,
          age: parseInt(editForm.age),
          sex: editForm.sex
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to update profile');
      }

      setProfile(data.user);
      setSuccessMessage('Profile updated successfully!');
      setIsEditing(false);
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditForm({
      name: profile.name,
      age: profile.age.toString(),
      sex: profile.sex
    });
    setIsEditing(false);
    setError('');
    setSuccessMessage('');
  };

  const loadReports = async () => {
    setReportsLoading(true);
    const token = localStorage.getItem('auth_token');

    if (!token) return;

    try {
      const response = await fetch('http://localhost:5000/api/auth/my-reports', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        setReports(data.reports || []);
      }
    } catch (err) {
      console.error('Failed to load reports:', err);
    } finally {
      setReportsLoading(false);
    }
  };

  const handleViewReport = (sessionId: string) => {
    // Store session_id and navigate to analysis page
    localStorage.setItem('session_id', sessionId);
    router.push('/app');
  };

  const handleLogout = () => {
    localStorage.clear();
    router.push('/landing');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="container mx-auto px-4 py-4 max-w-7xl">
          <div className="flex justify-between items-center">
            <button
              onClick={() => router.push('/app')}
              className="flex items-center gap-2 text-slate-600 hover:text-slate-900"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Analysis</span>
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Profile Content */}
      <div className="container mx-auto px-4 py-12 max-w-2xl">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-slate-900">My Profile</h1>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="btn btn-primary"
              >
                Edit Profile
              </button>
            )}
          </div>

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

          {isEditing ? (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Age
                  </label>
                  <input
                    type="number"
                    value={editForm.age}
                    onChange={(e) => setEditForm({ ...editForm, age: e.target.value })}
                    min="18"
                    max="120"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Sex
                  </label>
                  <select
                    value={editForm.sex}
                    onChange={(e) => setEditForm({ ...editForm, sex: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="btn btn-primary flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  onClick={handleCancel}
                  disabled={saving}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-start gap-3">
                <User className="w-5 h-5 text-slate-400 mt-1" />
                <div>
                  <p className="text-sm text-slate-500">Name</p>
                  <p className="text-lg font-medium text-slate-900">{profile.name}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-slate-400 mt-1" />
                <div>
                  <p className="text-sm text-slate-500">Email</p>
                  <p className="text-lg font-medium text-slate-900">{profile.email}</p>
                  {profile.email_verified && (
                    <span className="inline-block mt-1 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                      Verified
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-slate-400 mt-1" />
                <div>
                  <p className="text-sm text-slate-500">Age</p>
                  <p className="text-lg font-medium text-slate-900">{profile.age} years old</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Users className="w-5 h-5 text-slate-400 mt-1" />
                <div>
                  <p className="text-sm text-slate-500">Sex</p>
                  <p className="text-lg font-medium text-slate-900 capitalize">{profile.sex}</p>
                </div>
              </div>

              <div className="pt-6 border-t border-slate-200">
                <p className="text-sm text-slate-500">Member since</p>
                <p className="text-sm text-slate-700">
                  {new Date(profile.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Analysis Reports Section */}
        <div className="bg-white rounded-lg shadow-lg p-8 mt-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-slate-900">My Analysis Reports</h2>
            <button
              onClick={() => router.push('/app')}
              className="btn btn-primary text-sm"
            >
              New Analysis
            </button>
          </div>

          {reportsLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-slate-600">Loading reports...</p>
            </div>
          ) : reports.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-lg">
              <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <p className="text-slate-600 mb-2">No analysis reports yet</p>
              <p className="text-sm text-slate-500 mb-4">Upload your genetic data to get started</p>
              <button
                onClick={() => router.push('/app')}
                className="btn btn-primary"
              >
                Create Your First Report
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {reports.map((report) => (
                <div
                  key={report.session_id}
                  className="border border-slate-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
                  onClick={() => handleViewReport(report.session_id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="w-5 h-5 text-blue-600" />
                        <h3 className="font-semibold text-slate-900">{report.original_filename}</h3>
                        {report.is_complete && (
                          <CheckCircle className="w-5 h-5 text-green-500" />
                        )}
                        {!report.is_complete && (
                          <Clock className="w-5 h-5 text-orange-500" />
                        )}
                      </div>

                      <div className="flex flex-wrap gap-2 mb-2">
                        <span className={`text-xs px-2 py-1 rounded ${
                          report.is_complete
                            ? 'bg-green-100 text-green-800'
                            : 'bg-orange-100 text-orange-800'
                        }`}>
                          {report.status === 'complete' ? 'Complete' :
                           report.status === 'questionnaire_completed' ? 'Questionnaire Done' :
                           report.status === 'analyzed' ? 'Analyzed' : 'Uploaded'}
                        </span>

                        {report.has_genetic_results && (
                          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                            Genetic Results
                          </span>
                        )}
                        {report.has_recommendations && (
                          <span className="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded">
                            Recommendations
                          </span>
                        )}
                      </div>

                      <p className="text-sm text-slate-500">
                        Created {new Date(report.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewReport(report.session_id);
                      }}
                      className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                      View Report
                    </button>
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

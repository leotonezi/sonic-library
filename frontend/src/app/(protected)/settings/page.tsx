'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { User, Camera, Save, X, CheckCircle, AlertCircle } from 'lucide-react';
import Image from 'next/image';

interface UserProfile {
  id: number;
  name: string;
  email: string;
  profile_picture?: string;
}

export default function SettingsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [name, setName] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchProfile = useCallback(async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/users/me`, {
        credentials: 'include',
      });

      if (!response.ok) {
        router.push('/login');
        return;
      }

      const { data } = await response.json();
      setProfile(data);
      setName(data.name);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching profile:', error);
      router.push('/login');
    }
  }, [router]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  useEffect(() => {
    // Show success/error messages from URL params
    const success = searchParams.get('success');
    const error = searchParams.get('error');
    
    if (success === 'true') {
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } else if (success === 'picture_uploaded') {
      setMessage({ type: 'success', text: 'Profile picture uploaded successfully!' });
    } else if (error === 'update_failed') {
      setMessage({ type: 'error', text: 'Failed to update profile. Please try again.' });
    } else if (error === 'upload_failed') {
      setMessage({ type: 'error', text: 'Failed to upload profile picture. Please try again.' });
    }
  }, [searchParams]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleUploadProfilePicture = async () => {
    if (!selectedFile) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/users/me/profile-picture`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to upload profile picture');
      }

      const { data } = await response.json();
      setProfile(data);
      setSelectedFile(null);
      setPreviewUrl(null);
      setMessage({ type: 'success', text: 'Profile picture uploaded successfully!' });
      
      // Refresh the profile data
      await fetchProfile();
    } catch (error) {
      console.error('Error uploading profile picture:', error);
      setMessage({ type: 'error', text: 'Failed to upload profile picture. Please try again.' });
    } finally {
      setUploading(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/users/me/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name }),
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to update profile');
      }

      const { data } = await response.json();
      setProfile(data);
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } catch (error) {
      console.error('Error updating profile:', error);
      setMessage({ type: 'error', text: 'Failed to update profile. Please try again.' });
    } finally {
      setSaving(false);
    }
  };

  const getProfilePictureUrl = (filename?: string) => {
    if (!filename) return undefined;
    return `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/profile_pictures/${filename}`;
  };

  if (loading) {
    return (
      <main className="p-6 bg-blue-950 text-blue-50 min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </main>
    );
  }

  return (
    <main className="p-6 bg-blue-950 text-blue-50 min-h-screen">
      <div className="max-w-2xl mx-auto">
        {/* Message Display */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-2 ${
            message.type === 'success' 
              ? 'bg-green-900 border border-green-600 text-green-200' 
              : 'bg-red-900 border border-red-600 text-red-200'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle size={20} className="text-green-400" />
            ) : (
              <AlertCircle size={20} className="text-red-400" />
            )}
            <span>{message.text}</span>
            <button
              onClick={() => setMessage(null)}
              className="ml-auto text-blue-300 hover:text-blue-100"
            >
              <X size={16} />
            </button>
          </div>
        )}

        <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md mb-6">
          <h1 className="text-3xl font-bold text-blue-500 mb-6 flex items-center gap-2">
            <User size={32} />
            User Settings
          </h1>

          {/* Profile Picture Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-blue-400 mb-4">Profile Picture</h2>
            <div className="flex items-center gap-6">
              <div className="relative">
                {profile?.profile_picture ? (
                  <Image
                    src={getProfilePictureUrl(profile.profile_picture) || ''}
                    alt="Profile"
                    width={96}
                    height={96}
                    className="w-24 h-24 rounded-full object-cover border-2 border-blue-500"
                  />
                ) : (
                  <div className="w-24 h-24 bg-blue-800 border-2 border-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-3xl text-blue-200">
                      {profile?.name?.charAt(0).toUpperCase() || 'U'}
                    </span>
                  </div>
                )}
                
                {previewUrl && (
                  <div className="absolute inset-0 rounded-full overflow-hidden">
                    <Image
                      src={previewUrl}
                      alt="Preview"
                      width={96}
                      height={96}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
              </div>

              <div className="flex-1">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="profile-picture-input"
                />
                <label
                  htmlFor="profile-picture-input"
                  className="inline-flex items-center gap-2 bg-blue-700 hover:bg-blue-600 text-blue-100 px-4 py-2 rounded cursor-pointer transition-colors"
                >
                  <Camera size={16} />
                  Choose Image
                </label>
                
                {selectedFile && (
                  <div className="mt-2 flex gap-2">
                    <button
                      onClick={handleUploadProfilePicture}
                      disabled={uploading}
                      className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded text-sm transition-colors disabled:opacity-50"
                    >
                      <Save size={14} />
                      {uploading ? 'Uploading...' : 'Upload'}
                    </button>
                    <button
                      onClick={() => {
                        setSelectedFile(null);
                        setPreviewUrl(null);
                      }}
                      className="inline-flex items-center gap-2 bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-sm transition-colors"
                    >
                      <X size={14} />
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Profile Information Section */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-blue-400 mb-4">Profile Information</h2>
            <form onSubmit={handleUpdateProfile}>
              <div className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-blue-200 mb-2">
                    Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full bg-blue-800 border border-blue-600 rounded px-3 py-2 text-blue-100 focus:outline-none focus:border-blue-400"
                  />
                </div>
                
                <div>
                  <label className="block text-blue-200 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={profile?.email || ''}
                    disabled
                    className="w-full bg-blue-700 border border-blue-600 rounded px-3 py-2 text-blue-300 cursor-not-allowed"
                  />
                  <p className="text-sm text-blue-300 mt-1">Email cannot be changed</p>
                </div>
              </div>

              {/* Save Button */}
              <div className="flex justify-end mt-6">
                <button
                  type="submit"
                  disabled={saving}
                  className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded transition-colors disabled:opacity-50"
                >
                  <Save size={16} />
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </main>
  );
} 
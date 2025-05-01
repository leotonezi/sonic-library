'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import { apiFetch } from '@/utils/api';
import User from '@/types/user';
import { Mail, User as UserIcon } from 'lucide-react';

export default function ProfilePage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const [profile, setProfile] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      logout();
      router.push('/login');
    }
  }, [user, logout, router]);

  useEffect(() => {
    async function loadProfile() {
      if (!user?.id) return;
      
      try {
        const data = await apiFetch<User>(`/users/me`);
        setProfile(data);
      } catch (err) {
        console.error('Failed to load profile:', err);
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, [user?.id]);

  if (loading) {
    return (
      <main className="p-6 bg-blue-950 text-blue-50 min-h-screen">
        <p className="text-blue-200">Loading profile...</p>
      </main>
    );
  }

  if (!profile) {
    return (
      <main className="p-6 bg-blue-950 text-blue-50 min-h-screen">
        <p className="text-red-400">Profile not found.</p>
      </main>
    );
  }

  return (
    <main className="p-6 bg-blue-950 text-blue-50 min-h-screen flex flex-col items-center">
      <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
        <div className="flex items-center gap-6 mb-6">
          <div className="w-24 h-24 bg-blue-800 border-2 border-blue-500 rounded-full flex items-center justify-center">
            <span className="text-4xl text-blue-200">
              {profile.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="flex items-center text-blue-200">
            <UserIcon size={32} className="mr-2" />
            <h1 className="text-3xl font-bold text-blue-500">{profile.name}</h1>
          </div>
        </div>
        <div className="space-y-4">
          <div className="bg-blue-800 p-4 rounded-lg">
            <div className="flex items-center text-blue-200 mb-2">
              <Mail size={16} />
              <p className="text-blue-100 pl-2">{profile.email}</p>
            </div>
          </div>
        </div>
      </div>
      <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full">
        <h2 className="text-2xl font-semibold text-blue-500 mb-4">Activity</h2>
        <p className="text-blue-200 italic">
          Reading history and reviews will appear here soon.
        </p>
      </div>
    </main>
  );
}
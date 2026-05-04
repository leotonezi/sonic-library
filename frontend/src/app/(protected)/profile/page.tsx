// app/profile/page.tsx
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { Mail, User as UserIcon, Settings } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import User from '@/interfaces/user';

export default async function ProfilePage() {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  if (!accessToken) {
    redirect('/login');
  }

  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/users/me`, {
    headers: {
      Cookie: `access_token=${accessToken}`,
    },
    cache: 'no-store',
  });

  if (!res.ok) {
    redirect('/login');
  }

  const { data: profile }: { data: User } = await res.json();

  const getProfilePictureUrl = (filename?: string) => {
    if (!filename) return '';
    return `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/profile_pictures/${filename}`;
  };

  return (
    <div className="p-6 bg-blue-950 text-blue-50 min-h-screen flex flex-col items-center">
      <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-6">
            {profile.profile_picture ? (
              <Image
                src={getProfilePictureUrl(profile.profile_picture)}
                alt="Profile"
                width={96}
                height={96}
                className="w-24 h-24 rounded-full object-cover border-2 border-blue-500"
              />
            ) : (
              <div className="w-24 h-24 bg-blue-800 border-2 border-blue-500 rounded-full flex items-center justify-center">
                <span className="text-4xl text-blue-200">
                  {profile.name.charAt(0).toUpperCase()}
                </span>
              </div>
            )}
            <div className="flex items-center text-blue-200">
              <UserIcon size={32} className="mr-2" />
              <h1 className="text-3xl font-bold text-blue-500">{profile.name}</h1>
            </div>
          </div>
          <Link
            href="/settings"
            className="inline-flex items-center gap-2 bg-blue-700 hover:bg-blue-600 text-blue-100 px-4 py-2 rounded transition-colors"
          >
            <Settings size={16} />
            Settings
          </Link>
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
    </div>
  );
}
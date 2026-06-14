import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

function isJwtExpired(token: string): boolean {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return false;

    // Base64url → base64 → decode
    const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const padded = payload + '='.repeat((4 - payload.length % 4) % 4);
    const decoded = JSON.parse(atob(padded)) as { exp?: number };

    if (typeof decoded.exp !== 'number') return false;
    return decoded.exp < Date.now() / 1000;
  } catch {
    // If decoding fails, let the backend decide
    return false;
  }
}

export function middleware(request: NextRequest) {
  const tokenCookie = request.cookies.get('access_token');
  if (!tokenCookie) return NextResponse.redirect(new URL('/login', request.url));

  if (isJwtExpired(tokenCookie.value)) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/(library|books|profile|settings|admin|recommendation)(.*)'],
};

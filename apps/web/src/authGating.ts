export function canOpenEngine(engineName: string, isAuthenticated: boolean): boolean {
  if (!isAuthenticated) return false;
  return engineName === 'Landslide' || engineName === 'Glacier Collapse' || engineName === 'Farming Activities' || engineName === 'Flood';
}

export function isLandslideRouteAllowed(isAuthenticated: boolean): boolean {
  return isAuthenticated;
}

export type ApiConnectionStatus = 'idle' | 'checking' | 'ready' | 'error';

export function apiConnectionNotice(
  status: ApiConnectionStatus,
  error: string | null,
): string | null {
  if (status === 'idle') return null;
  if (status === 'checking') {
    return 'Google sign-in is active. Verifying Firebase ID token and the Monorepo Supabase job store…';
  }
  if (status === 'ready') {
    return 'Backend connection verified: Firebase ID token accepted and the Monorepo Supabase job store responded. No science workflow was started.';
  }
  return `Google sign-in succeeded, but the authenticated API/Supabase check failed: ${error || 'Unknown backend error.'} The session remains signed in; processing must remain disabled until this is resolved.`;
}

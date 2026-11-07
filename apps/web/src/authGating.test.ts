import { describe, expect, it } from 'vitest';
import { apiConnectionNotice, canOpenEngine, isLandslideRouteAllowed } from './authGating';

describe('engine authentication gating', () => {
  it('blocks all engines until a user is authenticated', () => {
    expect(canOpenEngine('Landslide', false)).toBe(false);
    expect(canOpenEngine('Glacier Collapse', false)).toBe(false);
    expect(canOpenEngine('Farming Activities', false)).toBe(false);
    expect(canOpenEngine('Flood', false)).toBe(false);
  });

  it('allows Landslide only after authentication', () => {
    expect(isLandslideRouteAllowed(false)).toBe(false);
    expect(isLandslideRouteAllowed(true)).toBe(true);
  });
});

describe('authenticated API readiness notice', () => {
  it('does not show a notice before sign-in', () => {
    expect(apiConnectionNotice('idle', null)).toBeNull();
  });

  it('explains the safe Firebase and Supabase read check while pending', () => {
    expect(apiConnectionNotice('checking', null)).toContain('Firebase ID token');
    expect(apiConnectionNotice('checking', null)).toContain('Supabase job store');
  });

  it('reports success without implying a science workflow ran', () => {
    const notice = apiConnectionNotice('ready', null);
    expect(notice).toContain('Backend connection verified');
    expect(notice).toContain('No science workflow was started');
  });

  it('shows a recoverable API failure and keeps processing disabled', () => {
    const notice = apiConnectionNotice('error', 'Firebase Admin is not configured');
    expect(notice).toContain('Firebase Admin is not configured');
    expect(notice).toContain('processing must remain disabled');
  });
});

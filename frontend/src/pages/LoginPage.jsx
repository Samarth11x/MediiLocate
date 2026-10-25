/**
 * Login page for MediLocate AI.
 * Light theme, accessible form inputs, error handling,
 * and quick-fill buttons for demonstration credentials.
 */

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter, Link } from '../context/RouterContext';

export default function LoginPage() {
  const { login } = useAuth();
  const { navigate } = useRouter();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const isDev = Boolean(
    import.meta.env.DEV ||
    import.meta.env.MODE === 'development' ||
    import.meta.env.MODE === 'test'
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!username.trim() || !password) {
      setError('Please enter both your username and password.');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await login(username.trim(), password);
      const role = res?.user?.role;
      if (role === 'ADMIN' || res?.user?.is_admin) {
        navigate('/admin/dashboard');
      } else if (role === 'PHARMACIST') {
        navigate('/pharmacist/dashboard');
      } else {
        navigate('/app');
      }
    } catch (err) {
      setError(err.message || 'Invalid credentials. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickFill = (u, p) => {
    setUsername(u);
    setPassword(p);
    setError(null);
  };

  return (
    <div
      className="login-page-wrapper responsive-page-container"
      style={{
        position: 'relative',
        minHeight: 'calc(100vh - 140px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'clamp(20px, 4vw, 40px) 16px clamp(40px, 6vw, 80px)',
        overflow: 'hidden',
      }}
    >
      {/* Background Video Layer */}
      <div className="hero-video-wrapper" aria-hidden="true" style={{ position: 'absolute', inset: 0 }}>
        <video
          className="hero-video"
          autoPlay
          muted
          loop
          playsInline
          aria-hidden="true"
        >
          <source src="/videos/medilocate-hero.mp4" type="video/mp4" />
        </video>
        <div className="hero-video-overlay hero-video-overlay--primary" />
        <div className="hero-video-overlay hero-video-overlay--mint" />
        <div className="hero-video-overlay hero-video-overlay--edge" />
      </div>

      <div className="responsive-card" style={{
        position: 'relative',
        zIndex: 10,
        maxWidth: '480px',
        width: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.96)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderRadius: '16px',
        padding: 'clamp(24px, 4vw, 36px) clamp(20px, 4vw, 32px)',
        boxShadow: '0 8px 32px rgba(18, 48, 71, 0.12)',
        border: '1px solid #E2E8F0',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: 'var(--color-mint-100, #D1FAE5)',
            color: 'var(--color-teal-700, #0F766E)',
            marginBottom: '12px'
          }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', margin: 0 }}>
            Sign In to MediLocate
          </h1>
          <p style={{ color: '#64748B', fontSize: '0.9rem', marginTop: '6px' }}>
            Access your patient, pharmacist, or administrator portal
          </p>
        </div>

        {error && (
          <div role="alert" style={{
            backgroundColor: '#FEF2F2',
            border: '1px solid #FCA5A5',
            color: '#B91C1C',
            padding: '12px 14px',
            borderRadius: '8px',
            fontSize: '0.88rem',
            marginBottom: '20px',
            display: 'flex',
            gap: '8px',
            alignItems: 'center'
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div style={{ marginBottom: '18px' }}>
            <label htmlFor="login-username" style={{
              display: 'block',
              fontSize: '0.88rem',
              fontWeight: 600,
              color: 'var(--color-navy-700, #123047)',
              marginBottom: '6px'
            }}>
              Username
            </label>
            <input
              id="login-username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. patient_demo"
              required
              style={{
                width: '100%',
                padding: '11px 14px',
                borderRadius: '8px',
                border: '1px solid #CBD5E1',
                fontSize: '16px',
                color: 'var(--color-navy-900, #0B1926)',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label htmlFor="login-password" style={{
              display: 'block',
              fontSize: '0.88rem',
              fontWeight: 600,
              color: 'var(--color-navy-700, #123047)',
              marginBottom: '6px'
            }}>
              Password
            </label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
              style={{
                width: '100%',
                padding: '11px 14px',
                borderRadius: '8px',
                border: '1px solid #CBD5E1',
                fontSize: '16px',
                color: 'var(--color-navy-900, #0B1926)',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              minHeight: '44px',
              padding: '12px',
              backgroundColor: 'var(--color-teal-600, #0F766E)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '8px',
              fontSize: '0.95rem',
              fontWeight: 600,
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              opacity: isSubmitting ? 0.7 : 1,
              transition: 'background-color 0.15s ease'
            }}
          >
            {isSubmitting ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        {/* Demo Credentials Quick-Fill Box (Only visible in Development/Test environments) */}
        {isDev && (
          <div style={{
            marginTop: '28px',
            padding: '16px',
            backgroundColor: '#F8FAFC',
            borderRadius: '10px',
            border: '1px solid #E2E8F0',
            fontSize: '0.85rem'
          }}>
            <p style={{ fontWeight: 600, color: 'var(--color-navy-700, #123047)', margin: '0 0 10px 0' }}>
              Quick Demo Accounts (Local Dev):
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              <button
                type="button"
                onClick={() => handleQuickFill('patient_demo', 'PatientPass123!')}
                style={{
                  padding: '6px 10px',
                  fontSize: '0.78rem',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  backgroundColor: '#FFFFFF',
                  color: 'var(--color-navy-800, #123047)',
                  cursor: 'pointer',
                  fontWeight: 500
                }}
              >
                Patient
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill('patient_demo_01', 'PatientPass123!')}
                style={{
                  padding: '6px 10px',
                  fontSize: '0.78rem',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  backgroundColor: '#F8FAFC',
                  color: 'var(--color-navy-800, #123047)',
                  cursor: 'pointer',
                  fontWeight: 500
                }}
              >
                Patient 01
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill('pharmacist_demo_01', 'PharmaPass123!')}
                style={{
                  padding: '6px 10px',
                  fontSize: '0.78rem',
                  borderRadius: '6px',
                  border: '1px solid #99F6E4',
                  backgroundColor: '#F0FDFA',
                  color: 'var(--color-teal-800, #115E59)',
                  cursor: 'pointer',
                  fontWeight: 500
                }}
              >
                Verified Pharmacist
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill('pharmacist_demo_pending', 'PharmaPass123!')}
                style={{
                  padding: '6px 10px',
                  fontSize: '0.78rem',
                  borderRadius: '6px',
                  border: '1px solid #FED7AA',
                  backgroundColor: '#FFF7ED',
                  color: '#9A3412',
                  cursor: 'pointer',
                  fontWeight: 500
                }}
              >
                Pending Pharmacist
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill('pharmacist_demo_rejected', 'PharmaPass123!')}
                style={{
                  padding: '6px 10px',
                  fontSize: '0.78rem',
                  borderRadius: '6px',
                  border: '1px solid #FECACA',
                  backgroundColor: '#FEF2F2',
                  color: '#991B1B',
                  cursor: 'pointer',
                  fontWeight: 500
                }}
              >
                Rejected Pharmacist
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill('admin_demo', 'AdminDemoPass123!')}
                style={{
                  padding: '6px 10px',
                  fontSize: '0.78rem',
                  borderRadius: '6px',
                  border: '1px solid #DDD6FE',
                  backgroundColor: '#F5F3FF',
                  color: '#5B21B6',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
              >
                Admin Demo
              </button>
            </div>
          </div>
        )}

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '0.88rem', color: '#64748B' }}>
          <span>Don't have an account? </span>
          <Link to="/register" style={{ color: 'var(--color-teal-600, #0F766E)', fontWeight: 600, textDecoration: 'none' }}>
            Register as Patient
          </Link>
          <span style={{ margin: '0 8px' }}>•</span>
          <Link to="/pharmacist/register" style={{ color: 'var(--color-teal-600, #0F766E)', fontWeight: 600, textDecoration: 'none' }}>
            For Pharmacists
          </Link>
        </div>
      </div>
    </div>
  );
}

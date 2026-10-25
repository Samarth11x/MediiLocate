/**
 * Role-aware ProtectedRoute component for MediLocate AI.
 * Guards client-side routes for Patient, Pharmacist, and Admin portals.
 * Gracefully handles loading, unauthenticated, and unauthorized role states.
 */

import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { useRouter, Link } from '../../context/RouterContext';

export default function ProtectedRoute({ allowedRoles = [], children }) {
  const { user, role, isAuthenticated, isLoading } = useAuth();
  const { navigate } = useRouter();

  if (isLoading) {
    return (
      <div className="portal-loading-container" style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        gap: '16px',
        color: 'var(--color-navy-700, #123047)'
      }}>
        <div className="spinner" style={{
          width: '40px',
          height: '40px',
          border: '3px solid #E2E8F0',
          borderTop: '3px solid var(--color-teal-600, #0F766E)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <p style={{ fontWeight: 500, fontSize: '0.95rem' }}>Verifying authenticated session...</p>
      </div>
    );
  }

  // Not signed in
  if (!isAuthenticated) {
    return (
      <div className="unauthorized-card" style={{
        maxWidth: '520px',
        margin: '60px auto',
        padding: '36px 32px',
        background: '#FFFFFF',
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(18, 48, 71, 0.08)',
        border: '1px solid #E2E8F0',
        textAlign: 'center'
      }}>
        <div style={{
          width: '56px',
          height: '56px',
          background: 'var(--color-mint-50, #ECFDF5)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px',
          color: 'var(--color-teal-700, #0F766E)'
        }}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        </div>
        <h2 style={{ color: 'var(--color-navy-800, #123047)', fontSize: '1.4rem', fontWeight: 700, marginBottom: '8px' }}>
          Authentication Required
        </h2>
        <p style={{ color: '#64748B', fontSize: '0.95rem', lineHeight: 1.5, marginBottom: '24px' }}>
          You need to be signed in to access this portal. Please log in with your credentials or register for an account.
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button
            onClick={() => navigate('/login')}
            className="btn btn-primary"
            style={{
              padding: '10px 20px',
              backgroundColor: 'var(--color-teal-600, #0F766E)',
              color: '#FFFFFF',
              borderRadius: '8px',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer'
            }}
          >
            Log In
          </button>
          <button
            onClick={() => navigate('/register')}
            className="btn btn-secondary"
            style={{
              padding: '10px 20px',
              backgroundColor: '#F1F5F9',
              color: 'var(--color-navy-800, #123047)',
              borderRadius: '8px',
              fontWeight: 600,
              border: '1px solid #CBD5E1',
              cursor: 'pointer'
            }}
          >
            Create Account
          </button>
        </div>
      </div>
    );
  }

  // Signed in, but role not permitted
  if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
    return (
      <div className="unauthorized-card" style={{
        maxWidth: '520px',
        margin: '60px auto',
        padding: '36px 32px',
        background: '#FFFFFF',
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(18, 48, 71, 0.08)',
        border: '1px solid #FECDD3',
        textAlign: 'center'
      }}>
        <div style={{
          width: '56px',
          height: '56px',
          background: '#FFF1F2',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px',
          color: '#E11D48'
        }}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        </div>
        <h2 style={{ color: 'var(--color-navy-800, #123047)', fontSize: '1.4rem', fontWeight: 700, marginBottom: '8px' }}>
          Restricted Portal Access
        </h2>
        <p style={{ color: '#64748B', fontSize: '0.95rem', lineHeight: 1.5, marginBottom: '16px' }}>
          This portal requires <strong>{allowedRoles.join(' or ')}</strong> role permissions. You are currently signed in as <strong>{user.username}</strong> ({role}).
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button
            onClick={() => navigate('/')}
            style={{
              padding: '10px 18px',
              backgroundColor: '#F1F5F9',
              color: 'var(--color-navy-800, #123047)',
              borderRadius: '8px',
              fontWeight: 600,
              border: '1px solid #CBD5E1',
              cursor: 'pointer'
            }}
          >
            Go to Home
          </button>
          {role === 'PHARMACIST' && (
            <button
              onClick={() => navigate('/pharmacist/dashboard')}
              style={{
                padding: '10px 18px',
                backgroundColor: 'var(--color-teal-600, #0F766E)',
                color: '#FFFFFF',
                borderRadius: '8px',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer'
              }}
            >
              Pharmacist Dashboard
            </button>
          )}
          {role === 'ADMIN' && (
            <button
              onClick={() => navigate('/admin/dashboard')}
              style={{
                padding: '10px 18px',
                backgroundColor: 'var(--color-teal-600, #0F766E)',
                color: '#FFFFFF',
                borderRadius: '8px',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer'
              }}
            >
              Admin Dashboard
            </button>
          )}
          {role === 'USER' && (
            <button
              onClick={() => navigate('/app')}
              style={{
                padding: '10px 18px',
                backgroundColor: 'var(--color-teal-600, #0F766E)',
                color: '#FFFFFF',
                borderRadius: '8px',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer'
              }}
            >
              Patient Portal
            </button>
          )}
        </div>
      </div>
    );
  }

  return children;
}

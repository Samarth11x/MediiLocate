/**
 * 404 Not Found Page for MediLocate AI.
 */

import React from 'react';
import { useRouter, Link } from '../context/RouterContext';

export default function NotFoundPage() {
  const { navigate } = useRouter();

  return (
    <div style={{
      maxWidth: '500px',
      margin: '80px auto',
      padding: '40px 24px',
      textAlign: 'center',
      backgroundColor: '#FFFFFF',
      borderRadius: '16px',
      border: '1px solid #E2E8F0',
      boxShadow: '0 4px 20px rgba(18, 48, 71, 0.06)'
    }}>
      <div style={{
        fontSize: '3rem',
        fontWeight: 800,
        color: 'var(--color-teal-600, #0F766E)',
        marginBottom: '8px'
      }}>
        404
      </div>
      <h1 style={{
        fontSize: '1.4rem',
        fontWeight: 700,
        color: 'var(--color-navy-800, #123047)',
        margin: '0 0 10px 0'
      }}>
        Page Not Found
      </h1>
      <p style={{ color: '#64748B', fontSize: '0.95rem', lineHeight: 1.5, marginBottom: '24px' }}>
        The healthcare portal or route you are looking for does not exist or has moved.
      </p>
      <button
        onClick={() => navigate('/')}
        style={{
          padding: '10px 22px',
          backgroundColor: 'var(--color-teal-600, #0F766E)',
          color: '#FFFFFF',
          border: 'none',
          borderRadius: '8px',
          fontWeight: 600,
          fontSize: '0.92rem',
          cursor: 'pointer'
        }}
      >
        Return to Home
      </button>
    </div>
  );
}

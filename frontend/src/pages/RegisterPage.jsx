/**
 * Patient registration page for MediLocate AI.
 * Creates USER role accounts and redirects to Patient Portal (/app).
 */

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter, Link } from '../context/RouterContext';

export default function RegisterPage() {
  const { register } = useAuth();
  const { navigate } = useRouter();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone_number: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!formData.username.trim()) {
      setError('Username is required.');
      return;
    }
    if (!formData.password) {
      setError('Password is required.');
      return;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setIsSubmitting(true);
    try {
      await register({
        username: formData.username.trim(),
        email: formData.email.trim(),
        password: formData.password,
        phone_number: formData.phone_number.trim(),
        role: 'USER',
      });
      navigate('/app');
    } catch (err) {
      setError(err.message || 'Registration failed. Please verify your details.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="register-page-wrapper responsive-page-container"
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
        maxWidth: '500px',
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
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="8.5" cy="7" r="4" />
              <line x1="20" y1="8" x2="20" y2="14" />
              <line x1="23" y1="11" x2="17" y2="11" />
            </svg>
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', margin: 0 }}>
            Create Patient Account
          </h1>
          <p style={{ color: '#64748B', fontSize: '0.9rem', marginTop: '6px' }}>
            Find real-time medicines and access the MediBot assistant
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
          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="reg-username" style={{
              display: 'block',
              fontSize: '0.88rem',
              fontWeight: 600,
              color: 'var(--color-navy-700, #123047)',
              marginBottom: '6px'
            }}>
              Username *
            </label>
            <input
              id="reg-username"
              name="username"
              type="text"
              autoComplete="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="e.g. priyapatel"
              required
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: '8px',
                border: '1px solid #CBD5E1',
                fontSize: '16px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="reg-email" style={{
              display: 'block',
              fontSize: '0.88rem',
              fontWeight: 600,
              color: 'var(--color-navy-700, #123047)',
              marginBottom: '6px'
            }}>
              Email Address (Optional)
            </label>
            <input
              id="reg-email"
              name="email"
              type="email"
              autoComplete="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="name@example.com"
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: '8px',
                border: '1px solid #CBD5E1',
                fontSize: '16px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="reg-phone" style={{
              display: 'block',
              fontSize: '0.88rem',
              fontWeight: 600,
              color: 'var(--color-navy-700, #123047)',
              marginBottom: '6px'
            }}>
              Phone Number (Optional)
            </label>
            <input
              id="reg-phone"
              name="phone_number"
              type="tel"
              value={formData.phone_number}
              onChange={handleChange}
              placeholder="+91 98765 43210"
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: '8px',
                border: '1px solid #CBD5E1',
                fontSize: '16px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '22px' }}>
            <div>
              <label htmlFor="reg-password" style={{
                display: 'block',
                fontSize: '0.88rem',
                fontWeight: 600,
                color: 'var(--color-navy-700, #123047)',
                marginBottom: '6px'
              }}>
                Password *
              </label>
              <input
                id="reg-password"
                name="password"
                type="password"
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Min. 8 chars"
                required
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1px solid #CBD5E1',
                  fontSize: '16px',
                  outline: 'none',
                  boxSizing: 'border-box'
                }}
              />
            </div>
            <div>
              <label htmlFor="reg-confirm-password" style={{
                display: 'block',
                fontSize: '0.88rem',
                fontWeight: 600,
                color: 'var(--color-navy-700, #123047)',
                marginBottom: '6px'
              }}>
                Confirm *
              </label>
              <input
                id="reg-confirm-password"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Re-enter"
                required
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  border: '1px solid #CBD5E1',
                  fontSize: '16px',
                  outline: 'none',
                  boxSizing: 'border-box'
                }}
              />
            </div>
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
            }}
          >
            {isSubmitting ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '0.88rem', color: '#64748B' }}>
          <span>Already registered? </span>
          <Link to="/login" style={{ color: 'var(--color-teal-600, #0F766E)', fontWeight: 600, textDecoration: 'none' }}>
            Sign In
          </Link>
          <div style={{ marginTop: '12px' }}>
            <span>Are you a pharmacy owner? </span>
            <Link to="/pharmacist/register" style={{ color: 'var(--color-teal-600, #0F766E)', fontWeight: 600, textDecoration: 'none' }}>
              Onboard Your Pharmacy
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

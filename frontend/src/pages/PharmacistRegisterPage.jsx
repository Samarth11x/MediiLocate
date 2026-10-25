/**
 * Pharmacist registration and pharmacy onboarding page.
 * Creates PHARMACIST role account and sets establishment to PENDING status.
 */

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter, Link } from '../context/RouterContext';

export default function PharmacistRegisterPage() {
  const { register } = useAuth();
  const { navigate } = useRouter();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone_number: '',
    pharmacy_name: '',
    license_number: '',
    address: '',
    area: '',
    city: 'Bengaluru',
    pin_code: '',
    contact_number: '',
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
    if (!formData.pharmacy_name.trim()) {
      setError('Pharmacy name is required.');
      return;
    }
    if (!formData.license_number.trim()) {
      setError('Drug license number is required.');
      return;
    }
    if (!formData.password || formData.password.length < 8) {
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
        role: 'PHARMACIST',
        pharmacy_name: formData.pharmacy_name.trim(),
        license_number: formData.license_number.trim(),
        address: formData.address.trim(),
        area: formData.area.trim(),
        city: formData.city.trim(),
        pin_code: formData.pin_code.trim(),
        contact_number: formData.contact_number.trim() || formData.phone_number.trim(),
      });
      navigate('/pharmacist/dashboard');
    } catch (err) {
      setError(err.message || 'Onboarding failed. Please review your details.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="pharmacist-register-page-wrapper responsive-page-container"
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
        maxWidth: '640px',
        width: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.96)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderRadius: '16px',
        padding: 'clamp(24px, 4vw, 36px) clamp(20px, 4vw, 32px)',
        boxShadow: '0 8px 32px rgba(18, 48, 71, 0.12)',
        border: '1px solid #E2E8F0',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
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
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <line x1="9" y1="12" x2="15" y2="12" />
              <line x1="12" y1="9" x2="12" y2="15" />
            </svg>
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', margin: 0 }}>
            Pharmacy Partner Onboarding
          </h1>
          <p style={{ color: '#64748B', fontSize: '0.9rem', marginTop: '6px' }}>
            Register your licensed pharmacy on the MediLocate network
          </p>
        </div>

        {/* Informational Banner */}
        <div style={{
          backgroundColor: '#F0FDF4',
          border: '1px solid #BBF7D0',
          borderRadius: '8px',
          padding: '12px 14px',
          marginBottom: '20px',
          fontSize: '0.85rem',
          color: '#166534',
          lineHeight: 1.45,
          display: 'flex',
          gap: '10px'
        }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0, marginTop: '2px' }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
          <div>
            <strong>Verification Process:</strong> Upon submission, your pharmacy application enters administrative review. You can log in immediately to view application status and prepare your profile. Stock publishing unlocks once verified.
          </div>
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
          <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', marginBottom: '14px', borderBottom: '1px solid #E2E8F0', paddingBottom: '8px' }}>
            1. Account Credentials
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '14px' }}>
            <div>
              <label htmlFor="ph-username" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                Pharmacist Username *
              </label>
              <input
                id="ph-username"
                name="username"
                type="text"
                autoComplete="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="e.g. rajesh_pharma"
                required
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label htmlFor="ph-email" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                Contact Email *
              </label>
              <input
                id="ph-email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="rajesh@carepoint.in"
                required
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '20px' }}>
            <div>
              <label htmlFor="ph-password" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                Password (min 8 chars) *
              </label>
              <input
                id="ph-password"
                name="password"
                type="password"
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label htmlFor="ph-confirm" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                Confirm Password *
              </label>
              <input
                id="ph-confirm"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                required
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
              />
            </div>
          </div>

          <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', marginBottom: '14px', borderBottom: '1px solid #E2E8F0', paddingBottom: '8px' }}>
            2. Pharmacy Establishment Details
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '14px' }}>
            <div>
              <label htmlFor="ph-name" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                Trading Pharmacy Name *
              </label>
              <input
                id="ph-name"
                name="pharmacy_name"
                type="text"
                value={formData.pharmacy_name}
                onChange={handleChange}
                placeholder="e.g. Apollo Life Care"
                required
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label htmlFor="ph-license" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                Drug License Number *
              </label>
              <input
                id="ph-license"
                name="license_number"
                type="text"
                value={formData.license_number}
                onChange={handleChange}
                placeholder="e.g. DL-KA-2024-00129"
                required
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '14px' }}>
            <label htmlFor="ph-address" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
              Street Address *
            </label>
            <input
              id="ph-address"
              name="address"
              type="text"
              value={formData.address}
              onChange={handleChange}
              placeholder="Door No, Building, Main Road"
              required
              style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px', marginBottom: '14px' }}>
            <div>
              <label htmlFor="ph-area" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                Locality / Area *
              </label>
              <input
                id="ph-area"
                name="area"
                type="text"
                value={formData.area}
                onChange={handleChange}
                placeholder="e.g. Indiranagar"
                required
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label htmlFor="ph-city" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                City *
              </label>
              <input
                id="ph-city"
                name="city"
                type="text"
                value={formData.city}
                onChange={handleChange}
                placeholder="Bengaluru"
                required
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
              />
            </div>
            <div>
              <label htmlFor="ph-pin" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
                PIN Code *
              </label>
              <input
                id="ph-pin"
                name="pin_code"
                type="text"
                value={formData.pin_code}
                onChange={handleChange}
                placeholder="560038"
                required
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label htmlFor="ph-contact" style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>
              Pharmacy Contact Phone Number
            </label>
            <input
              id="ph-contact"
              name="contact_number"
              type="tel"
              value={formData.contact_number}
              onChange={handleChange}
              placeholder="+91 99999 00001"
              style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '16px', boxSizing: 'border-box' }}
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              minHeight: '44px',
              padding: '13px',
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
            {isSubmitting ? 'Submitting Application...' : 'Submit Pharmacy Application'}
          </button>
        </form>

        <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '0.88rem', color: '#64748B' }}>
          <span>Already have an account? </span>
          <Link to="/login" style={{ color: 'var(--color-teal-600, #0F766E)', fontWeight: 600, textDecoration: 'none' }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}

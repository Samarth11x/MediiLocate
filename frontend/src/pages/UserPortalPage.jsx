/**
 * Patient Portal Page (/app)
 * Comprehensive healthcare dashboard for registered patients.
 * Provides personalized medicine discovery, stock visibility, and MediBot assistant.
 */

import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRouter } from '../context/RouterContext';
import { searchMedicines } from '../services/medicineService';
import { useGeolocation } from '../hooks/useGeolocation';
import SearchResults from '../components/medicine/SearchResults';
import MediBotDrawer from '../components/medibot/MediBotDrawer';

export default function UserPortalPage() {
  const { user, logout } = useAuth();
  const { navigate } = useRouter();

  const [searchQuery, setSearchQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const [validationError, setValidationError] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [isMediBotOpen, setIsMediBotOpen] = useState(false);

  const {
    coords,
    loading: geoLoading,
    error: geoError,
    requestLocation,
    clearLocation,
  } = useGeolocation();

  const quickPicks = [
    'Paracetamol 500mg',
    'Amoxicillin 500mg',
    'Dolo 650mg',
    'Cetirizine 10mg',
    'Azithromycin 500mg',
    'Augmentin 625mg',
  ];

  const handleSearch = async (queryText) => {
    const raw = queryText !== undefined ? queryText : searchQuery;
    const query = (raw || '').trim();

    if (!query) {
      setValidationError('Please enter a medicine name, strength, or brand to search.');
      setSubmittedQuery('');
      setSearchResults(null);
      setSearchError(null);
      return;
    }

    setValidationError(null);
    setSubmittedQuery(query);
    setIsSearching(true);
    setSearchError(null);

    try {
      const options = coords ? { lat: coords.lat, lon: coords.lon } : {};
      const data = await searchMedicines(query, options);
      setSearchResults(data);
    } catch (err) {
      setSearchError(err.message || 'Unable to connect to search service.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleQuickPickClick = (med) => {
    setSearchQuery(med);
    handleSearch(med);
  };

  return (
    <div className="user-portal-page" style={{ maxWidth: '1100px', margin: '20px auto 80px', padding: '0 clamp(12px, 3.5vw, 20px)', boxSizing: 'border-box' }}>
      {/* Patient Welcome Header */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        padding: 'clamp(16px, 3vw, 28px) clamp(16px, 3.5vw, 32px)',
        border: '1px solid #E2E8F0',
        boxShadow: '0 2px 12px rgba(18, 48, 71, 0.05)',
        marginBottom: '24px',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        boxSizing: 'border-box'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
          <div style={{
            width: '50px',
            height: '50px',
            borderRadius: '50%',
            backgroundColor: 'var(--color-mint-100, #D1FAE5)',
            color: 'var(--color-teal-700, #0F766E)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.3rem',
            fontWeight: 700,
            flexShrink: 0
          }}>
            {(user?.username || 'P')[0].toUpperCase()}
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
              <h1 style={{ margin: 0, fontSize: 'clamp(1.15rem, 3.5vw, 1.4rem)', fontWeight: 700, color: 'var(--color-navy-800, #123047)' }}>
                Welcome back, {user?.first_name || user?.username || 'Patient'}
              </h1>
              <span style={{
                backgroundColor: 'var(--color-mint-50, #ECFDF5)',
                color: 'var(--color-teal-800, #0F766E)',
                border: '1px solid #A7F3D0',
                padding: '2px 8px',
                borderRadius: '999px',
                fontSize: '0.75rem',
                fontWeight: 600
              }}>
                Patient Portal
              </span>
            </div>
            <p style={{ margin: '4px 0 0 0', color: '#64748B', fontSize: '0.85rem' }}>
              {user?.email || 'Logged in to patient workspace'} • Real-time medicine locator active
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={() => setIsMediBotOpen(true)}
            style={{
              padding: '9px 16px',
              minHeight: '42px',
              backgroundColor: 'var(--color-teal-50, #F0FDFA)',
              color: 'var(--color-teal-700, #0F766E)',
              border: '1px solid #99F6E4',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.88rem',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            Ask MediBot
          </button>
          <button
            onClick={logout}
            style={{
              padding: '9px 14px',
              minHeight: '42px',
              backgroundColor: '#F8FAFC',
              color: '#475569',
              border: '1px solid #CBD5E1',
              borderRadius: '8px',
              fontWeight: 500,
              fontSize: '0.88rem',
              cursor: 'pointer'
            }}
          >
            Log Out
          </button>
        </div>
      </div>

      {/* Main Search Panel */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        padding: 'clamp(18px, 3.5vw, 30px)',
        border: '1px solid #E2E8F0',
        boxShadow: '0 4px 16px rgba(18, 48, 71, 0.06)',
        marginBottom: '24px',
        boxSizing: 'border-box'
      }}>
        <div style={{ marginBottom: '18px' }}>
          <h2 style={{ fontSize: 'clamp(1.1rem, 3vw, 1.25rem)', fontWeight: 700, color: 'var(--color-navy-800, #123047)', margin: '0 0 6px 0' }}>
            Find Medicine at Nearby Pharmacies
          </h2>
          <p style={{ color: '#64748B', fontSize: '0.88rem', margin: 0, lineHeight: 1.45 }}>
            Search by chemical name, active strength, or branded formulation with live stock status.
          </p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          style={{ display: 'flex', gap: '10px', marginBottom: '16px', flexWrap: 'wrap' }}
        >
          <div style={{ position: 'relative', flex: '1 1 240px', minWidth: '200px' }}>
            <input
              type="search"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                if (validationError) setValidationError(null);
              }}
              placeholder="Search medicine name, strength or brand..."
              style={{
                width: '100%',
                padding: '12px 16px 12px 44px',
                borderRadius: '10px',
                border: '1px solid #CBD5E1',
                fontSize: '1rem',
                outline: 'none',
                boxSizing: 'border-box',
                minHeight: '46px'
              }}
            />
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#64748B"
              strokeWidth="2"
              style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }}
            >
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </div>
          <button
            type="submit"
            disabled={isSearching}
            style={{
              padding: '12px 24px',
              minHeight: '46px',
              backgroundColor: 'var(--color-teal-600, #0F766E)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '10px',
              fontWeight: 600,
              fontSize: '0.95rem',
              cursor: isSearching ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap',
              flex: '0 0 auto'
            }}
          >
            {isSearching ? 'Searching...' : 'Search Medicine'}
          </button>
        </form>

        {/* Validation Error Banner */}
        {validationError && (
          <div
            role="alert"
            style={{
              backgroundColor: '#FEF2F2',
              border: '1px solid #FCA5A5',
              color: '#B91C1C',
              padding: '10px 14px',
              borderRadius: '8px',
              fontSize: '0.88rem',
              marginBottom: '16px'
            }}
          >
            {validationError}
          </div>
        )}

        {/* Location selector indicator */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px', marginBottom: '16px' }}>
          <div style={{ fontSize: '0.85rem', color: '#64748B', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
            {coords ? (
              <span>
                Location active: <strong>{coords.lat.toFixed(4)}, {coords.lon.toFixed(4)} (Proximity enabled)</strong>
                <button
                  onClick={clearLocation}
                  style={{ marginLeft: '8px', background: 'none', border: 'none', color: '#DC2626', cursor: 'pointer', fontSize: '0.8rem', textDecoration: 'underline' }}
                >
                  Clear Location
                </button>
              </span>
            ) : (
              <span>
                Location disabled (showing Bangalore demo network).
                <button
                  type="button"
                  className="location-btn location-btn--request"
                  aria-label="Enable location for proximity ranking"
                  onClick={requestLocation}
                  disabled={geoLoading}
                  style={{ marginLeft: '8px', background: 'none', border: 'none', color: 'var(--color-teal-600, #0F766E)', cursor: 'pointer', fontSize: '0.8rem', textDecoration: 'underline' }}
                >
                  {geoLoading ? 'Detecting...' : 'Use My Location'}
                </button>
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
            <span style={{ color: '#64748B', fontWeight: 500 }}>Quick search:</span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {quickPicks.map((pick) => (
                <button
                  key={pick}
                  type="button"
                  onClick={() => handleQuickPickClick(pick)}
                  style={{
                    padding: '4px 8px',
                    borderRadius: '6px',
                    border: '1px solid #E2E8F0',
                    backgroundColor: '#F8FAFC',
                    color: 'var(--color-navy-700, #123047)',
                    fontSize: '0.78rem',
                    cursor: 'pointer'
                  }}
                >
                  {pick}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Geolocation Error Feedback */}
        {geoError && (
          <div style={{
            backgroundColor: '#FFFBEB',
            border: '1px solid #FDE68A',
            color: '#92400E',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '0.85rem',
            marginBottom: '16px'
          }}>
            {geoError}
          </div>
        )}

        {/* Search Results Display (Handles Results, Loading, & Error States) */}
        {(searchResults || searchError || isSearching) && (
          <div style={{ marginTop: '24px' }}>
            <SearchResults
              results={searchResults}
              searchQuery={submittedQuery}
              isLoading={isSearching}
              error={searchError}
              onClear={() => {
                setSearchResults(null);
                setSearchError(null);
                setSubmittedQuery('');
                setSearchQuery('');
              }}
            />
          </div>
        )}
      </div>

      {/* Clinical Safeguards and Quick Guidance Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          padding: '22px',
          border: '1px solid #E2E8F0',
          boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              backgroundColor: 'var(--color-mint-100, #D1FAE5)',
              color: 'var(--color-teal-700, #0F766E)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: 'var(--color-navy-800, #123047)' }}>
              Prescription Safeguards
            </h3>
          </div>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#64748B', lineHeight: 1.5 }}>
            Schedule H and antibiotic medications require a valid physical or digital doctor prescription upon pickup. Always confirm with the dispensing pharmacist.
          </p>
        </div>

        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          padding: '22px',
          border: '1px solid #E2E8F0',
          boxShadow: '0 2px 8px rgba(18, 48, 71, 0.04)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              backgroundColor: '#FEF3C7',
              color: '#B45309',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </div>
            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: 'var(--color-navy-800, #123047)' }}>
              Emergency Medical Guidance
            </h3>
          </div>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#64748B', lineHeight: 1.5 }}>
            MediLocate does not provide emergency intervention. For severe chest pain, breathing difficulty, or trauma, contact emergency medical response immediately (<strong>112</strong> / <strong>108</strong>).
          </p>
        </div>
      </div>

      {/* MediBot Conversational Assistant Drawer */}
      <MediBotDrawer
        isOpen={isMediBotOpen}
        onClose={() => setIsMediBotOpen(false)}
      />
    </div>
  );
}

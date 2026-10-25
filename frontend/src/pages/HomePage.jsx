import React, { useState } from 'react';
import { useRouter } from '../context/RouterContext';
import { useAuth } from '../context/AuthContext';
import { searchMedicines } from '../services/medicineService';
import { useGeolocation } from '../hooks/useGeolocation';
import SearchResults from '../components/medicine/SearchResults';
import MediBotDrawer from '../components/medibot/MediBotDrawer';

/**
 * HomePage
 * Upgraded modern healthcare technology landing page for MediLocate AI.
 * Includes Hero with direct portal CTA, How It Works guide, Product Features,
 * Inventory Preview Showcase, MediBot Assistant CTA, and Partner information.
 */
export default function HomePage() {
  const { navigate } = useRouter();
  const { isAuthenticated } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchStatus, setSearchStatus] = useState(null); // null | 'empty_error' | 'planned_info'
  const [submittedQuery, setSubmittedQuery] = useState('');

  // Live Search State
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const [searchResults, setSearchResults] = useState(null);

  // MediBot Drawer Open State
  const [isMediBotOpen, setIsMediBotOpen] = useState(false);

  // Privacy-preserving Geolocation
  const {
    coords,
    loading: geoLoading,
    error: geoError,
    requestLocation,
    clearLocation,
  } = useGeolocation();

  // Supported local demonstration formulations from catalog
  const suggestedQueries = [
    'Paracetamol 500mg',
    'Dolo 650mg',
    'Amoxicillin 500mg',
    'Augmentin 625mg',
    'Cetirizine 10mg',
  ];

  const executeSearch = async (queryText) => {
    const raw = queryText !== undefined ? queryText : searchQuery;
    const query = (raw || '').trim();

    if (!query) {
      setSearchStatus('empty_error');
      setSubmittedQuery('');
      setSearchResults(null);
      setSearchError(null);
      return;
    }

    setSubmittedQuery(query);
    setSearchStatus('planned_info');
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

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    executeSearch();
  };

  const handleSuggestionClick = (query) => {
    setSearchQuery(query);
    executeSearch(query);
  };

  const handleClearResults = () => {
    setSearchResults(null);
    setSearchError(null);
    setSearchStatus(null);
    setSubmittedQuery('');
    setSearchQuery('');
  };

  return (
    <div className="homepage">
      {/* ====================================================================
          SECTION 2: HERO SECTION WITH LIGHT-THEME BACKGROUND VIDEO
          ==================================================================== */}
      <section className="hero-section" aria-labelledby="hero-heading">
        {/* Full-width decorative background video with light theme overlays */}
        <div className="hero-video-wrapper" aria-hidden="true">
          <video
            className="hero-video"
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
            aria-hidden="true"
            tabIndex={-1}
          >
            <source src="/videos/medilocate-hero.mp4" type="video/mp4" />
          </video>
          {/* Layered light gradient overlays to seamlessly integrate dark-navy video into light theme */}
          <div className="hero-video-overlay hero-video-overlay--primary" />
          <div className="hero-video-overlay hero-video-overlay--mint" />
          <div className="hero-video-overlay hero-video-overlay--edge" />
        </div>

        <div className="content-wrapper hero-section__content">
          <div className="hero-section__tagline-badge">
            <span className="hero-section__tagline-icon" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
            </span>
            <span>MediLocate — Find Your Medicine. Right Around You.</span>
          </div>

          <h1 id="hero-heading" className="hero-section__heading">
            Find your medicine. Right around you.{' '}
            <span className="hero-section__heading-highlight">Closer to home.</span>
          </h1>

          <p className="hero-section__description">
            Search medicines by name, brand, or formulation and explore pharmacy inventory
            information in one simple place.
          </p>

          {/* Direct Healthcare Portal Actions */}
          <div className="hero-section__cta-group" style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', marginTop: '32px' }}>
            <button
              type="button"
              onClick={() => navigate(isAuthenticated ? '/app' : '/login')}
              style={{
                padding: '14px 28px',
                backgroundColor: 'var(--color-teal-600, #0F766E)',
                color: '#FFFFFF',
                borderRadius: '10px',
                fontSize: '1rem',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '10px',
                boxShadow: '0 4px 14px rgba(15, 118, 110, 0.25)',
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <span>Search Medicine</span>
            </button>
            <button
              type="button"
              onClick={() => navigate('/pharmacist/register')}
              style={{
                padding: '14px 24px',
                backgroundColor: '#FFFFFF',
                color: 'var(--color-navy-800, #123047)',
                borderRadius: '10px',
                fontSize: '1rem',
                fontWeight: 600,
                border: '1px solid #CBD5E1',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <span>For Pharmacies</span>
              <span aria-hidden="true">→</span>
            </button>
          </div>
        </div>
      </section>

      {/* ====================================================================
          SECTION 3: HOW IT WORKS
          ==================================================================== */}
      <section
        className="section-block section-block--alt"
        id="how-it-works"
        aria-labelledby="how-it-works-heading"
      >
        <div className="content-wrapper">
          <div className="section-header">
            <p className="section-header__tag">Platform Architecture</p>
            <h2 id="how-it-works-heading" className="section-header__title">
              How MediLocate Works
            </h2>
            <p className="section-header__subtitle">
              A patient-centric discovery system designed for reliability, clarity, and safety when you need
              medications most.
            </p>
          </div>

          <div className="steps-grid">
            {/* Step 1 */}
            <article className="step-card">
              <div className="step-card__header">
                <div className="step-card__number" aria-hidden="true">1</div>
                <span className="step-card__status-tag">Step 1 — Search</span>
              </div>
              <h3 className="step-card__title">Search for a Medicine</h3>
              <p className="step-card__text">
                Search for a medicine by name, brand, or supported formulation. Our search engine resolves commercial brand synonyms and matches exact dosages.
              </p>
            </article>

            {/* Step 2 */}
            <article className="step-card">
              <div className="step-card__header">
                <div className="step-card__number" aria-hidden="true">2</div>
                <span className="step-card__status-tag">Step 2 — Discover</span>
              </div>
              <h3 className="step-card__title">Review Pharmacy Listings</h3>
              <p className="step-card__text">
                Review matching medicine records and available pharmacy inventory information across verified local pharmacies in your area.
              </p>
            </article>

            {/* Step 3 */}
            <article className="step-card">
              <div className="step-card__header">
                <div className="step-card__number" aria-hidden="true">3</div>
                <span className="step-card__status-tag">Step 3 — Compare</span>
              </div>
              <h3 className="step-card__title">Compare Stock & Freshness</h3>
              <p className="step-card__text">
                Compare the displayed stock status and other available information, including proximity distance, transparent unit pricing, and reporting timestamps.
              </p>
            </article>
          </div>
        </div>
      </section>

      {/* ====================================================================
          SECTION 4: PRODUCT FEATURES
          ==================================================================== */}
      <section
        className="section-block"
        id="features"
        aria-labelledby="features-heading"
      >
        <div className="content-wrapper">
          <div className="section-header">
            <p className="section-header__tag">Core Capabilities</p>
            <h2 id="features-heading" className="section-header__title">
              Built for Medicine Safety & Discovery
            </h2>
            <p className="section-header__subtitle">
              Designed specifically around strict pharmaceutical safeguards, inventory clarity,
              and patient privacy.
            </p>
          </div>

          <div className="features-grid">
            {/* Feature 1 */}
            <article className="feature-card">
              <div className="feature-card__icon-badge" aria-hidden="true">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="M9 12l2 2 4-4" />
                </svg>
              </div>
              <span className="feature-card__tag">Clinical Safeguard</span>
              <h3 className="feature-card__title">Medicine Identity & Strength Matching</h3>
              <p className="feature-card__description">
                Strict formulation safeguards prevent dangerous dosage mix-ups. Our search engine distinguishes 500mg from 650mg tablets, validates syrups against solid forms, and maps commercial brands directly to generic compounds.
              </p>
            </article>

            {/* Feature 2 */}
            <article className="feature-card">
              <div className="feature-card__icon-badge" aria-hidden="true">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                  <line x1="12" y1="22.08" x2="12" y2="12" />
                </svg>
              </div>
              <span className="feature-card__tag">Real-Time Clarity</span>
              <h3 className="feature-card__title">Inventory Status Transparency</h3>
              <p className="feature-card__description">
                Transparent stock states keep you informed before you commute. Listings indicate four verified states—In Stock, Low Stock, Out of Stock, or Stock Unknown—with unit quantities and reporting timestamps.
              </p>
            </article>

            {/* Feature 3 */}
            <article className="feature-card">
              <div className="feature-card__icon-badge" aria-hidden="true">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
                </svg>
              </div>
              <span className="feature-card__tag">Patient Privacy</span>
              <h3 className="feature-card__title">Privacy-Conscious Location Search</h3>
              <p className="feature-card__description">
                Your location is never requested automatically or tracked in the background. Geolocation runs solely on demand via client permissions, computing proximity locally without storing personal location history.
              </p>
            </article>

            {/* Feature 4 */}
            <article className="feature-card">
              <div className="feature-card__icon-badge" aria-hidden="true">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <span className="feature-card__tag">Conversational Guide</span>
              <h3 className="feature-card__title">MediBot Discovery Assistance</h3>
              <p className="feature-card__description">
                A rule-based conversational assistant that answers questions about supported formulations, explains availability terms, and provides emergency safety routing. Strictly does not diagnose or prescribe.
              </p>
            </article>
          </div>
        </div>
      </section>

      {/* ====================================================================
          SECTION 5: PRODUCT PREVIEW & LIVE DEMONSTRATION WORKFLOW
          ==================================================================== */}
      <section
        className="section-block section-block--alt"
        id="product-preview"
        aria-labelledby="product-preview-heading"
      >
        <div className="content-wrapper">
          <div className="section-header">
            <p className="section-header__tag">Live Product Demonstration</p>
            <h2 id="product-preview-heading" className="section-header__title">
              Formulary & Inventory Preview
            </h2>
            <p className="section-header__subtitle">
              MediLocate integrates formulation matching with transparent pharmacy inventory.
              Select any demo formulation below to test the live discovery engine.
            </p>
          </div>

          {/* Interactive Demo Query Selector */}
          <div className="preview-showcase-box">
            <div className="preview-showcase-box__header">
              <span className="preview-showcase-box__badge">Interactive Demonstration</span>
              <h3 className="preview-showcase-box__title">
                Explore Verified Local Formulations
              </h3>
              <p className="preview-showcase-box__text">
                Click any supported sample to run a real catalogue lookup with distance calculation and stock status ranking:
              </p>
            </div>

            <div className="preview-showcase-box__chips">
              {suggestedQueries.map((query) => (
                <button
                  key={`preview-${query}`}
                  type="button"
                  className="preview-demo-chip"
                  onClick={() => navigate(isAuthenticated ? '/app' : '/login')}
                  disabled={isSearching}
                >
                  <span aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M10.5 20.5l10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7z" />
                      <line x1="8.5" y1="8.5" x2="15.5" y2="15.5" />
                    </svg>
                  </span>
                  <span>Explore {query}</span>
                </button>
              ))}
            </div>

            {/* Inventory Status Guide */}
            <div className="preview-status-grid" aria-label="Stock status indicators guide">
              <div className="preview-status-card">
                <span className="stock-badge stock-badge--available">Confirmed Available</span>
                <h4 className="preview-status-card__title">Ready for Fulfillment</h4>
                <p className="preview-status-card__desc">
                  Store actively confirms sufficient stock units on hand.
                </p>
              </div>

              <div className="preview-status-card">
                <span className="stock-badge stock-badge--low">Low Stock Alert</span>
                <h4 className="preview-status-card__title">Limited Units Remaining</h4>
                <p className="preview-status-card__desc">
                  Store stock has dropped below standard threshold reserves.
                </p>
              </div>

              <div className="preview-status-card">
                <span className="stock-badge stock-badge--out">Zero Supply</span>
                <h4 className="preview-status-card__title">Currently Depleted</h4>
                <p className="preview-status-card__desc">
                  Store reports zero current inventory for this specific formulation.
                </p>
              </div>

              <div className="preview-status-card">
                <span className="stock-badge stock-badge--unknown">Pending Verification</span>
                <h4 className="preview-status-card__title">Unconfirmed Status</h4>
                <p className="preview-status-card__desc">
                  Stock report is unverified or has passed freshness thresholds.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
          SECTION 7: MEDIBOT CALL TO ACTION
          ==================================================================== */}
      <section
        className="section-block"
        id="medibot-cta"
        aria-labelledby="medibot-cta-heading"
      >
        <div className="content-wrapper">
          <div className="medibot-cta-card">
            <div className="medibot-cta-card__content">
              <span className="medibot-cta-card__badge">Conversational Discovery</span>
              <h2 id="medibot-cta-heading" className="medibot-cta-card__title">
                Have questions about a medicine or availability?
              </h2>
              <p className="medibot-cta-card__description">
                Ask <strong>MediBot</strong>, our medicine discovery assistant. MediBot helps you look up supported formulations, understand inventory statuses, and navigate nearby pharmacy information.
              </p>
              <p className="medibot-cta-card__disclaimer">
                <strong>Informational only:</strong> MediBot does not diagnose conditions, prescribe medications, or provide emergency medical services.
              </p>
            </div>

            <div className="medibot-cta-card__action">
              <button
                type="button"
                className="medibot-cta-btn"
                onClick={() => setIsMediBotOpen(true)}
                aria-label="Open MediBot conversational assistant"
              >
                <span className="medibot-cta-btn__icon" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </span>
                <span>Open MediBot Assistant</span>
              </button>
              <p className="medibot-cta-card__note">
                Accessible assistant drawer opens instantly
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
          PHARMACY PARTNER SECTION
          ==================================================================== */}
      <section
        className="section-block section-block--alt"
        id="for-pharmacies"
        aria-labelledby="for-pharmacies-heading"
      >
        <div className="content-wrapper">
          <div className="partner-card">
            <div className="partner-card__content">
              <span className="partner-card__badge">Pharmacy Network</span>
              <h2 id="for-pharmacies-heading" className="partner-card__title">
                Partner with MediLocate AI
              </h2>
              <p className="partner-card__description">
                Help local patients find available medications quickly while reducing unnecessary
                phone inquiries. Join our network of verified pharmacies.
              </p>

              <ul className="partner-card__features">
                <li className="partner-card__feature-item">
                  <span className="partner-card__check-icon" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                  <span>Automated inventory synchronization</span>
                </li>
                <li className="partner-card__feature-item">
                  <span className="partner-card__check-icon" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                  <span>Low-stock alert thresholds</span>
                </li>
                <li className="partner-card__feature-item">
                  <span className="partner-card__check-icon" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                  <span>Verified license credentials</span>
                </li>
                <li className="partner-card__feature-item">
                  <span className="partner-card__check-icon" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                  <span>Patient direct navigation</span>
                </li>
              </ul>
            </div>

            <div className="partner-card__action">
              <button
                type="button"
                onClick={() => navigate('/pharmacist/register')}
                className="search-form__button"
                style={{ textDecoration: 'none', border: 'none', cursor: 'pointer' }}
              >
                Partner Onboarding
              </button>
              <p className="partner-card__note">
                Dashboard features planned for Phase 6.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
          MEDIBOT CONVERSATIONAL ASSISTANT DRAWER
          ==================================================================== */}
      <MediBotDrawer
        isOpen={isMediBotOpen}
        onOpenChange={setIsMediBotOpen}
      />
    </div>
  );
}
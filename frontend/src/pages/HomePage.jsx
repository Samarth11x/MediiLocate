import React, { useState } from 'react';

/**
 * HomePage
 * Shell for MediLocate AI featuring hero messaging, search input validation preview,
 * planned location explanation, How It Works guide, and partner information.
 */
export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchStatus, setSearchStatus] = useState(null); // null | 'empty_error' | 'planned_info'
  const [submittedQuery, setSubmittedQuery] = useState('');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const query = searchQuery.trim();

    if (!query) {
      setSearchStatus('empty_error');
      setSubmittedQuery('');
      return;
    }

    setSubmittedQuery(query);
    setSearchStatus('planned_info');
  };

  return (
    <div className="homepage">
      {/* ====================================================================
          A. HERO SECTION
          ==================================================================== */}
      <section className="hero-section" aria-labelledby="hero-heading">
        <div className="content-wrapper">
          <div className="hero-section__tagline-badge">
            <span>MediLocate — Find Your Medicine. Right Around You.</span>
          </div>

          <h1 id="hero-heading" className="hero-section__heading">
            Find your medicine. Right around you.
          </h1>

          <p className="hero-section__description">
            Quickly locate vital prescription and over-the-counter medicines across verified
            local pharmacies. Check stock availability, compare proximity, and navigate with confidence.
          </p>

          {/* ==================================================================
              B. SEARCH PREVIEW CARD
              ================================================================== */}
          <div className="search-card" id="search-section">
            <form
              className="search-form"
              onSubmit={handleSearchSubmit}
              noValidate
              role="search"
              aria-label="Medicine Search"
            >
              <div className="search-form__field">
                <label htmlFor="medicine-search-input" className="search-form__label">
                  Search Medicine or Generic Compound
                </label>
                <div className="search-form__input-group">
                  <input
                    id="medicine-search-input"
                    type="search"
                    className="search-form__input"
                    placeholder="Search medicine name, strength or brand..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      if (searchStatus === 'empty_error') setSearchStatus(null);
                    }}
                    aria-describedby={searchStatus ? 'search-feedback-message' : undefined}
                    autoComplete="off"
                  />
                  <button type="submit" className="search-form__button">
                    Search Medicine
                  </button>
                </div>
              </div>
            </form>

            {/* Validation & Planned Status Feedback */}
            {searchStatus === 'empty_error' && (
              <div
                id="search-feedback-message"
                className="feedback-message feedback-message--warning"
                role="alert"
              >
                <span>Please enter a medicine name, strength, or brand to search.</span>
              </div>
            )}

            {searchStatus === 'planned_info' && (
              <div
                id="search-feedback-message"
                className="feedback-message feedback-message--info"
                role="status"
              >
                <span className="feedback-message__badge">Phase 4 Notice</span>
                <div>
                  <strong>Search query "{submittedQuery}" captured.</strong>
                  <p style={{ marginTop: '4px', fontSize: '0.8125rem' }}>
                    Live medicine catalogue matching, phonetic search, and distance-aware ranking
                    will be enabled when Core Intelligence (Phase 4) and Backend APIs (Phase 3)
                    are integrated. No simulated or fake results are displayed.
                  </p>
                </div>
              </div>
            )}

            {/* ================================================================
                C. LOCATION PREVIEW
                ================================================================ */}
            <div className="location-preview-card">
              <svg
                className="location-preview-card__icon"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              <span>
                <strong>Proximity Ranking (Planned):</strong> Automatic distance calculations and
                geo-radius filtering will be enabled in Phase 4. Your browser location is not
                requested in this phase.
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
          D. HOW IT WORKS SECTION
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
              A patient-centric discovery system designed for reliability and speed when you need
              medications most.
            </p>
          </div>

          <div className="steps-grid">
            {/* Step 1 */}
            <article className="step-card">
              <div className="step-card__number" aria-hidden="true">1</div>
              <span className="step-card__status-tag">Planned Capability</span>
              <h3 className="step-card__title">Search for a Medicine</h3>
              <p className="step-card__text">
                Enter a commercial brand or generic chemical formulation. Our Core Intelligence
                engine maps synonyms and verifies exact dosages.
              </p>
            </article>

            {/* Step 2 */}
            <article className="step-card">
              <div className="step-card__number" aria-hidden="true">2</div>
              <span className="step-card__status-tag">Planned Capability</span>
              <h3 className="step-card__title">Explore Pharmacy Listings</h3>
              <p className="step-card__text">
                View verified nearby licensed pharmacies sorted by proximity, operating hours,
                and real-time stock levels.
              </p>
            </article>

            {/* Step 3 */}
            <article className="step-card">
              <div className="step-card__number" aria-hidden="true">3</div>
              <span className="step-card__status-tag">Planned Capability</span>
              <h3 className="step-card__title">Check Freshness & Stock</h3>
              <p className="step-card__text">
                Confirm stock states (In Stock, Low Stock, or Out of Stock) with clear batch
                verification timestamps before traveling to the store.
              </p>
            </article>
          </div>
        </div>
      </section>

      {/* ====================================================================
          E. PHARMACY PARTNER SECTION
          ==================================================================== */}
      <section
        className="section-block"
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
                  <span className="partner-card__check-icon" aria-hidden="true">✓</span>
                  <span>Automated inventory synchronization</span>
                </li>
                <li className="partner-card__feature-item">
                  <span className="partner-card__check-icon" aria-hidden="true">✓</span>
                  <span>Low-stock alert thresholds</span>
                </li>
                <li className="partner-card__feature-item">
                  <span className="partner-card__check-icon" aria-hidden="true">✓</span>
                  <span>Verified license credentials</span>
                </li>
                <li className="partner-card__feature-item">
                  <span className="partner-card__check-icon" aria-hidden="true">✓</span>
                  <span>Patient direct navigation</span>
                </li>
              </ul>
            </div>

            <div className="partner-card__action">
              <a
                href="#top"
                className="search-form__button"
                style={{ textDecoration: 'none' }}
              >
                Partner Onboarding
              </a>
              <p className="partner-card__note">
                Dashboard features planned for Phase 6.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

import React from 'react';
import MedicineCard from './MedicineCard';
import PharmacyCard from '../pharmacy/PharmacyCard';
import DemoNoticeCard from '../pharmacy/DemoNoticeCard';

/**
 * SearchResults
 * Renders the stateful output of the medicine and pharmacy search:
 * - Loading indicator
 * - Validation / network error cards
 * - Empty result state with suggestions
 * - Populated medicine matches and ranked pharmacy availability with demo notice.
 */
export default function SearchResults({
  isLoading,
  error,
  results,
  searchQuery,
  onClear,
}) {
  if (isLoading) {
    return (
      <div className="search-results search-results--loading" aria-live="polite">
        <div className="loading-spinner" aria-hidden="true" />
        <p className="search-results__loading-text">
          Searching medicine catalogue and checking pharmacy inventory...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="search-results" role="alert" aria-live="assertive">
        <div className="search-error-card">
          <h3 className="search-error-card__title">Search Unavailable</h3>
          <p className="search-error-card__message">{error}</p>
          <button
            type="button"
            className="search-error-card__button"
            onClick={onClear}
          >
            Clear and Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!results) {
    return null;
  }

  const { medicines = [], pharmacies = [], total_medicines = 0, total_pharmacies = 0 } = results;

  // Empty Results State
  if (total_medicines === 0) {
    return (
      <div className="search-results" aria-live="polite">
        <div className="empty-results-card">
          <div className="empty-results-card__icon" aria-hidden="true">🔍</div>
          <h3 className="empty-results-card__title">
            No medicines found matching "{searchQuery}"
          </h3>
          <p className="empty-results-card__message">
            We could not find an exact match in the local catalogue.
          </p>
          <ul className="empty-results-card__suggestions">
            <li>Verify the chemical generic name (e.g., <em>Paracetamol</em>, <em>Amoxicillin</em>)</li>
            <li>Check specific dosage strengths (e.g., <em>500mg</em>, <em>650mg</em>, <em>250mg</em>)</li>
            <li>Try searching by commercial trade brand (e.g., <em>Crocin</em>, <em>Dolo</em>, <em>Augmentin</em>)</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <section
      className="search-results"
      id="search-results-section"
      aria-label={`Search Results for ${searchQuery}`}
    >
      {/* 1. Header with Result Summary */}
      <div className="search-results__header">
        <div className="search-results__summary">
          <h2 className="search-results__title">
            Search Results for "{searchQuery}"
          </h2>
          <p className="search-results__count">
            Found {total_medicines} medicine match{total_medicines === 1 ? '' : 'es'} across {total_pharmacies} verified pharmacy listing{total_pharmacies === 1 ? '' : 's'}.
          </p>
        </div>
        <button
          type="button"
          className="search-results__clear-btn"
          onClick={onClear}
          aria-label="Clear current search results"
        >
          Clear Results
        </button>
      </div>

      {/* 2. Matched Medicine Formulary List */}
      <div className="search-results__section">
        <h3 className="search-results__section-heading">Matched Medicine Formulations</h3>
        <div className="medicines-grid">
          {medicines.map((med) => (
            <MedicineCard key={med.id} medicine={med} />
          ))}
        </div>
      </div>

      {/* 3. Mandatory Demo Data Notice */}
      <DemoNoticeCard />

      {/* 4. Ranked Pharmacy Inventory Listings */}
      <div className="search-results__section">
        <div className="pharmacies-section-header">
          <h3 className="search-results__section-heading">
            Verified Pharmacy Availability & Pricing
          </h3>
          <span className="pharmacies-section-tag">
            Ranked by Core Intelligence (Availability + Distance + Price)
          </span>
        </div>

        {pharmacies.length > 0 ? (
          <div className="pharmacies-list">
            {pharmacies.map((pharmItem) => (
              <PharmacyCard
                key={pharmItem.inventory_id || `${pharmItem.pharmacy.id}-${pharmItem.medicine?.id}`}
                pharmacyItem={pharmItem}
              />
            ))}
          </div>
        ) : (
          <div className="no-pharmacies-box">
            <p>
              No verified pharmacies currently report stock for this medicine formulation in the active directory.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}

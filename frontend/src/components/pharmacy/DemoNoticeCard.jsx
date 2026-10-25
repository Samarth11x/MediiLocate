import React from 'react';

/**
 * Conspicuous demo mode disclosure card required wherever demo pharmacy
 * or inventory data is presented.
 */
export default function DemoNoticeCard() {
  return (
    <div
      className="demo-notice-card"
      role="region"
      aria-label="Demonstration Data Disclosure"
    >
      <div className="demo-notice-card__header">
        <span className="demo-notice-card__badge" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
          Demonstration Dataset
        </span>
      </div>
      <p className="demo-notice-card__text" style={{ fontWeight: 600, color: 'var(--color-navy-800, #123047)', marginBottom: '8px' }}>
        DEMO DATA — Pharmacy names and listing details are user-provided and have not been independently verified. Medicine prices and stock quantities are sample values, not live pharmacy inventory. Please contact the pharmacy to confirm availability.
      </p>
      <p className="demo-notice-card__text" style={{ fontSize: '0.82rem', color: '#64748B', margin: 0 }}>
        DEMO MODE — All pharmacy listings, locations, prices, and inventory shown here
        are fictional examples and are not real-time pharmacy information.
      </p>
    </div>
  );
}

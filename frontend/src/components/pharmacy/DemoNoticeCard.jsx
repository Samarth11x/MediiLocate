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
        <span className="demo-notice-card__badge" aria-hidden="true">
          ⚠️ Fictional Development Data
        </span>
      </div>
      <p className="demo-notice-card__text">
        DEMO MODE — All pharmacy listings, locations, prices, and inventory shown here
        are fictional examples and are not real-time pharmacy information.
      </p>
    </div>
  );
}

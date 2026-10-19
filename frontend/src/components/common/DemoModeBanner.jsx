import React from 'react';

/**
 * DemoModeBanner
 * Mandatory warning banner indicating that all data shown is fictional.
 * Displays exact prompt-specified text with semantic accessibility attributes.
 */
export default function DemoModeBanner() {
  return (
    <aside
      className="demo-banner"
      role="region"
      aria-label="Demo mode warning"
    >
      <div className="demo-banner__content">
        <span className="demo-banner__badge" aria-hidden="true">
          Notice
        </span>
        <p className="demo-banner__text">
          DEMO MODE — All pharmacy listings, locations, prices, and inventory shown here are fictional examples and are not real-time pharmacy information.
        </p>
      </div>
    </aside>
  );
}

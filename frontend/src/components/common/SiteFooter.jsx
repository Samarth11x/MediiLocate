import React from 'react';
import BrandMark from './BrandMark';

/**
 * SiteFooter
 * Footer containing brand identity, approved tagline, in-page navigation links,
 * and a clear demonstration disclaimer.
 */
export default function SiteFooter() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="site-footer" role="contentinfo">
      <div className="content-wrapper">
        <div className="site-footer__grid">
          {/* Brand Column */}
          <div className="site-footer__brand-block">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <BrandMark size="sm" />
              <span className="site-footer__title">MediLocate AI</span>
            </div>
            <p className="site-footer__tagline">
              MediLocate — Find Your Medicine. Right Around You.
            </p>
            <p className="site-footer__disclaimer">
              MediLocate AI is an educational healthcare technology prototype. All pharmacy names,
              inventories, and coordinates displayed within this demonstration are fictional and do not
              represent real medical establishments or live drug inventories.
            </p>
          </div>

          {/* Quick Links Column */}
          <div className="site-footer__links-block">
            <h3 className="site-footer__heading">Navigation</h3>
            <a href="#top" className="site-footer__link">Home</a>
            <a href="#search-section" className="site-footer__link">Find Medicine</a>
            <a href="#how-it-works" className="site-footer__link">How It Works</a>
            <a href="#for-pharmacies" className="site-footer__link">For Pharmacies</a>
          </div>

          {/* Project Phases Column */}
          <div className="site-footer__links-block">
            <h3 className="site-footer__heading">Architecture</h3>
            <span className="site-footer__link" style={{ cursor: 'default' }}>
              Phase 1: Foundation (Complete)
            </span>
            <span className="site-footer__link" style={{ color: 'var(--color-light-mint)', cursor: 'default' }}>
              Phase 2: Frontend Shell (Active)
            </span>
            <span className="site-footer__link" style={{ cursor: 'default' }}>
              Phase 3: Backend & Database (Planned)
            </span>
            <span className="site-footer__link" style={{ cursor: 'default' }}>
              Phase 4: Core Intelligence (Planned)
            </span>
          </div>
        </div>

        {/* Footer Bottom Bar */}
        <div className="site-footer__bottom">
          <p>© {currentYear} MediLocate AI. All rights reserved.</p>
          <p>Built with React, Vite, and Plain CSS.</p>
        </div>
      </div>
    </footer>
  );
}

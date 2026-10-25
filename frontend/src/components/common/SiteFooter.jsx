import React from 'react';
import BrandMark from './BrandMark';
import { useRouter } from '../../context/RouterContext';
import { useAuth } from '../../context/AuthContext';

/**
 * SiteFooter
 * Footer containing brand identity, approved tagline, in-page navigation links,
 * and a clear demonstration disclaimer.
 */
export default function SiteFooter() {
  const currentYear = new Date().getFullYear();
  const { currentPath, navigate } = useRouter();
  const { isAuthenticated } = useAuth();

  const handleLinkClick = (e, target, label) => {
    e.preventDefault();
    if (label === 'Find Medicine' || label === 'Search Medicine') {
      navigate(isAuthenticated ? '/app' : '/login');
      return;
    }
    if (target === '/' || target === '#top') {
      navigate('/');
      return;
    }
    if (target.startsWith('#')) {
      if (currentPath !== '/') {
        navigate(`/${target}`);
      } else {
        const el = document.querySelector(target);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      navigate(target);
    }
  };

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
            <a href="/" className="site-footer__link" onClick={(e) => handleLinkClick(e, '/')}>Home</a>
            <a href="#search-section" className="site-footer__link" onClick={(e) => handleLinkClick(e, '#search-section', 'Find Medicine')}>Find Medicine</a>
            <a href="#how-it-works" className="site-footer__link" onClick={(e) => handleLinkClick(e, '#how-it-works')}>How It Works</a>
            <a href="#features" className="site-footer__link" onClick={(e) => handleLinkClick(e, '#features')}>Features</a>
            <a href="#for-pharmacies" className="site-footer__link" onClick={(e) => handleLinkClick(e, '#for-pharmacies')}>For Pharmacies</a>
          </div>

          {/* Core Capabilities Column */}
          <div className="site-footer__links-block">
            <h3 className="site-footer__heading">Architecture</h3>
            <span className="site-footer__link" style={{ color: 'var(--color-teal-green)', fontWeight: 'var(--font-bold)', cursor: 'default' }}>
              Medicine Search Engine
            </span>
            <span className="site-footer__link" style={{ cursor: 'default' }}>
              Core Intelligence Matching
            </span>
            <span className="site-footer__link" style={{ cursor: 'default' }}>
              MediBot Conversational Assistant
            </span>
            <span className="site-footer__link" style={{ cursor: 'default' }}>
              Verified Pharmacy Inventory
            </span>
          </div>
        </div>

        {/* Demo Environment Disclosure */}
        <div className="site-footer__demo-notice">
          <p>
            <strong>Demonstration Environment:</strong> All pharmacy records, coordinates, and stock counts shown within this prototype are fictional examples for local testing.
          </p>
        </div>

        {/* Footer Bottom Bar */}
        <div className="site-footer__bottom">
          <p>© {currentYear} MediLocate AI. All rights reserved.</p>
          <p className="site-footer__legal-note">
            Informational prototype only. MediLocate does not provide clinical diagnosis, medical advice, or prescriptions.
          </p>
        </div>
      </div>
    </footer>
  );
}

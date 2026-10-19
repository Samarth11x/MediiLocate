import React, { useState, useEffect } from 'react';
import BrandMark from './BrandMark';

/**
 * SiteHeader
 * Responsive site navigation with brand mark, tagline, desktop links,
 * and an accessible mobile drawer toggle.
 */
export default function SiteHeader() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((prev) => !prev);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  // Close mobile drawer on Escape key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isMobileMenuOpen) {
        setIsMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isMobileMenuOpen]);

  const navLinks = [
    { label: 'Home', href: '#top' },
    { label: 'Find Medicine', href: '#search-section' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'For Pharmacies', href: '#for-pharmacies' },
  ];

  return (
    <header className="site-header" role="banner">
      <div className="site-header__inner">
        <a href="#top" className="site-header__brand-link" onClick={closeMobileMenu}>
          <BrandMark size="md" />
          <div className="site-header__brand-text">
            <span className="site-header__title">MediLocate AI</span>
            <span className="site-header__tagline-pill">
              Find Your Medicine. Right Around You.
            </span>
          </div>
        </a>

        {/* Desktop Navigation */}
        <nav className="site-nav" aria-label="Main Navigation">
          <ul className="site-nav__list">
            {navLinks.map((item) => (
              <li key={item.label} className="site-nav__item">
                <a href={item.href} className="site-nav__link">
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        {/* Mobile Navigation Toggle Button */}
        <button
          type="button"
          className="mobile-nav-toggle"
          aria-label={isMobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={isMobileMenuOpen}
          aria-controls="mobile-nav-drawer"
          onClick={toggleMobileMenu}
        >
          <span className="mobile-nav-toggle__bar" />
          <span className="mobile-nav-toggle__bar" />
          <span className="mobile-nav-toggle__bar" />
        </button>
      </div>

      {/* Accessible Mobile Drawer */}
      {isMobileMenuOpen && (
        <nav
          id="mobile-nav-drawer"
          className="mobile-nav-drawer"
          aria-label="Mobile Navigation"
        >
          <ul className="mobile-nav-drawer__list">
            {navLinks.map((item) => (
              <li key={item.label} className="mobile-nav-drawer__item">
                <a
                  href={item.href}
                  className="mobile-nav-drawer__link"
                  onClick={closeMobileMenu}
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </header>
  );
}

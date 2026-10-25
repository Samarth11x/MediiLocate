import React, { useState, useEffect } from 'react';
import BrandMark from './BrandMark';
import { useAuth } from '../../context/AuthContext';
import { useRouter } from '../../context/RouterContext';

/**
 * SiteHeader
 * Responsive site navigation with brand mark, tagline, desktop links,
 * authenticated portal navigation, and accessible mobile drawer toggle.
 */
export default function SiteHeader() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, role, isAuthenticated, logout } = useAuth();
  const { currentPath, navigate } = useRouter();

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

  const handleNavClick = (e, href, label) => {
    closeMobileMenu();
    if (label === 'Find Medicine' || label === 'Search Medicine') {
      e.preventDefault();
      navigate(isAuthenticated ? '/app' : '/login');
      return;
    }
    if (href === '/' || href === '#top') {
      e.preventDefault();
      navigate('/');
      return;
    }
    if (href.startsWith('#')) {
      if (currentPath !== '/') {
        e.preventDefault();
        navigate(`/${href}`);
      }
      // On homepage, let the standard hash scroll occur
    } else {
      e.preventDefault();
      navigate(href);
    }
  };

  const navLinks = [
    { label: 'Home', href: '/' },
    { label: 'Find Medicine', href: '#search-section' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'Features', href: '#features' },
    { label: 'For Pharmacies', href: '#for-pharmacies' },
  ];

  const getPortalTarget = () => {
    if (role === 'ADMIN' || user?.is_admin) return { label: 'Admin Portal', path: '/admin/dashboard' };
    if (role === 'PHARMACIST') return { label: 'Pharmacist Portal', path: '/pharmacist/dashboard' };
    return { label: 'Patient Portal', path: '/app' };
  };

  const portalInfo = isAuthenticated ? getPortalTarget() : null;

  return (
    <header className="site-header" role="banner">
      <div className="site-header__inner">
        <a
          href="#top"
          className="site-header__brand-link"
          onClick={(e) => handleNavClick(e, '/')}
        >
          <BrandMark size="md" />
          <div className="site-header__brand-text">
            <span className="site-header__title">MediLocate AI</span>
            <span className="site-header__tagline-pill">
              Find Your Medicine. Right Around You.
            </span>
          </div>
        </a>

        {/* Desktop Navigation (Only displayed when guest / logged out) */}
        {!isAuthenticated && (
          <nav className="site-nav" aria-label="Main Navigation">
            <ul className="site-nav__list">
              {navLinks.map((item) => (
                <li key={item.label} className="site-nav__item">
                  <a
                    href={item.href}
                    className="site-nav__link"
                    onClick={(e) => handleNavClick(e, item.href, item.label)}
                  >
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        )}

        {/* Primary Action Button & Auth Navigation */}
        <div className="site-header__actions">
          {isAuthenticated ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              {role === 'USER' && currentPath !== '/app' && (
                <button
                  type="button"
                  onClick={() => navigate('/app')}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: 'var(--color-teal-600, #0F766E)',
                    color: '#FFFFFF',
                    borderRadius: '8px',
                    border: 'none',
                    fontSize: '0.88rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <rect x="3" y="3" width="7" height="7" />
                    <rect x="14" y="3" width="7" height="7" />
                    <rect x="14" y="14" width="7" height="7" />
                    <rect x="3" y="14" width="7" height="7" />
                  </svg>
                  <span>Patient Portal</span>
                </button>
              )}
              {role === 'PHARMACIST' && currentPath !== '/pharmacist/dashboard' && (
                <button
                  type="button"
                  onClick={() => navigate('/pharmacist/dashboard')}
                  style={{
                    padding: '8px 14px',
                    backgroundColor: '#F0FDFA',
                    color: 'var(--color-teal-700, #0F766E)',
                    border: '1px solid #99F6E4',
                    borderRadius: '8px',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Pharmacist Dashboard
                </button>
              )}
              {(role === 'ADMIN' || user?.is_admin) && currentPath !== '/admin/dashboard' && (
                <button
                  type="button"
                  onClick={() => navigate('/admin/dashboard')}
                  style={{
                    padding: '8px 14px',
                    backgroundColor: '#F5F3FF',
                    color: '#6D28D9',
                    border: '1px solid #DDD6FE',
                    borderRadius: '8px',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Admin Console
                </button>
              )}
              <button
                type="button"
                onClick={logout}
                title="Log Out"
                style={{
                  padding: '8px 12px',
                  backgroundColor: '#F1F5F9',
                  color: '#475569',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                }}
              >
                Log Out
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button
                type="button"
                onClick={() => navigate('/login')}
                style={{
                  padding: '7px 14px',
                  backgroundColor: 'transparent',
                  color: 'var(--color-navy-800, #123047)',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  fontSize: '0.84rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => navigate(isAuthenticated ? '/app' : '/login')}
                className="site-header__cta-btn"
                style={{ border: 'none', cursor: 'pointer' }}
              >
                Search Medicine
              </button>
            </div>
          )}

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
      </div>

      {/* Accessible Mobile Drawer */}
      {isMobileMenuOpen && (
        <nav
          id="mobile-nav-drawer"
          className="mobile-nav-drawer"
          aria-label="Mobile Navigation"
        >
          <ul className="mobile-nav-drawer__list">
            {!isAuthenticated && navLinks.map((item) => (
              <li key={item.label} className="mobile-nav-drawer__item">
                <a
                  href={item.href}
                  className="mobile-nav-drawer__link"
                  onClick={(e) => handleNavClick(e, item.href, item.label)}
                >
                  {item.label}
                </a>
              </li>
            ))}
            {isAuthenticated ? (
              <>
              {role === 'USER' && currentPath !== '/app' && (
                <li className="mobile-nav-drawer__item">
                  <button
                    type="button"
                    onClick={() => { closeMobileMenu(); navigate('/app'); }}
                    style={{
                      width: '100%',
                      textAlign: 'left',
                      padding: '12px 16px',
                      background: 'none',
                      border: 'none',
                      color: 'var(--color-teal-700, #0F766E)',
                      fontSize: '1rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    Patient Portal
                  </button>
                </li>
              )}
              {role === 'PHARMACIST' && currentPath !== '/pharmacist/dashboard' && (
                <li className="mobile-nav-drawer__item">
                  <button
                    type="button"
                    onClick={() => { closeMobileMenu(); navigate('/pharmacist/dashboard'); }}
                    style={{
                      width: '100%',
                      textAlign: 'left',
                      padding: '12px 16px',
                      background: 'none',
                      border: 'none',
                      color: 'var(--color-teal-700, #0F766E)',
                      fontSize: '1rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    Pharmacist Dashboard
                  </button>
                </li>
              )}
              {(role === 'ADMIN' || user?.is_admin) && currentPath !== '/admin/dashboard' && (
                <li className="mobile-nav-drawer__item">
                  <button
                    type="button"
                    onClick={() => { closeMobileMenu(); navigate('/admin/dashboard'); }}
                    style={{
                      width: '100%',
                      textAlign: 'left',
                      padding: '12px 16px',
                      background: 'none',
                      border: 'none',
                      color: '#6D28D9',
                      fontSize: '1rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    Admin Console
                  </button>
                </li>
              )}
                <li className="mobile-nav-drawer__item">
                  <button
                    type="button"
                    onClick={() => { closeMobileMenu(); logout(); }}
                    style={{
                      width: '100%',
                      textAlign: 'left',
                      padding: '12px 16px',
                      background: 'none',
                      border: 'none',
                      color: '#64748B',
                      fontSize: '1rem',
                      fontWeight: 500,
                      cursor: 'pointer',
                    }}
                  >
                    Log Out ({user?.username})
                  </button>
                </li>
              </>
            ) : (
              <li className="mobile-nav-drawer__item">
                <button
                  type="button"
                  onClick={() => { closeMobileMenu(); navigate('/login'); }}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '12px 16px',
                    background: 'none',
                    border: 'none',
                    color: 'var(--color-teal-700, #0F766E)',
                    fontSize: '1rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Sign In / Register
                </button>
              </li>
            )}
            <li className="mobile-nav-drawer__item mobile-nav-drawer__item--cta">
              <a
                href="#search-section"
                className="mobile-nav-drawer__cta-btn"
                onClick={(e) => handleNavClick(e, '#search-section', 'Search Medicine')}
              >
                Search Medicine
              </a>
            </li>
          </ul>
        </nav>
      )}
    </header>
  );
}

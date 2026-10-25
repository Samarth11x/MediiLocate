import React from 'react';
import DemoModeBanner from '../components/common/DemoModeBanner';
import SiteHeader from '../components/common/SiteHeader';
import SiteFooter from '../components/common/SiteFooter';
import PwaInstallPrompt from '../components/common/PwaInstallPrompt';

/**
 * MainLayout
 * Application frame providing skip link, mandatory demo warning,
 * responsive header, main content region, footer, and PWA capabilities.
 */
export default function MainLayout({ children }) {
  return (
    <div className="app-container" id="top">
      {/* Accessible skip link for keyboard navigation */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* Mandatory Demo Mode Banner */}
      <DemoModeBanner />

      {/* Global Site Navigation */}
      <SiteHeader />

      {/* Main Page Landmark */}
      <main id="main-content" className="main-content" tabIndex={-1}>
        {children}
      </main>

      {/* PWA Install Capability and Offline Warning */}
      <PwaInstallPrompt />

      {/* Global Site Footer */}
      <SiteFooter />
    </div>
  );
}

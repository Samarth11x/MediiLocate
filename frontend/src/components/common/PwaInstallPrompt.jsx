import React, { useState, useEffect } from 'react';

/**
 * PwaInstallPrompt
 * 1. Listens for beforeinstallprompt event and provides capability-detected installation.
 * 2. Detects standalone mode (PWA installed) and hides installation triggers.
 * 3. Provides iOS Safari Add-to-Home-Screen instructions.
 * 4. Displays real-time offline warning bar with safety notice (no stale medicine inventory).
 */
export default function PwaInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isStandalone, setIsStandalone] = useState(false);
  const [isIos, setIsIos] = useState(false);
  const [showIosGuide, setShowIosGuide] = useState(false);
  const [isOnline, setIsOnline] = useState(typeof navigator !== 'undefined' ? navigator.onLine : true);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    // Check if running in standalone mode (already installed)
    const checkStandalone = () => {
      const isStandaloneMode =
        window.matchMedia('(display-mode: standalone)').matches ||
        window.navigator.standalone === true ||
        document.referrer.includes('android-app://');
      setIsStandalone(Boolean(isStandaloneMode));
    };

    checkStandalone();

    // Check iOS
    const userAgent = window.navigator.userAgent || '';
    const isIosDevice = /iPad|iPhone|iPod/.test(userAgent) && !window.MSStream;
    setIsIos(isIosDevice);

    // beforeinstallprompt handler
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };

    // appinstalled handler
    const handleAppInstalled = () => {
      setIsStandalone(true);
      setDeferredPrompt(null);
    };

    // Online / Offline handlers
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleInstallClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const choiceResult = await deferredPrompt.userChoice;
      if (choiceResult.outcome === 'accepted') {
        setIsStandalone(true);
      }
      setDeferredPrompt(null);
    } else if (isIos) {
      setShowIosGuide((prev) => !prev);
    }
  };

  const showInstallButton = !isStandalone && (deferredPrompt !== null || isIos);

  return (
    <>
      {/* Offline Status Warning Banner */}
      {!isOnline && (
        <aside
          role="status"
          aria-live="polite"
          style={{
            backgroundColor: '#FFFBEB',
            borderBottom: '1px solid #FDE68A',
            padding: '8px 16px',
            color: '#92400E',
            fontSize: '0.84rem',
            fontWeight: 500,
            textAlign: 'center',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            position: 'sticky',
            top: 0,
            zIndex: 1100,
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden="true">
            <line x1="1" y1="1" x2="23" y2="23" />
            <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55" />
            <path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39" />
            <line x1="12" y1="20" x2="12.01" y2="20" />
          </svg>
          <span>
            <strong>Offline Mode:</strong> Live medicine stock checks are paused until you re-establish network connection.
          </span>
          <button
            type="button"
            onClick={() => window.location.reload()}
            style={{
              background: '#F59E0B',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '4px',
              padding: '2px 8px',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer',
              marginLeft: '6px',
            }}
          >
            Retry
          </button>
        </aside>
      )}

      {/* Floating or Inline PWA Install Banner */}
      {showInstallButton && !isDismissed && (
        <div
          className="pwa-install-banner"
          style={{
            position: 'fixed',
            bottom: '20px',
            left: '20px',
            right: '20px',
            maxWidth: '420px',
            margin: '0 auto',
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '14px',
            padding: '14px 18px',
            boxShadow: '0 8px 30px rgba(18, 48, 71, 0.16)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
            zIndex: 9990,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <img
              src="/icons/icon-192x192.png"
              alt="MediLocate Logo"
              style={{ width: '38px', height: '38px', borderRadius: '8px' }}
            />
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--color-navy-800, #123047)' }}>
                Install MediLocate App
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748B' }}>
                Instant access from your home screen
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <button
              type="button"
              onClick={handleInstallClick}
              style={{
                padding: '7px 14px',
                minHeight: '36px',
                backgroundColor: 'var(--color-teal-600, #0F766E)',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontSize: '0.82rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Install
            </button>
            <button
              type="button"
              onClick={() => setIsDismissed(true)}
              aria-label="Dismiss install banner"
              style={{
                background: 'none',
                border: 'none',
                fontSize: '1.2rem',
                color: '#94A3B8',
                cursor: 'pointer',
                padding: '4px 8px',
              }}
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* iOS Safari Installation Guide Modal */}
      {showIosGuide && (
        <div
          className="responsive-modal-overlay"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '16px',
          }}
        >
          <div
            className="responsive-modal-window"
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '16px',
              maxWidth: '380px',
              width: '100%',
              padding: '24px',
              textAlign: 'center',
            }}
          >
            <div style={{ width: '48px', height: '48px', margin: '0 auto 12px', borderRadius: '12px', background: '#D1FAE5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0F766E' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
                <polyline points="16 6 12 2 8 6" />
                <line x1="12" y1="2" x2="12" y2="15" />
              </svg>
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--color-navy-800, #123047)', marginBottom: '8px' }}>
              Install on iOS Safari
            </h3>
            <p style={{ fontSize: '0.88rem', color: '#64748B', lineHeight: 1.5, marginBottom: '18px' }}>
              To install MediLocate on your iPhone or iPad:
            </p>
            <ol style={{ textAlign: 'left', fontSize: '0.85rem', color: '#334155', lineHeight: 1.6, paddingLeft: '20px', marginBottom: '20px' }}>
              <li>Tap the <strong>Share</strong> button in Safari's bottom toolbar.</li>
              <li>Scroll down and select <strong>Add to Home Screen</strong>.</li>
              <li>Tap <strong>Add</strong> in the top-right corner.</li>
            </ol>
            <button
              type="button"
              onClick={() => setShowIosGuide(false)}
              style={{
                width: '100%',
                padding: '10px',
                minHeight: '44px',
                backgroundColor: 'var(--color-teal-600, #0F766E)',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: 'pointer',
              }}
            >
              Got It
            </button>
          </div>
        </div>
      )}
    </>
  );
}

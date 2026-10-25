import React, { useState, useEffect } from 'react';
import BrandMark from './BrandMark';

/**
 * SplashScreen
 * Brief branded introduction shown once on initial load (600-850ms).
 * Strictly respects prefers-reduced-motion and cleans up timers cleanly.
 */
export default function SplashScreen({ onFinish }) {
  const [isFading, setIsFading] = useState(false);

  useEffect(() => {
    // Check if user prefers reduced motion
    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      // Immediately complete splash without animations
      onFinish();
      return;
    }

    // Brief entrance (600ms), followed by smooth 250ms fade-out
    const fadeTimer = setTimeout(() => {
      setIsFading(true);
    }, 600);

    const finishTimer = setTimeout(() => {
      onFinish();
    }, 850);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(finishTimer);
    };
  }, [onFinish]);

  return (
    <div
      className={`splash-screen ${isFading ? 'splash-screen--fading' : ''}`}
      role="status"
      aria-live="polite"
      aria-label="MediLocate AI Splash Screen"
      style={{ overflow: 'hidden' }}
    >
      {/* Background Video Layer */}
      <div className="hero-video-wrapper" aria-hidden="true" style={{ position: 'absolute', inset: 0 }}>
        <video
          className="hero-video"
          autoPlay
          muted
          loop
          playsInline
          aria-hidden="true"
        >
          <source src="/videos/medilocate-hero.mp4" type="video/mp4" />
        </video>
        <div className="hero-video-overlay hero-video-overlay--primary" style={{
          background: 'rgba(248, 250, 252, 0.85)',
          zIndex: 1,
        }} />
        <div className="hero-video-overlay hero-video-overlay--mint" style={{ zIndex: 2 }} />
      </div>

      <div className="splash-screen__content" style={{ position: 'relative', zIndex: 10 }}>
        <BrandMark size="lg" />
        <h1 className="splash-screen__title">MediLocate AI</h1>
        <p className="splash-screen__tagline">
          MediLocate — Find Your Medicine. Right Around You.
        </p>
        <div className="splash-screen__pulse" aria-hidden="true" />
      </div>
    </div>
  );
}

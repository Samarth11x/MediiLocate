import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, act, within } from '@testing-library/react';
import App from '../App';

describe('MediLocate AI - Frontend Foundation', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  // Helper to render App and fast-forward through splash entrance
  const renderAppReady = () => {
    const utils = render(<App />);
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    return utils;
  };

  it('1. Renders MediLocate AI branding across header, main content, and footer', () => {
    renderAppReady();

    // Brand name appears in header and footer
    const brandElements = screen.getAllByText(/MediLocate AI/i);
    expect(brandElements.length).toBeGreaterThanOrEqual(1);

    // Hero heading renders prominently
    expect(
      screen.getByRole('heading', { level: 1, name: /Find your medicine\. Right around you\./i })
    ).toBeInTheDocument();
  });

  it('2. Displays the exact approved brand tagline', () => {
    renderAppReady();

    const expectedTagline = 'MediLocate — Find Your Medicine. Right Around You.';
    const taglineElements = screen.getAllByText(expectedTagline);
    expect(taglineElements.length).toBeGreaterThanOrEqual(1);
  });

  it('3. Displays the mandatory demo mode warning with exact required text', () => {
    renderAppReady();

    const exactWarning =
      'DEMO MODE — All pharmacy listings, locations, prices, and inventory shown here are fictional examples and are not real-time pharmacy information.';
    expect(screen.getByText(exactWarning)).toBeInTheDocument();
  });

  it('4. Renders the main navigation links and core homepage sections', () => {
    renderAppReady();

    // Navigation links within Main Navigation
    const mainNav = screen.getByRole('navigation', { name: /Main Navigation/i });
    expect(within(mainNav).getByRole('link', { name: /^Home$/i })).toBeInTheDocument();
    expect(within(mainNav).getByRole('link', { name: /^Find Medicine$/i })).toBeInTheDocument();
    expect(within(mainNav).getByRole('link', { name: /^How It Works$/i })).toBeInTheDocument();
    expect(within(mainNav).getByRole('link', { name: /^For Pharmacies$/i })).toBeInTheDocument();

    // Homepage sections
    expect(screen.getByRole('heading', { level: 2, name: /How MediLocate Works/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: /Partner with MediLocate AI/i })).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: /Search Medicine/i }).length).toBeGreaterThanOrEqual(1);
  });

  it('5. Handles mobile navigation drawer toggle interactions correctly', () => {
    renderAppReady();

    const toggleButton = screen.getByRole('button', { name: /Open navigation menu/i });
    expect(toggleButton).toHaveAttribute('aria-expanded', 'false');

    // Click to open mobile menu
    fireEvent.click(toggleButton);
    expect(toggleButton).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByLabelText(/Close navigation menu/i)).toBeInTheDocument();

    // Mobile navigation drawer should be present
    const mobileNav = screen.getByRole('navigation', { name: /Mobile Navigation/i });
    expect(mobileNav).toBeInTheDocument();

    // Clicking a link inside the drawer closes it
    const mobileHomeLink = screen.getAllByRole('link', { name: /^Home$/i })[1];
    fireEvent.click(mobileHomeLink);
    expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
  });

  it('6. Renders hero portal actions directing to patient discovery and pharmacy partner onboarding', () => {
    renderAppReady();

    const patientBtn = screen.getAllByRole('button', { name: /Search Medicine/i })[0];
    const pharmacyBtn = screen.getByRole('button', { name: /For Pharmacies/i });

    expect(patientBtn).toBeInTheDocument();
    expect(pharmacyBtn).toBeInTheDocument();
  });

  it('7. Displays interactive formulation exploration chips in preview showcase', () => {
    renderAppReady();

    const chip = screen.getByRole('button', { name: /Explore Paracetamol 500mg/i });
    expect(chip).toBeInTheDocument();
  });
});

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
    expect(screen.getByText(/Proximity Ranking \(Planned\):/i)).toBeInTheDocument();
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

  it('6. Produces an accessible validation error when submitting an empty search', () => {
    renderAppReady();

    const searchInput = screen.getByPlaceholderText(/Search medicine name, strength or brand\.\.\./i);
    const searchButton = screen.getByRole('button', { name: /Search Medicine/i });

    // Submit while empty
    fireEvent.change(searchInput, { target: { value: '   ' } });
    fireEvent.click(searchButton);

    const alertMessage = screen.getByRole('alert');
    expect(alertMessage).toBeInTheDocument();
    expect(alertMessage).toHaveTextContent(/Please enter a medicine name, strength, or brand to search/i);
  });

  it('7. Submitting a non-empty search reports that search is planned and does not invent fake results', () => {
    renderAppReady();

    const searchInput = screen.getByPlaceholderText(/Search medicine name, strength or brand\.\.\./i);
    const searchButton = screen.getByRole('button', { name: /Search Medicine/i });

    // Submit non-empty query
    fireEvent.change(searchInput, { target: { value: 'Amoxicillin 500mg' } });
    fireEvent.click(searchButton);

    const statusMessage = screen.getByRole('status');
    expect(statusMessage).toBeInTheDocument();
    expect(statusMessage).toHaveTextContent(/Search query "Amoxicillin 500mg" captured/i);
    expect(statusMessage).toHaveTextContent(/No simulated or fake results are displayed/i);
  });
});

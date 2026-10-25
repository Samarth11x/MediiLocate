import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import PwaInstallPrompt from '../components/common/PwaInstallPrompt';

describe('MediLocate PWA Capabilities & Medicine Safety', () => {
  let originalOnLine;

  beforeEach(() => {
    originalOnLine = navigator.onLine;
  });

  afterEach(() => {
    Object.defineProperty(navigator, 'onLine', {
      configurable: true,
      value: originalOnLine,
    });
  });

  it('renders without crashing and hides prompt in default standalone or unprompted mode', () => {
    render(<PwaInstallPrompt />);
    // With no beforeinstallprompt event fired and not iOS, no install banner appears
    expect(screen.queryByText(/Install MediLocate App/i)).not.toBeInTheDocument();
  });

  it('detects beforeinstallprompt event and renders the install trigger', () => {
    render(<PwaInstallPrompt />);

    const fakePromptEvent = new Event('beforeinstallprompt');
    fakePromptEvent.prompt = vi.fn();
    fakePromptEvent.userChoice = Promise.resolve({ outcome: 'accepted' });

    act(() => {
      window.dispatchEvent(fakePromptEvent);
    });

    expect(screen.getByText(/Install MediLocate App/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^Install$/i })).toBeInTheDocument();
  });

  it('triggers prompt() when Install button is clicked', async () => {
    render(<PwaInstallPrompt />);

    const fakePromptEvent = new Event('beforeinstallprompt');
    fakePromptEvent.prompt = vi.fn();
    fakePromptEvent.userChoice = Promise.resolve({ outcome: 'accepted' });

    act(() => {
      window.dispatchEvent(fakePromptEvent);
    });

    const installBtn = screen.getByRole('button', { name: /^Install$/i });
    await act(async () => {
      fireEvent.click(installBtn);
    });

    expect(fakePromptEvent.prompt).toHaveBeenCalled();
  });

  it('displays the offline safety warning when network goes offline', () => {
    render(<PwaInstallPrompt />);

    act(() => {
      window.dispatchEvent(new Event('offline'));
    });

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText(/Live medicine stock checks are paused/i)).toBeInTheDocument();
  });

  it('removes the offline banner when connection is restored', () => {
    render(<PwaInstallPrompt />);

    act(() => {
      window.dispatchEvent(new Event('offline'));
    });
    expect(screen.getByRole('status')).toBeInTheDocument();

    act(() => {
      window.dispatchEvent(new Event('online'));
    });
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('allows user to dismiss the install banner', () => {
    render(<PwaInstallPrompt />);

    const fakePromptEvent = new Event('beforeinstallprompt');
    fakePromptEvent.prompt = vi.fn();
    fakePromptEvent.userChoice = Promise.resolve({ outcome: 'dismissed' });

    act(() => {
      window.dispatchEvent(fakePromptEvent);
    });

    const dismissBtn = screen.getByLabelText(/Dismiss install banner/i);
    act(() => {
      fireEvent.click(dismissBtn);
    });

    expect(screen.queryByText(/Install MediLocate App/i)).not.toBeInTheDocument();
  });
});

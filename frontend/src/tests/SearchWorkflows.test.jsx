import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import HomePage from '../pages/HomePage';

describe('MediLocate AI - Phase 6: Medicine Search & Pharmacy Availability Workflows', () => {
  const mockSuccessResponse = {
    query: 'Paracetamol 500mg',
    total_medicines: 1,
    total_pharmacies: 4,
    medicines: [
      {
        id: 1,
        brand_name: 'Crocin',
        generic_name: 'Paracetamol',
        strength: '500mg',
        dosage_form: 'Tablet',
        is_prescription_required: false,
        schedule: null,
        pack_size: '15 tablets',
        score: 100,
      },
    ],
    pharmacies: [
      {
        inventory_id: 101,
        medicine: {
          id: 1,
          brand_name: 'Crocin',
          generic_name: 'Paracetamol',
          strength: '500mg',
          dosage_form: 'Tablet',
        },
        pharmacy: {
          id: 1,
          name: 'Apollo Pharmacy - Indiranagar',
          address: '100ft Road, Indiranagar, Bengaluru',
          city: 'Bengaluru',
          phone_number: '+91-80-25251100',
          is_verified: true,
          latitude: 12.9719,
          longitude: 77.6412,
        },
        stock_state: 'AVAILABLE',
        stock_quantity: 45,
        unit_price: '30.00',
        distance_km: 1.2,
        ranking_score: 92.5,
        ranking_explanation: 'In stock with proximity advantage (1.2 km away)',
        is_demo_data: true,
      },
      {
        inventory_id: 102,
        medicine: {
          id: 1,
          brand_name: 'Crocin',
          generic_name: 'Paracetamol',
          strength: '500mg',
          dosage_form: 'Tablet',
        },
        pharmacy: {
          id: 2,
          name: 'MedPlus - Koramangala',
          address: '80ft Road, Koramangala, Bengaluru',
          city: 'Bengaluru',
          phone_number: '+91-80-25531234',
          is_verified: true,
          latitude: 12.9352,
          longitude: 77.6245,
        },
        stock_state: 'LOW_STOCK',
        stock_quantity: 3,
        unit_price: '28.50',
        distance_km: 3.8,
        ranking_score: 75.0,
        ranking_explanation: 'Low stock reported (3 remaining)',
        is_demo_data: true,
      },
      {
        inventory_id: 103,
        medicine: {
          id: 1,
          brand_name: 'Crocin',
          generic_name: 'Paracetamol',
          strength: '500mg',
          dosage_form: 'Tablet',
        },
        pharmacy: {
          id: 3,
          name: 'Wellness Forever - Jayanagar',
          address: '9th Block, Jayanagar, Bengaluru',
          city: 'Bengaluru',
          phone_number: '+91-80-26659988',
          is_verified: true,
          latitude: 12.9250,
          longitude: 77.5938,
        },
        stock_state: 'OUT_OF_STOCK',
        stock_quantity: 0,
        unit_price: '30.00',
        distance_km: 6.5,
        ranking_score: 40.0,
        ranking_explanation: 'Out of stock reported by store',
        is_demo_data: true,
      },
      {
        inventory_id: 104,
        medicine: {
          id: 1,
          brand_name: 'Crocin',
          generic_name: 'Paracetamol',
          strength: '500mg',
          dosage_form: 'Tablet',
        },
        pharmacy: {
          id: 4,
          name: 'Corner Chemist',
          address: 'Whitefield Main Rd, Bengaluru',
          city: 'Bengaluru',
          phone_number: '+91-80-28452211',
          is_verified: true,
          latitude: 12.9698,
          longitude: 77.7499,
        },
        stock_state: 'UNKNOWN',
        stock_quantity: null,
        unit_price: null,
        distance_km: null,
        ranking_score: 25.0,
        ranking_explanation: 'Stock state unconfirmed',
        is_demo_data: true,
      },
    ],
  };

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('1. Searches medicine catalog and renders matched medicine formulation and ranked pharmacies', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockSuccessResponse,
    });

    render(<HomePage />);

    const searchInput = screen.getByPlaceholderText(/Search medicine name, strength or brand\.\.\./i);
    const searchButton = screen.getByRole('button', { name: /Search Medicine/i });

    fireEvent.change(searchInput, { target: { value: 'Paracetamol 500mg' } });
    fireEvent.click(searchButton);

    // Form inputs disable during submission
    expect(searchButton).toBeDisabled();

    // Results header appears
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 2, name: /Search Results for "Paracetamol 500mg"/i })).toBeInTheDocument();
    });

    // Medicine match card
    expect(screen.getByText('Crocin')).toBeInTheDocument();
    expect(screen.getByText('Paracetamol')).toBeInTheDocument();
    expect(screen.getAllByText(/500mg/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/tablet/i).length).toBeGreaterThanOrEqual(1);

    // Ranked pharmacy cards
    expect(screen.getByText('Apollo Pharmacy - Indiranagar')).toBeInTheDocument();
    expect(screen.getByText('MedPlus - Koramangala')).toBeInTheDocument();
    expect(screen.getByText('Wellness Forever - Jayanagar')).toBeInTheDocument();
    expect(screen.getByText('Corner Chemist')).toBeInTheDocument();
  });

  it('2. Correctly renders all four stock status badges (AVAILABLE, LOW_STOCK, OUT_OF_STOCK, UNKNOWN)', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockSuccessResponse,
    });

    render(<HomePage />);

    const searchInput = screen.getByPlaceholderText(/Search medicine name, strength or brand\.\.\./i);
    const searchButton = screen.getByRole('button', { name: /Search Medicine/i });

    fireEvent.change(searchInput, { target: { value: 'Paracetamol 500mg' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('In Stock')).toBeInTheDocument();
    });

    expect(screen.getByText('Low Stock')).toBeInTheDocument();
    expect(screen.getByText('Out of Stock')).toBeInTheDocument();
    expect(screen.getByText('Stock Unknown')).toBeInTheDocument();
  });

  it('3. Prominently displays the mandatory fictional demonstration warning notice', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => mockSuccessResponse,
    });

    render(<HomePage />);

    const searchInput = screen.getByPlaceholderText(/Search medicine name, strength or brand\.\.\./i);
    const searchButton = screen.getByRole('button', { name: /Search Medicine/i });

    fireEvent.change(searchInput, { target: { value: 'Paracetamol 500mg' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByRole('region', { name: /Demonstration Data Disclosure/i })).toBeInTheDocument();
    });

    // Exact required text
    expect(screen.getByText(/DEMO MODE — All pharmacy listings, locations, prices, and inventory shown here are fictional examples and are not real-time pharmacy information\./i)).toBeInTheDocument();
  });

  it('4. Renders helpful suggestions and empty state when query returns no medicines', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({
        query: 'NonexistentMedicineX',
        total_medicines: 0,
        total_pharmacies: 0,
        medicines: [],
        pharmacies: [],
      }),
    });

    render(<HomePage />);

    const searchInput = screen.getByPlaceholderText(/Search medicine name, strength or brand\.\.\./i);
    const searchButton = screen.getByRole('button', { name: /Search Medicine/i });

    fireEvent.change(searchInput, { target: { value: 'NonexistentMedicineX' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 3, name: /No medicines found matching "NonexistentMedicineX"/i })).toBeInTheDocument();
    });

    expect(screen.getByText(/Verify the chemical generic name/i)).toBeInTheDocument();
    expect(screen.getByText(/Check specific dosage strengths/i)).toBeInTheDocument();
  });

  it('5. Handles API network error gracefully with accessible error card and retry option', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network connection failed'));

    render(<HomePage />);

    const searchInput = screen.getByPlaceholderText(/Search medicine name, strength or brand\.\.\./i);
    const searchButton = screen.getByRole('button', { name: /Search Medicine/i });

    fireEvent.change(searchInput, { target: { value: 'Paracetamol' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(screen.getByRole('heading', { level: 3, name: /Search Unavailable/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Clear and Try Again/i })).toBeInTheDocument();

    // Click retry/clear button
    fireEvent.click(screen.getByRole('button', { name: /Clear and Try Again/i }));
    expect(screen.queryByRole('heading', { level: 3, name: /Search Unavailable/i })).not.toBeInTheDocument();
  });

  it('6. Does not request browser geolocation on mount, only upon user explicit click', async () => {
    const getCurrentPositionMock = vi.fn();
    Object.defineProperty(global.navigator, 'geolocation', {
      writable: true,
      value: {
        getCurrentPosition: getCurrentPositionMock,
      },
    });

    render(<HomePage />);

    // Geolocation was NOT called automatically on mount
    expect(getCurrentPositionMock).not.toHaveBeenCalled();

    // User explicitly requests location
    const locationBtn = screen.getByRole('button', { name: /Enable location for proximity ranking/i });
    fireEvent.click(locationBtn);

    expect(getCurrentPositionMock).toHaveBeenCalledTimes(1);
  });

  it('7. Handles browser geolocation permission denial gracefully', async () => {
    const getCurrentPositionMock = vi.fn((success, error) => {
      error({
        code: 1, // PERMISSION_DENIED
        PERMISSION_DENIED: 1,
        message: 'User denied geolocation',
      });
    });

    Object.defineProperty(global.navigator, 'geolocation', {
      writable: true,
      value: {
        getCurrentPosition: getCurrentPositionMock,
      },
    });

    render(<HomePage />);

    const locationBtn = screen.getByRole('button', { name: /Enable location for proximity ranking/i });
    fireEvent.click(locationBtn);

    await waitFor(() => {
      expect(screen.getByText(/Location permission was denied\. You can still search medicines without proximity ranking\./i)).toBeInTheDocument();
    });
  });
});

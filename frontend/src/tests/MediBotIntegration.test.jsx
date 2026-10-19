import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MediBotDrawer from '../components/medibot/MediBotDrawer';

describe('MediLocate AI - Phase 6: MediBot Conversational Assistant Integration', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('1. Toggles drawer open and closed using launcher and close button', () => {
    render(<MediBotDrawer />);

    // Initially drawer is closed, launcher is visible
    const launcher = screen.getByRole('button', { name: /Open MediBot conversational assistant/i });
    expect(launcher).toBeInTheDocument();
    expect(screen.queryByRole('dialog', { name: /MediBot Chat Session/i })).not.toBeInTheDocument();

    // Click to open
    fireEvent.click(launcher);
    expect(screen.getByRole('dialog', { name: /MediBot Chat Session/i })).toBeInTheDocument();
    expect(screen.getByText(/Medical Safety & Discovery Engine/i)).toBeInTheDocument();

    // Click close button
    const closeBtn = screen.getByRole('button', { name: /Close MediBot chat/i });
    fireEvent.click(closeBtn);
    expect(screen.queryByRole('dialog', { name: /MediBot Chat Session/i })).not.toBeInTheDocument();
  });

  it('2. Sends a message and renders the assistant response', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({
        status: 'success',
        message: 'Paracetamol 500mg is available across several verified local pharmacies.',
        intent: 'SEARCH_MEDICINE',
        safety_category: null,
        suggestions: ['Check pharmacy hours', 'Compare prices'],
        results: [],
        context: { last_searched_medicine: 'Paracetamol 500mg' },
      }),
    });

    render(<MediBotDrawer />);

    // Open drawer
    fireEvent.click(screen.getByRole('button', { name: /Open MediBot conversational assistant/i }));

    const input = screen.getByLabelText(/Type message for MediBot/i);
    const sendButton = screen.getByRole('button', { name: /Send message/i });

    fireEvent.change(input, { target: { value: 'Where can I find Paracetamol 500mg?' } });
    fireEvent.click(sendButton);

    // Assistant reply renders
    await waitFor(() => {
      expect(screen.getByText(/Paracetamol 500mg is available across several verified local pharmacies\./i)).toBeInTheDocument();
    });

    // Suggestions render
    expect(screen.getByRole('button', { name: 'Check pharmacy hours' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Compare prices' })).toBeInTheDocument();
  });

  it('3. Clicking a suggestion chip populates and triggers a chat query', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({
        status: 'success',
        message: 'Low stock indicates that the pharmacy has fewer units than the safety threshold.',
        intent: 'EXPLAIN_STOCK',
        suggestions: [],
        results: [],
      }),
    });

    render(<MediBotDrawer />);

    fireEvent.click(screen.getByRole('button', { name: /Open MediBot conversational assistant/i }));

    // Click default suggestion from welcome message
    const suggestionBtn = screen.getByRole('button', { name: 'What does low stock mean?' });
    fireEvent.click(suggestionBtn);

    await waitFor(() => {
      expect(screen.getByText(/Low stock indicates that the pharmacy has fewer units/i)).toBeInTheDocument();
    });
  });

  it('4. Renders medicine mini-cards when assistant returns discovery results', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({
        status: 'success',
        message: 'I found matching formulations for your query:',
        intent: 'SEARCH_MEDICINE',
        suggestions: [],
        results: [
          {
            id: 1,
            brand_name: 'Crocin 500',
            generic_name: 'Paracetamol',
            strength: '500mg',
            dosage_form: 'Tablet',
          },
        ],
      }),
    });

    render(<MediBotDrawer />);

    fireEvent.click(screen.getByRole('button', { name: /Open MediBot conversational assistant/i }));

    const input = screen.getByLabelText(/Type message for MediBot/i);
    const sendButton = screen.getByRole('button', { name: /Send message/i });

    fireEvent.change(input, { target: { value: 'Find Crocin' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Crocin 500 (Paracetamol)')).toBeInTheDocument();
    });

    expect(screen.getByText('500mg Tablet')).toBeInTheDocument();
  });

  it('5. Preserves multi-turn conversation context across interactions', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({
          status: 'success',
          message: 'Found Paracetamol 500mg. Do you want to see nearby pharmacies?',
          intent: 'SEARCH_MEDICINE',
          context: { medicine_name: 'Paracetamol', strength: '500mg' },
          suggestions: ['Yes, show pharmacies'],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({
          status: 'success',
          message: 'Showing pharmacies stocking Paracetamol 500mg nearby.',
          intent: 'FIND_PHARMACIES',
          context: { medicine_name: 'Paracetamol', strength: '500mg', step: 2 },
          suggestions: [],
        }),
      });

    global.fetch = fetchMock;

    render(<MediBotDrawer />);

    fireEvent.click(screen.getByRole('button', { name: /Open MediBot conversational assistant/i }));

    const input = screen.getByLabelText(/Type message for MediBot/i);
    const sendButton = screen.getByRole('button', { name: /Send message/i });

    // Turn 1
    fireEvent.change(input, { target: { value: 'Find Paracetamol' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Found Paracetamol 500mg\. Do you want to see nearby pharmacies\?/i)).toBeInTheDocument();
    });

    // Turn 2
    fireEvent.change(input, { target: { value: 'Yes, show pharmacies' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Showing pharmacies stocking Paracetamol 500mg nearby\./i)).toBeInTheDocument();
    });

    // Verify context was passed in second call
    expect(fetchMock).toHaveBeenCalledTimes(2);
    const secondCallBody = JSON.parse(fetchMock.mock.calls[1][1].body);
    expect(secondCallBody.context).toEqual({ medicine_name: 'Paracetamol', strength: '500mg' });
  });

  it('6. Displays prominent emergency notice styling for acute medical concerns', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({
        status: 'success',
        message: 'This may be a serious medical emergency. Please seek immediate professional medical attention or call emergency services (112 / 108 / 911).',
        intent: 'EMERGENCY_REDIRECT',
        safety_category: 'emergency_concern',
        suggestions: ['Emergency contacts', 'Find nearest emergency hospital'],
      }),
    });

    render(<MediBotDrawer />);

    fireEvent.click(screen.getByRole('button', { name: /Open MediBot conversational assistant/i }));

    const input = screen.getByLabelText(/Type message for MediBot/i);
    const sendButton = screen.getByRole('button', { name: /Send message/i });

    fireEvent.change(input, { target: { value: 'I have severe chest pain and cannot breathe' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/ACUTE MEDICAL EMERGENCY NOTICE/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/This may be a serious medical emergency/i)).toBeInTheDocument();
  });

  it('7. Renders pharmacy inventory mini-cards with stock badges and decodes HTML entities', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => 'application/json' },
      json: async () => ({
        status: 'success',
        message: "I found 2 verified pharmacies with inventory records for 'Crocin (Paracetamol) &#x35;00mg Tablet'. Availability varies by pharmacy; please note the stock status shown for each listing:",
        intent: 'PHARMACY_SEARCH',
        suggestions: ['Find another medicine', 'What does low stock mean?'],
        results: [
          {
            id: 1,
            pharmacy: {
              id: 1,
              name: 'CarePoint Pharmacy',
              area: 'Koramangala',
              city: 'Bengaluru',
            },
            quantity: 45,
            stock_status: 'AVAILABLE',
            stock_status_label: 'Available',
            price: 30.50,
            distance_km: null,
            is_demo: true,
          },
          {
            id: 2,
            pharmacy: {
              id: 2,
              name: 'Metro Chemist',
              area: 'Indiranagar',
              city: 'Bengaluru',
            },
            quantity: 5,
            stock_status: 'LOW_STOCK',
            stock_status_label: 'Low Stock',
            price: 32.00,
            distance_km: 2.5,
            is_demo: true,
          },
        ],
      }),
    });

    render(<MediBotDrawer />);

    fireEvent.click(screen.getByRole('button', { name: /Open MediBot conversational assistant/i }));

    const input = screen.getByLabelText(/Type message for MediBot/i);
    const sendButton = screen.getByRole('button', { name: /Send message/i });

    fireEvent.change(input, { target: { value: 'Find nearby pharmacies' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Verified Pharmacies:/i)).toBeInTheDocument();
    });

    // Decoded entity check: &#x35;00mg should become 500mg
    expect(screen.getByText(/Crocin \(Paracetamol\) 500mg Tablet/i)).toBeInTheDocument();
    expect(screen.queryByText(/&#x35;/i)).not.toBeInTheDocument();

    // Check rendered pharmacies
    expect(screen.getByText('CarePoint Pharmacy')).toBeInTheDocument();
    expect(screen.getByText('Metro Chemist')).toBeInTheDocument();

    // Check stock badges
    expect(screen.getByText('Available')).toBeInTheDocument();
    expect(screen.getByText('Low Stock')).toBeInTheDocument();
    expect(screen.getByText('45 in stock')).toBeInTheDocument();
    expect(screen.getByText('₹30.50')).toBeInTheDocument();
    expect(screen.getByText(/2.5 km/i)).toBeInTheDocument();
  });

  it('8. Follows up with Find nearby pharmacies suggestion preserving medicine context', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({
          status: 'success',
          message: 'I found 1 matching medicine(s) for Paracetamol 500mg:\n1. Crocin (Paracetamol) - 500mg Tablet',
          intent: 'MEDICINE_SEARCH',
          context: {
            last_intent: 'MEDICINE_SEARCH',
            searched_medicine: 'Paracetamol 500mg',
            searched_medicine_id: '1',
          },
          suggestions: ['Find nearby pharmacies', 'Search another medicine'],
          results: [
            {
              medicine: {
                id: 1,
                brand_name: 'Crocin',
                generic_name: 'Paracetamol',
                strength: '500mg',
                dosage_form: 'Tablet',
              },
            },
          ],
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({
          status: 'success',
          message: "I found 2 verified pharmacies with inventory records for 'Paracetamol 500mg'. Availability varies by pharmacy; please note the stock status shown for each listing:",
          intent: 'PHARMACY_SEARCH',
          context: {
            last_intent: 'PHARMACY_SEARCH',
            searched_medicine: 'Paracetamol 500mg',
            searched_medicine_id: '1',
          },
          suggestions: ['Find another medicine'],
          results: [
            {
              id: 1,
              pharmacy: { name: 'CarePoint Pharmacy', area: 'Koramangala', city: 'Bengaluru' },
              stock_status: 'AVAILABLE',
              stock_status_label: 'Available',
              quantity: 45,
            },
          ],
        }),
      });

    global.fetch = fetchMock;

    render(<MediBotDrawer />);

    fireEvent.click(screen.getByRole('button', { name: /Open MediBot conversational assistant/i }));

    const input = screen.getByLabelText(/Type message for MediBot/i);
    const sendButton = screen.getByRole('button', { name: /Send message/i });

    // Turn 1: Search Paracetamol 500mg
    fireEvent.change(input, { target: { value: 'Find Paracetamol 500mg' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Crocin \(Paracetamol\) - 500mg Tablet/i)).toBeInTheDocument();
    });

    // Verify 'Find nearby pharmacies' suggestion chip exists
    const findPharmaciesChip = screen.getByRole('button', { name: 'Find nearby pharmacies' });
    expect(findPharmaciesChip).toBeInTheDocument();

    // Turn 2: Click the suggestion chip
    fireEvent.click(findPharmaciesChip);

    await waitFor(() => {
      expect(screen.getByText('CarePoint Pharmacy')).toBeInTheDocument();
    });

    // Verify context was passed correctly in turn 2
    expect(fetchMock).toHaveBeenCalledTimes(2);
    const turn2Body = JSON.parse(fetchMock.mock.calls[1][1].body);
    expect(turn2Body.message).toBe('Find nearby pharmacies');
    expect(turn2Body.context).toEqual({
      last_intent: 'MEDICINE_SEARCH',
      searched_medicine: 'Paracetamol 500mg',
      searched_medicine_id: '1',
    });
  });
});

import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RouterProvider } from '../context/RouterContext';
import { AuthProvider, useAuth } from '../context/AuthContext';
import ProtectedRoute from '../components/common/ProtectedRoute';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import PharmacistRegisterPage from '../pages/PharmacistRegisterPage';
import PharmacistDashboardPage from '../pages/PharmacistDashboardPage';
import AdminDashboardPage from '../pages/AdminDashboardPage';
import UserPortalPage from '../pages/UserPortalPage';
import NotFoundPage from '../pages/NotFoundPage';
import { authService } from '../services/authService';
import { portalService } from '../services/portalService';

vi.mock('../services/authService');
vi.mock('../services/portalService');

describe('MediLocate AI - Phase 8: Authentication & Role-Based Portals', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ---------------------------------------------------------------------------
  // 1. Authentication Pages & Form Validation
  // ---------------------------------------------------------------------------

  it('1. Renders the Sign In page with demonstration credential quick-fill helpers', () => {
    authService.getCurrentUser.mockResolvedValue({ authenticated: false, user: null });

    render(
      <RouterProvider initialPath="/login">
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </RouterProvider>
    );

    expect(screen.getByRole('heading', { name: /Sign In to MediLocate/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();

    // Quick fill buttons exist
    const patientQuickBtn = screen.getByRole('button', { name: /^Patient$/i });
    expect(patientQuickBtn).toBeInTheDocument();

    // Click quick fill fills inputs
    fireEvent.click(patientQuickBtn);
    expect(screen.getByLabelText(/Username/i)).toHaveValue('patient_demo');
    expect(screen.getByLabelText(/Password/i)).toHaveValue('PatientPass123!');
  });

  it('2. Renders the Patient Registration page and handles password mismatch error', async () => {
    authService.getCurrentUser.mockResolvedValue({ authenticated: false, user: null });

    render(
      <RouterProvider initialPath="/register">
        <AuthProvider>
          <RegisterPage />
        </AuthProvider>
      </RouterProvider>
    );

    expect(screen.getByRole('heading', { name: /Create Patient Account/i })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/^Username \*/i), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText(/^Password \*/i), { target: { value: 'Password123' } });
    fireEvent.change(screen.getByLabelText(/^Confirm \*/i), { target: { value: 'Mismatch999' } });

    fireEvent.click(screen.getByRole('button', { name: /Create Account/i }));

    const errorAlert = await screen.findByRole('alert');
    expect(errorAlert).toHaveTextContent(/Passwords do not match/i);
  });

  it('3. Renders the Pharmacist Onboarding page with regulatory drug license input', () => {
    authService.getCurrentUser.mockResolvedValue({ authenticated: false, user: null });

    render(
      <RouterProvider initialPath="/pharmacist/register">
        <AuthProvider>
          <PharmacistRegisterPage />
        </AuthProvider>
      </RouterProvider>
    );

    expect(screen.getByRole('heading', { name: /Pharmacy Partner Onboarding/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Drug License Number \*/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Trading Pharmacy Name \*/i)).toBeInTheDocument();
    expect(screen.getByText(/Verification Process:/i)).toBeInTheDocument();
  });

  it('4. Renders 404 Not Found for unmapped routes', () => {
    render(
      <RouterProvider initialPath="/unknown-route">
        <NotFoundPage />
      </RouterProvider>
    );

    expect(screen.getByRole('heading', { name: /Page Not Found/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Return to Home/i })).toBeInTheDocument();
  });

  // ---------------------------------------------------------------------------
  // 2. Protected Route Guards & Role Boundaries
  // ---------------------------------------------------------------------------

  it('5. Protects Admin Portal from unauthenticated visitors', async () => {
    authService.getCurrentUser.mockResolvedValue({ authenticated: false, user: null });

    render(
      <RouterProvider initialPath="/admin/dashboard">
        <AuthProvider>
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AdminDashboardPage />
          </ProtectedRoute>
        </AuthProvider>
      </RouterProvider>
    );

    expect(await screen.findByRole('heading', { name: /Authentication Required/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^Log In$/i })).toBeInTheDocument();
  });

  it('6. Blocks Patient user from accessing Admin Portal with clear 403 guidance', async () => {
    authService.getCurrentUser.mockResolvedValue({
      authenticated: true,
      user: { id: 1, username: 'patient_demo', role: 'USER' },
    });

    render(
      <RouterProvider initialPath="/admin/dashboard">
        <AuthProvider>
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AdminDashboardPage />
          </ProtectedRoute>
        </AuthProvider>
      </RouterProvider>
    );

    expect(await screen.findByRole('heading', { name: /Restricted Portal Access/i })).toBeInTheDocument();
    expect(screen.getByText(/requires/i)).toHaveTextContent('ADMIN');
    expect(screen.getByRole('button', { name: /Patient Portal/i })).toBeInTheDocument();
  });

  // ---------------------------------------------------------------------------
  // 3. Pharmacist Portal States: PENDING vs VERIFIED
  // ---------------------------------------------------------------------------

  it('7. Displays pharmacy details, Add/Edit establishment button, and Excel/CSV import options', async () => {
    authService.getCurrentUser.mockResolvedValue({
      authenticated: true,
      user: { id: 2, username: 'pharma_user', role: 'PHARMACIST' },
    });

    portalService.getPharmacistPharmacy.mockResolvedValue({
      id: 10,
      name: 'Demo GreenCross Meds',
      license_number: 'DL-KA-2026-99881',
      area: 'Whitefield',
      city: 'Bengaluru',
      pin_code: '560066',
      verification_status: 'VERIFIED',
    });

    portalService.getPharmacistInventory.mockResolvedValue({
      pharmacy_status: 'VERIFIED',
      is_verified: true,
      inventory: [],
    });

    render(
      <RouterProvider initialPath="/pharmacist/dashboard">
        <AuthProvider>
          <PharmacistDashboardPage />
        </AuthProvider>
      </RouterProvider>
    );

    expect(await screen.findByText(/ACTIVE ESTABLISHMENT/i)).toBeInTheDocument();
    expect(screen.getByText(/Demo GreenCross Meds/i)).toBeInTheDocument();
    expect(screen.getByText(/DL-KA-2026-99881/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Import Excel \/ CSV/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Add Medicine Stock/i })).toBeInTheDocument();
  });

  it('8. Renders full inventory management table and CSV export for pharmacists', async () => {
    authService.getCurrentUser.mockResolvedValue({
      authenticated: true,
      user: { id: 3, username: 'pharma_verified', role: 'PHARMACIST' },
    });

    portalService.getPharmacistPharmacy.mockResolvedValue({
      id: 11,
      name: 'Demo CarePoint Pharmacy',
      license_number: 'DL-KA-2024-00129',
      area: 'Indiranagar',
      city: 'Bengaluru',
      pin_code: '560038',
      verification_status: 'VERIFIED',
    });

    portalService.getPharmacistInventory.mockResolvedValue({
      pharmacy_status: 'VERIFIED',
      is_verified: true,
      inventory: [
        {
          id: 101,
          quantity: 45,
          price: '28.50',
          availability_status: 'AVAILABLE',
          availability_label: 'Available',
          medicine_details: {
            id: 1,
            generic_name: 'Paracetamol',
            brand_name: 'Crocin',
            strength: '500mg',
            dosage_form: 'Tablet',
            pack_size: 'Strip of 10',
          },
        },
      ],
    });

    render(
      <RouterProvider initialPath="/pharmacist/dashboard">
        <AuthProvider>
          <PharmacistDashboardPage />
        </AuthProvider>
      </RouterProvider>
    );

    expect(await screen.findByText(/ACTIVE ESTABLISHMENT/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Add Medicine Stock/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Export CSV/i })).toBeInTheDocument();
    expect(screen.getByText(/Paracetamol/i)).toBeInTheDocument();
    expect(screen.getByText(/Crocin/i)).toBeInTheDocument();
    expect(screen.getByText(/₹28.50/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Available/i).length).toBeGreaterThanOrEqual(1);
  });

  // ---------------------------------------------------------------------------
  // 4. Admin Portal: Metrics & Verification Queue
  // ---------------------------------------------------------------------------

  it('9. Renders platform metrics and pending pharmacy verifications in Admin Portal', async () => {
    authService.getCurrentUser.mockResolvedValue({
      authenticated: true,
      user: { id: 99, username: 'admin', role: 'ADMIN', is_admin: true },
    });

    portalService.getAdminOverview.mockResolvedValue({
      total_users: 12,
      total_pharmacists: 4,
      pending_pharmacies: 1,
      verified_pharmacies: 3,
      total_medicines: 10,
      total_inventories: 15,
    });

    portalService.getAdminPharmacies.mockResolvedValue([
      {
        id: 201,
        name: 'New City Meds',
        license_number: 'DL-PENDING-001',
        area: 'Koramangala',
        city: 'Bengaluru',
        pin_code: '560095',
        owner_username: 'new_pharma',
        verification_status: 'PENDING',
      },
    ]);

    render(
      <RouterProvider initialPath="/admin/dashboard">
        <AuthProvider>
          <AdminDashboardPage />
        </AuthProvider>
      </RouterProvider>
    );

    expect(await screen.findByRole('heading', { name: /Platform Administration/i })).toBeInTheDocument();
    expect(screen.getByText(/ADMIN CONSOLE/i)).toBeInTheDocument();

    // Metric counts
    expect(screen.getByText('12')).toBeInTheDocument(); // total users

    // Pending verification table row
    expect(screen.getByText(/New City Meds/i)).toBeInTheDocument();
    expect(screen.getByText(/DL-PENDING-001/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^Approve$/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^Reject$/i })).toBeInTheDocument();
  });

  // ---------------------------------------------------------------------------
  // 5. Patient Portal (/app)
  // ---------------------------------------------------------------------------

  it('10. Renders Patient Portal with personalized welcome and MediBot access', async () => {
    authService.getCurrentUser.mockResolvedValue({
      authenticated: true,
      user: { id: 15, username: 'priya_patel', first_name: 'Priya', role: 'USER' },
    });

    render(
      <RouterProvider initialPath="/app">
        <AuthProvider>
          <UserPortalPage />
        </AuthProvider>
      </RouterProvider>
    );

    expect(await screen.findByRole('heading', { name: /Welcome back, Priya/i })).toBeInTheDocument();
    expect(screen.getByText(/Patient Portal/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Ask MediBot/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Search Medicine/i })).toBeInTheDocument();
  });
});

/**
 * Portal service for Pharmacist and Admin operations.
 * Communicates with role-guarded backend APIs.
 */

import { apiRequest } from './apiClient';

export const portalService = {
  // ---------------------------------------------------------------------------
  // Pharmacist Portal APIs
  // ---------------------------------------------------------------------------

  async getPharmacistPharmacy() {
    return await apiRequest('/api/v1/pharmacist/pharmacy/');
  },

  async createPharmacistPharmacy(data) {
    return await apiRequest('/api/v1/pharmacist/pharmacy/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updatePharmacistPharmacy(data) {
    return await apiRequest('/api/v1/pharmacist/pharmacy/', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async getPharmacistInventory() {
    return await apiRequest('/api/v1/pharmacist/inventory/');
  },

  async addPharmacistInventory(data) {
    return await apiRequest('/api/v1/pharmacist/inventory/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async bulkImportPharmacistInventory(items) {
    return await apiRequest('/api/v1/pharmacist/inventory/bulk/', {
      method: 'POST',
      body: JSON.stringify({ items }),
    });
  },

  async updatePharmacistInventory(id, data) {
    return await apiRequest(`/api/v1/pharmacist/inventory/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deletePharmacistInventory(id) {
    return await apiRequest(`/api/v1/pharmacist/inventory/${id}/`, {
      method: 'DELETE',
    });
  },

  async getPharmacistMedicineCatalog(query = '') {
    const qParam = query ? `?q=${encodeURIComponent(query)}` : '';
    return await apiRequest(`/api/v1/pharmacist/medicines/${qParam}`);
  },

  // ---------------------------------------------------------------------------
  // Admin Portal APIs
  // ---------------------------------------------------------------------------

  async getAdminOverview() {
    return await apiRequest('/api/v1/admin/overview/');
  },

  async getAdminPharmacies(statusFilter = '') {
    const sParam = statusFilter ? `?status=${encodeURIComponent(statusFilter)}` : '';
    return await apiRequest(`/api/v1/admin/pharmacies/${sParam}`);
  },

  async verifyAdminPharmacy(pharmacyId, action, reason = '') {
    return await apiRequest(`/api/v1/admin/pharmacies/${pharmacyId}/verify/`, {
      method: 'POST',
      body: JSON.stringify({ action, reason }),
    });
  },

  async getAdminMedicines(query = '') {
    const qParam = query ? `?q=${encodeURIComponent(query)}` : '';
    return await apiRequest(`/api/v1/admin/medicines/${qParam}`);
  },

  async createAdminMedicine(data) {
    return await apiRequest('/api/v1/admin/medicines/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateAdminMedicine(id, data) {
    return await apiRequest(`/api/v1/admin/medicines/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteAdminMedicine(id) {
    return await apiRequest(`/api/v1/admin/medicines/${id}/`, {
      method: 'DELETE',
    });
  },

  async getAdminUsers() {
    return await apiRequest('/api/v1/admin/users/');
  },

  async getAdminAuditLogs() {
    return await apiRequest('/api/v1/admin/audit/');
  },
};

/**
 * Medicine and pharmacy search service.
 * Connects frontend UI to Django REST Framework backend endpoints:
 * - GET /api/v1/search/medicines/
 * - GET /api/v1/search/pharmacies/
 */

import { apiRequest } from './apiClient';

/**
 * Search medicine catalog and retrieve verified pharmacy availability.
 * @param {string} query - Medicine or generic search query
 * @param {object} [options]
 * @param {number} [options.lat] - Optional user latitude
 * @param {number} [options.lon] - Optional user longitude
 * @param {number} [options.radius=50] - Search radius in km
 * @param {number} [options.limit=10] - Max results
 * @returns {Promise<object>}
 */
export async function searchMedicines(query, options = {}) {
  const params = new URLSearchParams();
  params.append('query', query.trim());

  if (options.lat != null && options.lon != null) {
    params.append('lat', String(options.lat));
    params.append('lon', String(options.lon));
  }
  if (options.radius != null) {
    params.append('radius', String(options.radius));
  }
  if (options.limit != null) {
    params.append('limit', String(options.limit));
  }

  return apiRequest(`/api/v1/search/medicines/?${params.toString()}`);
}

/**
 * Query pharmacies stocking a specific medicine.
 * @param {number|string} medicineId
 * @param {object} [options]
 * @returns {Promise<object>}
 */
export async function getPharmaciesForMedicine(medicineId, options = {}) {
  const params = new URLSearchParams();
  params.append('medicine_id', String(medicineId));

  if (options.lat != null && options.lon != null) {
    params.append('lat', String(options.lat));
    params.append('lon', String(options.lon));
  }
  if (options.query) {
    params.append('query', options.query.trim());
  }

  return apiRequest(`/api/v1/search/pharmacies/?${params.toString()}`);
}

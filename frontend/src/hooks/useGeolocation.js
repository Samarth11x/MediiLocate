/**
 * Custom React hook for privacy-preserving user geolocation.
 *
 * Privacy Guarantees:
 * - NEVER requests location automatically on mount or page load.
 * - Only activates when user explicitly invokes `requestLocation()`.
 * - Handles browser permission denial without crashing or breaking search.
 * - Does not persist coordinate data to local storage or external databases.
 */

import { useState, useCallback } from 'react';

export function useGeolocation() {
  const [coords, setCoords] = useState(null); // { lat, lon } | null
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [permissionDenied, setPermissionDenied] = useState(false);

  const requestLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser.');
      return;
    }

    setLoading(true);
    setError(null);
    setPermissionDenied(false);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoords({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        });
        setLoading(false);
        setError(null);
      },
      (geoError) => {
        setLoading(false);
        if (geoError.code === geoError.PERMISSION_DENIED) {
          setPermissionDenied(true);
          setError('Location permission was denied. You can still search medicines without proximity ranking.');
        } else if (geoError.code === geoError.POSITION_UNAVAILABLE) {
          setError('Location information is currently unavailable from your device.');
        } else if (geoError.code === geoError.TIMEOUT) {
          setError('Location request timed out. Please try again.');
        } else {
          setError('An unknown error occurred while requesting your location.');
        }
      },
      {
        enableHighAccuracy: false, // Standard accuracy is sufficient for city pharmacy search
        timeout: 10000,
        maximumAge: 60000,
      }
    );
  }, []);

  const clearLocation = useCallback(() => {
    setCoords(null);
    setError(null);
    setPermissionDenied(false);
  }, []);

  return {
    coords,
    loading,
    error,
    permissionDenied,
    requestLocation,
    clearLocation,
  };
}

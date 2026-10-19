import React from 'react';
import { decodeHtmlEntities } from '../../utils/textUtils';

/**
 * PharmacyCard
 * Renders verified pharmacy establishment with real inventory data,
 * Core Intelligence stock status, distance (if location provided), and pricing.
 */
export default function PharmacyCard({ pharmacyItem }) {
  if (!pharmacyItem) return null;

  const rawPharmacy = pharmacyItem.pharmacy || {};
  const rawMedicine = pharmacyItem.medicine || {};

  const pharmacy = {
    ...rawPharmacy,
    name: decodeHtmlEntities(rawPharmacy.name || ''),
    address: decodeHtmlEntities(rawPharmacy.address || ''),
    area: decodeHtmlEntities(rawPharmacy.area || ''),
    city: decodeHtmlEntities(rawPharmacy.city || ''),
  };

  const medicine = {
    ...rawMedicine,
    brand_name: decodeHtmlEntities(rawMedicine.brand_name || ''),
    generic_name: decodeHtmlEntities(rawMedicine.generic_name || ''),
    strength: decodeHtmlEntities(rawMedicine.strength || ''),
  };

  const {
    quantity,
    price,
    distance_km,
    ranking_score,
    ranking_explanation,
    is_demo,
  } = pharmacyItem;

  const stockStatus = (pharmacyItem.stock_status || pharmacyItem.stock_state || 'UNKNOWN').toUpperCase();

  // Determine stock badge CSS modifier
  const getStatusClass = (status) => {
    switch (status) {
      case 'AVAILABLE':
        return 'stock-badge--available';
      case 'LOW_STOCK':
        return 'stock-badge--low';
      case 'OUT_OF_STOCK':
        return 'stock-badge--out';
      case 'UNKNOWN':
      default:
        return 'stock-badge--unknown';
    }
  };

  const getStatusLabel = () => {
    if (pharmacyItem.stock_label) return pharmacyItem.stock_label;
    switch (stockStatus) {
      case 'AVAILABLE':
        return 'In Stock';
      case 'LOW_STOCK':
        return 'Low Stock';
      case 'OUT_OF_STOCK':
        return 'Out of Stock';
      case 'UNKNOWN':
      default:
        return 'Stock Unknown';
    }
  };

  const stockLabel = getStatusLabel();

  return (
    <article
      className="pharmacy-card"
      aria-label={`${pharmacy.name} - ${stockLabel}`}
    >
      <div className="pharmacy-card__header">
        <div className="pharmacy-card__title-area">
          <div className="pharmacy-card__badges">
            {is_demo && (
              <span className="demo-chip" title="Fictional development demonstration example">
                Demo Pharmacy
              </span>
            )}
            <span className="verified-chip" title="Licensed pharmacy verified by MediLocate">
              ✓ Verified Store
            </span>
          </div>
          <h3 className="pharmacy-card__name">{pharmacy.name}</h3>
          <p className="pharmacy-card__address">
            {pharmacy.area ? `${pharmacy.area}, ` : ''}{pharmacy.city || ''}
            {pharmacy.pin_code ? ` - ${pharmacy.pin_code}` : ''}
          </p>
        </div>

        {/* Stock Status Badge */}
        <div className="pharmacy-card__status-col">
          <span className={`stock-badge ${getStatusClass(stockStatus)}`}>
            {stockLabel}
          </span>
          {quantity != null ? (
            <span className="pharmacy-card__quantity">
              {quantity > 0 ? `${quantity} in stock` : '0 available'}
            </span>
          ) : (
            <span className="pharmacy-card__quantity pharmacy-card__quantity--unreported">
              Stock unconfirmed
            </span>
          )}
        </div>
      </div>

      {/* Pharmacy Details Grid */}
      <div className="pharmacy-card__details">
        {distance_km != null && (
          <div className="pharmacy-card__detail-item">
            <span className="pharmacy-card__detail-label">Distance</span>
            <span className="pharmacy-card__detail-value">
              📍 {typeof distance_km === 'number' ? distance_km.toFixed(1) : distance_km} km away
            </span>
          </div>
        )}

        {price != null ? (
          <div className="pharmacy-card__detail-item">
            <span className="pharmacy-card__detail-label">Unit Price</span>
            <span className="pharmacy-card__detail-value pharmacy-card__detail-value--price">
              ₹{price}
            </span>
          </div>
        ) : (
          <div className="pharmacy-card__detail-item">
            <span className="pharmacy-card__detail-label">Price</span>
            <span className="pharmacy-card__detail-value">Not Listed</span>
          </div>
        )}

        {pharmacy.contact_number && (
          <div className="pharmacy-card__detail-item">
            <span className="pharmacy-card__detail-label">Phone</span>
            <span className="pharmacy-card__detail-value">{pharmacy.contact_number}</span>
          </div>
        )}
      </div>

      {/* Medicine Confirmation & Ranking Explanation */}
      <div className="pharmacy-card__footer">
        {medicine?.name && (
          <span className="pharmacy-card__medicine-tag">
            Matched: {medicine.brand_name ? `${medicine.brand_name} (${medicine.generic_name})` : medicine.generic_name} {medicine.strength || ''}
          </span>
        )}
        {ranking_explanation && (
          <p className="pharmacy-card__ranking-info" title="Core Intelligence ranking score">
            <span className="sr-only">Ranking insight: </span>
            {ranking_explanation}
          </p>
        )}
      </div>
    </article>
  );
}

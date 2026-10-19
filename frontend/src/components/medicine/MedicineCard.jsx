import React from 'react';
import { decodeHtmlEntities } from '../../utils/textUtils';

/**
 * MedicineCard
 * Displays individual matched medicine catalog details with strength safeguards and form.
 */
export default function MedicineCard({ medicine, isSelected = false, onSelect = null }) {
  if (!medicine) return null;

  const rawGeneric = medicine.generic_name || '';
  const rawBrand = medicine.brand_name || '';
  const rawStrength = medicine.strength || '';
  const rawForm = medicine.dosage_form || '';
  const rawPack = medicine.pack_size || '';

  const generic_name = decodeHtmlEntities(rawGeneric);
  const brand_name = decodeHtmlEntities(rawBrand);
  const strength = decodeHtmlEntities(rawStrength);
  const dosage_form = decodeHtmlEntities(rawForm);
  const pack_size = decodeHtmlEntities(rawPack);
  const { match_score, match_type, explanation } = medicine;

  return (
    <article
      className={`medicine-card ${isSelected ? 'medicine-card--selected' : ''}`}
      tabIndex={onSelect ? 0 : undefined}
      role={onSelect ? 'button' : 'article'}
      onClick={onSelect ? () => onSelect(medicine) : undefined}
      onKeyDown={
        onSelect
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onSelect(medicine);
              }
            }
          : undefined
      }
      aria-label={`${brand_name ? `${brand_name} (` : ''}${generic_name}${brand_name ? ')' : ''} ${strength} ${dosage_form}`}
    >
      <div className="medicine-card__header">
        <div>
          {brand_name && <span className="medicine-card__brand">{brand_name}</span>}
          <h3 className="medicine-card__generic">{generic_name}</h3>
        </div>
        {match_score != null && (
          <span
            className={`medicine-card__badge ${match_score >= 1.0 ? 'medicine-card__badge--exact' : 'medicine-card__badge--match'}`}
            title={explanation || undefined}
          >
            {match_score >= 1.0 ? 'Exact Match' : `${Math.round(match_score * 100)}% Match`}
          </span>
        )}
      </div>

      <div className="medicine-card__specs">
        <span className="medicine-card__tag medicine-card__tag--strength">
          <strong>Strength:</strong> {strength}
        </span>
        <span className="medicine-card__tag medicine-card__tag--form">
          <strong>Form:</strong> {dosage_form}
        </span>
        {pack_size && (
          <span className="medicine-card__tag">
            <strong>Packaging:</strong> {pack_size}
          </span>
        )}
      </div>

      {explanation && (
        <p className="medicine-card__explanation" title={match_type}>
          {explanation}
        </p>
      )}
    </article>
  );
}

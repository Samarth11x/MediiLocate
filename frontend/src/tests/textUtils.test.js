import { describe, it, expect } from 'vitest';
import { decodeHtmlEntities } from '../utils/textUtils';

describe('textUtils - decodeHtmlEntities', () => {
  it('decodes hex entities like &#x35; and &#x31;', () => {
    expect(decodeHtmlEntities('Crocin (Paracetamol) &#x35;00mg Tablet')).toBe('Crocin (Paracetamol) 500mg Tablet');
    expect(decodeHtmlEntities('Cetzine (Cetirizine Hydrochloride) &#x31;0mg Tablet')).toBe('Cetzine (Cetirizine Hydrochloride) 10mg Tablet');
    expect(decodeHtmlEntities('&#x35;00 mg')).toBe('500 mg');
    expect(decodeHtmlEntities('&#x31;0 mg')).toBe('10 mg');
  });

  it('decodes decimal entities like &#53; and &#49;', () => {
    expect(decodeHtmlEntities('Paracetamol &#53;00mg')).toBe('Paracetamol 500mg');
    expect(decodeHtmlEntities('Cetirizine &#49;0mg')).toBe('Cetirizine 10mg');
  });

  it('decodes standard named HTML entities without DOM injection', () => {
    expect(decodeHtmlEntities('Amoxicillin &amp; Clavulanate')).toBe('Amoxicillin & Clavulanate');
    expect(decodeHtmlEntities('&quot;Dolo 650&quot;')).toBe('"Dolo 650"');
    expect(decodeHtmlEntities('Brand&#39;s Formulation')).toBe("Brand's Formulation");
    expect(decodeHtmlEntities('Item &lt;1&gt;')).toBe('Item <1>');
  });

  it('handles null, undefined, empty, and numeric non-string values safely', () => {
    expect(decodeHtmlEntities(null)).toBe('');
    expect(decodeHtmlEntities(undefined)).toBe('');
    expect(decodeHtmlEntities('')).toBe('');
    expect(decodeHtmlEntities(500)).toBe('500');
  });
});

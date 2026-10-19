/**
 * Pure JavaScript utility for safely decoding HTML and numeric entities (decimal and hex)
 * without DOM manipulation, eval(), or dangerous innerHTML injection.
 *
 * Examples:
 * - decodeHtmlEntities("Crocin (Paracetamol) &#x35;00mg Tablet") -> "Crocin (Paracetamol) 500mg Tablet"
 * - decodeHtmlEntities("Cetzine (Cetirizine Hydrochloride) &#x31;0mg Tablet") -> "Cetzine (Cetirizine Hydrochloride) 10mg Tablet"
 * - decodeHtmlEntities("Amoxicillin &amp; Clavulanate") -> "Amoxicillin & Clavulanate"
 */

const NAMED_ENTITIES = {
  '&amp;': '&',
  '&lt;': '<',
  '&gt;': '>',
  '&quot;': '"',
  '&#39;': "'",
  '&apos;': "'",
  '&nbsp;': ' ',
};

export function decodeHtmlEntities(text) {
  if (text == null || typeof text !== 'string') {
    return text == null ? '' : String(text);
  }

  return text
    // 1. Standard named entities
    .replace(/&(amp|lt|gt|quot|apos|nbsp);/gi, (match) => NAMED_ENTITIES[match.toLowerCase()] || match)
    // 2. Hexadecimal entities (e.g. &#x35; -> 5, &#x31; -> 1)
    .replace(/&#x([0-9a-fA-F]+);/gi, (match, hex) => {
      const code = parseInt(hex, 16);
      return !isNaN(code) && code > 0 ? String.fromCharCode(code) : match;
    })
    // 3. Decimal entities (e.g. &#53; -> 5, &#49; -> 1)
    .replace(/&#([0-9]+);/g, (match, dec) => {
      const code = parseInt(dec, 10);
      return !isNaN(code) && code > 0 ? String.fromCharCode(code) : match;
    });
}

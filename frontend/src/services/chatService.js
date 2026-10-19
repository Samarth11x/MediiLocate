/**
 * MediBot conversational assistant service.
 * Connects frontend chat drawer to Django backend endpoint:
 * - POST /api/v1/chat/
 */

import { apiRequest } from './apiClient';

/**
 * Send a chat message to MediBot.
 * @param {string} message - User query text (1-500 chars)
 * @param {object} [context] - Optional conversation context tokens
 * @returns {Promise<object>}
 */
export async function sendChatMessage(message, context = null) {
  const payload = {
    message: String(message).trim(),
  };

  if (context && typeof context === 'object') {
    payload.context = context;
  }

  return apiRequest('/api/v1/chat/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

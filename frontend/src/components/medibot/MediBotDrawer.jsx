import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../../services/chatService';
import { decodeHtmlEntities } from '../../utils/textUtils';

/**
 * MediBotDrawer
 * Cohesive conversational assistant widget connected to POST /api/v1/chat/.
 *
 * Features:
 * - Floating trigger with unread / open toggle
 * - Stateful conversation feed with user & bot messages
 * - Interactive suggestion chips
 * - Direct medicine result card rendering
 * - Preserves stateless multi-turn context
 * - Prominent emergency guidance and medical advice disclaimers
 * - Clear fictional demonstration notice
 */
export default function MediBotDrawer({
  isOpen: externalIsOpen,
  onOpenChange: onExternalOpenChange,
} = {}) {
  const [internalIsOpen, setInternalIsOpen] = useState(false);
  const isControlled = externalIsOpen !== undefined;
  const isOpen = isControlled ? externalIsOpen : internalIsOpen;

  const setIsOpen = (nextState) => {
    const resolvedState = typeof nextState === 'function' ? nextState(isOpen) : nextState;
    if (isControlled) {
      if (onExternalOpenChange) {
        onExternalOpenChange(resolvedState);
      }
    } else {
      setInternalIsOpen(resolvedState);
    }
  };
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationContext, setConversationContext] = useState({});
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      text: 'Hello! I am MediBot, your medicine discovery assistant. I can help you search for medicines, explain stock availability, and answer questions about the MediLocate platform.',
      suggestions: [
        'Find Paracetamol 500mg',
        'What does low stock mean?',
        'How does MediLocate work?',
      ],
      results: [],
      safetyCategory: null,
    },
  ]);

  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (isOpen && typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSendMessage = async (textToSend = null) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isLoading) return;

    const userMessageId = `user-${Date.now()}`;
    const newMessages = [
      ...messages,
      {
        id: userMessageId,
        sender: 'user',
        text,
      },
    ];

    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(text, conversationContext);

      // Preserve context returned by API
      if (response?.context && typeof response.context === 'object') {
        setConversationContext(response.context);
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `bot-${Date.now()}`,
          sender: 'bot',
          text: response.message,
          suggestions: response.suggestions || [],
          results: response.results || [],
          status: response.status,
          safetyCategory: response.safety_category,
          demoNotice: response.demo_notice,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: 'bot',
          text: 'I am currently unable to connect to the MediBot assistant service. Please check that the local backend server is running.',
          suggestions: ['Try again', 'Find Paracetamol 500mg'],
          results: [],
          status: 'error',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <aside
      className={`medibot-widget ${isOpen ? 'medibot-widget--open' : ''}`}
      aria-label="MediBot Assistant"
    >
      {/* 1. Floating Launch Button */}
      {!isOpen && (
        <button
          type="button"
          className="medibot-launcher"
          onClick={() => setIsOpen(true)}
          aria-expanded="false"
          aria-label="Open MediBot conversational assistant"
        >
          <span className="medibot-launcher__icon" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </span>
          <span className="medibot-launcher__text">Ask MediBot</span>
        </button>
      )}

      {/* 2. Chat Drawer Panel */}
      {isOpen && (
        <div
          className="medibot-drawer"
          role="dialog"
          aria-label="MediBot Chat Session"
          aria-modal="false"
        >
          {/* Header */}
          <div className="medibot-drawer__header">
            <div className="medibot-drawer__branding">
              <span className="medibot-drawer__avatar" aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="10" rx="2" />
                  <circle cx="12" cy="5" r="2" />
                  <path d="M12 7v4" />
                  <line x1="8" y1="16" x2="8.01" y2="16" />
                  <line x1="16" y1="16" x2="16.01" y2="16" />
                </svg>
              </span>
              <div>
                <h3 className="medibot-drawer__title">MediBot Assistant</h3>
                <span className="medibot-drawer__subtitle">Medical Safety & Discovery Engine</span>
              </div>
            </div>
            <button
              type="button"
              className="medibot-drawer__close"
              onClick={() => setIsOpen(false)}
              aria-label="Close MediBot chat"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>

          {/* Safety Disclaimer Banner */}
          <div className="medibot-drawer__disclaimer" role="note">
            <span>
              <strong>Informational only:</strong> MediBot does not diagnose conditions or prescribe medications. In an emergency, dial 112 / 108 / 911.
            </span>
          </div>

          {/* Messages Feed */}
          <div className="medibot-drawer__feed" tabIndex={0} aria-live="polite">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-bubble chat-bubble--${msg.sender} ${
                  msg.safetyCategory === 'emergency_concern'
                    ? 'chat-bubble--emergency'
                    : msg.safetyCategory === 'medical_advice'
                    ? 'chat-bubble--advice'
                    : ''
                }`}
              >
                {/* Emergency Indicator */}
                {msg.safetyCategory === 'emergency_concern' && (
                  <div className="chat-bubble__emergency-tag">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '6px', verticalAlign: '-2px' }}>
                      <polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2" />
                      <line x1="12" y1="8" x2="12" y2="12" />
                      <line x1="12" y1="16" x2="12.01" y2="16" />
                    </svg>
                    ACUTE MEDICAL EMERGENCY NOTICE
                  </div>
                )}

                {/* Message Body */}
                <div className="chat-bubble__content" style={{ whiteSpace: 'pre-line' }}>
                  {decodeHtmlEntities(msg.text)}
                </div>

                {/* Structured Results (Medicines or Pharmacies) */}
                {msg.results && msg.results.length > 0 && (
                  <div className="chat-bubble__results">
                    {msg.results[0]?.pharmacy || msg.results[0]?.stock_status ? (
                      <>
                        <span className="chat-bubble__results-title">Verified Pharmacies:</span>
                        {msg.results.map((item, idx) => {
                          const p = item.pharmacy || item;
                          const status = (item.stock_status || item.stock_state || 'UNKNOWN').toUpperCase();
                          const badgeClass =
                            status === 'AVAILABLE'
                              ? 'stock-badge--available'
                              : status === 'LOW_STOCK'
                              ? 'stock-badge--low'
                              : status === 'OUT_OF_STOCK'
                              ? 'stock-badge--out'
                              : 'stock-badge--unknown';
                          const label = item.stock_status_label || item.stock_label || status;

                          return (
                            <div key={item.id || p.id || idx} className="chat-mini-card chat-mini-card--pharmacy">
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
                                <span className="chat-mini-card__name">{decodeHtmlEntities(p.name)}</span>
                                <span className={`stock-badge ${badgeClass}`} style={{ fontSize: '0.625rem', padding: '2px 6px' }}>
                                  <span className="stock-badge__dot" aria-hidden="true" />
                                  {label}
                                </span>
                              </div>
                              <span className="chat-mini-card__specs">
                                {p.area ? `${decodeHtmlEntities(p.area)}, ` : ''}{decodeHtmlEntities(p.city || '')}
                              </span>
                              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '0.6875rem' }}>
                                {item.price != null && (
                                  <span style={{ fontWeight: 600, color: 'var(--color-teal-green)' }}>
                                    ₹{typeof item.price === 'number' ? item.price.toFixed(2) : item.price}
                                  </span>
                                )}
                                {item.distance_km != null && (
                                  <span style={{ color: 'var(--color-text-muted)', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                      <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" />
                                      <circle cx="12" cy="10" r="3" />
                                    </svg>
                                    {typeof item.distance_km === 'number' ? item.distance_km.toFixed(1) : item.distance_km} km
                                  </span>
                                )}
                                {item.quantity != null && (
                                  <span style={{ color: 'var(--color-text-muted)' }}>
                                    {item.quantity > 0 ? `${item.quantity} in stock` : '0 available'}
                                  </span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </>
                    ) : (
                      <>
                        <span className="chat-bubble__results-title">Found Medicines:</span>
                        {msg.results.map((item, idx) => {
                          const m = item.medicine || item;
                          return (
                            <div key={m.id || idx} className="chat-mini-card">
                              <span className="chat-mini-card__name">
                                {decodeHtmlEntities(m.brand_name ? `${m.brand_name} (${m.generic_name})` : m.generic_name)}
                              </span>
                              <span className="chat-mini-card__specs">
                                {decodeHtmlEntities(`${m.strength || ''} ${m.dosage_form || ''}`.trim())}
                              </span>
                            </div>
                          );
                        })}
                      </>
                    )}
                  </div>
                )}

                {/* Suggestion Chips */}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="chat-bubble__suggestions" role="group" aria-label="Quick reply suggestions">
                    {msg.suggestions.map((suggestion, sIdx) => (
                      <button
                        key={sIdx}
                        type="button"
                        className="suggestion-chip"
                        onClick={() => handleSendMessage(suggestion)}
                        disabled={isLoading}
                      >
                        {decodeHtmlEntities(suggestion)}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="chat-bubble chat-bubble--bot chat-bubble--thinking" role="status">
                <span className="thinking-dots">MediBot is looking up...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form
            className="medibot-drawer__form"
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
          >
            <input
              type="text"
              className="medibot-drawer__input"
              placeholder="Ask MediBot (e.g. Find Paracetamol 500mg)..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              disabled={isLoading}
              maxLength={500}
              aria-label="Type message for MediBot"
            />
            <button
              type="submit"
              className="medibot-drawer__send"
              disabled={isLoading || !inputMessage.trim()}
              aria-label="Send message"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </aside>
  );
}

# MediBot Conversational Intelligence & Medical Safety Architecture

## 1. Executive Summary & Purpose

**MediBot** is the specialized conversational assistant module for the **MediLocate AI** platform. It provides an intuitive, chat-driven interface helping patients and healthcare consumers locate verified medicines, understand inventory availability labels, find nearby registered pharmacies, and onboard retail chemist stores.

```
                      +-----------------------------+
                      |       User / Client         |
                      |   (Web / Mobile Frontend)   |
                      +--------------+--------------+
                                     |
                          POST /api/v1/chat/
                                     |
                      +--------------v--------------+
                      |  Django REST API Adapter    |
                      |  (Input Validation & Auth)  |
                      +--------------+--------------+
                                     |
               Injected Tools        |  Process Query & Context
          +------------------------->|
          |                          v
+---------+----------+   +--------------------------+
| Django ORM Models  |   |    Dialogue Manager      |
| (Medicine Catalog) |   |  (medibot.dialogue)      |
+--------------------+   +-------------+------------+
                                       |
                 1. Emergency Check    |
            +--------------------------+--------------------------+
            |                          |                          |
            v                          v                          v
+-----------------------+  +-----------------------+  +-----------------------+
|  Emergency Interceptor|  | Medical Advice Guard  |  |  Intent Classifier    |
| (Chest Pain, Stroke)  |  | (Dosage, Diagnosis)   |  | (Search, FAQ, Help)   |
+-----------+-----------+  +-----------+-----------+  +-----------+-----------+
            |                          |                          |
            | Emergency Guidance       | Clinical Redirection     |
            | (112 / 108 / 911)        | (Doctors / Pharmacists)  | Dispatches Tools
            +--------------------+     +-------------+            |
                                 |                   |            v
                                 |                   |   +--------------------+
                                 |                   |   | MedicineSearchTool |
                                 |                   |   | (Core Intelligence)|
                                 |                   |   +---------+----------+
                                 |                   |             |
                                 v                   v             v
                           +----------------------------------------------+
                           |   Structured JSON Response Contract          |
                           |   (message, intent, status, results, etc.)   |
                           +----------------------------------------------+
```

---

## 2. Architectural Boundaries & Decoupling Philosophy

MediBot adheres strictly to clean architectural separation:

1. **Independent Pure-Python Package (`medibot/`)**:
   - Zero imports from Django (`django.db`, `django.views`, `rest_framework`, etc.).
   - Zero direct SQL or PostgreSQL queries.
   - Zero dependencies on external paid APIs, cloud services, or closed proprietary AI keys.
2. **Reuses Core Intelligence (`core_intelligence/`)**:
   - Normalization algorithms (`normalize_text`, `normalize_query`, `normalize_strength`).
   - Pure-Python search and ranking algorithms (`search_medicines`).
   - Does not duplicate search, fuzzy matching, or distance calculation code.
3. **Core Intelligence Remains Pure**:
   - `core_intelligence/` never imports `medibot/`.
4. **Backend Inversion of Control (`backend/services/`)**:
   - The Django backend owns database access and instantiates `DjangoMedicineCatalogueProvider`.
   - Backend services inject the data provider into `MedicineSearchTool`, which is passed to `DialogueManager`.
5. **Stateless Privacy by Design**:
   - Conversations are not stored in any database table.
   - No chat transcripts, query strings, or medical inputs are logged or persisted.

---

## 3. Why MediBot is Rule-Based in Phase 5

In Phase 5, MediBot is intentionally implemented using deterministic, pattern-driven rule matching rather than an unrestricted Large Language Model (LLM):

1. **Patient Safety & Zero Hallucination Risk**:
   - In medicine discovery, hallucinating nonexistent strengths (e.g. 1000mg vs 500mg) or fabricating non-stocked pharmacies can lead to life-threatening clinical errors. Rule-based execution produces deterministic, verifiable outputs.
2. **Deterministic Medical Safety Interception**:
   - Immediate detection and interception of acute medical emergencies and clinical advice requests without latency, prompt injection vulnerability, or probabilistic non-determinism.
3. **Zero External API Cost & Offline Resilience**:
   - Functions 100% locally with zero cloud API keys, zero network latency, and complete developer autonomy.
4. **Future-Proof Modular Design**:
   - The system is architected so that an LLM provider (e.g. Google Gemini or local small models) can be introduced as an optional intent classifier or natural-language formatter behind `DialogueManager` without altering the API contract or bypassing the safety guardrails.

---

## 4. Medical Safety Philosophy & Guardrails

MediBot enforces a strict **Zero-Prescription / No-Medical-Advice** rule alongside **Immediate Acute Emergency Interception**.

### 4.1 Acute Medical Emergency Interceptor (`medibot.safety.emergency`)
- **Precedence**: Evaluated before any intent parsing, dialogue state, or tool lookup.
- **Trigger Symptoms**: Chest pain, acute breathing difficulty, shortness of breath, anaphylaxis, overdose, stroke signs (facial drooping, slurred speech, sudden paralysis), poisoning, suicidal thoughts, profuse bleeding.
- **Behavior**:
  - Immediately halts ordinary flow.
  - Returns `intent: "EMERGENCY_CONCERN"`, `status: "safety_response"`, `safety_category: "emergency_concern"`.
  - Prominently directs the user to regional emergency medical hotlines:
    - **112 / 108** (India National Emergency & Ambulance)
    - **911** (US / International standard)
    - Local hospital emergency room (Casualty).

### 4.2 Medical Advice & Prescribing Guardrail (`medibot.safety.safety_rules`)
- **Precedence**: Evaluated immediately after acute emergencies and before general intent classification.
- **Prohibited Inquiries**:
  - Treatment recommendations ("What medicine should I take for fever?").
  - Personalized or pediatric dosage instructions ("How much Paracetamol should I give my child?").
  - Drug interaction assessments ("Can I take Ibuprofen with Aspirin?").
  - Symptom diagnostics ("Diagnose my rash", "Why is my stomach hurting?").
  - Altering/stopping prescribed medications ("Should I stop taking blood pressure pills?").
- **Behavior**:
  - Returns `intent: "MEDICAL_ADVICE"`, `status: "safety_response"`, `safety_category: "medical_advice"`.
  - Informs the user that MediBot is an inventory discovery assistant, not a clinician.
  - Redirects the patient to consult licensed doctors or registered pharmacists.
  - Provides quick-reply suggestions for finding prescribed medications once authorized.

---

## 5. Supported Intent Taxonomy

MediBot classifies inputs into 8 deterministic intent categories:

| Intent Identifier | Description | Examples |
|---|---|---|
| `EMERGENCY_CONCERN` | Life-threatening acute medical symptoms | *"Chest pain", "Cannot breathe", "Overdose"* |
| `MEDICAL_ADVICE` | Clinical advice, prescribing, dosage questions | *"What should I take for fever?", "Safe dose"* |
| `GREETING` | Friendly conversation starter | *"Hello", "Hi MediBot", "Good morning"* |
| `HOW_IT_WORKS` | Explanation of MediLocate platform | *"How does MediLocate work?", "What is this app?"* |
| `PHARMACY_ONBOARDING` | Guidance for chemists to register stores | *"How can my pharmacy join?", "Partner with MediLocate"* |
| `AVAILABILITY_HELP` | Clarification of inventory badges | *"What does low stock mean?", "Explain stock status"* |
| `PHARMACY_SEARCH` | Store location inquiries (Phase 6 preview) | *"Find pharmacies near me", "Nearby chemist"* |
| `MEDICINE_SEARCH` | Explicit medicine formulary lookup | *"Find Paracetamol 500mg", "Crocin tablets"* |
| `UNKNOWN` | Fallback for unclassified inquiries | *"Tell me a joke", "What is the capital of France"* |

---

## 6. Response Payload Contract

Every response generated by MediBot conforms to the `MediBotResponse` schema:

```json
{
  "message": "Found 1 matching medicine(s) for 'Paracetamol 500mg'.",
  "intent": "MEDICINE_SEARCH",
  "status": "success",
  "suggestions": [
    "Check nearby pharmacies",
    "Search another medicine",
    "How does MediLocate work?"
  ],
  "results": [
    {
      "medicine": {
        "id": 1,
        "generic_name": "Paracetamol",
        "brand_name": "Crocin",
        "strength": "500mg",
        "dosage_form": "Tablet",
        "pack_size": "Strip of 10",
        "search_aliases": ["pcm", "fever tablet"]
      },
      "match_score": 1.0,
      "match_type": "exact_name",
      "matched_fields": ["generic_name"],
      "explanation": "Exact match on generic name 'Paracetamol'"
    }
  ],
  "demo_notice": true,
  "safety_category": null,
  "context": {
    "last_intent": "MEDICINE_SEARCH",
    "searched_medicine": "Paracetamol 500mg"
  }
}
```

### Status Codes
- `success`: Intent recognized and successfully handled or tool returned results.
- `needs_clarification`: User expressed a search intent but did not specify the medicine name; multi-turn prompt awaiting follow-up.
- `no_results`: Medicine searched but zero matches found in formulary.
- `unavailable`: External dependency or provider is disconnected or unpopulated.
- `safety_response`: Medical advice or emergency interceptor triggered.
- `error`: Malformed request, invalid types, or input length exceeded.

---

## 7. Multi-Turn Conversation Handling

MediBot supports lightweight, stateless multi-turn dialogue using client-supplied context tokens:

1. **Step 1 — Clarification Trigger**:
   - User inputs: `"Find a medicine"`
   - Intent: `MEDICINE_SEARCH` (without entity).
   - MediBot responds: `"Which medicine are you looking for? Please provide the name or strength (e.g. 'Paracetamol 500mg')."`
   - Returns context: `{"step": "awaiting_medicine_name", "last_intent": "MEDICINE_SEARCH"}`.
2. **Step 2 — Client Continuation**:
   - Client sends follow-up with context:
     ```json
     {
       "message": "Amoxicillin 250mg",
       "context": {"step": "awaiting_medicine_name"}
     }
     ```
   - `DialogueManager` checks `context.step == "awaiting_medicine_name"`, clears the step, sets the query, and executes `MedicineSearchTool` without requiring re-parsing.

---

## 8. Backend API Adapter (`POST /api/v1/chat/`)

### Request Specification
- **Method**: `POST`
- **URL**: `/api/v1/chat/`
- **Headers**: `Content-Type: application/json`
- **Payload Schema**:
  ```json
  {
    "message": "string (required, 1-500 characters)",
    "context": "object (optional, key-value dictionary)"
  }
  ```

### HTTP Validation Rules
- **HTTP 200 OK**: Valid message processed through DialogueManager.
- **HTTP 400 Bad Request**:
  - Missing `message` field.
  - Non-string or whitespace-only `message`.
  - `message` length $> 500$ characters.
  - `context` is present but not a JSON object.
- **HTTP 405 Method Not Allowed**: Calling `GET`, `PUT`, `DELETE`, or `PATCH`.
- **HTTP 500 Internal Server Error**: Safe, opaque fallback error without leaking system paths or Python tracebacks.

---

## 9. Future LLM Provider Integration Path

MediBot's decoupled design allows straightforward integration of modern LLMs (e.g., Google Gemini Flash or local Ollama models) without breaking clients or compromising safety:

```
                    User Message
                         |
           +-------------v-------------+
           | Acute Emergency Guardrail | (Deterministic Python Regex)
           +-------------+-------------+
                         |
           +-------------v-------------+
           | Medical Advice Guardrail  | (Deterministic Python Regex)
           +-------------+-------------+
                         |
         +---------------v---------------+
         | Optional AI Provider / LLM    |
         | (NLU Intent & Entity Parser)  |
         +---------------+---------------+
                         |
          Deterministic Tools Execution
        (Core Intelligence Search & Rules)
                         |
         +---------------v---------------+
         | Optional AI Provider / LLM    |
         | (Natural Language Formatter)  |
         +---------------+---------------+
                         |
             Validated Response Schema
```

1. **Pre-LLM Safety Firewall**: Emergency and clinical advice checks execute *before* calling any external AI provider, eliminating prompt injection risks and reducing cloud API expenses.
2. **Strict Tool Execution**: The LLM never synthesizes medicines or inventory directly; it only extracts entities to pass into Core Intelligence search algorithms.
3. **Fallback Resiliency**: If the LLM provider experiences latency, network timeouts, or API quota exhaustion, MediBot automatically degrades gracefully to the rule-based classifier implemented in Phase 5.

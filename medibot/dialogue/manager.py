"""
MediBot Dialogue Manager.

Orchestrates input validation, medical safety checks, intent resolution,
and tool dispatching into structured MediBotResponse payloads.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from medibot.dialogue.context import ConversationContext, MediBotResponse
from medibot.dialogue.responses import (
    GREETING_MESSAGE,
    GREETING_SUGGESTIONS,
    HOW_IT_WORKS_MESSAGE,
    HOW_IT_WORKS_SUGGESTIONS,
    PHARMACY_ONBOARDING_MESSAGE,
    PHARMACY_ONBOARDING_SUGGESTIONS,
    AVAILABILITY_HELP_MESSAGE,
    AVAILABILITY_HELP_SUGGESTIONS,
    UNKNOWN_QUERY_MESSAGE,
    UNKNOWN_SUGGESTIONS,
    MEDICINE_CLARIFICATION_MESSAGE,
    MEDICINE_CLARIFICATION_SUGGESTIONS,
    format_medicine_search_response,
    format_pharmacy_search_response,
)
from medibot.intents.patterns import IntentType
from medibot.intents.classifier import classify_intent
from medibot.safety.input_validation import validate_input, MAX_MESSAGE_LENGTH
from medibot.safety.emergency import check_emergency
from medibot.safety.safety_rules import check_medical_advice
from medibot.tools.interfaces import (
    MedicineSearchToolProtocol,
    PharmacySearchToolProtocol,
)
from medibot.tools.medicine_search import MedicineSearchTool
from medibot.tools.pharmacy_search import PharmacySearchTool


class DialogueManager:
    """
    Stateful or stateless conversational dialogue manager for MediBot.

    Coordinates safety evaluations, intent parsing, and tool execution without
    coupling directly to database ORMs or external AI APIs.
    """

    def __init__(
        self,
        medicine_tool: Optional[MedicineSearchToolProtocol] = None,
        pharmacy_tool: Optional[PharmacySearchToolProtocol] = None,
        max_message_length: int = MAX_MESSAGE_LENGTH,
    ) -> None:
        self.medicine_tool = medicine_tool or MedicineSearchTool()
        self.pharmacy_tool = pharmacy_tool or PharmacySearchTool()
        self.max_message_length = max_message_length

    def process_message(
        self,
        user_message: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> MediBotResponse:
        """
        Process a user input message and generate a structured MediBot response.

        Flow:
        1. Validate input format and enforce length bounds.
        2. Evaluate urgent medical safety guardrails (emergency & medical advice).
        3. Match conversational or tool intents.
        4. Execute tool if applicable and format predictable response.

        Args:
            user_message: Raw client message.
            context: Optional client-provided state dictionary.

        Returns:
            MediBotResponse dataclass.
        """
        # Step 1: Input Validation
        is_valid, cleaned_message, validation_resp = validate_input(
            user_message,
            max_length=self.max_message_length,
        )
        if not is_valid:
            assert validation_resp is not None
            return validation_resp

        assert cleaned_message is not None
        conv_context = ConversationContext.from_dict(context)

        # Step 2: Safety Layer (Precedes ordinary dialogue & tools)
        emergency_resp = check_emergency(cleaned_message)
        if emergency_resp is not None:
            emergency_resp.context = conv_context.to_dict()
            return emergency_resp

        advice_resp = check_medical_advice(cleaned_message)
        if advice_resp is not None:
            advice_resp.context = conv_context.to_dict()
            return advice_resp

        # Step 3: Multi-turn Context Resolution
        # If previous step was awaiting a medicine name from user:
        if conv_context.step == "awaiting_medicine_name":
            conv_context.step = None
            conv_context.last_intent = IntentType.MEDICINE_SEARCH
            return self._handle_medicine_search(cleaned_message, conv_context)

        # Step 4: Intent Classification
        intent_result = classify_intent(cleaned_message)
        conv_context.last_intent = intent_result.intent

        # Step 5: Intent Handlers
        if intent_result.intent == IntentType.GREETING:
            return MediBotResponse(
                message=GREETING_MESSAGE,
                intent=IntentType.GREETING,
                status="success",
                suggestions=GREETING_SUGGESTIONS,
                context=conv_context.to_dict(),
            )

        if intent_result.intent == IntentType.HOW_IT_WORKS:
            return MediBotResponse(
                message=HOW_IT_WORKS_MESSAGE,
                intent=IntentType.HOW_IT_WORKS,
                status="success",
                suggestions=HOW_IT_WORKS_SUGGESTIONS,
                context=conv_context.to_dict(),
            )

        if intent_result.intent == IntentType.PHARMACY_ONBOARDING:
            return MediBotResponse(
                message=PHARMACY_ONBOARDING_MESSAGE,
                intent=IntentType.PHARMACY_ONBOARDING,
                status="success",
                suggestions=PHARMACY_ONBOARDING_SUGGESTIONS,
                context=conv_context.to_dict(),
            )

        if intent_result.intent == IntentType.AVAILABILITY_HELP:
            return MediBotResponse(
                message=AVAILABILITY_HELP_MESSAGE,
                intent=IntentType.AVAILABILITY_HELP,
                status="success",
                suggestions=AVAILABILITY_HELP_SUGGESTIONS,
                context=conv_context.to_dict(),
            )

        if intent_result.intent == IntentType.PHARMACY_SEARCH:
            # If user mentions a specific medicine inline, extract it
            if not conv_context.searched_medicine:
                import re
                med_match = re.search(
                    r"(?:for|stocking|with|having)\s+([a-zA-Z0-9\s]+)",
                    cleaned_message,
                    re.IGNORECASE,
                )
                if med_match:
                    candidate = med_match.group(1).strip()
                    if candidate.lower() not in {"me", "us", "you", "here", "my area", "the area"}:
                        conv_context.searched_medicine = candidate

            tool_res = self.pharmacy_tool.search_pharmacies(
                query=cleaned_message,
                medicine_name=conv_context.searched_medicine,
                medicine_id=conv_context.searched_medicine_id,
                lat=conv_context.user_lat,
                lon=conv_context.user_lon,
            )

            if tool_res.status == "success":
                has_loc = conv_context.user_lat is not None and conv_context.user_lon is not None
                formatted_text = format_pharmacy_search_response(
                    results=tool_res.data,
                    medicine_name=conv_context.searched_medicine,
                    has_location=has_loc,
                )
                return MediBotResponse(
                    message=formatted_text,
                    intent=IntentType.PHARMACY_SEARCH,
                    status="success",
                    results=tool_res.data,
                    suggestions=["Find another medicine", "What does low stock mean?", "How does MediLocate work?"],
                    context=conv_context.to_dict(),
                )

            if tool_res.status == "no_results":
                medicine_desc = f" for '{conv_context.searched_medicine}'" if conv_context.searched_medicine else ""
                return MediBotResponse(
                    message=(
                        f"No matching pharmacies found in the directory{medicine_desc} for the specified criteria. "
                        "You can try searching for a different medicine or checking back later as pharmacies update their inventories."
                    ),
                    intent=IntentType.PHARMACY_SEARCH,
                    status="no_results",
                    results=[],
                    suggestions=["Search for a medicine", "How does MediLocate work?"],
                    context=conv_context.to_dict(),
                )

            if tool_res.status == "unavailable":
                return MediBotResponse(
                    message=tool_res.message,
                    intent=IntentType.PHARMACY_SEARCH,
                    status="unavailable",
                    suggestions=["Search for a medicine", "How does MediLocate work?"],
                    context=conv_context.to_dict(),
                )

            return MediBotResponse(
                message=f"Pharmacy directory error: {tool_res.message}",
                intent=IntentType.PHARMACY_SEARCH,
                status="error",
                suggestions=["Search for a medicine", "How does MediLocate work?"],
                context=conv_context.to_dict(),
            )

        if intent_result.intent == IntentType.MEDICINE_SEARCH:
            # Did the user provide a specific entity, or generic "find a medicine"?
            if not intent_result.extracted_entity:
                conv_context.step = "awaiting_medicine_name"
                return MediBotResponse(
                    message=MEDICINE_CLARIFICATION_MESSAGE,
                    intent=IntentType.MEDICINE_SEARCH,
                    status="needs_clarification",
                    suggestions=MEDICINE_CLARIFICATION_SUGGESTIONS,
                    context=conv_context.to_dict(),
                )
            return self._handle_medicine_search(intent_result.extracted_entity, conv_context)

        # Fallback: UNKNOWN intent
        return MediBotResponse(
            message=UNKNOWN_QUERY_MESSAGE,
            intent=IntentType.UNKNOWN,
            status="needs_clarification",
            suggestions=UNKNOWN_SUGGESTIONS,
            context=conv_context.to_dict(),
        )

    def _handle_medicine_search(
        self,
        medicine_query: str,
        context: ConversationContext,
    ) -> MediBotResponse:
        """Helper to invoke the injected medicine tool and construct the response."""
        context.searched_medicine = medicine_query
        tool_res = self.medicine_tool.search(query=medicine_query)

        if tool_res.status == "success":
            # Extract medicine ID and canonical name from top match when available
            if tool_res.data and isinstance(tool_res.data, list) and len(tool_res.data) > 0:
                top_item = tool_res.data[0]
                med_info = (
                    top_item.get("medicine")
                    if isinstance(top_item, dict) and "medicine" in top_item
                    else top_item
                )
                if isinstance(med_info, dict):
                    if "id" in med_info:
                        context.searched_medicine_id = str(med_info["id"])
                    gen = med_info.get("generic_name") or ""
                    strn = med_info.get("strength") or ""
                    if gen and strn:
                        context.searched_medicine = f"{gen} {strn}".strip()
                    elif gen:
                        context.searched_medicine = gen

            message_text = format_medicine_search_response(medicine_query, tool_res.data)
            return MediBotResponse(
                message=message_text,
                intent=IntentType.MEDICINE_SEARCH,
                status="success",
                results=tool_res.data,
                suggestions=["Find nearby pharmacies", "Search another medicine"],
                context=context.to_dict(),
            )

        if tool_res.status == "no_results":
            return MediBotResponse(
                message=(
                    f"I couldn't find any medicines matching '{medicine_query}' in the catalogue. "
                    "Please check the spelling or try searching by generic chemical name (e.g., 'Paracetamol')."
                ),
                intent=IntentType.MEDICINE_SEARCH,
                status="no_results",
                suggestions=["Paracetamol 500mg", "Amoxicillin 500mg", "How does MediLocate work?"],
                context=context.to_dict(),
            )

        if tool_res.status == "unavailable":
            return MediBotResponse(
                message=tool_res.message,
                intent=IntentType.MEDICINE_SEARCH,
                status="unavailable",
                suggestions=["How does MediLocate work?", "What does low stock mean?"],
                context=context.to_dict(),
            )

        # Generic error fallback
        return MediBotResponse(
            message=f"Catalogue error: {tool_res.message}",
            intent=IntentType.MEDICINE_SEARCH,
            status="error",
            context=context.to_dict(),
        )

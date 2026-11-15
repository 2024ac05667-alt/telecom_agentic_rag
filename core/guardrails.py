"""
Guardrails Module for Multilingual Diagnostic Agent.
Handles PII Scrubbing using Microsoft Presidio and Custom Qatar QID / Mobile Regexes.
"""

import re
from typing import Any, Dict
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


class PIIGuardrail:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

        # Custom Recognizer for Qatar National ID (QID: 11 digits starting with 2 or 3)
        qid_pattern = Pattern(
            name="qatar_qid_pattern",
            regex=r"\b[23]\d{10}\b",
            score=0.95,
        )
        qid_recognizer = PatternRecognizer(
            supported_entity="QATAR_ID",
            patterns=[qid_pattern],
            context=["qid", "qatar id", "id number", "civil id", "national id", "بطاقة"],
        )

        # Custom Recognizer for Doha Connect Numbers (8 digits starting with 3, 5, 6, or 7)
        qa_phone_pattern = Pattern(
            name="dohaconnect_pattern",
            regex=r"(?:\+974\s?)?\b[3567]\d{7}\b",
            score=0.90,
        )
        qa_phone_recognizer = PatternRecognizer(
            supported_entity="PHONE_NUMBER",
            patterns=[qa_phone_pattern],
            context=["mobile", "phone", "number", "contact", "call", "whatsapp", "جوال", "هاتف"],
        )

        self.analyzer.registry.add_recognizer(qid_recognizer)
        self.analyzer.registry.add_recognizer(qa_phone_recognizer)

        self.target_entities = [
            "PHONE_NUMBER",
            "EMAIL_ADDRESS",
            "PERSON",
            "QATAR_ID",
            "CREDIT_CARD",
        ]

    def scrub_text(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "clean_text": "",
                "pii_detected": False,
                "detected_entities": [],
            }

        analysis_results = self.analyzer.analyze(
            text=text,
            entities=self.target_entities,
            language="en",
        )

        pii_found = len(analysis_results) > 0
        detected_types = sorted(list({res.entity_type for res in analysis_results}))

        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analysis_results,
            operators={
                "DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED_PII]"}),
                "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[REDACTED_PHONE]"}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[REDACTED_EMAIL]"}),
                "PERSON": OperatorConfig("replace", {"new_value": "[REDACTED_NAME]"}),
                "QATAR_ID": OperatorConfig("replace", {"new_value": "[REDACTED_QID]"}),
            },
        )

        # Secondary deterministic safeguard for QIDs/phones even if NLP context score is low
        clean_text = re.sub(r"\b[23]\d{10}\b", "[REDACTED_QID]", anonymized_result.text)
        clean_text = re.sub(r"(?:\+974\s?)?\b[3567]\d{7}\b", "[REDACTED_PHONE]", clean_text)

        if clean_text != text and not pii_found:
            pii_found = True
            detected_types.append("QATAR_IDENTIFIER")

        return {
            "clean_text": clean_text,
            "pii_detected": pii_found,
            "detected_entities": detected_types,
        }
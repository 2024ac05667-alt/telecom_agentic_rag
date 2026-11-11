"""
Guardrails Module for Multilingual Diagnostic Agent.
Handles PII Scrubbing using Microsoft Presidio and Custom QID Regex.
"""

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
            name="qid_pattern", regex=r"\b[23]\d{10}\b", score=0.95
        )

        qid_recognizer = PatternRecognizer(
            supported_entity="QATAR_ID",
            patterns=[qid_pattern],
            context=["qid", "qatar id", "id number", "civil id", "national id"],
        )

        self.analyzer.registry.add_recognizer(qid_recognizer)

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
            text=text, entities=self.target_entities, language="en"
        )

        pii_found = len(analysis_results) > 0
        detected_types = list(set([res.entity_type for res in analysis_results]))

        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analysis_results,
            operators={
                "DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED_PII>"}),
                "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE_NUMBER>"}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
                "PERSON": OperatorConfig("replace", {"new_value": "<NAME>"}),
                "QATAR_ID": OperatorConfig("replace", {"new_value": "<QATAR_ID>"}),
            },
        )

        return {
            "clean_text": anonymized_result.text,
            "pii_detected": pii_found,
            "detected_entities": detected_types,
        }
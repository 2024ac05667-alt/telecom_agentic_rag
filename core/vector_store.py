import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import chromadb

logger = logging.getLogger(__name__)

# Resolve an absolute path inside the project root so uvicorn working-directory shifts never create empty DBs
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DB_DIR = str(PROJECT_ROOT / "chroma_db")
COLLECTION_NAME = "qatar_telecom_consumer_law"

# ============================================================================
# QATAR LEGAL & TELECOM SLA CORPUS (LAW NO. 8 OF 2008 & CRA REGULATIONS)
# ============================================================================
QATAR_LEGAL_CORPUS: List[Dict[str, Any]] = [
    {
        "id": "law8_art1_art5_warranty_and_misuse",
        "metadata": {
            "law": "Qatar Law No. 8 of 2008",
            "article": "Articles 1 & 5",
            "topic": "warranty_eligibility_liquid_drop_exclusion",
        },
        "text": (
            "Qatar Law No. 8 of 2008 on Consumer Protection (Articles 1 & 5): "
            "Upon discovering a manufacturing defect or non-conformity with standard specifications, the supplier "
            "must recall the device and provide the consumer with a refund, exchange, or free-of-charge repair. "
            "However, under Article 1, defects or faults caused by the consumer—such as liquid/water ingress, "
            "charging port corrosion, or accidental physical drops—are excluded from free manufacturer warranty coverage."
        ),
    },
    {
        "id": "dec68_reg11_out_of_warranty_estimate",
        "metadata": {
            "law": "Ministerial Decision No. 68 of 2012",
            "article": "Regulation 11",
            "topic": "paid_repair_written_estimate_and_parts_warranty",
        },
        "text": (
            "Qatar Consumer Protection Executive Regulations (Decision No. 68 of 2012, Regulation 11): "
            "For out-of-warranty repairs (including accidental drop damage or liquid corrosion), the authorized service "
            "center in Qatar must provide a written statement specifying the exact repair cost and expected turnaround "
            "time (typically 3 to 5 business days for standard parts) for consumer approval before starting work, "
            "and replaced spare parts carry a mandatory 6-month warranty."
        ),
    },
    {
        "id": "law8_art9_substitute_device_15_days",
        "metadata": {
            "law": "Qatar Law No. 8 of 2008",
            "article": "Article 9 & Reg. 10",
            "topic": "repair_delay_substitute_loaner_device",
        },
        "text": (
            "Qatar Law No. 8 of 2008 on Consumer Protection (Article 9) & Executive Regulation 10: "
            "Each trade agent or authorized distributor in Qatar is legally obliged to execute all manufacturer guarantees. "
            "Where executing warranty repairs requires more than fifteen (15) days, the trade agent or distributor must "
            "provide a similar substitute device for the consumer to use free of charge until repairs are completed."
        ),
    },
    {
        "id": "law8_art16_repeat_defect_refund",
        "metadata": {
            "law": "Qatar Law No. 8 of 2008",
            "article": "Article 16",
            "topic": "repeated_repair_failure_replacement_refund",
        },
        "text": (
            "Qatar Law No. 8 of 2008 on Consumer Protection (Article 16): "
            "If the same manufacturing defect recurs after repeated repair attempts by the authorized Doha service center, "
            "the consumer has the statutory right to reject further repairs and demand a brand-new replacement or full refund."
        ),
    },
    {
        "id": "law8_art13_battery_safety_2yr_warranty",
        "metadata": {
            "law": "Qatar Law No. 8 of 2008",
            "article": "Articles 5, 8 & 13",
            "topic": "swollen_battery_safety_2_year_warranty",
        },
        "text": (
            "Qatar Law No. 8 of 2008 (Articles 5, 8 & 13 — Safety & Conformity): "
            "Suppliers guarantee device conformity to approved public health and safety standards. "
            "Premature lithium-ion battery swelling or thermal expansion without external impact is treated as a critical "
            "safety and manufacturing defect covered under the standard 2-year GCC/Qatar warranty, with a 3 to 5 business "
            "day inspection and replacement turnaround."
        ),
    },
    {
        "id": "cra_qos_fiber_5g_outage_sla",
        "metadata": {
            "law": "CRA Qatar Consumer Protection Policy",
            "article": "Telecom QoS & Billing SLA",
            "topic": "fiber_los_broadband_outage_bill_credit",
        },
        "text": (
            "Qatar Communications Regulatory Authority (CRA) Consumer Protection Policy & QoS Regulations: "
            "Licensed telecom providers in Qatar (Ooredoo / Vodafone Qatar) must resolve fixed fiber broadband faults "
            "such as Optical Loss of Signal (Red LOS) within prescribed SLA repair windows (typically 24 to 48 hours). "
            "If service outage exceeds the SLA threshold, subscribers are entitled to pro-rata monthly bill credits."
        ),
    },
]


class QatarLegalVectorStore:
    """
    Persistent ChromaDB wrapper for Qatar Consumer Protection Law No. 8 (2008)
    and CRA Telecom Quality-of-Service regulations.
    """

    def __init__(self, persist_dir: str = CHROMA_DB_DIR, collection_name: str = COLLECTION_NAME):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self._ensure_seeded()

    def _ensure_seeded(self) -> None:
        """Idempotently upserts the Qatar legal corpus into ChromaDB if empty or outdated."""
        try:
            current_count = self.collection.count()
            if current_count < len(QATAR_LEGAL_CORPUS):
                self.collection.upsert(
                    ids=[item["id"] for item in QATAR_LEGAL_CORPUS],
                    documents=[item["text"] for item in QATAR_LEGAL_CORPUS],
                    metadatas=[item["metadata"] for item in QATAR_LEGAL_CORPUS],
                )
                logger.info(
                    "Seeded %d Qatar legal clauses into ChromaDB at %s",
                    len(QATAR_LEGAL_CORPUS),
                    CHROMA_DB_DIR,
                )
        except Exception as exc:
            logger.exception("Failed seeding ChromaDB collection: %s", exc)

    def query(self, query_text: str, top_k: int = 2) -> List[str]:
        """Performs semantic similarity search and returns top_k grounded policy clauses."""
        if not query_text or not query_text.strip():
            return []

        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(top_k, max(1, self.collection.count())),
            )
            docs = results.get("documents") or []
            return docs[0] if docs else []
        except Exception as exc:
            logger.exception("ChromaDB query failed: %s", exc)
            return []


# Singleton instance + helper function expected by graph/workflow.py
_vector_store = QatarLegalVectorStore()


def query_legal_docs(query_text: str, top_k: int = 2) -> List[str]:
    """Retrieves top_k relevant Qatar Law No. 8 (2008) / CRA policy chunks."""
    return _vector_store.query(query_text=query_text, top_k=top_k)


if __name__ == "__main__":
    # Quick standalone CLI test
    sample_q = "My phone fell in water and the charging port has white corrosion. Free warranty?"
    matches = query_legal_docs(sample_q, top_k=2)
    print(f"ChromaDB Path: {CHROMA_DB_DIR}")
    print(f"Total Indexed Clauses: {_vector_store.collection.count()}\n")
    for idx, doc in enumerate(matches, 1):
        print(f"[{idx}] {doc}\n")
"""
Persistent ChromaDB Vector Store for Qatar Consumer Protection Law No. 8 (2008),
Ministerial Decision No. 68 of 2012, CRA Telecom Quality-of-Service Regulations,
and the internal Qatar Mobile SLA Warranty Policy PDF.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from pypdf import PdfReader

from config.settings import settings
from core.generate_pdf import generate_policy_pdf

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SLA_PDF_PATH = PROJECT_ROOT / "data" / "qatar_sla_policy.pdf"

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


def _load_sla_pdf_chunks(pdf_path: Path = DEFAULT_SLA_PDF_PATH) -> List[Dict[str, Any]]:
    """
    Auto-generates data/qatar_sla_policy.pdf if missing and extracts its pages
    for ChromaDB indexing so internal SLA turnaround matrices are searchable.
    """
    try:
        if not pdf_path.exists():
            generate_policy_pdf(str(pdf_path))

        reader = PdfReader(str(pdf_path))
        chunks: List[Dict[str, Any]] = []
        for page_idx, page in enumerate(reader.pages):
            page_text = (page.extract_text() or "").strip()
            if page_text:
                chunks.append(
                    {
                        "id": f"qatar_mobile_sla_pdf_page_{page_idx + 1}",
                        "metadata": {
                            "law": "Qatar Mobile Internal SLA & Law No. 8 of 2008",
                            "article": f"SLA Policy PDF (Page {page_idx + 1})",
                            "topic": "sla_turnaround_and_warranty_matrix",
                        },
                        "text": page_text,
                    }
                )
        return chunks
    except Exception as exc:
        logger.warning("Could not ingest SLA PDF at %s: %s", pdf_path, exc)
        return []


class QatarLegalVectorStore:
    """
    Persistent ChromaDB wrapper for Qatar Consumer Protection Law No. 8 (2008),
    CRA Telecom Quality-of-Service regulations, and Qatar Mobile SLA policy PDFs.
    """

    def __init__(
        self,
        persist_dir: str = settings.PERSIST_DIRECTORY,
        collection_name: str = settings.COLLECTION_NAME,
    ):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self._ensure_seeded()

    def _ensure_seeded(self) -> None:
        """Idempotently upserts both the Qatar legal corpus and generated SLA PDF into ChromaDB."""
        try:
            pdf_chunks = _load_sla_pdf_chunks()
            combined_corpus = QATAR_LEGAL_CORPUS + pdf_chunks

            current_count = self.collection.count()
            if current_count < len(combined_corpus):
                self.collection.upsert(
                    ids=[item["id"] for item in combined_corpus],
                    documents=[item["text"] for item in combined_corpus],
                    metadatas=[item["metadata"] for item in combined_corpus],
                )
                logger.info(
                    "Seeded %d Qatar legal & SLA PDF clauses into ChromaDB at %s",
                    len(combined_corpus),
                    settings.PERSIST_DIRECTORY,
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


_vector_store = QatarLegalVectorStore()


def query_legal_docs(query_text: str, top_k: int = 2) -> List[str]:
    """Retrieves top_k relevant Qatar Law No. 8 (2008), CRA, and SLA PDF policy chunks."""
    return _vector_store.query(query_text=query_text, top_k=top_k)


if __name__ == "__main__":
    sample_q = "My phone fell in water and the charging port has white corrosion. What is the SLA turnaround?"
    matches = query_legal_docs(sample_q, top_k=2)
    print(f"ChromaDB Path: {settings.PERSIST_DIRECTORY}")
    print(f"Total Indexed Clauses (Legal + PDF): {_vector_store.collection.count()}\n")
    for idx, doc in enumerate(matches, 1):
        print(f"[{idx}] {doc}\n")
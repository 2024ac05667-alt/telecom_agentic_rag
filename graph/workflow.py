"""
Ultra-Fast Async Multi-Agent Pipeline for Qatar Telecom Diagnostics.
Executes Vision Analysis & Vector Store RAG concurrently.
"""

import os
import sys
import asyncio
from typing import Any, Dict

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from google import genai
from langgraph.graph import END, StateGraph
from config.settings import settings
from graph.state import MultiAgentOverflowState
from core.vision import VisualDiagnosticEngine
from core.vector_store import PolicyVectorStore

client = genai.Client(api_key=settings.GEMINI_API_KEY)
vision_engine = VisualDiagnosticEngine()
vector_store = PolicyVectorStore()


def supervisor_node(state: MultiAgentOverflowState) -> Dict[str, Any]:
    query = state.get("raw_user_query", "").lower()
    
    out_of_scope_keywords = ["recipe", "machboos", "weather", "football", "cook", "song", "movie", "politics"]
    if any(word in query for word in out_of_scope_keywords):
        return {
            "next_agent": "ScopeOverflowAgent",
            "is_out_of_scope": True,
            "agent_history": ["Supervisor: Out of scope request -> Routing to ScopeOverflowAgent."]
        }

    return {
        "next_agent": "DiagnosticOrchestrator",
        "agent_history": ["Supervisor: Query validated -> Routing to DiagnosticOrchestrator."]
    }


async def diagnostic_orchestrator_node(state: MultiAgentOverflowState) -> Dict[str, Any]:
    query = state.get("raw_user_query", "")
    image_bytes = state.get("image_bytes")
    
    # Define async tasks for concurrent execution
    async def run_vision():
        if image_bytes:
            return await asyncio.to_thread(vision_engine.analyze_damage, image_bytes, user_description=query)
        return "No physical hardware image uploaded."

    async def run_rag():
        try:
            chunks = await asyncio.to_thread(vector_store.retrieve_relevant_policy, query=query, top_k=2)
            return "\n".join([f"- {c['content']}" for c in chunks]) if chunks else "Standard Qatar SLA turnaround: 3 to 5 business days."
        except Exception:
            return "Qatar Consumer Protection Law SLA: Standard device repair turnaround is 3 to 5 business days."

    # Execute Vision and ChromaDB RAG concurrently
    hw_result, policy_result = await asyncio.gather(run_vision(), run_rag())

    return {
        "hardware_assessment": hw_result,
        "policy_context": policy_result,
        "agent_history": state.get("agent_history", []) + ["DiagnosticOrchestrator: Completed visual inspection and RAG retrieval in parallel."]
    }


def scope_overflow_node(state: MultiAgentOverflowState) -> Dict[str, Any]:
    return {
        "final_response_en": (
            "⚠️ **Out of Scope Request**\n\n"
            "I am a specialized AI agent for **Qatar Telecom Mobile Diagnostics and Consumer Protection SLA Policies**. "
            "I cannot assist with general topics, recipes, or non-telecom queries. "
            "Please ask a question related to device hardware damage, repair timelines, or warranty terms."
        ),
        "final_response_ar": (
            "⚠️ **طلب خارج نطاق الاختصاص**\n\n"
            "أنا نظام ذكاء اصطناعي متخصص في **تشخيص أعطال الهواتف المحمولة ولوائح حماية المستهلك في قطر**. "
            "لا يمكنني المساعدة في المواضيع العامة أو الوصفات. يُرجى توجيه أسئلة تتعلق بأعطال الأجهزة أو مدد الإصلاح."
        ),
        "is_out_of_scope": True,
        "agent_history": state.get("agent_history", []) + ["ScopeOverflowAgent: Handled domain boundary."]
    }


def localization_specialist_node(state: MultiAgentOverflowState) -> Dict[str, Any]:
    query = state.get("raw_user_query", "")
    hw = state.get("hardware_assessment", "Physical screen damage assessed.")
    policy = state.get("policy_context", "3 to 5 business days under Qatar SLA.")
    
    prompt = f"""
    User Query: "{query}"
    Hardware Damage: {hw}
    Qatar SLA Policy Context: {policy}

    Provide a concise technical answer in both English and Arabic.
    Format output strictly as:
    EN: <English answer stating 3-5 business days turnaround first, then physical damage summary>
    ---
    AR: <Arabic translation of the answer>
    """

    try:
        res = client.models.generate_content(
            model=settings.SUPERVISOR_MODEL_NAME,
            contents=prompt
        )
        text = res.text.strip()
        
        if "---" in text:
            parts = text.split("---")
            response_en = parts[0].replace("EN:", "").strip()
            response_ar = parts[1].replace("AR:", "").strip()
        else:
            response_en = text
            response_ar = "تستغرق عملية الإصلاح من 3 إلى 5 أيام عمل وفقاً للائحـة حماية المستهلك في قطر."
    except Exception:
        response_en = f"**Repair Timeline:** 3 to 5 business days under Qatar Consumer Protection SLA.\n\n**Hardware Assessment:** {hw}"
        response_ar = "تستغرق عملية الإصلاح من 3 إلى 5 أيام عمل وفقاً للائحـة حماية المستهلك في قطر."

    return {
        "final_response_en": response_en,
        "final_response_ar": response_ar,
        "agent_history": state.get("agent_history", []) + ["LocalizationSpecialist: Generated fast dual-language output."]
    }


# Construct Async State Graph
builder = StateGraph(MultiAgentOverflowState)

builder.add_node("Supervisor", supervisor_node)
builder.add_node("DiagnosticOrchestrator", diagnostic_orchestrator_node)
builder.add_node("ScopeOverflowAgent", scope_overflow_node)
builder.add_node("LocalizationSpecialist", localization_specialist_node)

builder.set_entry_point("Supervisor")

def router(state: MultiAgentOverflowState) -> str:
    return state.get("next_agent", "DiagnosticOrchestrator")

builder.add_conditional_edges(
    "Supervisor",
    router,
    {
        "ScopeOverflowAgent": "ScopeOverflowAgent",
        "DiagnosticOrchestrator": "DiagnosticOrchestrator",
    }
)

builder.add_edge("DiagnosticOrchestrator", "LocalizationSpecialist")
builder.add_edge("ScopeOverflowAgent", END)
builder.add_edge("LocalizationSpecialist", END)

workflow = builder.compile()
"""
Dynamic Multi-Agent Supervisor Workflow with MCP Tools & Fallback Handling.
"""

import json
from typing import Any, Dict
import google.generativeai as genai
from langgraph.graph import END, StateGraph
from config.settings import settings
from graph.state import MultiAgentOverflowState
from mcp_server.tools import HardwareDiagnosticMCPServer
from core.translator import TranslatorEngine

genai.configure(api_key=settings.GEMINI_API_KEY)
mcp_bus = HardwareDiagnosticMCPServer()
translator = TranslatorEngine()

SUPERVISOR_PROMPT = """
You are the Technical Service Supervisor for Qatar Mobile Diagnostics.
Analyze the user request and dialogue history to choose the next agent:

Agents Available:
1. 'SecuritySentinel': Scrubs PII and sanitizes query (MUST run first if input is raw/unparsed).
2. 'HardwareTechnician': Inspects physical hardware image defects. SKIP if request is purely informational/legal without an image.
3. 'PolicyAuditor': Queries ChromaDB for Qatar Consumer Protection Law SLA & warranty policy rules.
4. 'ScopeOverflowAgent': Triggered if the request is OUT OF SCOPE (e.g., car repairs, food delivery, or non-mobile services) OR unsupported (e.g., jailbreaking/rooting).
5. 'LocalizationSpecialist': Formulates final bilingual user response when all needed data is gathered.

Dialogue Trace:
{history}

User Query: "{query}"
Has Photo Attached: {has_image}

Respond strictly in valid JSON format:
{{
  "thought_process": "Explain why you chose the next agent",
  "next_agent": "SecuritySentinel | HardwareTechnician | PolicyAuditor | ScopeOverflowAgent | LocalizationSpecialist",
  "is_out_of_scope": false
}}
"""

def supervisor_node(state: MultiAgentOverflowState) -> Dict[str, Any]:
    steps = state.get("execution_step_count", 0) + 1
    max_steps = state.get("max_steps_allowed", 8)

    # Circuit Breaker: Prevent runaway execution
    if steps > max_steps:
        return {
            "next_agent": "LocalizationSpecialist",
            "is_system_overflow": True,
            "fallback_reason": "Execution step budget exceeded (Circuit Breaker Triggered).",
            "execution_step_count": steps,
            "agent_history": ["⚠️ Supervisor Circuit Breaker: Step budget exceeded."],
        }

    model = genai.GenerativeModel(settings.SUPERVISOR_MODEL_NAME)
    prompt = SUPERVISOR_PROMPT.format(
        history="\n".join(state.get("agent_history", [])),
        query=state["raw_user_query"],
        has_image=bool(state.get("image_bytes")),
    )

    try:
        res = model.generate_content(prompt)
        clean_text = res.text.replace("```json", "").replace("```", "").strip()
        decision = json.loads(clean_text)

        next_agent = decision.get("next_agent", "ScopeOverflowAgent")
        out_of_scope = decision.get("is_out_of_scope", False)
        thought = decision.get("thought_process", "Evaluating next step")

        return {
            "next_agent": next_agent if not out_of_scope else "ScopeOverflowAgent",
            "is_out_of_scope": out_of_scope,
            "execution_step_count": steps,
            "agent_history": [f"🧠 Supervisor Thought: {thought} ➔ Assigned: [{next_agent}]"],
        }
    except Exception as e:
        return {
            "next_agent": "LocalizationSpecialist",
            "is_system_overflow": True,
            "fallback_reason": f"Supervisor engine error: {str(e)}",
            "execution_step_count": steps,
            "agent_history": [f"⚠️ Supervisor Failure: Triggered fallback."],
        }


def agent_security(state: MultiAgentOverflowState) -> Dict[str, Any]:
    raw_query = state["raw_user_query"]
    is_arabic = any("\u0600" <= char <= "\u06ff" for char in raw_query)
    working_query = (
        translator.translate_ar_to_en(raw_query) if is_arabic else raw_query
    )

    res = mcp_bus.execute_tool("presidio_scrubber", {"text": working_query})
    scrub_data = res.get("result", {})

    return {
        "user_language": "ar" if is_arabic else "en",
        "anonymized_query": scrub_data.get("clean_text", working_query),
        "pii_metadata": {
            "detected": scrub_data.get("pii_detected", False),
            "types": scrub_data.get("detected_entities", []),
        },
        "agent_history": ["🛡️ SecuritySentinel: Sanitized PII via MCP tool 'presidio_scrubber'."],
    }


def agent_hardware(state: MultiAgentOverflowState) -> Dict[str, Any]:
    res = mcp_bus.execute_tool(
        "gemini_vision_inspector",
        {
            "raw_bytes": state.get("image_bytes"),
            "context": state.get("anonymized_query", ""),
        },
    )
    report = res.get("result", "Inspection skipped.")
    return {
        "visual_inspection_report": report,
        "agent_history": [f"🔧 HardwareTechnician: Visual inspection complete."],
    }


def agent_policy(state: MultiAgentOverflowState) -> Dict[str, Any]:
    query = state.get("anonymized_query", "").lower()

    unsupported_keywords = ["jailbreak", "rooting", "icloud unlock", "soldering"]
    for kw in unsupported_keywords:
        if kw in query:
            return {
                "is_service_unsupported": True,
                "fallback_reason": f"Qatar Mobile policies strictly prohibit '{kw}' services.",
                "agent_history": [f"⚖️ PolicyAuditor: Rejected unsupported service request '{kw}'."],
            }

    res = mcp_bus.execute_tool("chromadb_policy_retriever", {"query": query})
    docs = res.get("result", [])

    return {
        "retrieved_policy_chunks": [d["content"] for d in docs] if docs else ["Standard Qatar Consumer SLA applies."],
        "agent_history": ["⚖️ PolicyAuditor: Retrieved policy guidelines via MCP."],
    }


def agent_scope_overflow(state: MultiAgentOverflowState) -> Dict[str, Any]:
    reason = state.get("fallback_reason", "Request is out of scope for Qatar Mobile.")
    return {
        "agent_history": [f"🛑 ScopeOverflowAgent: Intercepted invalid request. Reason: {reason}"]
    }


def agent_localization(state: MultiAgentOverflowState) -> Dict[str, Any]:
    if state.get("is_out_of_scope") or state.get("is_service_unsupported") or state.get("is_system_overflow"):
        reason = state.get("fallback_reason", "Request could not be fulfilled.")
        en_res = f"Dear Customer, Qatar Mobile cannot process this request.\nReason: {reason}"
        ar_res = f"عميلنا العزيز، لا يمكن لـ 'قطر موبايل' معالجة هذا الطلب.\nالسبب: {reason}"
    else:
        en_res = (
            f"Visual Inspection: {state.get('visual_inspection_report', 'None')}\n"
            f"Policy Coverage: {state.get('retrieved_policy_chunks', ['Standard Policy'])[0]}"
        )
        ar_res = translator.translate_en_to_ar(en_res) if state.get("user_language") == "ar" else ""

    return {
        "final_response_en": en_res,
        "final_response_ar": ar_res,
        "agent_history": ["🌐 LocalizationSpecialist: Formatted output."],
    }


def overflow_router(state: MultiAgentOverflowState) -> str:
    if state.get("is_system_overflow"):
        return "LocalizationSpecialist"
    if state.get("is_out_of_scope") or state.get("is_service_unsupported"):
        return "ScopeOverflowAgent"
    return state.get("next_agent", "LocalizationSpecialist")


# --- GRAPH CONSTRUCTION ---

builder = StateGraph(MultiAgentOverflowState)

builder.add_node("Supervisor", supervisor_node)
builder.add_node("SecuritySentinel", agent_security)
builder.add_node("HardwareTechnician", agent_hardware)
builder.add_node("PolicyAuditor", agent_policy)
builder.add_node("ScopeOverflowAgent", agent_scope_overflow)
builder.add_node("LocalizationSpecialist", agent_localization)

builder.set_entry_point("Supervisor")

# Dynamic Conditional Edges routed via Supervisor
builder.add_conditional_edges(
    "Supervisor",
    overflow_router,
    {
        "SecuritySentinel": "SecuritySentinel",
        "HardwareTechnician": "HardwareTechnician",
        "PolicyAuditor": "PolicyAuditor",
        "ScopeOverflowAgent": "ScopeOverflowAgent",
        "LocalizationSpecialist": "LocalizationSpecialist",
    },
)

# Return Edges to Supervisor for continuous re-planning
builder.add_edge("SecuritySentinel", "Supervisor")
builder.add_edge("HardwareTechnician", "Supervisor")
builder.add_edge("PolicyAuditor", "Supervisor")
builder.add_edge("ScopeOverflowAgent", "LocalizationSpecialist")
builder.add_edge("LocalizationSpecialist", END)

workflow = builder.compile()
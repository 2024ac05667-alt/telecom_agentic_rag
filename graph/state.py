"""
State Definition for Multi-Agent Overflow Diagnostics.
"""

from typing import List, Optional, TypedDict, Any


class MultiAgentOverflowState(TypedDict, total=False):
    # Inputs
    raw_user_query: str
    user_language: str
    image_bytes: Optional[bytes]
    
    # Internal Agent Execution & Context
    next_agent: str
    hardware_assessment: Optional[str]
    policy_context: Optional[str]
    pii_metadata: Optional[dict]
    
    # Output & Traceability
    final_response_en: Optional[str]
    final_response_ar: Optional[str]
    agent_history: List[str]
    execution_step_count: int
    max_steps_allowed: int
    is_out_of_scope: bool
    is_system_overflow: bool
    fallback_reason: Optional[str]
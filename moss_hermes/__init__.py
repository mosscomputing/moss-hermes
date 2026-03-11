"""
MOSS Hermes Integration - Cryptographic Signing for Hermes Agent Outputs

Sign tool calls, reasoning chains, and agent actions from Nous Research's Hermes models.

Quick Start:
    from moss_hermes import sign_tool_call, sign_reasoning_chain
    
    # After Hermes executes a tool
    signed = sign_tool_call(
        tool_name="send_email",
        tool_input={"to": "user@example.com", "body": "Hello"},
        tool_output={"status": "sent", "message_id": "msg_123"},
        agent_id="hermes-assistant"
    )
    print(f"Signature: {signed.signature}")

Enterprise Mode:
    Set MOSS_API_KEY environment variable to enable:
    - Policy evaluation (allow/block/hold)
    - Evidence retention
    - Kill-switch monitoring
    - Registry certification
"""

__version__ = "0.1.0"

from .signing import (
    sign_tool_call,
    sign_tool_call_async,
    sign_reasoning_chain,
    sign_reasoning_chain_async,
    sign_memory_retrieval,
    sign_memory_retrieval_async,
    sign_agent_action,
    sign_agent_action_async,
    sign_function_call,
    sign_function_call_async,
    verify_envelope,
)

from .wrapper import (
    MossHermesWrapper,
    moss_signed,
)

from .kill_switch import (
    KillSwitchMonitor,
    check_kill_switch,
)

from moss import SignResult, VerifyResult, Envelope, enterprise_enabled

__all__ = [
    # Explicit signing functions
    "sign_tool_call",
    "sign_tool_call_async",
    "sign_reasoning_chain",
    "sign_reasoning_chain_async",
    "sign_memory_retrieval",
    "sign_memory_retrieval_async",
    "sign_agent_action",
    "sign_agent_action_async",
    "sign_function_call",
    "sign_function_call_async",
    "verify_envelope",
    
    # Wrapper for automatic signing
    "MossHermesWrapper",
    "moss_signed",
    
    # Kill-switch
    "KillSwitchMonitor",
    "check_kill_switch",
    
    # Core types
    "SignResult",
    "VerifyResult",
    "Envelope",
    "enterprise_enabled",
]

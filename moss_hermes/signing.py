"""
MOSS Hermes Integration - Signing Functions

Provides explicit signing functions for Hermes agent outputs.
Compatible with Nous Research Hermes models (Hermes-2, Hermes-3, etc.)

Example:
    from moss_hermes import sign_tool_call
    
    # After Hermes executes a tool
    signed = sign_tool_call(
        tool_name="execute_code",
        tool_input={"code": "print('hello')"},
        tool_output={"result": "hello", "exit_code": 0},
        agent_id="hermes-coder"
    )
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from moss import sign, sign_async, verify, SignResult, VerifyResult


def sign_tool_call(
    tool_name: str,
    tool_input: Dict[str, Any],
    tool_output: Any,
    agent_id: str,
    *,
    parent_sig: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> SignResult:
    """
    Sign a Hermes tool call execution.
    
    Args:
        tool_name: Name of the tool executed (e.g., "send_email", "execute_code")
        tool_input: Parameters passed to the tool
        tool_output: Result returned by the tool
        agent_id: Identifier for the Hermes agent
        parent_sig: Optional parent signature for causal linking
        context: Optional context (user_id, session_id, etc.)
    
    Returns:
        SignResult with envelope and enterprise info
    
    Example:
        signed = sign_tool_call(
            tool_name="web_search",
            tool_input={"query": "latest AI news"},
            tool_output={"results": [...]},
            agent_id="hermes-researcher"
        )
    """
    payload = {
        "type": "hermes_tool_call",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_output": _serialize_output(tool_output),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if parent_sig:
        payload["parent_sig"] = parent_sig
    
    return sign(
        output=payload,
        agent_id=agent_id,
        action=f"hermes_tool:{tool_name}",
        context=context,
    )


async def sign_tool_call_async(
    tool_name: str,
    tool_input: Dict[str, Any],
    tool_output: Any,
    agent_id: str,
    *,
    parent_sig: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> SignResult:
    """Async version of sign_tool_call."""
    payload = {
        "type": "hermes_tool_call",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_output": _serialize_output(tool_output),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if parent_sig:
        payload["parent_sig"] = parent_sig
    
    return await sign_async(
        output=payload,
        agent_id=agent_id,
        action=f"hermes_tool:{tool_name}",
        context=context,
    )


def sign_reasoning_chain(
    reasoning_steps: List[Dict[str, Any]],
    final_conclusion: str,
    agent_id: str,
    *,
    parent_sig: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> SignResult:
    """
    Sign a Hermes reasoning chain (chain-of-thought).
    
    Args:
        reasoning_steps: List of reasoning steps with 'thought' and 'action'
        final_conclusion: The final conclusion or answer
        agent_id: Identifier for the Hermes agent
        parent_sig: Optional parent signature for causal linking
        context: Optional context
    
    Returns:
        SignResult with envelope and enterprise info
    
    Example:
        signed = sign_reasoning_chain(
            reasoning_steps=[
                {"thought": "I need to search for...", "action": "web_search"},
                {"thought": "Based on results...", "action": "summarize"}
            ],
            final_conclusion="The answer is...",
            agent_id="hermes-analyst"
        )
    """
    payload = {
        "type": "hermes_reasoning_chain",
        "steps": reasoning_steps,
        "step_count": len(reasoning_steps),
        "conclusion": final_conclusion,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if parent_sig:
        payload["parent_sig"] = parent_sig
    
    return sign(
        output=payload,
        agent_id=agent_id,
        action="hermes_reasoning",
        context=context,
    )


async def sign_reasoning_chain_async(
    reasoning_steps: List[Dict[str, Any]],
    final_conclusion: str,
    agent_id: str,
    *,
    parent_sig: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> SignResult:
    """Async version of sign_reasoning_chain."""
    payload = {
        "type": "hermes_reasoning_chain",
        "steps": reasoning_steps,
        "step_count": len(reasoning_steps),
        "conclusion": final_conclusion,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if parent_sig:
        payload["parent_sig"] = parent_sig
    
    return await sign_async(
        output=payload,
        agent_id=agent_id,
        action="hermes_reasoning",
        context=context,
    )


def sign_memory_retrieval(
    query: str,
    retrieved_memories: List[Dict[str, Any]],
    agent_id: str,
    *,
    memory_type: str = "episodic",
    context: Optional[Dict[str, Any]] = None,
) -> SignResult:
    """
    Sign a Hermes memory retrieval event.
    
    Args:
        query: The query used for memory retrieval
        retrieved_memories: List of retrieved memory items
        agent_id: Identifier for the Hermes agent
        memory_type: Type of memory (episodic, semantic, procedural)
        context: Optional context
    
    Returns:
        SignResult with envelope and enterprise info
    
    Example:
        signed = sign_memory_retrieval(
            query="previous conversations about project X",
            retrieved_memories=[{"content": "...", "timestamp": "..."}],
            agent_id="hermes-assistant",
            memory_type="episodic"
        )
    """
    payload = {
        "type": "hermes_memory_retrieval",
        "query": query,
        "memory_type": memory_type,
        "retrieved_count": len(retrieved_memories),
        "memories": retrieved_memories,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    return sign(
        output=payload,
        agent_id=agent_id,
        action=f"hermes_memory:{memory_type}",
        context=context,
    )


async def sign_memory_retrieval_async(
    query: str,
    retrieved_memories: List[Dict[str, Any]],
    agent_id: str,
    *,
    memory_type: str = "episodic",
    context: Optional[Dict[str, Any]] = None,
) -> SignResult:
    """Async version of sign_memory_retrieval."""
    payload = {
        "type": "hermes_memory_retrieval",
        "query": query,
        "memory_type": memory_type,
        "retrieved_count": len(retrieved_memories),
        "memories": retrieved_memories,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    return await sign_async(
        output=payload,
        agent_id=agent_id,
        action=f"hermes_memory:{memory_type}",
        context=context,
    )


def sign_agent_action(
    action_type: str,
    action_input: Dict[str, Any],
    action_output: Any,
    agent_id: str,
    *,
    parent_sig: Optional[str] = None,
    reasoning: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> SignResult:
    """
    Sign a generic Hermes agent action.
    
    Args:
        action_type: Type of action performed
        action_input: Input parameters for the action
        action_output: Output of the action
        agent_id: Identifier for the Hermes agent
        parent_sig: Optional parent signature for causal linking
        reasoning: Optional reasoning that led to this action
        context: Optional context
    
    Returns:
        SignResult with envelope and enterprise info
    """
    payload = {
        "type": "hermes_agent_action",
        "action_type": action_type,
        "input": action_input,
        "output": _serialize_output(action_output),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if parent_sig:
        payload["parent_sig"] = parent_sig
    if reasoning:
        payload["reasoning"] = reasoning
    
    return sign(
        output=payload,
        agent_id=agent_id,
        action=f"hermes_action:{action_type}",
        context=context,
    )


async def sign_agent_action_async(
    action_type: str,
    action_input: Dict[str, Any],
    action_output: Any,
    agent_id: str,
    *,
    parent_sig: Optional[str] = None,
    reasoning: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> SignResult:
    """Async version of sign_agent_action."""
    payload = {
        "type": "hermes_agent_action",
        "action_type": action_type,
        "input": action_input,
        "output": _serialize_output(action_output),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if parent_sig:
        payload["parent_sig"] = parent_sig
    if reasoning:
        payload["reasoning"] = reasoning
    
    return await sign_async(
        output=payload,
        agent_id=agent_id,
        action=f"hermes_action:{action_type}",
        context=context,
    )


def sign_function_call(
    function_name: str,
    arguments: Dict[str, Any],
    result: Any,
    agent_id: str,
    *,
    parent_sig: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> SignResult:
    """
    Sign a Hermes function call (OpenAI-compatible function calling).
    
    Args:
        function_name: Name of the function called
        arguments: Arguments passed to the function
        result: Result of the function call
        agent_id: Identifier for the Hermes agent
        parent_sig: Optional parent signature for causal linking
        context: Optional context
    
    Returns:
        SignResult with envelope and enterprise info
    
    Example:
        signed = sign_function_call(
            function_name="get_weather",
            arguments={"city": "San Francisco"},
            result={"temp": 65, "condition": "sunny"},
            agent_id="hermes-weather-bot"
        )
    """
    payload = {
        "type": "hermes_function_call",
        "function_name": function_name,
        "arguments": arguments,
        "result": _serialize_output(result),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if parent_sig:
        payload["parent_sig"] = parent_sig
    
    return sign(
        output=payload,
        agent_id=agent_id,
        action=f"hermes_function:{function_name}",
        context=context,
    )


async def sign_function_call_async(
    function_name: str,
    arguments: Dict[str, Any],
    result: Any,
    agent_id: str,
    *,
    parent_sig: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> SignResult:
    """Async version of sign_function_call."""
    payload = {
        "type": "hermes_function_call",
        "function_name": function_name,
        "arguments": arguments,
        "result": _serialize_output(result),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if parent_sig:
        payload["parent_sig"] = parent_sig
    
    return await sign_async(
        output=payload,
        agent_id=agent_id,
        action=f"hermes_function:{function_name}",
        context=context,
    )


def verify_envelope(envelope: Any, payload: Any = None) -> VerifyResult:
    """
    Verify a signed envelope.
    
    Args:
        envelope: MOSS Envelope or dict
        payload: Original payload for hash verification (optional)
    
    Returns:
        VerifyResult with valid=True/False and details
    """
    return verify(envelope, payload)


def _serialize_output(output: Any) -> Any:
    """Serialize output to JSON-compatible format."""
    if output is None:
        return None
    if isinstance(output, (str, int, float, bool)):
        return output
    if isinstance(output, dict):
        return output
    if isinstance(output, list):
        return output
    if hasattr(output, "model_dump"):
        return output.model_dump()
    if hasattr(output, "__dict__"):
        return output.__dict__
    return str(output)

"""
MOSS Hermes Wrapper - Automatic signing for Hermes agents

Provides a wrapper class and decorator for automatic signing of all tool calls.

Example:
    from moss_hermes import MossHermesWrapper
    
    # Wrap any Hermes-compatible agent
    agent = MossHermesWrapper(
        agent=my_hermes_agent,
        agent_id="hermes-assistant",
        moss_api_key="moss_live_xxx"
    )
    
    # All tool calls are now automatically signed
    result = agent.run("Search for AI news and summarize")
"""

from typing import Any, Callable, Dict, Optional, List
from functools import wraps
import os

from .signing import sign_tool_call, sign_function_call, sign_agent_action


class MossHermesWrapper:
    """
    Wrapper for Hermes agents that automatically signs all tool/function calls.
    
    Example:
        from transformers import AutoModelForCausalLM
        from moss_hermes import MossHermesWrapper
        
        model = AutoModelForCausalLM.from_pretrained("NousResearch/Hermes-3-Llama-3.1-8B")
        
        wrapped = MossHermesWrapper(
            agent=model,
            agent_id="hermes-3-assistant",
            moss_api_key="moss_live_xxx"
        )
    """
    
    def __init__(
        self,
        agent: Any,
        agent_id: str,
        *,
        moss_api_key: Optional[str] = None,
        auto_sign_tools: bool = True,
        auto_sign_functions: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the MOSS Hermes wrapper.
        
        Args:
            agent: The Hermes agent/model to wrap
            agent_id: Identifier for this agent in MOSS
            moss_api_key: MOSS API key (or set MOSS_API_KEY env var)
            auto_sign_tools: Automatically sign tool calls
            auto_sign_functions: Automatically sign function calls
            context: Default context for all signatures
        """
        self.agent = agent
        self.agent_id = agent_id
        self.moss_api_key = moss_api_key or os.environ.get("MOSS_API_KEY")
        self.auto_sign_tools = auto_sign_tools
        self.auto_sign_functions = auto_sign_functions
        self.context = context or {}
        self._last_signature: Optional[str] = None
        self._signature_chain: List[str] = []
    
    @property
    def last_signature(self) -> Optional[str]:
        """Get the last signature generated."""
        return self._last_signature
    
    @property
    def signature_chain(self) -> List[str]:
        """Get all signatures in the current chain."""
        return self._signature_chain.copy()
    
    def clear_chain(self):
        """Clear the signature chain (start fresh)."""
        self._signature_chain = []
        self._last_signature = None
    
    def execute_tool(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_executor: Callable,
    ) -> Any:
        """
        Execute a tool and sign the result.
        
        Args:
            tool_name: Name of the tool
            tool_input: Input parameters
            tool_executor: Function that executes the tool
        
        Returns:
            Tool output (with signature attached if enterprise mode)
        """
        # Execute the tool
        output = tool_executor(tool_input)
        
        # Sign if enabled
        if self.auto_sign_tools:
            signed = sign_tool_call(
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=output,
                agent_id=self.agent_id,
                parent_sig=self._last_signature,
                context=self.context,
            )
            self._last_signature = signed.signature
            self._signature_chain.append(signed.signature)
            
            # Check if blocked
            if signed.blocked:
                raise ToolBlockedError(
                    f"Tool '{tool_name}' blocked by policy: {signed.enterprise.policy.reason}"
                )
        
        return output
    
    def execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        function_executor: Callable,
    ) -> Any:
        """
        Execute a function call and sign the result.
        
        Args:
            function_name: Name of the function
            arguments: Function arguments
            function_executor: Function that executes the call
        
        Returns:
            Function result (with signature attached if enterprise mode)
        """
        # Execute the function
        result = function_executor(arguments)
        
        # Sign if enabled
        if self.auto_sign_functions:
            signed = sign_function_call(
                function_name=function_name,
                arguments=arguments,
                result=result,
                agent_id=self.agent_id,
                parent_sig=self._last_signature,
                context=self.context,
            )
            self._last_signature = signed.signature
            self._signature_chain.append(signed.signature)
            
            # Check if blocked
            if signed.blocked:
                raise FunctionBlockedError(
                    f"Function '{function_name}' blocked by policy: {signed.enterprise.policy.reason}"
                )
        
        return result
    
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to wrapped agent."""
        return getattr(self.agent, name)


class ToolBlockedError(Exception):
    """Raised when a tool call is blocked by MOSS policy."""
    pass


class FunctionBlockedError(Exception):
    """Raised when a function call is blocked by MOSS policy."""
    pass


def moss_signed(
    agent_id: str,
    *,
    action_type: str = "tool_call",
    context: Optional[Dict[str, Any]] = None,
):
    """
    Decorator to automatically sign function/tool outputs.
    
    Example:
        @moss_signed(agent_id="hermes-bot", action_type="web_search")
        def search_web(query: str) -> dict:
            # ... perform search ...
            return results
        
        # Function output is automatically signed
        results = search_web("latest AI news")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract input
            tool_input = {"args": args, "kwargs": kwargs}
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Sign the result
            signed = sign_agent_action(
                action_type=action_type,
                action_input=tool_input,
                action_output=result,
                agent_id=agent_id,
                context=context,
            )
            
            # Check if blocked
            if signed.blocked:
                raise ToolBlockedError(
                    f"Action blocked by policy: {signed.enterprise.policy.reason}"
                )
            
            return result
        
        return wrapper
    return decorator

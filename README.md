# moss-hermes

MOSS integration for [Nous Research Hermes](https://nousresearch.com) - cryptographic signing for AI agent actions.

**Unsigned agent output is broken output.**

All signatures use **ML-DSA-44** (NIST FIPS 204), the post-quantum cryptographic standard.

[![PyPI](https://img.shields.io/pypi/v/moss-hermes)](https://pypi.org/project/moss-hermes/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Installation

```bash
pip install moss-hermes
```

## Quick Start

```python
from moss_hermes import sign_tool_call

# After Hermes executes a tool
signed = sign_tool_call(
    tool_name="send_email",
    tool_input={"to": "user@example.com", "body": "Hello"},
    tool_output={"status": "sent", "message_id": "msg_123"},
    agent_id="hermes-assistant"
)

print(f"Signature: {signed.signature[:32]}...")
print(f"Certified: {signed.is_certified}")
```

## What Gets Signed

| Function | Use Case |
|----------|----------|
| `sign_tool_call` | Tool executions (send_email, execute_code, etc.) |
| `sign_function_call` | OpenAI-compatible function calls |
| `sign_reasoning_chain` | Chain-of-thought reasoning steps |
| `sign_memory_retrieval` | Memory/RAG retrieval events |
| `sign_agent_action` | Generic agent actions |

## Sign Tool Calls

```python
from moss_hermes import sign_tool_call

result = sign_tool_call(
    tool_name="web_search",
    tool_input={"query": "latest AI research"},
    tool_output={"results": [...]},
    agent_id="hermes-researcher",
    context={"user_id": "u123", "session_id": "s456"}
)

if result.blocked:
    print(f"Blocked: {result.enterprise.policy.reason}")
else:
    print(f"Signed: {result.signature}")
```

## Sign Reasoning Chains

```python
from moss_hermes import sign_reasoning_chain

signed = sign_reasoning_chain(
    reasoning_steps=[
        {"thought": "I need to search for information", "action": "web_search"},
        {"thought": "Based on results, I should summarize", "action": "summarize"}
    ],
    final_conclusion="The answer is...",
    agent_id="hermes-analyst"
)
```

## Sign Function Calls (OpenAI-compatible)

```python
from moss_hermes import sign_function_call

signed = sign_function_call(
    function_name="get_weather",
    arguments={"city": "San Francisco"},
    result={"temp": 65, "condition": "sunny"},
    agent_id="hermes-weather-bot"
)
```

## Causal Linking (Parent Signatures)

Link actions in a chain for full traceability:

```python
from moss_hermes import sign_tool_call

# First action
result1 = sign_tool_call(
    tool_name="search",
    tool_input={"query": "AI news"},
    tool_output={"results": [...]},
    agent_id="hermes-bot"
)

# Second action - linked to first
result2 = sign_tool_call(
    tool_name="summarize",
    tool_input={"text": "..."},
    tool_output={"summary": "..."},
    agent_id="hermes-bot",
    parent_sig=result1.signature  # Causal link!
)
```

## Automatic Signing with Wrapper

```python
from moss_hermes import MossHermesWrapper

# Wrap your Hermes agent
agent = MossHermesWrapper(
    agent=my_hermes_agent,
    agent_id="hermes-assistant",
    moss_api_key="moss_live_xxx"
)

# All tool calls are now automatically signed
result = agent.execute_tool(
    tool_name="send_email",
    tool_input={"to": "user@example.com"},
    tool_executor=my_email_function
)
```

## Decorator for Functions

```python
from moss_hermes import moss_signed

@moss_signed(agent_id="hermes-bot", action_type="web_search")
def search_web(query: str) -> dict:
    # ... perform search ...
    return results

# Output is automatically signed
results = search_web("latest AI news")
```

## Kill-Switch Integration

Monitor for agent revocation and respond immediately:

```python
from moss_hermes import KillSwitchMonitor
import sys

def on_revoked():
    print("Agent revoked! Shutting down...")
    sys.exit(1)

monitor = KillSwitchMonitor(
    agent_id="hermes-trading-bot",
    moss_api_key="moss_live_xxx",
    on_revoked=on_revoked,
    check_interval_seconds=10
)

# Start monitoring in background
monitor.start()

# Run your agent - it will shut down if revoked
agent.run()
```

One-time check:

```python
from moss_hermes import check_kill_switch

if not check_kill_switch("my-agent"):
    print("Agent has been revoked!")
    sys.exit(1)
```

## Enterprise Mode

Set `MOSS_API_KEY` to enable enterprise features:

```python
import os
os.environ["MOSS_API_KEY"] = "moss_live_xxx"

from moss_hermes import sign_tool_call

result = sign_tool_call(
    tool_name="execute_trade",
    tool_input={"symbol": "AAPL", "quantity": 1000},
    tool_output={"order_id": "ORD-123"},
    agent_id="hermes-trader"
)

# Check policy decision
if result.blocked:
    print(f"Blocked: {result.enterprise.policy.reason}")
else:
    print(f"Allowed, evidence ID: {result.evidence_id}")
```

## Async Support

All signing functions have async versions:

```python
from moss_hermes import sign_tool_call_async

signed = await sign_tool_call_async(
    tool_name="analyze",
    tool_input={...},
    tool_output={...},
    agent_id="hermes-analyzer"
)
```

## Verification

```python
from moss_hermes import verify_envelope

result = verify_envelope(signed.envelope)
if result.valid:
    print(f"Verified: signed by {result.subject}")
else:
    print(f"Invalid: {result.reason}")
```

## Why Sign Hermes Actions?

1. **Compliance** - Prove to auditors exactly what your AI did
2. **Accountability** - Cryptographic proof of every action
3. **Kill-Switch** - Instant remote shutdown if agent goes rogue
4. **Debugging** - Trace multi-step reasoning chains
5. **Future-Proof** - ML-DSA-44 (post-quantum) signatures

## Pricing

| Tier | Price | Agents | Signatures |
|------|-------|--------|------------|
| **Free** | $0 | 5 | 1,000/day |
| **Pro** | $1,499/mo | Unlimited | Unlimited |
| **Enterprise** | Custom | Unlimited | Unlimited |

All new signups get a **14-day free trial** of Pro.

## Links

- [mosscomputing.com](https://mosscomputing.com) - Project site
- [app.mosscomputing.com](https://app.mosscomputing.com) - Developer Console
- [moss-sdk](https://pypi.org/project/moss-sdk/) - Core MOSS SDK
- [Nous Research](https://nousresearch.com) - Hermes creators
- [Hermes Models](https://huggingface.co/NousResearch) - HuggingFace

## License

MIT - See [LICENSE](LICENSE) for terms.

# moss-hermes

MOSS integration for [Nous Research Hermes](https://nousresearch.com) agents.

## Overview

Cryptographic signing for Hermes AI agent actions using ML-DSA-44 (NIST FIPS 204) post-quantum signatures.

## Installation

```bash
pip install moss-hermes
```

## Quick Start

```python
from moss_hermes import sign_tool_call

signed = sign_tool_call(
    tool_name="send_email",
    tool_input={"to": "user@example.com", "body": "Hello"},
    tool_output={"status": "sent"},
    agent_id="hermes-assistant"
)
```

## What Gets Signed

| Function | Use Case |
|----------|----------|
| `sign_tool_call` | Tool executions |
| `sign_function_call` | OpenAI-compatible function calls |
| `sign_reasoning_chain` | Chain-of-thought reasoning |
| `sign_memory_retrieval` | Memory/RAG retrieval events |

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MOSS_API_KEY` | Enterprise API key | None (local mode) |
| `MOSS_API_URL` | API endpoint | `https://api.mosscomputing.com` |

## Features

- **ML-DSA-44 Signatures**: Post-quantum cryptographic signing
- **Causal Linking**: Link actions via `parent_sig` parameter
- **Kill-Switch**: Monitor for agent revocation
- **Async Support**: All functions have async versions

## Links

- [Documentation](https://docs.mosscomputing.com/sdks/hermes)
- [Nous Research](https://nousresearch.com)
- [Hermes Models](https://huggingface.co/NousResearch)
- [PyPI](https://pypi.org/project/moss-hermes/)

## License

MIT - See [LICENSE](LICENSE) for details.

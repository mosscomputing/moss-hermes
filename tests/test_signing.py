"""Tests for MOSS Hermes signing functions."""

import pytest
from unittest.mock import patch, MagicMock


class TestSignToolCall:
    """Tests for sign_tool_call function."""
    
    def test_sign_tool_call_basic(self):
        """Test basic tool call signing."""
        with patch("moss_hermes.signing.sign") as mock_sign:
            mock_sign.return_value = MagicMock(
                signature="test_sig",
                blocked=False,
            )
            
            from moss_hermes import sign_tool_call
            
            result = sign_tool_call(
                tool_name="test_tool",
                tool_input={"key": "value"},
                tool_output={"result": "success"},
                agent_id="test-agent"
            )
            
            assert result.signature == "test_sig"
            assert not result.blocked
            mock_sign.assert_called_once()
    
    def test_sign_tool_call_with_parent(self):
        """Test tool call signing with parent signature."""
        with patch("moss_hermes.signing.sign") as mock_sign:
            mock_sign.return_value = MagicMock(
                signature="child_sig",
                blocked=False,
            )
            
            from moss_hermes import sign_tool_call
            
            result = sign_tool_call(
                tool_name="child_tool",
                tool_input={},
                tool_output={},
                agent_id="test-agent",
                parent_sig="parent_sig_123"
            )
            
            call_args = mock_sign.call_args
            assert call_args[1]["output"]["parent_sig"] == "parent_sig_123"


class TestSignReasoningChain:
    """Tests for sign_reasoning_chain function."""
    
    def test_sign_reasoning_chain(self):
        """Test reasoning chain signing."""
        with patch("moss_hermes.signing.sign") as mock_sign:
            mock_sign.return_value = MagicMock(
                signature="reasoning_sig",
                blocked=False,
            )
            
            from moss_hermes import sign_reasoning_chain
            
            result = sign_reasoning_chain(
                reasoning_steps=[
                    {"thought": "Step 1", "action": "search"},
                    {"thought": "Step 2", "action": "summarize"}
                ],
                final_conclusion="The answer is 42",
                agent_id="test-agent"
            )
            
            assert result.signature == "reasoning_sig"
            call_args = mock_sign.call_args
            assert call_args[1]["output"]["step_count"] == 2


class TestSignFunctionCall:
    """Tests for sign_function_call function."""
    
    def test_sign_function_call(self):
        """Test function call signing."""
        with patch("moss_hermes.signing.sign") as mock_sign:
            mock_sign.return_value = MagicMock(
                signature="func_sig",
                blocked=False,
            )
            
            from moss_hermes import sign_function_call
            
            result = sign_function_call(
                function_name="get_weather",
                arguments={"city": "NYC"},
                result={"temp": 72},
                agent_id="test-agent"
            )
            
            assert result.signature == "func_sig"
            call_args = mock_sign.call_args
            assert call_args[1]["action"] == "hermes_function:get_weather"


class TestKillSwitch:
    """Tests for kill-switch functionality."""
    
    def test_check_kill_switch_active(self):
        """Test kill-switch check returns True for active agent."""
        with patch("moss_hermes.kill_switch.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"status": "active"}
            )
            
            from moss_hermes import check_kill_switch
            
            result = check_kill_switch(
                "test-agent",
                moss_api_key="test_key"
            )
            
            assert result is True
    
    def test_check_kill_switch_revoked(self):
        """Test kill-switch check returns False for revoked agent."""
        with patch("moss_hermes.kill_switch.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"status": "revoked"}
            )
            
            from moss_hermes import check_kill_switch
            
            result = check_kill_switch(
                "test-agent",
                moss_api_key="test_key"
            )
            
            assert result is False

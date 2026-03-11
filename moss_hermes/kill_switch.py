"""
MOSS Hermes Kill-Switch Integration

Monitors the MOSS Kill-Switch API and terminates agent capabilities if revoked.

Example:
    from moss_hermes import KillSwitchMonitor
    
    monitor = KillSwitchMonitor(
        agent_id="hermes-trading-bot",
        moss_api_key="moss_live_xxx",
        on_revoked=lambda: sys.exit(1)
    )
    
    # Start monitoring in background
    monitor.start()
    
    # Run your agent
    agent.run()
"""

import os
import time
import threading
from typing import Callable, Optional
import requests


class KillSwitchMonitor:
    """
    Monitor MOSS kill-switch status and respond to revocations.
    
    When an agent is revoked via the MOSS console or API, this monitor
    will detect it and call the on_revoked callback.
    """
    
    def __init__(
        self,
        agent_id: str,
        *,
        moss_api_key: Optional[str] = None,
        moss_api_url: str = "https://api.mosscomputing.com",
        check_interval_seconds: int = 10,
        on_revoked: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        """
        Initialize the kill-switch monitor.
        
        Args:
            agent_id: The agent ID to monitor
            moss_api_key: MOSS API key (or set MOSS_API_KEY env var)
            moss_api_url: MOSS API base URL
            check_interval_seconds: How often to check status (default 10s)
            on_revoked: Callback when agent is revoked
            on_error: Callback on API errors
        """
        self.agent_id = agent_id
        self.moss_api_key = moss_api_key or os.environ.get("MOSS_API_KEY")
        self.moss_api_url = moss_api_url.rstrip("/")
        self.check_interval = check_interval_seconds
        self.on_revoked = on_revoked or self._default_on_revoked
        self.on_error = on_error
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._revoked = False
    
    @property
    def is_revoked(self) -> bool:
        """Check if agent has been revoked."""
        return self._revoked
    
    @property
    def is_running(self) -> bool:
        """Check if monitor is running."""
        return self._running
    
    def start(self):
        """Start the kill-switch monitor in a background thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the kill-switch monitor."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def check_status(self) -> bool:
        """
        Check if agent is still active (not revoked).
        
        Returns:
            True if active, False if revoked
        """
        if not self.moss_api_key:
            return True  # No API key = assume active
        
        try:
            response = requests.get(
                f"{self.moss_api_url}/v1/agents/{self.agent_id}",
                headers={"Authorization": f"Bearer {self.moss_api_key}"},
                timeout=5,
            )
            
            if response.status_code == 404:
                # Agent not found
                return False
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "active")
                return status == "active"
            
            return True  # On error, assume active
            
        except Exception as e:
            if self.on_error:
                self.on_error(e)
            return True  # On error, assume active
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self._running:
            if not self.check_status():
                self._revoked = True
                self._running = False
                self.on_revoked()
                return
            
            time.sleep(self.check_interval)
    
    @staticmethod
    def _default_on_revoked():
        """Default revocation handler - raises exception."""
        raise AgentRevokedException("Agent has been revoked via MOSS kill-switch")


class AgentRevokedException(Exception):
    """Raised when an agent is revoked via MOSS kill-switch."""
    pass


def check_kill_switch(
    agent_id: str,
    *,
    moss_api_key: Optional[str] = None,
    moss_api_url: str = "https://api.mosscomputing.com",
) -> bool:
    """
    One-time check if agent is revoked.
    
    Args:
        agent_id: The agent ID to check
        moss_api_key: MOSS API key
        moss_api_url: MOSS API base URL
    
    Returns:
        True if agent is active, False if revoked
    
    Example:
        from moss_hermes import check_kill_switch
        
        if not check_kill_switch("my-agent"):
            print("Agent has been revoked!")
            sys.exit(1)
    """
    monitor = KillSwitchMonitor(
        agent_id=agent_id,
        moss_api_key=moss_api_key,
        moss_api_url=moss_api_url,
    )
    return monitor.check_status()

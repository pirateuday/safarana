from __future__ import annotations
from typing import Dict, Any, List, Optional
import time
from pydantic import BaseModel, Field
from tools.registry import ToolRegistry, registry

class AgentMessage(BaseModel):
    sender: str
    recipient: str
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: str = "SUCCESS"
    notes: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)

class BaseAgent:
    def __init__(self, name: str, role: str, description: str, tool_registry: ToolRegistry = registry):
        self.name = name
        self.role = role
        self.description = description
        self.tools = tool_registry
        self.history: List[AgentMessage] = []

    def log_step(self, recipient: str, action: str, payload: Dict[str, Any], notes: Optional[str] = None, status: str = "SUCCESS") -> AgentMessage:
        msg = AgentMessage(
            sender=self.name,
            recipient=recipient,
            action=action,
            payload=payload,
            status=status,
            notes=notes
        )
        self.history.append(msg)
        return msg

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        return self.tools.execute(tool_name, **kwargs)

    def to_trace_dict(self) -> List[Dict[str, Any]]:
        return [
            {
                "sender": m.sender,
                "recipient": m.recipient,
                "action": m.action,
                "status": m.status,
                "notes": m.notes,
                "timestamp": m.timestamp,
                "summary": f"[{m.sender} ➔ {m.recipient}] {m.action}: {m.notes or ''}"
            }
            for m in self.history
        ]

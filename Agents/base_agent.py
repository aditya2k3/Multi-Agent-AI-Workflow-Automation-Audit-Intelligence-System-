from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all audit agents"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logs = []
        
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log agent actions for debugging and monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "action": action,
            "details": details or {}
        }
        self.logs.append(log_entry)
        print(f"[{self.name}] {action}: {json.dumps(details or {}, indent=2)}")
    
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data and return results"""
        pass
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all agent logs"""
        return self.logs
    
    def clear_logs(self):
        """Clear agent logs"""
        self.logs = []

from typing import Dict, List
from pydantic_ai.messages import ModelMessage
from datetime import datetime, timedelta

class ChatHistoryManager:
    def __init__(self, max_history_age: int = 30):
        self.sessions: Dict[str, List[ModelMessage]] = {}
        self.session_timestamps: Dict[str, datetime] = {}
        self.max_history_age = timedelta(minutes=max_history_age)

    def add_message(self, session_id: str, message: ModelMessage) -> None:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(message)
        self.session_timestamps[session_id] = datetime.now()

    def get_history(self, session_id: str) -> List[ModelMessage]:
        self.cleanup_old_sessions()
        return self.sessions.get(session_id, [])

    def cleanup_old_sessions(self) -> None:
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, timestamp in self.session_timestamps.items()
            if current_time - timestamp > self.max_history_age
        ]
        for session_id in expired_sessions:
            del self.sessions[session_id]
            del self.session_timestamps[session_id]
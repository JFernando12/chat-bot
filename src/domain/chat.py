# domain/chat.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ChatTurn:
    user: str
    assistant: Optional[str] = None

@dataclass
class Conversation:
    """Representa el estado de una conversación."""
    turns: list[ChatTurn] = field(default_factory=list)

    def add_turn(self, user_msg: str, assistant_msg: Optional[str] = None):
        self.turns.append(ChatTurn(user=user_msg, assistant=assistant_msg))

    def get_history_text(self, last_n: int = 5) -> str:
        recent = self.turns[-last_n:]
        return "\n".join([f"U: {t.user}\nA: {t.assistant or ''}" for t in recent])

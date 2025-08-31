import uuid
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .models import Conversation, Message, MessageRole

logger = logging.getLogger(__name__)


class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
    
    def create_conversation(self) -> str:
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = Conversation(
            id=conversation_id,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        logger.info(f"Created new conversation: {conversation_id}")
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return self.conversations.get(conversation_id)
    
    def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Conversation {conversation_id} not found")
            return False
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        conversation.messages.append(message)
        conversation.updated_at = datetime.now()
        logger.info(f"Added message to conversation {conversation_id}")
        return True
    
    def get_messages(self, conversation_id: str) -> List[Message]:
        conversation = self.get_conversation(conversation_id)
        if conversation:
            return conversation.messages
        return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation {conversation_id}")
            return True
        return False
    
    def list_conversations(self) -> List[Dict]:
        return [
            {
                "id": conv.id,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": len(conv.messages)
            }
            for conv in self.conversations.values()
        ]
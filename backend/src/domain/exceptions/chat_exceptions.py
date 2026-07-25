class ConversationNotFoundError(Exception):
    """Exception raised when a requested conversation ID does not exist or belong to the user."""

    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        super().__init__(f"Conversation with ID '{conversation_id}' was not found.")


class MessageProcessingError(Exception):
    """Exception raised when processing a chat Q&A message fails."""

    def __init__(self, message: str = "Chat message processing failure"):
        self.message = message
        super().__init__(self.message)

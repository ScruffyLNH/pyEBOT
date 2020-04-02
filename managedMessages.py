from pydantic import BaseModel
from typing import List


class Message(BaseModel):

    id: int
    content: str
    last: bool = False


class Commentor:

    id: int
    name: str
    messages: List[Message] = []

    @property
    def removeMessage(self):
        # Return last message and remove it from list
        if self.messages:
            return self.messages.pop()
        else:
            return False

    def addMessage(self, message):
        self.messages.append(message)
        # Limit the amount of messages to store.
        self.messages = self.messages[-3000:]
        self.messages[0].last = True


class ManagedMessages(BaseModel):
    """Stores people (commentors) and their messages if they have posted messages
    in a moderated channel.
    """

    commentors: List[Commentor] = []

    def addCommentor(self, commentor):
        self.commentors.append(commentor)

    def removeCommentor(self, commentor):
        self.commentors[:] = [c for c in self.commentors if not c == commentor]

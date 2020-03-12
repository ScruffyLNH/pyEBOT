class ManagedMessages:
    """Stores people (commentors) and their messages if they have posted messages
    in a moderated channel.
    """

    def __init__(self):
        self.commentors = []

    def addCommentor(self, commentor):
        self.commentors.append(commentor)

    def removeCommentor(self, commentor):
        self.commentors[:] = [c for c in self.commentors if not c == commentor]


class Message:
    def __init__(self, id, content):
        self.id = id
        self.content = content
        self.last = False


class Commentor:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.messages = []

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

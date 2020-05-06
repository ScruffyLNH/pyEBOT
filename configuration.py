from pydantic import BaseModel


class Configuration(BaseModel):

    guildId: int = None
    mainCategoryChannelId: int = None
    signupChannelId: int = None
    discussionChannelId: int = None
    archiveChannelId: int = None
    defaultVoiceChannelId: int = None
    adminChannelId: int = None
    adminId: int = 312381318891700224
    eventManagerId: int = None
    eventManagerRoleId: int = None
    memberRoleId: int = None
    collaboratorRoleId: int = None

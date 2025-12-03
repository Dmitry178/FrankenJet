# ruff: noqa

from app.db.models.aircraft import (
    Aircraft,
)
from app.db.models.articles import (
    Articles,
    ArticlesTagsAssociation,
    Tags,
    TagsCategories,
)
from app.db.models.auth import (
    RefreshTokens,
)
from app.db.models.chatbot import (
    ChatBotSettings,
    ChatHistory,
)
from app.db.models.countries import (
    Countries,
)
from app.db.models.facts import (
    Facts,
)
from app.db.models.knowledge_base import (
    ProjectKnowledge,
)
from app.db.models.users import (
    Roles,
    Users,
    UsersRolesAssociation,
)

__all__ = [
    "Aircraft",
    "Articles",
    "ArticlesTagsAssociation",
    "ChatBotSettings",
    "ChatHistory",
    "Countries",
    "Facts",
    "ProjectKnowledge",
    "RefreshTokens",
    "Roles",
    "Tags",
    "TagsCategories",
    "Users",
    "UsersRolesAssociation",
]

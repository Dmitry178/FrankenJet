""" Константы настроек приложения """

# JWT
JWT_TYPE_ACCESS = "access"
JWT_TYPE_REFRESH = "refresh"
JWT_ALGORITHM: str = "HS256"  # TODO: переделать на RS256
JWT_ACCESS_EXPIRE_MINUTES: int = 15  # время жизни access-токена (в минутах)
JWT_REFRESH_EXPIRE_MINUTES: int = 60 * 24 * 30  # время жизни refresh-токена (в минутах)

# OAuth2
OAUTH2_GOOGLE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH2_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"  # nosec B105
OAUTH2_GOOGLE_REDIRECT_URL = "http://localhost:3000/auth/google"  # TODO: переделать с учётом test и production
OAUTH2_VK_URL = "https://id.vk.com/authorize"
OAUTH2_VK_TOKEN_URL = "https://api.vk.com/method/auth.exchangeSilentAuthToken"  # nosec B105
OAUTH2_VK_REDIRECT_URL = "http://localhost/auth/vk"  # TODO: переделать с учётом test и production
# VK при использовании http поддерживает только localhost (без порта)  # TODO учесть этот момент

# очереди RabbitMQ
RMQ_FJ_OUTPUT_QUEUE = "fj_output"  # очередь для приёма сообщений ботом от бэкенда
RMQ_FJ_INPUT_QUEUE = "fj_input"  # очередь для приёма сообщения бэкендом от бота

# настройки S3
BUCKET_IMAGES = "images"

# настройки индексов Elasticsearch
ARTICLES_INDEX_NAME = "articles"
RAGBOT_INDEX_NAME = "rag-bot"

# настройки GigaChat API
GIGACHAT_USER_MESSAGE_MAX_SIZE = 200  # максимальная длина сообщения от пользователя

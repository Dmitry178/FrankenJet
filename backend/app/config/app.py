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
RMQ_NOTIFICATIONS_QUEUE = "notification"  # уведомления бота
RMQ_ADMIN_AUTH_QUEUE = "admin_auth"  # уведомление об аутентификации админа
RMQ_MODERATION_QUEUE = "moderation"  # комментарии на модерацию
RMQ_BACKEND_QUEUE = "backend_bot"  # очередь для приёма сообщения бэкендом от бота

# настройки S3
BUCKET_IMAGES = "images"

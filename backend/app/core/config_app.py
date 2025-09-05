OAUTH2_GOOGLE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH2_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
OAUTH2_GOOGLE_REDIRECT_URL = "http://localhost:3000/auth/google"  # TODO: переделать с учётом test и production

OAUTH2_VK_URL = "https://id.vk.com/authorize"
OAUTH2_VK_TOKEN_URL = "https://api.vk.com/method/auth.exchangeSilentAuthToken"
OAUTH2_VK_REDIRECT_URL = "http://localhost/auth/vk"  # TODO: переделать с учётом test и production
# VK при использовании http поддерживает только localhost (без порта)  # TODO учесть этот момент

# типы токенов
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

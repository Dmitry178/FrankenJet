from fastapi.params import Example

login_example = {
    "example": Example(
        summary="Default login",
        value={
            "email": "user@example.com",
            "password": "password",
        }
    )
}

notification_example = {
    "example": Example(
        summary="Notification",
        value={
            "notification": "Здесь должно быть какое-нибудь уведомление",
        }
    )
}

moderation_example = {
    "example": Example(
        summary="Moderation",
        value={
            "id": 1,
            "comment": "Когда будут статьи про рецепт приготовления плюшек к кофе?",
        }
    )
}
